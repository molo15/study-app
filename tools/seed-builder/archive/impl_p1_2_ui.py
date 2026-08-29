# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

p = r'D:\study_app\app\lib\ui\mock_exam_page.dart'
s = open(p, encoding='utf-8').read()

# (1) import 回顾页
old = """import 'glass_app_bar.dart';
import 'practice_page.dart' show typeColor, typeLabel;"""
new = """import 'glass_app_bar.dart';
import 'mock_review_page.dart';
import 'practice_page.dart' show typeColor, typeLabel;"""
assert old in s, 'import anchor'
s = s.replace(old, new, 1)

# (2) 结果弹窗 actions 加"查看逐题解析"
old = """        actions: [
          FilledButton(
            onPressed: () {
              Navigator.of(context).pop();
              Navigator.of(context).pop(); // 返回列表页
            },
            child: const Text('完成'),
          ),
        ],
      ),
    );
  }"""
new = """        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(context).pop(); // 关结果弹窗
              Navigator.of(context).push(
                AppPageRoute(
                  builder: (_) => MockReviewPage(
                    questions: _questions,
                    answers: _answers,
                  ),
                ),
              );
            },
            child: const Text('查看逐题解析'),
          ),
          FilledButton(
            onPressed: () {
              Navigator.of(context).pop();
              Navigator.of(context).pop(); // 返回列表页
            },
            child: const Text('完成'),
          ),
        ],
      ),
    );
  }"""
assert old in s, 'result actions anchor'
s = s.replace(old, new, 1)

# (3) P2-3 综合卷学科标签：build 里章节行
old = """              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  q.chapter,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Theme.of(context).colorScheme.outline,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),"""
new = """              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  // 综合卷跨科标注：学科名 · 章节（P2-3）
                  widget.pointsByType == null
                      ? q.chapter
                      : [mockBankLabel(q.bankId), q.chapter]
                            .where((s) => s.isNotEmpty)
                            .join(' · '),
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Theme.of(context).colorScheme.outline,
                  ),
                  overflow: TextOverflow.ellipsis,
                ),
              ),"""
assert old in s, 'chapter label anchor'
s = s.replace(old, new, 1)

open(p, 'w', encoding='utf-8').write(s)
print('[5] mock_exam_page ok')

# ============ home_page.dart：P2-2 计数含综合卷 ============
p = r'D:\study_app\app\lib\ui\home_page.dart'
s = open(p, encoding='utf-8').read()
old = """            subtitle: Text(
              _mockPapers.isEmpty
                  ? '暂未配置模拟卷'
                  : '${_mockPapers.length} 套卷 · 限时作答',
            ),"""
new = """            subtitle: Text(
              // 综合卷恒存在（随机组卷），计数 +1（P2-2）
              _mockPapers.isEmpty
                  ? '1 套综合卷 · 随机组卷'
                  : '${_mockPapers.length + 1} 套卷 · 限时作答',
            ),"""
assert old in s, 'home subtitle anchor'
s = s.replace(old, new, 1)
open(p, 'w', encoding='utf-8').write(s)
print('[6] home_page ok')
