/// 刷题页：一次刷题会话（设计方案 §3.5 刷题状态机）
///
/// 交互流程：展示题目 → 作答 → 判分 → 展示解析 → 四档评分
/// （Again/Hard/Good/Easy 进 FSRS 调度）→ 写 answer_logs → 下一题 → 结算页。
///
/// M2 新增：复习模式（review，取到期队列）、错题重刷模式（wrongRework，
/// 连续正确达阈值自动移出错题本）、评分接入 fsrs 调度。
library;

import 'dart:async';
import 'dart:convert';
import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fsrs/fsrs.dart' show Rating;

import '../data/grading.dart';
import '../data/quiz_repository.dart';
import '../models/models.dart';
import '../services/app_log.dart';
import 'theme/ios_animations.dart';
import 'theme/ios_tokens.dart';

import 'theme_controller.dart';

import 'glass_app_bar.dart';
import 'app_toast.dart';
import 'responsive.dart';

part 'practice_question_view.dart';
part 'practice_answer_sheet.dart';
part 'practice_summary.dart';


/// 刷题模式（设计方案 §3.5：模式只决定取哪些题，SRS 只负责到期队列）
enum PracticeMode { learn, review, wrongRework }

/// 题型中文名与主题色
String typeLabel(QuestionType type) => switch (type) {
  QuestionType.singleChoice => '单选',
  QuestionType.multiChoice => '多选',
  QuestionType.blank => '填空',
  QuestionType.shortAnswer => '简答',
  QuestionType.trueFalse => '判断',
};

/// 语义色集中定义（审查 P2：判分/评分色不再散落魔法值）
/// 深色模式用亮色变体保证对比度（UI 复审 P1-1）
const _kSuccessDark = Color(0xFF81C784);
const _kWarning = Color(0xFFB2780A);
const _kWarningDark = Color(0xFFE2B93B);
const _kErrorDark = Color(0xFFF2B8B5);

Color _semantic(BuildContext context, Color light, Color dark) =>
    Theme.of(context).brightness == Brightness.dark ? dark : light;

Color typeColor(BuildContext context, QuestionType type) {
  final dark = Theme.of(context).brightness == Brightness.dark;
  return switch (type) {
    QuestionType.singleChoice =>
      dark ? const Color(0xFF6BD4D8) : const Color(0xFF00696D),
    QuestionType.multiChoice =>
      dark ? const Color(0xFF9FA8DA) : const Color(0xFF525E7D),
    QuestionType.blank =>
      dark ? const Color(0xFFCE93D8) : const Color(0xFF7D5260),
    QuestionType.shortAnswer =>
      dark ? const Color(0xFF80CBC4) : const Color(0xFF4A6364),
    QuestionType.trueFalse => dark ? _kWarningDark : _kWarning,
  };
}

/// 构造方式：
/// - 章节/随机刷：`PracticePage(bankId: ..., chapter: ..., random: true)`
/// - 重点题目合集：`PracticePage(bankId: ..., questions: [...])`
/// - 今日复习：`PracticePage(mode: PracticeMode.review)`
/// - 错题重刷：`PracticePage(mode: PracticeMode.wrongRework)`
class PracticePage extends ConsumerStatefulWidget {
  const PracticePage({
    super.key,
    this.bankId,
    this.chapter,
    this.chapters,
    this.purpose,
    this.random = false,
    this.randomLimit,
    this.questions,
    this.progressKey,
    this.mode = PracticeMode.learn,
  });

  final String? bankId;
  final String? chapter;

  /// 题目类别过滤（v0.9.0 双轨）：basic=基础题，test=测试题，null=全部。
  final String? purpose;

  /// 多章节合集（重点章节刷题用）；与 [chapter] 二选一，优先 [chapters]
  final List<String>? chapters;
  final bool random;

  /// 整本随机刷题量（50/100/150，用户要求）；>0 时按题型顺序排列
  final int? randomLimit;

  /// 预取题目列表（重点题目合集用）；非空时直接刷这批题，跳过重新查询
  final List<Question>? questions;

