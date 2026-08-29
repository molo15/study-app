# -*- coding: utf-8 -*-
f = r'D:\study_app\app\lib\ui\settings_theme_panel.dart'
s = open(f, encoding='utf-8').read()
n = s.count('const _SectionHeader(')
s = s.replace('const _SectionHeader(', 'const AppSectionHeader(')
open(f, 'w', encoding='utf-8').write(s)
print(f'settings_theme_panel: 替换 _SectionHeader -> AppSectionHeader x{n}')
print('  残留 _SectionHeader:', s.count('_SectionHeader'))
