/// 领域模型：题目 / 作答日志 / 题库包清单
///
/// 与设计方案 §3.3 表结构对应：questions / answer_logs / card_scheduling /
/// settings。判分等纯函数在 data/grading.dart。
library;

import 'dart:convert';

/// 题型枚举（对应题库包 JSON 的字符串编码）
enum QuestionType {
  singleChoice('single_choice'),
  multiChoice('multi_choice'),
  blank('blank'),
  shortAnswer('short_answer'),
  trueFalse('true_false');

  const QuestionType(this.json);

  /// 题库包 JSON 中的编码
  final String json;

  static QuestionType fromJson(String value) =>
      QuestionType.values.firstWhere((t) => t.json == value,
          orElse: () => throw FormatException('未知题型: $value'));
}

/// 单选题选项
class QuestionOption {
  const QuestionOption({required this.key, required this.text});

  final String key;
  final String text;

  Map<String, dynamic> toJson() => {'key': key, 'text': text};

  static QuestionOption fromJson(Map<String, dynamic> json) =>
      QuestionOption(key: json['key'] as String, text: json['text'] as String);
}

/// 题目（对应 questions 表）
class Question {
  const Question({
    required this.id,
    required this.bankId,
    required this.type,
    required this.stem,
    this.options = const [],
    required this.answer,
    this.explanation = '',
    this.chapter = '',
    this.tags = const [],
    this.difficulty = 'medium',
    this.purpose = '',
    this.answerFormat,
    this.answerVariants = const [],
    this.knowledgeId,
    this.status = 'active',
    this.sourceBlockId,
    this.sourceDocPath,
    this.createdAt,
    this.updatedAt,
    this.userEdited = false,
  });

  final String id;
  final String bankId;
  final QuestionType type;
  final String stem;
  final List<QuestionOption> options;

  /// 标准答案，统一编码为字符串集合（见设计方案 §2.4）：
  /// 单选/判断 = 单元素；多选 = 多个选项 key；填空 = 参考答案（可多个）；
  /// 简答 = 单个参考答案文本。
  final Set<String> answer;
  final String explanation;
  final String chapter;
  final List<String> tags;
  final String difficulty;

  /// 题目类别（v0.9.0 双轨）：basic=辅助记忆的基础题，test=检验回忆与答案组织的测试题。
  /// 空白/缺省时视为普通练习（旧包兼容），不分区。
  final String purpose;

  /// 答题格式提示（v3，仅 short_answer 类可带，如名解/翻译/论述的作答格式）
  final String? answerFormat;

  /// 等价答案分组（v0.9.0）：填空按"空"分组、简答按"要点"分组，
  /// 组内任一命中即该空/该要点判对（如"夸大"=“夸饰”）。
  /// 无此字段的题走原判分逻辑，完全兼容旧包。
  final List<List<String>> answerVariants;

  /// 绑定的知识点 id（v4，对应题库包 knowledge 树节点；旧包无此字段为 null）
  final String? knowledgeId;

  /// active / archived（题库包更新时软归档，保留作答历史）
  final String status;

  /// 来源思源笔记块（容错字段，非外键；块被删后降级为纯文本展示）
  final String? sourceBlockId;
  final String? sourceDocPath;
  final int? createdAt;
  final int? updatedAt;

  /// 用户是否本地修改过此题（题目编辑保存后置 true）。
  /// 内置式题库更新时，user_edited=true 的题跳过 REPLACE，保留本地版本。
  final bool userEdited;

  Question copyWith({
    String? stem,
    String? explanation,
    Set<String>? answer,
    List<List<String>>? answerVariants,
    String? status,
    String? chapter,
    String? purpose,
    List<QuestionOption>? options,
  }) => Question(
        id: id,
        bankId: bankId,
        type: type,
        stem: stem ?? this.stem,
        options: options ?? this.options,
        answer: answer ?? this.answer,
        explanation: explanation ?? this.explanation,
        answerVariants: answerVariants ?? this.answerVariants,
        chapter: chapter ?? this.chapter,
        tags: tags,
        difficulty: difficulty,
        purpose: purpose ?? this.purpose,
        answerFormat: answerFormat,
        status: status ?? this.status,
        knowledgeId: knowledgeId,
        sourceBlockId: sourceBlockId,
        sourceDocPath: sourceDocPath,
        createdAt: createdAt,
        updatedAt: updatedAt,
        userEdited: userEdited,
      );

