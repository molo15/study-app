# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

p = r'D:\study_app\app\lib\ui\mock_exam_list_page.dart'
s = open(p, encoding='utf-8').read()

# (1) import 历史页
old = """import 'mock_exam_page.dart';
import 'composite_loading_page.dart';"""
new = """import 'mock_exam_page.dart';
import 'mock_history_page.dart';
import 'composite_loading_page.dart';"""
assert old in s, 'import anchor'
s = s.replace(old, new, 1)

# (2) 综合卷卡片 trailing 加历史入口
old = """                      subtitle: Text(
                        '150 分 · 5 科随机组卷 · 限时 180 分钟'
                        '${sessions.isNotEmpty ? ' · 最近 ${sessions.first.score} / 150' : ''}',
                      ),
                      trailing: const Icon(Icons.chevron_right),
                      onTap: () => Navigator.of(context).push(
                        AppPageRoute(builder: (_) => const CompositeLoadingPage()),
                      ),
                    ),
                  );"""
new = """                      subtitle: Text(
                        '150 分 · 5 科随机组卷 · 限时 180 分钟'
                        '${sessions.isNotEmpty ? ' · 最近 ${sessions.first.score} / 150' : ''}',
                      ),
                      trailing: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          IconButton(
                            icon: const Icon(Icons.history),
                            tooltip: '历史成绩',
                            onPressed: () => Navigator.of(context).push(
                              AppPageRoute(
                                builder: (_) => MockHistoryPage(paper: _composite),
                              ),
                            ),
                          ),
                          const Icon(Icons.chevron_right),
                        ],
                      ),
                      onTap: () => Navigator.of(context).push(
                        AppPageRoute(builder: (_) => const CompositeLoadingPage()),
                      ),
                    ),
                  );"""
assert old in s, 'composite trailing anchor'
s = s.replace(old, new, 1)

# (3) 单科卷卡片 trailing 加历史入口
old = """                    subtitle: Text(
                      '${p.questionIds.length} 题 · 限时 ${p.durationMin} 分钟'
                      '${sessions.isNotEmpty ? ' · 最近 ${sessions.first.score} 分' : ''}',
                    ),
                    trailing: const Icon(Icons.chevron_right),
                    onTap: () => Navigator.of(context).push(
                      AppPageRoute(builder: (_) => MockExamPage(paper: p)),
                    ),
                  ),
                );"""
new = """                    subtitle: Text(
                      '${p.questionIds.length} 题 · 限时 ${p.durationMin} 分钟'
                      '${sessions.isNotEmpty ? ' · 最近 ${sessions.first.score} 分' : ''}',
                    ),
                    trailing: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        IconButton(
                          icon: const Icon(Icons.history),
                          tooltip: '历史成绩',
                          onPressed: () => Navigator.of(context).push(
                            AppPageRoute(
                              builder: (_) => MockHistoryPage(paper: p),
                            ),
                          ),
                        ),
                        const Icon(Icons.chevron_right),
                      ],
                    ),
                    onTap: () => Navigator.of(context).push(
                      AppPageRoute(builder: (_) => MockExamPage(paper: p)),
                    ),
                  ),
                );"""
assert old in s, 'paper trailing anchor'
s = s.replace(old, new, 1)

open(p, 'w', encoding='utf-8').write(s)
print('[2] mock_exam_list_page ok')
