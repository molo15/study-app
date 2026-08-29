# -*- coding: utf-8 -*-
"""P2: 章节掌握度优化 — 排序+筛选+折叠+分档着色"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
p = r'D:\study_app\app\lib\ui\stats_page.dart'
s = open(p, encoding='utf-8').read()

# 1. _StatsPageState 加状态变量（在 _stats 后）
old_state = """  StudyStats? _stats;

  @override
  void initState() {"""
new_state = """  StudyStats? _stats;
  // P2 章节掌握度：排序/筛选/折叠状态
  bool _chapterSortByAccuracy = true; // true=按正确率升序（薄弱在前），false=章节顺序
  int _chapterFilter = 0; // 0=全部 1=薄弱(<60%) 2=中等(60-80%) 3=掌握(>=80%)
  bool _chapterExpanded = false; // 超过8章时默认折叠

  @override
  void initState() {"""
s = s.replace(old_state, new_state)

# 2. 替换章节掌握度 Card
old_card = """        // 章节分布
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const _SectionHeader(title: '章节掌握度', helperText: '各章节作答量与正确率'),
                const SizedBox(height: 8),
                if (s.byChapter.isEmpty)
                  Padding(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    child: Center(
                      child: Text(
                        '暂无作答记录，去刷几题吧',
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.outline,
                        ),
                      ),
                    ),
                  )
                else
                  for (final c in s.byChapter) _ChapterRow(stats: c),
              ],
            ),
          ),
        ),"""

new_card = """        // P2 章节掌握度：排序+筛选+折叠+分档着色
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Expanded(
                      child: _SectionHeader(title: '章节掌握度', helperText: '各章节作答量与正确率'),
                    ),
                    // 排序切换：薄弱在前 / 章节顺序
                    IconButton(
                      icon: Icon(
                        _chapterSortByAccuracy ? Icons.sort : Icons.menu_open,
                        size: 20,
                      ),
                      tooltip: _chapterSortByAccuracy ? '按章节顺序' : '按薄弱程度排序',
                      onPressed: s.byChapter.isEmpty
                          ? null
                          : () => setState(() => _chapterSortByAccuracy = !_chapterSortByAccuracy),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                if (s.byChapter.isEmpty)
                  Padding(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    child: Center(
                      child: Text(
                        '暂无作答记录，去刷几题吧',
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.outline,
                        ),
                      ),
                    ),
                  )
                else ...[
                  // 筛选标签：全部/薄弱/中等/掌握
                  Wrap(
                    spacing: 8,
                    children: [
                      for (var i = 0; i < _filterLabels.length; i++)
                        ChoiceChip(
                          label: Text(_filterLabels[i]),
                          selected: _chapterFilter == i,
                          onSelected: (_) => setState(() => _chapterFilter = i),
                        ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  // 过滤+排序后的章节列表
                  for (final c in _filteredChapters(s.byChapter))
                    _ChapterRow(stats: c),
                  // 折叠/展开：超过8章时默认只显示8条
                  if (_filteredChapters(s.byChapter).length > 8 && !_chapterExpanded) ...[
                    const SizedBox(height: 4),
                    TextButton(
                      onPressed: () => setState(() => _chapterExpanded = true),
                      child: Text('展开全部（共 ${_filteredChapters(s.byChapter).length} 章）'),
                    ),
                  ] else if (_chapterExpanded && _filteredChapters(s.byChapter).length > 8) ...[
                    const SizedBox(height: 4),
                    TextButton(
                      onPressed: () => setState(() => _chapterExpanded = false),
                      child: const Text('收起'),
                    ),
                  ],
                ],
              ],
            ),
          ),
        ),"""

s = s.replace(old_card, new_card)

# 3. 在 _StatsPageState 类里加 _filterLabels 和 _filteredChapters 方法
# 找到 build 方法前插入
old_build_anchor = """  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    // 标题居中"""

new_build_anchor = """  static const List<String> _filterLabels = ['全部', '薄弱', '中等', '掌握'];

  /// P2：按筛选+排序返回章节列表；折叠时只取前8条
  List<ChapterStats> _filteredChapters(List<ChapterStats> all) {
    var list = all.where((c) {
      switch (_chapterFilter) {
        case 1: return c.accuracy < 60;
        case 2: return c.accuracy >= 60 && c.accuracy < 80;
        case 3: return c.accuracy >= 80;
        default: return true;
      }
    }).toList();
    if (_chapterSortByAccuracy) {
      list.sort((a, b) => a.accuracy.compareTo(b.accuracy));
    }
    if (!_chapterExpanded && list.length > 8) {
      list = list.sublist(0, 8);
    }
    return list;
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    // 标题居中"""

s = s.replace(old_build_anchor, new_build_anchor)

# 4. _ChapterRow 进度条分档着色
old_row = """          SizedBox(
            width: 80,
            child: LinearProgressIndicator(
              value: stats.accuracy / 100,
              backgroundColor: theme.colorScheme.surfaceContainerHighest,
            ),
          ),"""
new_row = """          SizedBox(
            width: 80,
            child: LinearProgressIndicator(
              value: stats.accuracy / 100,
              backgroundColor: theme.colorScheme.surfaceContainerHighest,
              color: stats.accuracy < 60
                  ? theme.colorScheme.error
                  : stats.accuracy < 80
                      ? Colors.orange
                      : theme.colorScheme.primary,
            ),
          ),"""
s = s.replace(old_row, new_row)

open(p, 'w', encoding='utf-8', newline='').write(s)
print('章节掌握度优化完成')
print('  状态变量:', '_chapterSortByAccuracy' in s)
print('  筛选标签:', '_filterLabels' in s)
print('  折叠逻辑:', '_chapterExpanded' in s)
print('  分档着色:', 'stats.accuracy < 60' in s)
