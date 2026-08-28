# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
s = open(r'D:\study_app\app\lib\data\app_database.dart', encoding='utf-8').read()
for m in re.finditer(r"CREATE TABLE (?:IF NOT EXISTS )?(\w+)", s):
    print('表:', m.group(1))
# 查找涉及 bank_id 的表
for m in re.finditer(r"bank_id", s):
    line_no = s[:m.start()].count('\n') + 1
for tbl in re.findall(r"CREATE TABLE (?:IF NOT EXISTS )?(\w+)", s):
    pass
# 定位每个建表语句上下文里是否含 bank_id
blocks = re.split(r"CREATE TABLE ", s)[1:]
for b in blocks:
    name = b.split('(')[0].strip().replace('IF NOT EXISTS ', '')
    print('  {} 含bank_id: {}'.format(name, 'bank_id' in b.split(')')[0]))
