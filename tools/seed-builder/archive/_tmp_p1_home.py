# -*- coding: utf-8 -*-
"""P1-3: 首页题库卡 AppCard 替换 + 交错入场 + import"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
p = r'D:\study_app\app\lib\ui\home_page.dart'
s = open(p, encoding='utf-8').read()

# 1. 加 import
old_import = "import 'app_routes.dart';"
new_import = """import 'app_routes.dart';
import 'widgets/app_card.dart';
import 'widgets/staggered_item.dart';"""
s = s.replace(old_import, new_import, 1)

# 2. _buildBankCard: Card → AppCard（padding zero，onTap 移到 AppCard）
old_card = """    return Card(
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        leading: Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: theme.colorScheme.primary.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(
            Icons.menu_book_outlined,
            color: theme.colorScheme.primary,
            size: 22,
          ),
        ),
        title: Text(
          bank.name,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: const TextStyle(fontWeight: FontWeight.w600),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '共 ${bank.active} 题',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 6),
            _BankProgress(
              answered: _answeredByBank[bank.bankId] ?? 0,
              total: bank.active,
            ),
          ],
        ),
        isThreeLine: true,
        trailing: const Icon(Icons.chevron_right),
        onTap: () => _push(BankPage(bankId: bank.bankId)),
      ),
    );"""

new_card = """    return AppCard(
      padding: EdgeInsets.zero,
      margin: const EdgeInsets.only(bottom: 10),
      onTap: () => _push(BankPage(bankId: bank.bankId)),
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        leading: Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: theme.colorScheme.primary.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(
            Icons.menu_book_outlined,
            color: theme.colorScheme.primary,
            size: 22,
          ),
        ),
        title: Text(
          bank.name,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: const TextStyle(fontWeight: FontWeight.w600),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '共 ${bank.active} 题',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 6),
            _BankProgress(
              answered: _answeredByBank[bank.bankId] ?? 0,
              total: bank.active,
            ),
          ],
        ),
        isThreeLine: true,
        trailing: const Icon(Icons.chevron_right),
      ),
    );"""

s = s.replace(old_card, new_card)

# 3. 首页题库列表加 StaggeredItem
old_bank_list = """        for (final bank in _banks) _buildBankCard(theme, bank),
        const SizedBox(height: 16),"""
new_bank_list = """        for (var i = 0; i < _banks.length; i++)
          StaggeredItem(
            index: i,
            child: _buildBankCard(theme, _banks[i]),
          ),
        const SizedBox(height: 16),"""
s = s.replace(old_bank_list, new_bank_list)

open(p, 'w', encoding='utf-8', newline='').write(s)
print('首页 AppCard + 交错入场已添加')
print('  import app_card:', "widgets/app_card.dart" in s)
print('  import staggered:', "widgets/staggered_item.dart" in s)
print('  AppCard:', 'return AppCard(' in s)
print('  StaggeredItem:', 'StaggeredItem(' in s)
