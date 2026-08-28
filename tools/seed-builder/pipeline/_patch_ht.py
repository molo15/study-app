# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
f = r'D:\study_app\app\lib\ui\settings_page.dart'
s = open(f, encoding='utf-8').read()
old = "helperText: '考试倒计时与每日任务（计划倒排为建议，可自由覆盖）',"
new = "helperText: '设置考试日期，首页显示倒计时',"
if old in s:
    s = s.replace(old, new)
    open(f, 'w', encoding='utf-8').write(s)
    print('helperText 已更新')
else:
    for l in s.split('\n'):
        if '学习目标' in l or 'helperText' in l:
            print('  实际:', l.strip()[:90])