  /// 刷题范围标识（固定顺序刷题用）：进入时从上次进度继续，退出/切题时保存。
  /// 随机刷/复习/错题重刷不传（每次重新开始属预期行为）。
  final String? progressKey;
  final PracticeMode mode;

  @override
  ConsumerState<PracticePage> createState() => _PracticePageState();
}

class _PracticePageState extends ConsumerState<PracticePage>
    with WidgetsBindingObserver {
  bool _loading = true;
  String? _error;

  final Stopwatch _practiceStopwatch = Stopwatch();
  Timer? _timerRefresh;
  bool _showPracticeTimer = false;
  bool _reviewEnabled = false; // 审题标记开关（默认关，主题定制中开启）
  int _displayedSeconds = 0;
  int _questionStartedElapsedSeconds = 0;
  bool _pageFinished = false;

  List<Question> _queue = const [];
  int _index = 0;
  int _correct = 0;
  int _partial = 0;

  /// 本轮每题作答结果（与 [_queue] 对齐；null=未答，判分后写入）。
  /// 答题卡按此渲染红绿灰格子，并支持点击跳题。
  List<Grade?> _results = const [];

  // 当前题作答状态
  final Set<String> _selection = {};
  bool _submitted = false;
  bool _ratingInFlight = false; // 防评分按钮重复点击（审查 P1-3）
  Grade _grade = Grade.skip;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _practiceStopwatch.start();
    _load();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) {
      if (!_pageFinished && !_practiceStopwatch.isRunning) {
        _practiceStopwatch.start();
        _syncDisplayedDuration();
      }
    } else if (state == AppLifecycleState.inactive ||
        state == AppLifecycleState.paused ||
        state == AppLifecycleState.hidden) {
      _practiceStopwatch.stop();
      _syncDisplayedDuration();
    }
  }

  void _syncDisplayedDuration() {
    final seconds = _practiceStopwatch.elapsed.inSeconds;
    if (_showPracticeTimer && mounted && seconds != _displayedSeconds) {
      setState(() => _displayedSeconds = seconds);
    } else {
      _displayedSeconds = seconds;
    }
  }

  void _startTimerRefresh() {
    _timerRefresh ??= Timer.periodic(const Duration(seconds: 1), (_) {
      _syncDisplayedDuration();
    });
  }

  void _stopPracticeTimer({bool updateUi = true}) {
    _practiceStopwatch.stop();
    _timerRefresh?.cancel();
    _timerRefresh = null;
    if (updateUi && mounted) {
      _syncDisplayedDuration();
    } else {
      _displayedSeconds = _practiceStopwatch.elapsed.inSeconds;
    }
  }

  void _startPracticeTimer() {
    if (!_pageFinished && !_practiceStopwatch.isRunning) {
      _practiceStopwatch.start();
    }
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _stopPracticeTimer(updateUi: false);
    super.dispose();
  }

  String get _modeLabel => switch (widget.mode) {
    PracticeMode.learn => '刷题',
    PracticeMode.review => '复习',
    PracticeMode.wrongRework => '错题重刷',
  };

  Future<void> _load() async {
    try {
      final repo = await ref.read(quizRepositoryProvider);
      final showPracticeTimer = await repo.practiceTimerVisible();
      final reviewEnabled = await repo.reviewModeEnabled();
      final List<Question> questions;
      if (widget.questions != null) {
        // 重点题目合集：直接刷预取题目，不重新查询题库
        questions = widget.questions!;
      } else {
        switch (widget.mode) {
          case PracticeMode.learn:
            questions = widget.randomLimit != null
                ? await repo.randomByType(
                    widget.bankId!,
                    limit: widget.randomLimit!,
                  )
                : widget.random
                ? await repo.randomQuestions(bankId: widget.bankId)
                : widget.chapters != null
                ? await repo.questionsInChapters(
                    widget.bankId!,
                    widget.chapters!,
                  )
                : await repo.questions(
                    bankId: widget.bankId,
                    chapter: widget.chapter,
                    purpose: widget.purpose,
                  );
          case PracticeMode.review:
            questions = await repo.reviewQueue(
              bankId: widget.bankId,
            ); // 审查 P1-1：bankId 穿透
          case PracticeMode.wrongRework:
            questions = await repo.wrongBookQuestions(
              bankId: widget.bankId,
            ); // 审查 P1-1
        }
      }
      if (!mounted) return;
      // 恢复上次进度：固定顺序刷题（有 progressKey）时，从上次题目继续
      var startIndex = 0;
      var restored = false;
      if (widget.progressKey != null && questions.isNotEmpty) {
        final lastId = await repo.practiceProgress(widget.progressKey!);
        if (lastId != null && lastId.isNotEmpty) {
          final idx = questions.indexWhere((q) => q.id == lastId);
          if (idx >= 0) {
            startIndex = idx;
            restored = true;
          }
        }
      }
      if (!mounted) return;
      setState(() {
        _showPracticeTimer = showPracticeTimer;
        _reviewEnabled = reviewEnabled;
        _queue = questions;
        _results = List<Grade?>.filled(questions.length, null);
        _index = startIndex;
        _questionStartedElapsedSeconds = _practiceStopwatch.elapsed.inSeconds;
        if (questions.isEmpty) {
          _error = '该范围暂无题目';
          _pageFinished = true;
        }
      });
      // 恢复上次答题卡结果：必须在 _loading=false 之前完成，
      // 避免恢复期间用户作答被恢复结果覆盖（审查修复：恢复竞态）
      await _restoreResults();
      if (!mounted) return;
      // 恢复点若落在"已作答"的题上（回答后未评分/未跳转就退出、或从答题卡跳回
      // 已答题后退出），自动续到下一道未答题，避免「已从上次进度继续」弹窗与
      // 实际展示（空白未答）不一致；全部已答完则直接落到结算页。
      var resumeIndex = startIndex;
      if (restored) {
        while (resumeIndex < questions.length &&
            _results[resumeIndex] != null &&
            _results[resumeIndex] != Grade.skip) {
          resumeIndex++;
        }
        if (resumeIndex != _index) {
          final finished = resumeIndex >= questions.length;
          setState(() {
            _index = resumeIndex;
            _questionStartedElapsedSeconds =
                _practiceStopwatch.elapsed.inSeconds;
          });
          if (finished) {
            _pageFinished = true;
            _stopPracticeTimer();
          }
        }
      }
      setState(() => _loading = false);
      _loadFlagState();
      if (restored && resumeIndex < questions.length && mounted) {
        // 暂停计时，避免弹窗等待时间计入刷题耗时
        _practiceStopwatch.stop();
        await _confirmResume(repo, resumeIndex, questions.length);
      }
      if (_showPracticeTimer && !_pageFinished) _startTimerRefresh();
      if (_pageFinished) _stopPracticeTimer();
    } catch (e) {
      _pageFinished = true;
      _stopPracticeTimer(updateUi: false);
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error = '加载失败：$e';
      });
    }
  }

  Question get _current => _queue[_index];

  /// 恢复进度确认弹窗：替代原来随手可滑掉的 SnackBar。
  /// 用户必须明确点击「继续」（保留进度与答题卡结果）或「重新开始」
  /// （清空进度从头刷）才进入刷题；弹窗不可点外部关闭、返回键也被拦截。
  /// 计时在弹窗打开前已暂停，选择后才恢复，等待时间不计入刷题耗时。
  Future<void> _confirmResume(
    QuizRepository repo,
    int resumeIndex,
    int total,
  ) async {
    if (!mounted) return;
    final key = widget.progressKey;
    if (key == null) return;
    final continueFromHere = await showDialog<bool>(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => PopScope(
        canPop: false,
        child: AlertDialog(
          title: const Text('继续上次进度？'),
          content: Text(
            '上次刷到第 ${resumeIndex + 1} / $total 题。\n'
            '「继续」保留当前作答进度与答题卡，「重新开始」清空进度从头刷。',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx, false),
              child: const Text('重新开始'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(ctx, true),
              child: const Text('继续'),
            ),
          ],
        ),
      ),
    );
    if (!mounted) return;
    _startPracticeTimer(); // 恢复计时（弹窗等待时间不计入）
    if (continueFromHere != false) return; // 继续：进度与答题卡结果已就绪
    // 重新开始：清除持久化进度与答题卡结果，从第 1 题开始
    await repo.clearPracticeProgress(key);
    await repo.clearSetting(QuizRepository.practiceResultsKey(key));
    if (!mounted) return;
    setState(() {
      _index = 0;
      _pageFinished = false;
      // 重置本轮全部作答状态（审查修复：防跨轮重复统计/残留提交态）
      _results = List<Grade?>.filled(_queue.length, null);
      _correct = 0;
      _partial = 0;
      _selection.clear();
      _submitted = false;
      _grade = Grade.skip;
      _flagged = false;
      // 重置当前题计时起点，避免"重新开始"后首题耗时虚高
      _questionStartedElapsedSeconds = _practiceStopwatch.elapsed.inSeconds;
    });
    _loadFlagState();
  }

  // 当前题是否已标记为待审（v7 审题标记）
  bool _flagged = false;

  // ---------- 审题标记交互 ----------

  Future<void> _loadFlagState() async {
    // 空队列或已到末题之后（_index 越界）时跳过，避免 RangeError
    if (_queue.isEmpty || _index >= _queue.length) {
      if (mounted) setState(() => _flagged = false);
      return;
    }
    final repo = await ref.read(quizRepositoryProvider);
    final flagged = await repo.isFlagged(_current.id);
    if (mounted) setState(() => _flagged = flagged);
  }

  /// 标记/取消标记当前题为"待审"（可带备注）
  Future<void> _toggleFlag() async {
    final repo = await ref.read(quizRepositoryProvider);
    if (_flagged) {
      await repo.unflagQuestion(_current.id);
      if (mounted) setState(() => _flagged = false);
      return;
    }
    if (!mounted) return;
    final comment = await showDialog<String>(
      context: context,
      builder: (dialogCtx) => _FlagDialog(questionId: _current.id),
    );
    final trimmed = comment?.trim();
    await repo.flagQuestion(
      _current.id,
      _current.bankId,
      comment: (trimmed == null || trimmed.isEmpty) ? null : trimmed,
    );
    if (mounted) setState(() => _flagged = true);
  }

  // ---------- 作答交互 ----------

  void _onSelect(String value) {
    if (_submitted) return;
    setState(() {
      // 单选/判断题互斥：选新即取消旧（审查 P1-6）
      if (_current.type == QuestionType.singleChoice ||
          _current.type == QuestionType.trueFalse) {
        _selection
          ..clear()
          ..add(value);
      } else if (_selection.contains(value)) {
        _selection.remove(value);
      } else {
        _selection.add(value);
      }
    });
    // 单选/判断：选完即判分显示答案（需求「选择题选完会显示答案」）
    if (_current.type == QuestionType.singleChoice ||
        _current.type == QuestionType.trueFalse) {
      _submit();
    }
  }
  /// 自由作答确认（填空多空/简答）：合并非空输入到 _selection；
  /// 判分由底部「提交」按钮统一触发（与旧交互一致：填入 → 提交）
  void _onFreeSubmit(List<String> texts) {
    if (_submitted) return;
    setState(() {
      _selection
        ..clear()
        ..addAll(texts.where((t) => t.trim().isNotEmpty));
    });
  }


  /// 提交作答：判分 → 写入本轮结果表 → 展示解析（四档评分条随后出现）
  void _submit() {
    final grade = gradeQuestion(_current, _selection);
    setState(() {
      _submitted = true;
      _grade = grade;
      if (_index < _results.length) _results[_index] = grade;
    });
    // 计数一律从结果表重算（审查修复：恢复进度后重答/跳回已答题不再重复累计）
    _correct = _results.where((g) => g == Grade.correct).length;
    _partial = _results.where((g) => g == Grade.partial).length;
    _saveResultsIfNeeded(); // 答题卡结果持久化（中途退出可恢复）
  }

  /// 四档评分：answer_logs + FSRS 调度原子写入 → 错题自动移出 → 下一题
  /// （审查 P2-8：logAnswerAndSchedule 单事务，避免日志与调度不一致/统计双计）
  Future<void> _rate(Rating rating) async {
    if (_ratingInFlight) return; // 防重入（审查 P1-3）
    _ratingInFlight = true;
    try {
      final question = _current;
      final now = DateTime.now().millisecondsSinceEpoch;
      _syncDisplayedDuration();
      final elapsedSeconds = _practiceStopwatch.elapsed.inSeconds;
      final questionTimeMs =
          (elapsedSeconds - _questionStartedElapsedSeconds).clamp(
            0,
            elapsedSeconds,
          ) *
          1000;
      final repo = await ref.read(quizRepositoryProvider);
      final srs = await ref.read(srsProvider);

      final log = AnswerLog(
        questionId: question.id,
        mode: switch (widget.mode) {
          PracticeMode.learn => 'learn',
          PracticeMode.review => 'review',
          PracticeMode.wrongRework => 'wrong_rework',
        },
        result: _grade.name,
        rating: rating.value,
        timeMs: questionTimeMs,
        answeredAt: now,
      );
      final card = await srs.compute(
        question.id,
        rating,
        durationMs: questionTimeMs,
        now: DateTime.fromMillisecondsSinceEpoch(now),
      );
      await repo.logAnswerAndSchedule(
        log,
        card,
        now: DateTime.fromMillisecondsSinceEpoch(now),
      );
      AppLog.quiz(
        '评分: ${widget.mode.name} 题${question.id} rating=${rating.name} 结果=${_grade.name}',
      );

      // 错题重刷：连续正确达阈值自动移出错题本（设计方案 §3.5）。
      // 审查 B2：链条以最近一次答错为界，重新归集后重新连对。
      if (widget.mode == PracticeMode.wrongRework &&
          _grade == Grade.correct &&
          await repo.consecutiveCorrectCount(question.id) >=
              QuizRepository.wrongBookRetireThreshold) {
        // 连续答对自动移出：静默执行，不弹横幅打断练习节奏（UI 审查 P2-4）
        await repo.removeFromWrongBook(question.id);
      }
      if (!mounted) return; // 页面可能已被用户返回（审查 P1-4）
      _stopPracticeTimer();
      _next();
    } finally {
      _ratingInFlight = false;
    }
  }

  /// 手动移出错题本
  Future<void> _removeFromWrongBook() async {
    final repo = await ref.read(quizRepositoryProvider);
    await repo.removeFromWrongBook(_current.id);
    if (mounted) {
      showAppToast(context, '已移出错题本');
    }
  }

  void _next() {
    final isLastQuestion = _index + 1 >= _queue.length;
    if (isLastQuestion) {
      _pageFinished = true;
      _stopPracticeTimer();
    }
    setState(() {
      _index++;
      _selection.clear();
      _submitted = false;
      _grade = Grade.skip;
      _flagged = false; // 避免切题瞬间串显示上一题标记状态（异步加载前先复位）
      _questionStartedElapsedSeconds = _practiceStopwatch.elapsed.inSeconds;
    });
    _startPracticeTimer();
    if (_showPracticeTimer) _startTimerRefresh();
    _saveProgressIfNeeded();
    _loadFlagState();
  }

  /// 答题卡跳题：跳到指定题。被跳离的题若未判分保持"未答"（结果不记录），
  /// 可随时跳回继续——跳题不等于跳过（设计：答题卡功能）。
  void _jumpTo(int index) {
    if (index < 0 || index >= _queue.length) return;
    setState(() {
      _index = index;
      // 从完成页答题卡跳回某题回顾时，解除"已完成"态，恢复计时与作答流程
      _pageFinished = false;
      _selection.clear();
      _submitted = false;
      _grade = Grade.skip;
      _flagged = false; // 避免切题瞬间串显示上一题标记状态
      _questionStartedElapsedSeconds = _practiceStopwatch.elapsed.inSeconds;
    });
    _startPracticeTimer();
    if (_showPracticeTimer) _startTimerRefresh();
    _saveProgressIfNeeded();
    _loadFlagState();
  }

  /// 打开答题卡（UI v2 三形态：手机底部弹层 / 平板右下浮层 / 桌面右侧滑入）
  /// 做题中与完成页共用；完成页时无当前题高亮。
  void _showAnswerSheet() {
    final layout = appLayoutOf(context);
    // 手机：底部弹层（现状，体验稳定）
    if (layout == AppLayout.compact) {
      showModalBottomSheet<void>(
        context: context,
        isScrollControlled: true,
        backgroundColor: Theme.of(context).colorScheme.surface,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        builder: (_) => _AnswerSheet(
          queue: _queue,
          results: _results,
          currentIndex: _index < _queue.length ? _index : -1,
          onJump: _jumpTo,
        ),
      );
      return;
    }
    // 平板 / 桌面：定位浮层（对齐原型答题卡形态适配）
    final isDesktop = layout == AppLayout.expanded;
    showGeneralDialog<void>(
      context: context,
      barrierDismissible: true,
      barrierLabel: '答题卡',
      barrierColor: Colors.black.withValues(alpha: 0.25),
      transitionDuration: const Duration(milliseconds: 320),
      pageBuilder: (ctx, a1, a2) => Align(
        // 平板右下 / 桌面右侧
        alignment: isDesktop ? Alignment.centerRight : Alignment.bottomRight,
        child: SafeArea(
          child: Container(
            width: isDesktop ? 280 : 300,
            height: isDesktop ? double.infinity : null,
            constraints: isDesktop
                ? null
                : BoxConstraints(
                    maxHeight: MediaQuery.of(ctx).size.height * 0.74),
            margin: isDesktop
                ? null
                : const EdgeInsets.only(right: 14, bottom: 16),
            decoration: BoxDecoration(
              borderRadius: isDesktop
                  ? null
                  : BorderRadius.circular(26), // 平板 r-lg
              boxShadow: const [
                BoxShadow(
                  color: Color(0x26263A5C),
                  blurRadius: 44,
                  offset: Offset(0, 14),
                ),
              ],
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: isDesktop
                    ? const [
                        Color(0xEBE7EEF7),
                        Color(0xEBC9D7EA),
                      ]
                    : const [
                        Color(0xFFE7EEF7),
                        Color(0xFFC9D7EA),
                      ],
              ),
            ),
            child: ClipRRect(
              borderRadius: isDesktop
                  ? BorderRadius.zero
                  : BorderRadius.circular(26),
              child: _AnswerSheet(
                queue: _queue,
                results: _results,
                currentIndex: _index < _queue.length ? _index : -1,
                onJump: _jumpTo,
              ),
            ),
          ),
        ),
      ),
      transitionBuilder: (ctx, anim, a2, child) => SlideTransition(
        position: Tween<Offset>(
          begin: isDesktop ? const Offset(1, 0) : const Offset(0, 0.2),
          end: Offset.zero,
        ).animate(
          CurvedAnimation(parent: anim, curve: Curves.easeOutCubic),
        ),
        child: child,
      ),
    );
  }

  /// 固定顺序刷题：把当前题目位置写入进度（下次进入从这里继续）。
  /// 到最后一题时先保存（供中途退出续刷），完成页「完成」时清除。
  void _saveProgressIfNeeded() {
    final key = widget.progressKey;
    if (key == null || _queue.isEmpty || _index >= _queue.length) return;
    unawaited(() async {
      final repo = await ref.read(quizRepositoryProvider);
      await repo.savePracticeProgress(key, _current.id);
    }());
  }

  /// 恢复上次答题卡结果（按题 id 匹配，题库更新后仍能对上已答记录）
  Future<void> _restoreResults() async {
    final key = widget.progressKey;
    if (key == null || _queue.isEmpty) return;
    final repo = await ref.read(quizRepositoryProvider);
    final raw = await repo.setting(QuizRepository.practiceResultsKey(key));
    if (raw == null || raw.isEmpty) return;
    try {
      final decoded = jsonDecode(raw) as Map<String, dynamic>;
      final restored = <Grade?>[];
      var correct = 0, partial = 0;
      for (final q in _queue) {
        final name = decoded[q.id];
        final g = name is String && name.isNotEmpty
            ? Grade.values.asNameMap()[name]
            : null;
        if (g == Grade.correct) correct++;
        if (g == Grade.partial) partial++;
        restored.add(g);
      }
      if (!mounted) return;
      setState(() {
        _results = restored;
        _correct = correct;
        _partial = partial;
      });
    } catch (_) {
      // 缓存损坏视为新轮（不阻断刷题）
    }
  }

  /// 保存答题卡结果（固定顺序刷题；判分后即写入，中途退出再进入可恢复）
  void _saveResultsIfNeeded() {
    final key = widget.progressKey;
    if (key == null || _queue.isEmpty) return;
    final map = <String, String>{};
    for (var i = 0; i < _queue.length; i++) {
      final g = _results[i];
      if (g != null && g != Grade.skip) map[_queue[i].id] = g.name;
    }
    unawaited(() async {
      final repo = await ref.read(quizRepositoryProvider);
      await repo.setSetting(
        QuizRepository.practiceResultsKey(key),
        jsonEncode(map),
      );
    }());
  }

  void _finish() {
    _pageFinished = true;
    _stopPracticeTimer();
    final key = widget.progressKey;
    if (key != null) {
      // 整轮刷完：清除进度与答题卡结果，下次从头开始
      unawaited(() async {
        final repo = await ref.read(quizRepositoryProvider);
        await repo.clearPracticeProgress(key);
        await repo.clearSetting(QuizRepository.practiceResultsKey(key));
      }());
    }
    Navigator.of(context).pop();
  }

  // ---------- 构建 ----------

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return Scaffold(
        appBar: _V3PracticeAppBar(title: _modeLabel),
        body: const Center(child: CircularProgressIndicator(strokeWidth: 2.5)),
      );
    }
    if (_error != null) {
      // 统一空/错误态：图标 + 说明 + 返回操作（设计方案 §3.4 状态机）
      final isLoadError = _error!.startsWith('加载失败');
      return Scaffold(
        appBar: _V3PracticeAppBar(title: _modeLabel),
        body: isLoadError
            ? _PracticeStateView(
                icon: Icons.error_outline,
                title: '加载失败',
                message: _error!,
                actionLabel: '返回',
                actionIcon: Icons.arrow_back,
                onAction: () => Navigator.of(context).pop(),
              )
            : _PracticeStateView(
                icon: Icons.menu_book_outlined,
                title: '该范围暂无题目',
                message: '当前范围没有可作答的题目，请返回后选择其他章节或题库',
                actionLabel: '返回',
                actionIcon: Icons.arrow_back,
                onAction: () => Navigator.of(context).pop(),
              ),
      );
    }
    if (_index >= _queue.length) {
      return _SummaryView(
        total: _queue.length,
        correct: _correct,
        partial: _partial,
        onFinish: _finish,
        onReview: _showAnswerSheet,
      );
    }
    final isWrongRework = widget.mode == PracticeMode.wrongRework;
    // P0 手感优化：减少动效开关（主题配置持久化）
    final reduceMotion = ref.watch(themeControllerProvider).value?.reduceMotion ?? false;
    return Scaffold(
      // V3 iOS 顶栏：模式标签 + 计时 + 答题卡入口 + 进度条
      appBar: _V3PracticeAppBar(
        title: _modeLabel,
        progress: (_index + 1) / _queue.length,
        showTimer: _showPracticeTimer,
        seconds: _displayedSeconds,
        showAnswerSheet: _queue.isNotEmpty,
        onAnswerSheet: _showAnswerSheet,
      ),
      body: Center(
        child: ConstrainedBox(
          // 桌面答题内容限宽 760 居中（P4 对齐原型 d-desktop 答题限宽）
          constraints: const BoxConstraints(maxWidth: 760),
          child: _QuestionView(
        reduceMotion: reduceMotion,
        question: _current,
        selection: _selection,
        submitted: _submitted,
        grade: _grade,
        index: _index + 1,
        total: _queue.length,
        flagged: _flagged,
        showFlag: _reviewEnabled,
        onToggleFlag: _toggleFlag,
        showRating: _submitted,
        showRemoveWrong: isWrongRework && _submitted,
        onSelect: _onSelect,
        onSubmit: _submit,
        onFreeSubmit: _onFreeSubmit,
        onRate: _rate,
        onRemoveWrong: _removeFromWrongBook,
      ),
        ),
      ),
    );
  }
}

