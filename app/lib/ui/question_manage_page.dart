/// 题目管理：题库包题目浏览器 + 单题编辑表单（设计：bank_management）
///
/// - 浏览器：按章节分组/题型筛选/关键词搜索，显示审题标记与本地修改状态；
/// - 编辑页：改题干/选项/答案/解析/章节/answerVariants，保存置 user_edited=1；
/// - 提供"还原为官方版"（清除本地修改标记，下次更新恢复官方内容）。
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/quiz_repository.dart';
import '../models/models.dart';
import 'app_toast.dart';
import 'practice_page.dart' show typeColor, typeLabel;
import 'app_routes.dart';

/// 题库包题目浏览器（入口：设置 → 题库包管理 → 编辑题目）
class QuestionManagePage extends ConsumerStatefulWidget {
  const QuestionManagePage({super.key, required this.bankId, required this.bankName});

  final String bankId;
  final String bankName;

  @override
  ConsumerState<QuestionManagePage> createState() => _QuestionManagePageState();
}

class _QuestionManagePageState extends ConsumerState<QuestionManagePage> {
  List<Question> _questions = const [];
  List<String> _chapters = const [];
  Set<String> _flaggedIds = const {};
  bool _loading = true;
  String _keyword = '';
  String? _type;
  String? _chapter;
  int _querySeq = 0; // 搜索/筛选并发时丢弃过期结果（审查修复：防结果错位）

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final repo = await ref.read(quizRepositoryProvider);
    final chapters = await repo.chaptersForManage(widget.bankId);
    // 该库审题标记的题（联动：标记的题可一键跳转编辑）
    final flags = await repo.reviewFlags();
    final flagged = flags
        .where((m) => m['question_id'] is String &&
            (m['question_id'] as String).startsWith('${widget.bankId}:'))
        .map((m) => m['question_id'] as String)
        .toSet();
    if (!mounted) return;
    setState(() {
      _chapters = chapters;
      _flaggedIds = flagged;
    });
    await _loadQuestions();
  }

  Future<void> _loadQuestions() async {
    final seq = ++_querySeq;
    final repo = await ref.read(quizRepositoryProvider);
    final list = await repo.questionsForManage(
      widget.bankId,
      chapter: _chapter,
      type: _type == null ? null : QuestionType.fromJson(_type!),
      keyword: _keyword,
    );
    if (!mounted || seq != _querySeq) return; // 丢弃过期查询结果
    setState(() {
      _questions = list;
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(title: Text('${widget.bankName} · 题目管理')),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
            child: TextField(
              decoration: const InputDecoration(
                hintText: '搜索题干 / 答案 / 解析…',
                prefixIcon: Icon(Icons.search, size: 20),
                isDense: true,
                border: OutlineInputBorder(),
              ),
              onChanged: (v) {
                _keyword = v.trim();
                _loadQuestions();
              },
            ),
          ),
          // 题型 + 章节筛选
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: [
                  _FilterChip(
                    label: '全部',
                    selected: _type == null,
                    onTap: () {
                      _type = null;
                      _loadQuestions();
                    },
                  ),
                  for (final t in const [
                    'single_choice',
                    'multi_choice',
                    'true_false',
                    'blank',
                    'short_answer',
                  ])
                    _FilterChip(
                      label: typeLabel(QuestionType.fromJson(t)),
                      selected: _type == t,
                      onTap: () {
                        _type = t;
                        _loadQuestions();
                      },
                    ),
                  const SizedBox(width: 8),
                  DropdownButton<String?>(
                    value: _chapter,
                    hint: const Text('全部章节'),
                    underline: const SizedBox.shrink(),
                    items: [
                      const DropdownMenuItem<String?>(
                        value: null,
                        child: Text('全部章节'),
                      ),
                      for (final c in _chapters)
                        DropdownMenuItem<String?>(value: c, child: Text(c)),
                    ],
                    onChanged: (v) {
                      _chapter = v;
                      _loadQuestions();
                    },
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 4),
          Expanded(
            child: _loading
                ? const Center(child: CircularProgressIndicator())
                : _questions.isEmpty
                    ? const Center(child: Text('没有符合条件的题目'))
                    : ListView.builder(
                        itemCount: _questions.length,
                        itemBuilder: (context, i) {
                          final q = _questions[i];
                          final flagged = _flaggedIds.contains(q.id);
                          final edited = q.userEdited;
                          return ListTile(
                            dense: true,
                            leading: _TypeBadge(type: q.type),
                            title: Text(
                              q.stem,
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                            ),
                            subtitle: Text(
                              '${q.chapter}${edited ? ' · 已本地修改' : ''}'
                              '${flagged ? ' · 待审' : ''}',
                              style: theme.textTheme.bodySmall?.copyWith(
                                color: edited || flagged
                                    ? theme.colorScheme.error
                                    : theme.colorScheme.outline,
                              ),
                            ),
                            trailing: const Icon(Icons.edit_outlined, size: 20),
                            onTap: () => _openEdit(q.id),
                          );
                        },
                      ),
          ),
        ],
      ),
    );
  }

  Future<void> _openEdit(String id) async {
    final changed = await Navigator.of(context).push<bool>(
      AppPageRoute(
        builder: (_) => QuestionEditPage(questionId: id),
      ),
    );
    if (changed == true) _loadQuestions();
  }
}

