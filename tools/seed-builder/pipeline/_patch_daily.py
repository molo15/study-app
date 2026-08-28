# -*- coding: utf-8 -*-
"""删除设置页学习目标下的每日新题/复习目标（UI + 方法 + _GoalInput 组件），并调整相关文案。"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ---------- settings_page ----------
f = r'D:\study_app\app\lib\ui\settings_page.dart'
s = open(f, encoding='utf-8').read()

# 1) 删除两个 ListTile（每日新题/复习目标）+ 中间 Divider
old1 = """          const Divider(height: 1, indent: 16, endIndent: 16),
          ListTile(
            enabled: goal.enabled,
            leading: const Icon(Icons.add_circle_outline),
            title: const Text('每日新题目标'),
            trailing: _GoalInput(
              value: goal.dailyNew,
              onDelta: (delta) => _adjustDaily(isNew: true, delta: delta),
              onCommit: (v) => _setDaily(isNew: true, value: v),
            ),
          ),
          ListTile(
            enabled: goal.enabled,
            leading: const Icon(Icons.autorenew),
            title: const Text('每日复习目标'),
            trailing: _GoalInput(
              value: goal.dailyReview,
              onDelta: (delta) => _adjustDaily(isNew: false, delta: delta),
              onCommit: (v) => _setDaily(isNew: false, value: v),
            ),
          ),
          Padding("""
new1 = """          Padding("""
assert old1 in s, 'anchor1 not found'
s = s.replace(old1, new1)

# 2) 删除 _adjustDaily 与 _setDaily 方法
old2 = """  Future<void> _adjustDaily({required bool isNew, required int delta}) async {
    final base = isNew ? _studyGoal.dailyNew : _studyGoal.dailyReview;
    final next = (base + delta).clamp(0, 200);
    setState(() => _studyGoal = StudyGoal(
      examDate: _studyGoal.examDate,
      dailyNew: isNew ? next : _studyGoal.dailyNew,
      dailyReview: isNew ? _studyGoal.dailyReview : next,
      enabled: _studyGoal.enabled,
    ));
    await _saveStudyGoal();
  }

  /// 输入式目标：直接设置每日题量（clamp 0-200）
  Future<void> _setDaily({required bool isNew, required int value}) async {
    final clamped = value.clamp(0, 200);
    setState(() => _studyGoal = StudyGoal(
      examDate: _studyGoal.examDate,
      dailyNew: isNew ? clamped : _studyGoal.dailyNew,
      dailyReview: isNew ? _studyGoal.dailyReview : clamped,
      enabled: _studyGoal.enabled,
    ));
    await _saveStudyGoal();
  }

"""
assert old2 in s, 'anchor2 not found'
s = s.replace(old2, '')

# 3) 开关 subtitle 文案
old3 = """            subtitle: Text(goal.enabled
                ? '已启用 · 首页显示倒计时与每日任务'
                : '设置考试日期与每日题量，首页显示倒计时'),"""
new3 = """            subtitle: Text(goal.enabled
                ? '已启用 · 首页显示考试倒计时'
                : '设置考试日期，首页显示倒计时'),"""
assert old3 in s, 'anchor3 not found'
s = s.replace(old3, new3)

# 4) 底部提示文案
old4 = "'计划倒排仅为建议，可随时在首页覆盖或暂停',"
new4 = "'设置考试日期后，首页会显示距离考试的天数',"
assert old4 in s, 'anchor4 not found'
s = s.replace(old4, new4)

open(f, 'w', encoding='utf-8').write(s)
print('settings_page: 每日目标 UI/方法/文案 已删改')
print('  残留 _GoalInput 使用:', s.count('_GoalInput('), '| 残留 _adjustDaily:', s.count('_adjustDaily'))

# ---------- 删除 _GoalInput 类 ----------
lines = s.split('\n')
# 找到 class _GoalInput 起始（含其上方错位注释）
start = None
for i, l in enumerate(lines):
    if l.startswith('class _GoalInput extends StatefulWidget'):
        start = i
        break
assert start is not None, 'GoalInput class not found'
# 上方的错位注释（主题定制面板）一并删除：从它前面最近的空行后开始
# 回溯：start-3 到 start 的注释块
del_start = start - 1
# 若上方是注释块（/// 或空行），向前扩展
while del_start > 0:
    prev = lines[del_start - 1].strip()
    if prev.startswith('///') or prev == '':
        del_start -= 1
    else:
        break
# 保留类前一个非注释行（类的 }）后的结构
del lines[del_start:start + 5]  # 仅作占位，实际下面精确删到文件尾
open(f, 'w', encoding='utf-8').write('\n'.join(lines))
print('（_GoalInput 类待精确删除）')

# 重新精确删除：从 del_start 到文件尾（类到末尾）
lines = open(f, encoding='utf-8').read().split('\n')
for i, l in enumerate(lines):
    if l.startswith('class _GoalInput extends StatefulWidget'):
        start = i
        break
else:
    start = -1
if start != -1:
    # 回溯到上方注释块起点
    ds = start - 1
    while ds > 0:
        prev = lines[ds - 1].strip()
        if prev.startswith('///') or prev == '':
            ds -= 1
        else:
            break
    # 删除 ds..末尾，但保留最后一个非空（类的右括号 }）
    # 文件末尾是类的 }，删除后文件应以倒数第二个顶层元素结束
    del lines[ds:]
    # 去掉尾部多余空行
    while lines and lines[-1].strip() == '':
        lines.pop()
    open(f, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print(f'settings_page: 已删除 _GoalInput 类（行 {ds+1} 起至文件尾）')
else:
    print('settings_page: _GoalInput 类未找到')

# ---------- home_page 倒计时卡副标题 ----------
f2 = r'D:\study_app\app\lib\ui\home_page.dart'
s2 = open(f2, encoding='utf-8').read()
old5 = """                    Text(
                      goal.dailyNew + goal.dailyReview == 0
                          ? '每日目标未设置 · 点击设置'
                          : '每日目标：新题 ${goal.dailyNew} · 复习 ${goal.dailyReview}'
                              ' · 今日已做 $_todayAnswered',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),"""
new5 = """                    Text(
                      '考试日期 ${goal.examDate ?? '未设置'} · 今日已做 $_todayAnswered 题',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),"""
assert old5 in s2, 'anchor5 not found'
s2 = s2.replace(old5, new5)
open(f2, 'w', encoding='utf-8').write(s2)
print('home_page: 倒计时卡副标题已去除每日目标文案')