/// V3 iOS 轻量顶栏（答题会话）：模式标签 + 计时 + 答题卡入口 + 底部进度条。
class _V3PracticeAppBar extends StatelessWidget implements PreferredSizeWidget {
  const _V3PracticeAppBar({
    required this.title,
    this.progress,
    this.showTimer = false,
    this.seconds = 0,
    this.showAnswerSheet = false,
    this.onAnswerSheet,
  });

  final String title;
  final double? progress;
  final bool showTimer;
  final int seconds;
  final bool showAnswerSheet;
  final VoidCallback? onAnswerSheet;

  @override
  Size get preferredSize => const Size.fromHeight(72);

  static String _fmt(int seconds) {
    final m = seconds ~/ 60;
    final s = seconds % 60;
    return '${m.toString().padLeft(2, '0')}:${s.toString().padLeft(2, '0')}';
  }

  @override
  Widget build(BuildContext context) {
    final colors = IOSColors.of(context);
    return Container(
      color: Colors.transparent,
      height: 72,
      child: Column(
        children: [
          Expanded(
            child: Row(
              children: [
                const SizedBox(width: IOSSpacing.s16),
                Text(title, style: IOSTypography.headline(color: colors.text)),
                const Spacer(),
                if (showTimer) ...[
                  Icon(Icons.timer_outlined, size: 16, color: colors.text2),
                  const SizedBox(width: 4),
                  Text(
                    _fmt(seconds),
                    style: IOSTypography.footnote(
                      color: colors.text2,
                    ).copyWith(fontFeatures: const [FontFeature.tabularFigures()]),
                  ),
                  const SizedBox(width: IOSSpacing.s8),
                ],
                if (showAnswerSheet)
                  IconButton(
                    tooltip: '答题卡',
                    visualDensity: VisualDensity.compact,
                    icon: Icon(
                      Icons.grid_view_outlined,
                      color: colors.primary,
                      size: 22,
                    ),
                    onPressed: onAnswerSheet,
                  ),
                const SizedBox(width: IOSSpacing.s4),
              ],
            ),
          ),
          if (progress != null)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: IOSSpacing.s16),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(2),
                child: TweenAnimationBuilder<double>(
                  tween: Tween(begin: progress, end: progress),
                  duration: const Duration(milliseconds: 300),
                  curve: Curves.easeOutCubic,
                  builder: (context, value, _) => LinearProgressIndicator(
                    value: value.clamp(0.0, 1.0),
                    minHeight: 3,
                    backgroundColor: colors.fill2,
                    color: colors.primary,
                  ),
                ),
              ),
            ),
          const SizedBox(height: 10),
        ],
      ),
    );
  }
}

/// 题目展示 + 作答区 + 评分条
class _FlagDialog extends StatefulWidget {
  const _FlagDialog({required this.questionId});

  final String questionId;

  @override
  State<_FlagDialog> createState() => _FlagDialogState();
}

class _FlagDialogState extends State<_FlagDialog> {
  final _controller = TextEditingController();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return AlertDialog(
      title: const Text('标记为待修改'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '题目：${widget.questionId}',
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.outline,
              fontFamily: 'monospace',
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _controller,
            maxLines: 3,
            decoration: const InputDecoration(
              hintText: '备注（可选）：如"答案错误"、"题干歧义"、"重复题"…',
              border: OutlineInputBorder(),
            ),
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('取消'),
        ),
        FilledButton(
          onPressed: () => Navigator.pop(context, _controller.text),
          child: const Text('标记'),
        ),
      ],
    );
  }
}