  /// 题库包 JSON 项 → 模型（设计方案 §2.4；v3 支持 answerFormat）
  factory Question.fromBankJson(Map<String, dynamic> json, {required String bankId}) {
    final rawAnswer = json['answer'];
    final type = QuestionType.fromJson(json['type'] as String);
    final options = (json['options'] as List<dynamic>? ?? const [])
        .map((e) => QuestionOption.fromJson(e as Map<String, dynamic>))
        .toList();
    // v4：选择题 answer 编码为正确项文本，映射回选项 key（旧包为 key 则原样保留）
    final answer = (type == QuestionType.singleChoice ||
            type == QuestionType.multiChoice)
        ? _mapChoiceAnswer(_decodeAnswer(rawAnswer), options)
        : _decodeAnswer(rawAnswer);
    return Question(
      id: json['id'] as String,
      bankId: bankId,
      type: type,
      stem: json['stem'] as String,
      options: options,
      answer: answer,
      explanation: json['explanation'] as String? ?? '',
      chapter: json['chapter'] as String? ?? '',
      tags: (json['tags'] as List<dynamic>? ?? const []).cast<String>(),
      difficulty: json['difficulty'] as String? ?? 'medium',
      purpose: json['purpose'] as String? ?? '',
      answerFormat: json['answerFormat'] as String?,
      answerVariants: _decodeVariants(json['answerVariants']),
      knowledgeId: json['knowledgeId'] as String?,
      sourceBlockId: (json['source'] as Map<String, dynamic>?)?['blockId'] as String?,
      sourceDocPath: (json['source'] as Map<String, dynamic>?)?['docPath'] as String?,
    );
  }

  /// 选择题答案编码归一：若 answer 元素已是选项 key（单字符）则原样保留（旧包）；
  /// 否则视为 v4 正确项文本，映射回对应选项 key。
  static Set<String> _mapChoiceAnswer(
      Set<String> answer, List<QuestionOption> options) {
    if (answer.isEmpty || options.isEmpty) return answer;
    final keys = {for (final o in options) o.key};
    final allKeys = answer.every((a) => a.length == 1 && keys.contains(a));
    if (allKeys) return answer;
    final textToKey = {for (final o in options) o.text: o.key};
    return answer.map((a) => textToKey[a] ?? a).toSet();
  }

  /// 统一答案编码：字符串 → 单元素集合；数组 → 集合
  static Set<String> _decodeAnswer(dynamic raw) {
    if (raw == null) return const {};
    if (raw is String) return {raw};
    if (raw is List) return raw.cast<String>().toSet();
    throw FormatException('answer 编码不符合约定: $raw');
  }

  /// 等价答案解码：[[“夸大”,“夸饰”],[“谦辞”,“谦敬词”]] → 分组列表；空/缺省 → []
  static List<List<String>> _decodeVariants(dynamic raw) {
    if (raw is! List) return const [];
    final result = <List<String>>[];
    for (final group in raw) {
      if (group is List) {
        result.add(group.whereType<String>().toList());
      }
    }
    return result;
  }

  // ---------- 数据库映射 ----------

  Map<String, dynamic> toMap() => {
        'id': id,
        'bank_id': bankId,
        'type': type.json,
        'stem': stem,
        'options': _encodeOptions(),
        'answer': _encodeAnswer(),
        'explanation': explanation,
        'chapter': chapter,
        'tags': tags.isEmpty ? null : _encodeJson(tags), // 审查 P2-8：JSON 数组存储
        'difficulty': difficulty,
        'purpose': purpose.isEmpty ? null : purpose,
        'answer_format': answerFormat,
        'answer_variants':
            answerVariants.isEmpty ? null : _encodeJson(answerVariants),
        'knowledge_id': knowledgeId,
        'status': status,
        'source_block_id': sourceBlockId,
        'source_doc_path': sourceDocPath,
        'created_at': createdAt,
        'updated_at': updatedAt,
        'user_edited': userEdited ? 1 : 0,
      };

