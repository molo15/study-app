# -*- coding: utf-8 -*-
import io
p = r'D:\study_app\app\lib\ui\home_page.dart'
s = open(p, encoding='utf-8').read()
old = "days == null ? '考试日已过或未设置' : '距考试还有 $days 天'"
new = ("days == null\n"
       "                          ? (goal.examDate == null\n"
       "                                ? '未设置考试日期'\n"
       "                                : '考试日期已过')\n"
       "                          : '距考试还有 $days 天'")
assert old in s, 'old not found'
s = s.replace(old, new, 1)
open(p, 'w', encoding='utf-8').write(s)
print('ok')
