# -*- coding: utf-8 -*-
"""P1-5: bank_page 章节列表交错入场 + import"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
p = r'D:\study_app\app\lib\ui\bank_page.dart'
s = open(p, encoding='utf-8').read()

# 1. 加 import（在最后一个 import 后）
old_import = "import 'app_routes.dart';"
new_import = """import 'app_routes.dart';
import 'widgets/staggered_item.dart';"""
s = s.replace(old_import, new_import, 1)

# 2. 章节分组 for 循环改成带索引 + StaggeredItem
old_for = """                  for (final group in _groups) ...[
                    _buildGroupCard(theme, group),
                    const SizedBox(height: 12),
                  ],"""
new_for = """                  for (var i = 0; i < _groups.length; i++) ...[
                    StaggeredItem(
                      index: i,
                      child: _buildGroupCard(theme, _groups[i]),
                    ),
                    const SizedBox(height: 12),
                  ],"""
s = s.replace(old_for, new_for)

open(p, 'w', encoding='utf-8', newline='').write(s)
print('bank_page 交错入场已添加')
print('  import:', "widgets/staggered_item.dart" in s)
print('  StaggeredItem:', 'StaggeredItem(' in s)