class _FilterChip extends StatelessWidget {
  const _FilterChip({
    required this.label,
    required this.selected,
    required this.onTap,
  });

  final String label;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.only(right: 6),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
          decoration: BoxDecoration(
            color: selected
                ? theme.colorScheme.primaryContainer
                : theme.colorScheme.surfaceContainerHighest,
            borderRadius: BorderRadius.circular(16),
          ),
          child: Text(
            label,
            style: theme.textTheme.labelMedium?.copyWith(
              color: selected
                  ? theme.colorScheme.onPrimaryContainer
                  : theme.colorScheme.onSurfaceVariant,
            ),
          ),
        ),
      ),
    );
  }
}

class _TypeBadge extends StatelessWidget {
  const _TypeBadge({required this.type});

  final QuestionType type;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 40,
      alignment: Alignment.center,
      padding: const EdgeInsets.symmetric(vertical: 3),
      decoration: BoxDecoration(
        color: typeColor(context, type).withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Text(
        typeLabel(type),
        style: Theme.of(context).textTheme.labelSmall?.copyWith(color: typeColor(context, type)),
      ),
    );
  }
}

/// 单题编辑表单
class QuestionEditPage extends ConsumerStatefulWidget {
  const QuestionEditPage({super.key, required this.questionId});

  final String questionId;

  @override
  ConsumerState<QuestionEditPage> createState() => _QuestionEditPageState();
}

class _QuestionEditPageState extends ConsumerState<QuestionEditPage> {
  Question? _q;
  bool _loading = true;
  bool _saving = false;

