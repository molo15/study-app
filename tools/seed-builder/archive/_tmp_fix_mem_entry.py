# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
p = r'D:\study_app\app\lib\ui\home_page.dart'
s = open(p, encoding='utf-8').read()

# 1. 修复背题卡 onTap：改成弹出题库选择
old = """            title: '背题',
            subtitle: '选章背诵',
            onTap: () => _push(const BankPage()),"""
new = """            title: '背题',
            subtitle: '选章背诵',
            onTap: _showBankPickerForMem,"""
s = s.replace(old, new)

# 2. 在 _QuickEntryCard 方法后加 _showBankPickerForMem 方法
old_anchor = """  /// P1.5 快捷入口小卡：图标 + 标题 + 副标题
  Widget _QuickEntryCard({"""

new_anchor = """  /// 背题入口：弹出题库选择，选科后跳转到该科章节列表（用户选章进入背题）
  Future<void> _showBankPickerForMem() async {
    final theme = Theme.of(context);
    final picked = await showModalBottomSheet<String>(
      context: context,
      builder: (ctx) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Padding(
              padding: const EdgeInsets.all(16),
              child: Text('选择科目开始背题', style: theme.textTheme.titleMedium),
            ),
            for (final bank in _banks)
              ListTile(
                leading: const Icon(Icons.menu_book_outlined),
                title: Text(bank.name),
                subtitle: Text('${bank.active} 题'),
                trailing: const Icon(Icons.chevron_right),
                onTap: () => Navigator.pop(ctx, bank.bankId),
              ),
            const SizedBox(height: 8),
          ],
        ),
      ),
    );
    if (picked != null && mounted) {
      _push(BankPage(bankId: picked));
    }
  }

  /// P1.5 快捷入口小卡：图标 + 标题 + 副标题
  Widget _QuickEntryCard({"""

s = s.replace(old_anchor, new_anchor)

open(p, 'w', encoding='utf-8', newline='').write(s)
print('背题入口修复完成')
print('  _showBankPickerForMem:', '_showBankPickerForMem' in s)
print('  const BankPage() 已移除:', 'const BankPage()' not in s)
