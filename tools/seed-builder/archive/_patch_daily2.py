# -*- coding: utf-8 -*-
f = r'D:\study_app\app\lib\ui\settings_page.dart'
lines = open(f, encoding='utf-8').read().split('\n')
# 行 652-741（0-based 651-740）为残留 _GoalInput 类体，删除；保留 651 行 _IconBox 的 }
assert lines[650].strip() == '}', 'line651 not closing brace'
del lines[651:]
while lines and lines[-1].strip() == '':
    lines.pop()
open(f, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('settings_page: 已清理残留类体，现总行数', len(lines))
print('  残留 _GoalInput:', open(f, encoding='utf-8').read().count('_GoalInput'))