  final _stemCtrl = TextEditingController();
  final _explainCtrl = TextEditingController();
  final _chapterCtrl = TextEditingController();
  final _answerCtrl = TextEditingController();
  final _variantsCtrl = TextEditingController();
  final List<TextEditingController> _optionCtrls = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final repo = await ref.read(quizRepositoryProvider);
    final q = await repo.questionById(widget.questionId);
    if (!mounted) return;
    if (q == null) {
      setState(() => _loading = false);
      return;
    }
    _stemCtrl.text = q.stem;
    _explainCtrl.text = q.explanation;
    _chapterCtrl.text = q.chapter;
    _answerCtrl.text = q.answer.toList().join('，');
    _variantsCtrl.text = q.answerVariants.isEmpty
        ? ''
        : q.answerVariants.map((g) => g.join(' / ')).join('；');
    for (final o in q.options) {
      _optionCtrls.add(TextEditingController(text: o.text));
    }
    setState(() {
      _q = q;
      _loading = false;
    });
  }

  @override
  void dispose() {
    _stemCtrl.dispose();
    _explainCtrl.dispose();
    _chapterCtrl.dispose();
    _answerCtrl.dispose();
    _variantsCtrl.dispose();
    for (final c in _optionCtrls) {
      c.dispose();
    }
    super.dispose();
  }

  Future<void> _save() async {
    final q = _q;
    if (q == null || _saving) return;
    final stem = _stemCtrl.text.trim();
    if (stem.isEmpty) {
      _toast('题干不能为空');
      return;
    }
    final answerText = _answerCtrl.text.trim();
    if (answerText.isEmpty) {
      _toast('答案不能为空');
      return;
    }
    final answerSet = answerText
        .split(RegExp(r'[，,、\s]+'))
        .where((s) => s.isNotEmpty)
        .toSet();
    if (answerSet.isEmpty) {
      _toast('答案不能为空');
      return;
    }
    if (q.type != QuestionType.blank &&
        q.type != QuestionType.shortAnswer &&
        q.options.isNotEmpty) {
      final valid = q.options.map((o) => o.key).toSet();
      if (!answerSet.every(valid.contains)) {
        _toast('选择题答案必须是已有选项');
        return;
      }
    }
    // 等价答案解析：组间「；」分隔，组内「/」分隔
    final variants = <List<String>>[];
    for (final group in _variantsCtrl.text.split('；')) {
      final words = group
          .split('/')
          .map((s) => s.trim())
          .where((s) => s.isNotEmpty)
          .toList();
      if (words.isNotEmpty) variants.add(words);
    }
    final updated = q.copyWith(
      stem: stem,
      explanation: _explainCtrl.text.trim(),
      chapter: _chapterCtrl.text.trim(),
      answer: answerSet,
      answerVariants: variants,
      options: q.options.asMap().entries.map((e) {
        final o = e.value;
        final text = e.key < _optionCtrls.length
            ? _optionCtrls[e.key].text.trim()
            : o.text;
        return QuestionOption(key: o.key, text: text);
      }).toList(),
    );
    setState(() => _saving = true);
    try {
      final repo = await ref.read(quizRepositoryProvider);
      await repo.updateQuestion(updated);
      if (mounted) {
        _toast('已保存（标记为本地修改，更新时保留）');
        Navigator.of(context).pop(true);
      }
    } catch (e) {
      if (mounted) _toast('保存失败：$e');
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  Future<void> _restoreOfficial() async {
    final q = _q;
    if (q == null) return;
    final ok = await showDialog<bool>(
      context: context,
      builder: (dialogCtx) => AlertDialog(
        title: const Text('还原为官方版？'),
        content: const Text('将放弃本地修改并清除"已修改"标记，下次题库更新时恢复为官方内容。'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(dialogCtx).pop(false),
            child: const Text('取消'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(dialogCtx).pop(true),
            child: const Text('还原'),
          ),
        ],
      ),
    );
    if (ok != true || !mounted) return;
    final repo = await ref.read(quizRepositoryProvider);
    await repo.restoreQuestionToOfficial(q.id);
    if (mounted) {
      _toast('已还原，下次更新恢复官方内容');
      Navigator.of(context).pop(true);
    }
  }

  void _toast(String msg) {
    if (!mounted) return;
    showAppToast(context, msg);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final q = _q;
    return Scaffold(
      appBar: AppBar(
        title: const Text('编辑题目'),
        actions: [
          if (q != null && q.userEdited)
            TextButton.icon(
              onPressed: _saving ? null : _restoreOfficial,
              icon: const Icon(Icons.restore, size: 18),
              label: const Text('还原为官方版'),
            ),
          TextButton(
            onPressed: _saving ? null : _save,
            child: const Text('保存'),
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : q == null
              ? const Center(child: Text('题目不存在'))
              : ListView(
                  padding: const EdgeInsets.all(16),
                  children: [
                    Row(
                      children: [
                        _TypeBadge(type: q.type),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            '${q.bankId} · ${q.id.split(':').last}',
                            style: theme.textTheme.bodySmall?.copyWith(
                              color: theme.colorScheme.outline,
                            ),
                          ),
                        ),
                        if (q.userEdited)
                          Text(
                            '已本地修改',
                            style: theme.textTheme.bodySmall?.copyWith(
                              color: theme.colorScheme.error,
                            ),
                          ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: _stemCtrl,
                      maxLines: 4,
                      decoration: const InputDecoration(
                        labelText: '题干',
                        border: OutlineInputBorder(),
                        alignLabelWithHint: true,
                      ),
                    ),
                    const SizedBox(height: 12),
                    if (q.options.isNotEmpty) ...[
                      Text('选项（仅编辑文字，选项编号不可改）',
                          style: theme.textTheme.bodySmall),
                      for (var i = 0; i < q.options.length; i++) ...[
                        const SizedBox(height: 6),
                        TextField(
                          controller: _optionCtrls[i],
                          decoration: InputDecoration(
                            labelText: '选项 ${q.options[i].key}',
                            isDense: true,
                            border: const OutlineInputBorder(),
                          ),
                        ),
                      ],
                      const SizedBox(height: 12),
                    ],
                    TextField(
                      controller: _answerCtrl,
                      decoration: const InputDecoration(
                        labelText: '答案（多值用逗号/顿号分隔）',
                        border: OutlineInputBorder(),
                        isDense: true,
                      ),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: _explainCtrl,
                      maxLines: 4,
                      decoration: const InputDecoration(
                        labelText: '解析',
                        border: OutlineInputBorder(),
                        alignLabelWithHint: true,
                      ),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: _chapterCtrl,
                      decoration: const InputDecoration(
                        labelText: '章节',
                        border: OutlineInputBorder(),
                        isDense: true,
                      ),
                    ),
                    if (q.answerVariants.isNotEmpty) ...[
                      const SizedBox(height: 12),
                      TextField(
                        controller: _variantsCtrl,
                        maxLines: 3,
                        decoration: const InputDecoration(
                          labelText: '等价答案（组内用 / 分隔，组间用 ；分隔）',
                          border: OutlineInputBorder(),
                          alignLabelWithHint: true,
                        ),
                      ),
                    ],
                    const SizedBox(height: 24),
                    Text(
                      '保存后该题标记为"本地修改"：题库更新导入时会保留你的版本，不被官方覆盖；'
                      '如需恢复官方内容可点右上角"还原为官方版"。',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.outline,
                      ),
                    ),
                  ],
                ),
    );
  }
}
