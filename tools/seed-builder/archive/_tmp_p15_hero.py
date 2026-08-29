# -*- coding: utf-8 -*-
"""P1.5-2: Hero 共享元素 — 章节标题 ↔ 详情页 AppBar 标题"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. bank_page.dart _ChapterTile 两个章节标题都加 Hero
p = r'D:\study_app\app\lib\ui\bank_page.dart'
s = open(p, encoding='utf-8').read()

# 1a. 无分类数据的章节（ListTile title）
old1 = """        title: Text(
          chapter,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: theme.textTheme.bodyMedium,
        ),
        trailing: Text(
          '$total 题',"""
new1 = """        title: Hero(
          tag: 'chapter-title:$bankId:$chapter',
          child: Text(
            chapter,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: theme.textTheme.bodyMedium,
          ),
        ),
        trailing: Text(
          '$total 题',"""
s = s.replace(old1, new1)

# 1b. 有分类数据的章节（ExpansionTile title）
old2 = """      title: Text(
        chapter,
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
        style: theme.textTheme.bodyMedium,
      ),
      subtitle: Text(
        '共 $total 题 · 展开按基础/测试分类刷',"""
new2 = """      title: Hero(
        tag: 'chapter-title:$bankId:$chapter',
        child: Text(
          chapter,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: theme.textTheme.bodyMedium,
        ),
      ),
      subtitle: Text(
        '共 $total 题 · 展开按基础/测试分类刷',"""
s = s.replace(old2, new2)

open(p, 'w', encoding='utf-8', newline='').write(s)
print('bank_page Hero 已添加')
print('  无分类 Hero:', "tag: 'chapter-title:$bankId:$chapter'," in s)
print('  Hero 出现次数:', s.count("tag: 'chapter-title:"))

# 2. chapter_overview_page.dart AppBar 标题加 Hero
p2 = r'D:\study_app\app\lib\ui\chapter_overview_page.dart'
s2 = open(p2, encoding='utf-8').read()

old3 = """      appBar: GlassAppBar(
        title: Text(widget.chapter),
        centerTitle: true,
      ),"""
new3 = """      appBar: GlassAppBar(
        title: Hero(
          tag: 'chapter-title:${widget.bankId}:${widget.chapter}',
          child: Text(widget.chapter),
        ),
        centerTitle: true,
      ),"""
s2 = s2.replace(old3, new3)
open(p2, 'w', encoding='utf-8', newline='').write(s2)
print('chapter_overview_page Hero 已添加')
print('  Hero tag:', "tag: 'chapter-title:${widget.bankId}:${widget.chapter}'" in s2)