  static Question fromMap(Map<String, dynamic> row) => Question(
        id: row['id'] as String,
        bankId: row['bank_id'] as String,
        type: QuestionType.fromJson(row['type'] as String),
        stem: row['stem'] as String,
        options: _decodeOptions(row['options'] as String?),
        answer: _decodeAnswerDb(row['answer'] as String?),
        explanation: row['explanation'] as String? ?? '',
        chapter: row['chapter'] as String? ?? '',
        tags: _decodeTags(row['tags'] as String?),
        difficulty: row['difficulty'] as String? ?? 'medium',
        purpose: row['purpose'] as String? ?? '',
        answerFormat: row['answer_format'] as String?,
        answerVariants: _decodeVariantsDb(row['answer_variants'] as String?),
        knowledgeId: row['knowledge_id'] as String?,
        status: row['status'] as String? ?? 'active',
        sourceBlockId: row['source_block_id'] as String?,
        sourceDocPath: row['source_doc_path'] as String?,
        createdAt: row['created_at'] as int?,
        updatedAt: row['updated_at'] as int?,
        userEdited: (row['user_edited'] as int? ?? 0) == 1,
      );

  String _encodeOptions() =>
      options.isEmpty ? '' : _encodeJson(options.map((o) => o.toJson()).toList());

  /// answer 序列化为 JSON 数组，保证与题库包编码一致（"C" 也存为 ["C"]）
  String _encodeAnswer() => _encodeJson(answer.toList()..sort());

  static Set<String> _decodeAnswerDb(String? raw) {
    if (raw == null || raw.isEmpty) return const {};
    final decoded = _decodeJson(raw);
    return decoded is List ? decoded.cast<String>().toSet() : {decoded.toString()};
  }

  /// 等价答案（DB 版）解码：JSON 字符串 → 分组列表
  static List<List<String>> _decodeVariantsDb(String? raw) {
    if (raw == null || raw.isEmpty) return const [];
    try {
      return _decodeVariants(_decodeJson(raw));
    } on FormatException {
      return const [];
    }
  }

