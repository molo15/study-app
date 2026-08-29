# -*- coding: utf-8 -*-
p = r'D:\study_app\app\lib\ui\chapter_overview_page.dart'
s = open(p, encoding='utf-8').read()
start = s.find('  /// 背题模式（可整章或单知识点）')
end = s.find('  /// 知识点名称兜底查找')
assert start != -1 and end != -1 and start < end, (start, end)
new = '''  /// 背题模式：整章进入「知识点卡/题目背诵」双 Tab；单知识点保持逐题背诵
  Future<void> _startMemorize({String? knowledgeId}) async {
    final repo = await ref.read(quizRepositoryProvider);
    final List<Question> questions;
    if (knowledgeId != null) {
      questions = await repo.questionsByKnowledge(widget.bankId, knowledgeId);
    } else {
      questions = await repo.questions(
        bankId: widget.bankId,
        chapter: widget.chapter,
      );
    }
    if (!mounted) return;
    final kpName = _kpName(knowledgeId);
    if (knowledgeId == null) {
      // 整章：双 Tab 背题（知识点卡默认）
      Navigator.of(context).push(
        AppPageRoute(
          builder: (_) => MemorizeTabsPage(
            bankId: widget.bankId,
            chapter: widget.chapter,
            title: '${widget.chapter} · 背题',
            questions: questions,
            knowledge: _knowledge,
          ),
        ),
      );
    } else {
      // 单知识点：逐题背诵
      Navigator.of(context).push(
        AppPageRoute(
          builder: (_) => MemorizePage(
            bankId: widget.bankId,
            chapter: widget.chapter,
            title: kpName.isEmpty ? '${widget.chapter} · 背题' : '$kpName · 背题',
            questions: questions,
          ),
        ),
      );
    }
  }

'''
s = s[:start] + new + s[end:]
open(p, 'w', encoding='utf-8').write(s)
print('replaced, MemorizeTabsPage count =', s.count('MemorizeTabsPage'))
