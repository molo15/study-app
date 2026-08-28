# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

p = r'D:\study_app\app\lib\ui\mock_exam_list_page.dart'
s = open(p, encoding='utf-8').read()

# (1) import 排题页
old = """import '../data/quiz_repository.dart';
import '../models/models.dart';
import 'mock_exam_page.dart';
import 'glass_app_bar.dart';
import 'app_routes.dart';"""
new = """import '../data/quiz_repository.dart';
import '../models/models.dart';
import 'mock_exam_page.dart';
import 'composite_loading_page.dart';
import 'glass_app_bar.dart';
import 'app_routes.dart';"""
assert old in s, 'import anchor'
s = s.replace(old, new, 1)

# (2) _load 里查综合卷历史成绩
old = """  bool _loading = true;
  String? _error;
  List<MockPaper> _papers = const [];
  Map<String, List<MockSession>> _history = const {};"""
new = """  bool _loading = true;
  String? _error;
  List<MockPaper> _papers = const [];
  Map<String, List<MockSession>> _history = const {};

  /// 综合模拟卷（随机组卷，150 分制；不落 mock_papers 表，列表页恒置顶）
  static const _composite = MockPaper(
    id: 'composite',
    bankId: 'composite',
    name: '综合模拟卷',
    durationMin: 180,
    questionIds: [],
  );"""
assert old in s, 'field anchor'
s = s.replace(old, new, 1)

old = """      final papers = await repo.mockPapers(bankId: widget.bankId);
      final history = <String, List<MockSession>>{};
      for (final p in papers) {
        history[p.id] = await repo.mockSessions(paperId: p.id);
      }"""
new = """      final papers = await repo.mockPapers(bankId: widget.bankId);
      final history = <String, List<MockSession>>{};
      history['composite'] = await repo.mockSessions(paperId: 'composite');
      for (final p in papers) {
        history[p.id] = await repo.mockSessions(paperId: p.id);
      }"""
assert old in s, 'load history anchor'
s = s.replace(old, new, 1)

# (3) build：列表顶部加综合卷卡片（index 0），其余为各科卷
old = """          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _papers.length,
              itemBuilder: (context, index) {
                final p = _papers[index];
                final sessions = _history[p.id] ?? const <MockSession>[];
                return Card(
                  child: ListTile(
                    leading: Container(
                      width: 40,
                      height: 40,
                      decoration: BoxDecoration(
                        color: theme.colorScheme.tertiary.withValues(
                          alpha: 0.12,
                        ),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Icon(
                        Icons.assignment_outlined,
                        color: theme.colorScheme.tertiary,
                      ),
                    ),
                    title: Text(p.name),
                    subtitle: Text(
                      '${p.questionIds.length} 题 · 限时 ${p.durationMin} 分钟'
                      '${sessions.isNotEmpty ? ' · 最近 ${sessions.first.score} 分' : ''}',
                    ),
                    trailing: const Icon(Icons.chevron_right),
                    onTap: () => Navigator.of(context).push(
                      AppPageRoute(builder: (_) => MockExamPage(paper: p)),
                    ),
                  ),
                );
              },
            ),
    );
  }
}"""
new = """          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _papers.length + 1,
              itemBuilder: (context, index) {
                if (index == 0) {
                  // 综合模拟卷：随机组卷入口（恒置顶）
                  final sessions =
                      _history['composite'] ?? const <MockSession>[];
                  return Card(
                    child: ListTile(
                      leading: Container(
                        width: 40,
                        height: 40,
                        decoration: BoxDecoration(
                          color: theme.colorScheme.primary.withValues(
                            alpha: 0.12,
                          ),
                          borderRadius: BorderRadius.circular(10),
                        ),
                        child: Icon(
                          Icons.auto_awesome,
                          color: theme.colorScheme.primary,
                        ),
                      ),
                      title: Text(
                        _composite.name,
                        style: const TextStyle(fontWeight: FontWeight.w700),
                      ),
                      subtitle: Text(
                        '150 分 · 5 科随机组卷 · 限时 180 分钟'
                        '${sessions.isNotEmpty ? ' · 最近 ${sessions.first.score} 分' : ''}',
                      ),
                      trailing: const Icon(Icons.chevron_right),
                      onTap: () => Navigator.of(context).push(
                        AppPageRoute(builder: (_) => const CompositeLoadingPage()),
                      ),
                    ),
                  );
                }
                final p = _papers[index - 1];
                final sessions = _history[p.id] ?? const <MockSession>[];
                return Card(
                  child: ListTile(
                    leading: Container(
                      width: 40,
                      height: 40,
                      decoration: BoxDecoration(
                        color: theme.colorScheme.tertiary.withValues(
                          alpha: 0.12,
                        ),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Icon(
                        Icons.assignment_outlined,
                        color: theme.colorScheme.tertiary,
                      ),
                    ),
                    title: Text(p.name),
                    subtitle: Text(
                      '${p.questionIds.length} 题 · 限时 ${p.durationMin} 分钟'
                      '${sessions.isNotEmpty ? ' · 最近 ${sessions.first.score} 分' : ''}',
                    ),
                    trailing: const Icon(Icons.chevron_right),
                    onTap: () => Navigator.of(context).push(
                      AppPageRoute(builder: (_) => MockExamPage(paper: p)),
                    ),
                  ),
                );
              },
            ),
    );
  }
}"""
assert old in s, 'build anchor'
s = s.replace(old, new, 1)

open(p, 'w', encoding='utf-8').write(s)
print('[3] mock_exam_list_page ok')
