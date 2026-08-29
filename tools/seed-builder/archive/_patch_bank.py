# -*- coding: utf-8 -*-
f = r'D:\study_app\app\lib\ui\bank_page.dart'
s = open(f, encoding='utf-8').read()

# 1) bottom sheet 标题：const + 裸 TextStyle -> Theme.of(ctx).textTheme.titleMedium
old1 = """            const Padding(
              padding: EdgeInsets.all(16),
              child: Text(
                '选择随机刷题量',
                style: TextStyle(fontWeight: FontWeight.w600, fontSize: 16),
              ),
            ),"""
new1 = """            Padding(
              padding: const EdgeInsets.all(16),
              child: Text(
                '选择随机刷题量',
                style: Theme.of(ctx).textTheme.titleMedium,
              ),
            ),"""
assert old1 in s, 'anchor1 not found'
s = s.replace(old1, new1)

# 2) 知识概览 subtitle：裸 TextStyle(fontSize:12) -> textTheme.bodySmall
old2 = """            subtitle: const Text(
              '知识点树 · 直达刷题/背题',
              style: TextStyle(fontSize: 12),
            ),"""
new2 = """            subtitle: Text(
              '知识点树 · 直达刷题/背题',
              style: theme.textTheme.bodySmall,
            ),"""
assert old2 in s, 'anchor2 not found'
s = s.replace(old2, new2)

open(f, 'w', encoding='utf-8').write(s)
print('bank_page: 2 处裸 TextStyle 已改')
print('  残留裸 TextStyle(fontSize:', s.count('TextStyle(fontSize'))