  static List<QuestionOption> _decodeOptions(String? raw) {
    if (raw == null || raw.isEmpty) return const [];
    final decoded = _decodeJson(raw);
    return (decoded as List<dynamic>)
        .map((e) => QuestionOption.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  /// 标签解码：优先 JSON 数组，兼容旧版逗号分隔（审查 P2-8）
  static List<String> _decodeTags(String? raw) {
    if (raw == null || raw.isEmpty) return const [];
    try {
      final decoded = _decodeJson(raw);
      if (decoded is List) return decoded.cast<String>().toList();
    } on FormatException {
      // fallthrough 到旧格式
    }
    return raw.split(',').where((t) => t.isNotEmpty).toList();
  }
}

/// 作答日志（对应 answer_logs 表，append-only）
class AnswerLog {
  const AnswerLog({
    required this.questionId,
    required this.mode,
    required this.result,
    this.rating,
    required this.timeMs,
    required this.answeredAt,
    this.sessionId,
    this.userAnswer,
  });

  final String questionId;

  /// learn / review / wrong_rework / mock / browse（设计方案 §3.5）
  final String mode;

  /// correct / wrong / partial / skip
  final String result;

  /// SRS 评分 1..4（Again/Hard/Good/Easy），仅 review/learn 有
  final int? rating;

  /// 单题用时（毫秒）
  final int timeMs;

  /// 作答时间（epoch ms）
  final int answeredAt;

  /// 关联模拟卷会话（仅 mock 模式，v3）
  final int? sessionId;

  /// 用户作答快照（v10，模拟卷逐题回顾用；选择题为选项 key 如"A、B"，填空/简答为文本）
  final String? userAnswer;

  Map<String, dynamic> toMap() => {
        'question_id': questionId,
        'mode': mode,
        'result': result,
        'rating': rating,
        'time_ms': timeMs,
        'answered_at': answeredAt,
        'session_id': sessionId,
        'user_answer': userAnswer,
      };

  static AnswerLog fromMap(Map<String, dynamic> row) => AnswerLog(
        questionId: row['question_id'] as String,
        mode: row['mode'] as String,
        result: row['result'] as String,
        rating: row['rating'] as int?,
        timeMs: row['time_ms'] as int,
        answeredAt: row['answered_at'] as int,
        sessionId: row['session_id'] as int?,
        userAnswer: row['user_answer'] as String?,
      );
}

/// 模拟卷（需求：题库含模拟卷，formatVersion=2，mock_papers 表）
class MockPaper {
  const MockPaper({
    required this.id,
    required this.bankId,
    required this.name,
    required this.durationMin,
    required this.questionIds,
    this.status = 'active',
  });

  /// {bank_id}:{paper_id}，全局唯一
  final String id;
  final String bankId;
  final String name;
  final int durationMin;

  /// 按序题目 id 列表（JSON 存储）
  final List<String> questionIds;
  final String status;

  factory MockPaper.fromBankJson(Map<String, dynamic> json, {required String bankId}) =>
      MockPaper(
        id: json['id'] as String,
        bankId: bankId,
        name: json['name'] as String,
        durationMin: json['durationMin'] as int? ?? 60,
        questionIds:
            (json['questionIds'] as List<dynamic>? ?? const []).cast<String>(),
      );

  Map<String, dynamic> toMap() => {
        'id': id,
        'bank_id': bankId,
        'name': name,
        'duration_min': durationMin,
        'question_ids': const JsonEncoder().convert(questionIds),
        'status': status,
      };

  static MockPaper fromMap(Map<String, dynamic> row) => MockPaper(
        id: row['id'] as String,
        bankId: row['bank_id'] as String,
        name: row['name'] as String,
        durationMin: row['duration_min'] as int,
        questionIds:
            ((row['question_ids'] as String?)?.isEmpty ?? true)
                ? const []
                : (const JsonDecoder().convert(row['question_ids'] as String)
                        as List<dynamic>)
                    .cast<String>(),
        status: row['status'] as String? ?? 'active',
      );
}

/// 模拟卷成绩单（mock_sessions 表）
class MockSession {
  const MockSession({
    this.id,
    required this.paperId,
    required this.startedAt,
    required this.durationMin,
    required this.total,
    required this.correct,
    required this.partial,
    required this.wrong,
    required this.skipped,
    required this.score,
    required this.submittedAt,
  });

  final int? id;
  final String paperId;
  final int startedAt;
  final int durationMin;
  final int total;
  final int correct;
  final int partial;
  final int wrong;
  final int skipped;

  /// 百分制得分
  final int score;
  final int submittedAt;

  Map<String, dynamic> toMap() => {
        if (id != null) 'id': id,
        'paper_id': paperId,
        'started_at': startedAt,
        'duration_min': durationMin,
        'total': total,
        'correct': correct,
        'partial': partial,
        'wrong': wrong,
        'skipped': skipped,
        'score': score,
        'submitted_at': submittedAt,
      };

  static MockSession fromMap(Map<String, dynamic> row) => MockSession(
        id: row['id'] as int,
        paperId: row['paper_id'] as String,
        startedAt: row['started_at'] as int,
        durationMin: row['duration_min'] as int,
        total: row['total'] as int,
        correct: row['correct'] as int,
        partial: row['partial'] as int,
        wrong: row['wrong'] as int,
        skipped: row['skipped'] as int,
        score: row['score'] as int,
        submittedAt: row['submitted_at'] as int,
      );
}

/// 题库包清单（manifest，设计方案 §2.4）
/// 章节分组（v3 两级 chapters：group → chapters，如 上编/中编/下编）
class ReviewFlag {
  const ReviewFlag({
    required this.questionId,
    required this.bankId,
    this.comment,
    required this.createdAt,
  });

  final String questionId;
  final String bankId;

  /// 用户备注（如"答案错误""题干歧义""重复"），可为空
  final String? comment;
  final int createdAt;

  Map<String, dynamic> toMap() => {
        'question_id': questionId,
        'bank_id': bankId,
        'comment': comment,
        'created_at': createdAt,
      };

  static ReviewFlag fromMap(Map<String, dynamic> row) => ReviewFlag(
        questionId: row['question_id'] as String,
        bankId: row['bank_id'] as String,
        comment: row['comment'] as String?,
        createdAt: row['created_at'] as int? ?? 0,
      );
}

class ChapterGroup {
  const ChapterGroup({required this.group, required this.chapters});

  final String group;
  final List<String> chapters;

  factory ChapterGroup.fromJson(Map<String, dynamic> json) => ChapterGroup(
        group: json['group'] as String,
        chapters: (json['chapters'] as List<dynamic>? ?? const []).cast<String>(),
      );
}

/// 知识点树节点（v4，manifest.knowledge）
class KnowledgePoint {
  const KnowledgePoint({
    required this.id,
    required this.name,
    required this.chapter,
    this.parent,
    this.summary = '',
    this.hot = false,
    this.examRef = '',
    this.questionCount = 0,
  });

  final String id;
  final String name;
  final String chapter;

  /// 父级知识点 id（当前为占位根节点时可为空）
  final String? parent;
  final String summary;

  /// 高频考点标记
  final bool hot;
  final String examRef;

  /// 该知识点在包内绑定的基础题数
  final int questionCount;

  factory KnowledgePoint.fromJson(Map<String, dynamic> json) => KnowledgePoint(
        id: json['id'] as String,
        name: json['name'] as String,
        chapter: json['chapter'] as String? ?? '',
        parent: json['parent'] as String?,
        summary: json['summary'] as String? ?? '',
        hot: json['hot'] as bool? ?? false,
        examRef: json['examRef'] as String? ?? '',
        questionCount: json['questionCount'] as int? ?? 0,
      );
}

/// 章节知识概览（v4，manifest.overviews）
class ChapterOverview {
  const ChapterOverview({
    required this.chapter,
    this.knowledgeCount = 0,
    this.questionCount = 0,
    this.summary = '',
  });

  final String chapter;
  final int knowledgeCount;
  final int questionCount;
  final String summary;

  factory ChapterOverview.fromJson(Map<String, dynamic> json) => ChapterOverview(
        chapter: json['chapter'] as String,
        knowledgeCount: json['knowledgeCount'] as int? ?? 0,
        questionCount: json['questionCount'] as int? ?? 0,
        summary: json['summary'] as String? ?? '',
      );
}

class BankManifest {
  const BankManifest({
    required this.formatVersion,
    required this.bankId,
    required this.name,
    required this.version,
    this.idSchema,
    this.chapterGroups = const [],
    this.knowledge = const [],
    this.overviews = const [],
  });

  final int formatVersion;
  final String bankId;
  final String name;
  final String version;

  /// 题 id 体系标识（v1.1.3）：v0.12 起为 'q-b'（题 id 用 q_/b_ 前缀）；
  /// 旧包（v0.11 及更早，kb_ 前缀）无此字段。idSchema 变化 = 不兼容升级，
  /// 导入时整库重建（见 seed_loader），避免旧题被整批软归档堆积。
  final String? idSchema;

  /// 两级章节分组（v3）；旧包可转为 [{group:'全部', chapters:[...]}]
  final List<ChapterGroup> chapterGroups;

  /// 知识点树（v4；旧包为空列表）
  final List<KnowledgePoint> knowledge;

  /// 章节知识概览（v4；旧包为空列表）
  final List<ChapterOverview> overviews;

  static const int supportedFormatVersion = 4;

  factory BankManifest.fromJson(Map<String, dynamic> json) {
    final raw = json['chapters'] as List<dynamic>? ?? const [];
    List<ChapterGroup> groups;
    if (raw.isEmpty || raw.first is String) {
      // v2/v3 兼容：字符串数组 → 单个「全部」分组
      groups = raw.isEmpty
          ? const []
          : [ChapterGroup(group: '全部', chapters: raw.cast<String>())];
    } else {
      groups = raw
          .map((e) => ChapterGroup.fromJson(e as Map<String, dynamic>))
          .toList();
    }
    return BankManifest(
      formatVersion: json['formatVersion'] as int,
      bankId: json['bankId'] as String,
      name: json['name'] as String,
      version: json['version'] as String,
      idSchema: json['idSchema'] as String?,
      chapterGroups: groups,
      knowledge: (json['knowledge'] as List<dynamic>? ?? const [])
          .map((e) => KnowledgePoint.fromJson(e as Map<String, dynamic>))
          .toList(),
      overviews: (json['overviews'] as List<dynamic>? ?? const [])
          .map((e) => ChapterOverview.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }

  /// 校验清单是否兼容；不兼容抛 [FormatException]
  void validate() {
    if (formatVersion > supportedFormatVersion) {
      throw FormatException(
          '题库包版本过新: formatVersion=$formatVersion（本 App 支持 ≤ $supportedFormatVersion），请升级 App');
    }
  }
}

/// 学习统计（设计方案 §3.8，M3）
class StudyStats {
  const StudyStats({
    required this.totalAnswered,
    required this.correctCount,
    required this.partialCount,
    required this.wrongCount,
    required this.totalTimeMs,
    required this.dueCount,
    required this.byChapter,
    required this.daily,
    this.typeDistribution = const {},
    this.resultDistribution = const {},
  });

  final int totalAnswered;
  final int correctCount;
  final int partialCount;
  final int wrongCount;
  final int totalTimeMs;
  final int dueCount;

  /// 各章节：题数/正确/错误
  final List<ChapterStats> byChapter;

  /// 最近 N 天每日做题数（index N-1 = 今天，由早到晚；审查 P2-5 修正注释）
  final List<DailyData> daily;

  /// 题型分布（饼图）：single_choice → 已做题数
  final Map<String, int> typeDistribution;

  /// 作答结果分布（饼图）：correct/wrong/partial/skip → 次数
  final Map<String, int> resultDistribution;

  double get accuracy =>
      totalAnswered == 0 ? 0 : correctCount / totalAnswered * 100;
}

class ChapterStats {
  const ChapterStats({
    this.bankId = '',
    required this.chapter,
    required this.total,
    required this.correct,
    required this.wrong,
  });

  /// 所属题库（多题库：跨库同名章节区分，需求）
  final String bankId;
  final String chapter;
  final int total;
  final int correct;
  final int wrong;

  double get accuracy => total == 0 ? 0 : correct / total * 100;
}

class DailyData {
  const DailyData({required this.day, required this.count});

  final String day;
  final int count;
}

/// 学习目标（P2）：考试日期 + 每日新题/复习目标。
/// 计划倒排结果仅为建议，用户可逐项覆盖/暂停/开关。
class StudyGoal {
  const StudyGoal({
    this.examDate, // yyyy-MM-dd；null=未设
    this.dailyNew = 0,
    this.dailyReview = 0,
    this.enabled = false,
  });

  final String? examDate;
  final int dailyNew;
  final int dailyReview;
  final bool enabled;

  /// 距考试天数（examDate - 今天；未设/已过返回 null）
  int? daysUntilExam(DateTime now) {
    final date = examDate;
    if (date == null) return null;
    final parts = date.split('-');
    if (parts.length != 3) return null;
    final exam = DateTime(
      int.parse(parts[0]),
      int.parse(parts[1]),
      int.parse(parts[2]),
    );
    final today = DateTime(now.year, now.month, now.day);
    final diff = exam.difference(today).inDays;
    return diff < 0 ? null : diff;
  }

  Map<String, dynamic> toJson() => {
        'examDate': examDate,
        'dailyNew': dailyNew,
        'dailyReview': dailyReview,
        'enabled': enabled,
      };

  static StudyGoal fromJson(Map<String, dynamic> json) => StudyGoal(
        examDate: json['examDate'] as String?,
        dailyNew: json['dailyNew'] as int? ?? 0,
        dailyReview: json['dailyReview'] as int? ?? 0,
        enabled: json['enabled'] as bool? ?? false,
      );
}

// ---------- JSON 工具 ----------

String _encodeJson(Object value) => const JsonEncoder().convert(value);

dynamic _decodeJson(String raw) => const JsonDecoder().convert(raw);


/// 背题卡记忆状态（v11 背题存档）
enum MemorizeCardState {
  /// 学习中（背过但未掌握，或尚未连续背会）
  learning,

  /// 已掌握（连续 2 次自评"背会"）
  mastered,
}

/// 背题存档记录（v11）：一张记忆卡（知识点卡或题目卡）的跨会话记忆状态
class MemorizeProgress {
  const MemorizeProgress({
    required this.cardKey,
    required this.bankId,
    required this.chapter,
    required this.cardType,
    this.knowledgeId,
    this.questionId,
    this.state = MemorizeCardState.learning,
    this.correctStreak = 0,
    this.reviewedCount = 0,
    this.lastReviewedAt,
  });

  /// 卡唯一键：知识点卡 `kp:{knowledgeId}`，题目卡 `q:{questionId}`
  final String cardKey;
  final String bankId;
  final String chapter;

  /// 'knowledge' | 'question'
  final String cardType;

  /// 知识点卡关联的知识点 id（cardType=knowledge 时非空）
  final String? knowledgeId;

  /// 题目卡关联的题目 id（cardType=question 时非空）
  final String? questionId;

  final MemorizeCardState state;

  /// 连续"背会"次数（>=2 进入 mastered）
  final int correctStreak;

  /// 累计自评次数
  final int reviewedCount;

  /// 最近一次自评时间
  final DateTime? lastReviewedAt;

  bool get mastered => state == MemorizeCardState.mastered;

  MemorizeProgress copyWith({
    MemorizeCardState? state,
    int? correctStreak,
    int? reviewedCount,
    DateTime? lastReviewedAt,
  }) =>
      MemorizeProgress(
        cardKey: cardKey,
        bankId: bankId,
        chapter: chapter,
        cardType: cardType,
        knowledgeId: knowledgeId,
        questionId: questionId,
        state: state ?? this.state,
        correctStreak: correctStreak ?? this.correctStreak,
        reviewedCount: reviewedCount ?? this.reviewedCount,
        lastReviewedAt: lastReviewedAt ?? this.lastReviewedAt,
      );
}
