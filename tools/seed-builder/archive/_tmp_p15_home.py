# -*- coding: utf-8 -*-
"""P1.5-1: 首页快捷入口重排为三并排卡（模拟考/背题/错题本）"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
p = r'D:\study_app\app\lib\ui\home_page.dart'
s = open(p, encoding='utf-8').read()

# 替换整个 _buildQuickEntries 方法
old_method = """  /// 快捷入口：错题本 + 模拟考试（次级卡片，模拟卷为空时保留入口占位）
  Widget _buildQuickEntries(ThemeData theme) {
    return Card(
      margin: EdgeInsets.zero,
      child: Column(
        children: [
          ListTile(
            contentPadding: const EdgeInsets.symmetric(
              horizontal: 16,
              vertical: 4,
            ),
            leading: Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: theme.colorScheme.error.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(Icons.error_outline, color: theme.colorScheme.error),
            ),
            title: const Text('错题本'),
            subtitle: Text(_wrongCount == 0 ? '暂无错题' : '共 $_wrongCount 道错题待巩固'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => _push(WrongBookPage(bankId: _currentBankId)),
          ),
          const Divider(height: 1, indent: 72, endIndent: 16),
          // 模拟卷：为空时显示轻量空态，入口仍保留（不破坏 mockPapers 判断逻辑）
          ListTile(
            contentPadding: const EdgeInsets.symmetric(
              horizontal: 16,
              vertical: 4,
            ),
            leading: Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: theme.colorScheme.tertiary.withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(
                Icons.assignment_outlined,
                color: theme.colorScheme.tertiary,
              ),
            ),
            title: const Text('模拟考试'),
            subtitle: Text(
              // 综合卷恒存在（随机组卷），计数 +1（P2-2）
              _mockPapers.isEmpty
                  ? '1 套综合卷 · 随机组卷'
                  : '${_mockPapers.length + 1} 套卷 · 限时作答',
            ),
            trailing: const Icon(Icons.chevron_right),
            onTap: () => _push(MockExamListPage(bankId: _currentBankId)),
          ),
        ],
      ),
    );
  }"""

new_method = """  /// P1.5 快捷入口：三并排卡（模拟考 / 背题 / 错题本）
  Widget _buildQuickEntries(ThemeData theme) {
    return Row(
      children: [
        Expanded(
          child: _QuickEntryCard(
            icon: Icons.assignment_outlined,
            iconColor: theme.colorScheme.tertiary,
            title: '模拟考',
            subtitle: _mockPapers.isEmpty
                ? '综合卷'
                : '${_mockPapers.length + 1} 套',
            onTap: () => _push(MockExamListPage(bankId: _currentBankId)),
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: _QuickEntryCard(
            icon: Icons.style_outlined,
            iconColor: theme.colorScheme.primary,
            title: '背题',
            subtitle: '选章背诵',
            onTap: () => _push(const BankPage()),
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: _QuickEntryCard(
            icon: Icons.error_outline,
            iconColor: theme.colorScheme.error,
            title: '错题本',
            subtitle: _wrongCount == 0 ? '暂无' : '$_wrongCount 道',
            onTap: () => _push(WrongBookPage(bankId: _currentBankId)),
          ),
        ),
      ],
    );
  }

  /// P1.5 快捷入口小卡：图标 + 标题 + 副标题
  Widget _QuickEntryCard({
    required IconData icon,
    required Color iconColor,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    final theme = Theme.of(context);
    return AppCard(
      padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 8),
      onTap: onTap,
      child: Column(
        children: [
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              color: iconColor.withValues(alpha: 0.12),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: iconColor, size: 20),
          ),
          const SizedBox(height: 8),
          Text(
            title,
            style: theme.textTheme.labelLarge?.copyWith(fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 2),
          Text(
            subtitle,
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
        ],
      ),
    );
  }"""

s = s.replace(old_method, new_method)

# 今日任务卡也用 AppCard 替换 Card
old_today = """  /// 今日任务卡：三项计数 + 唯一主按钮（禁用逻辑不变）+ 无任务时的次级入口
  Widget _buildTodayCard(ThemeData theme) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),"""
new_today = """  /// 今日任务卡：三项计数 + 唯一主按钮（禁用逻辑不变）+ 无任务时的次级入口
  Widget _buildTodayCard(ThemeData theme) {
    return AppCard(
      child: Padding(
        padding: const EdgeInsets.all(16),"""
s = s.replace(old_today, new_today)

open(p, 'w', encoding='utf-8', newline='').write(s)
print('首页快捷入口重排完成')
print('  _QuickEntryCard:', '_QuickEntryCard(' in s)
print('  背题入口:', "title: '背题'" in s)
print('  今日卡 AppCard:', 'return AppCard(' in s)
