# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ============ settings_page.dart ============
p = r'D:\study_app\app\lib\ui\settings_page.dart'
s = open(p, encoding='utf-8').read()

# (1) 加 _reviewEnabled 字段
old = "  bool _showPracticeTimer = false;\n  StudyGoal _studyGoal = const StudyGoal();"
new = ("  bool _showPracticeTimer = false;\n"
       "  bool _reviewEnabled = false; // 审题标记开关（默认关）\n"
       "  StudyGoal _studyGoal = const StudyGoal();")
assert old in s, 'settings field anchor'
s = s.replace(old, new, 1)

# (2) _load 里读取 reviewModeEnabled
old = """      final showPracticeTimer = await repo.practiceTimerVisible();
      final studyGoal = await repo.studyGoal() ?? const StudyGoal();
      if (!mounted) return;
      setState(() {
        _banks = banks;
        _desiredRetention = retention;
        _showPracticeTimer = showPracticeTimer;
        _studyGoal = studyGoal;
        _loading = false;
      });"""
new = """      final showPracticeTimer = await repo.practiceTimerVisible();
      final reviewEnabled = await repo.reviewModeEnabled();
      final studyGoal = await repo.studyGoal() ?? const StudyGoal();
      if (!mounted) return;
      setState(() {
        _banks = banks;
        _desiredRetention = retention;
        _showPracticeTimer = showPracticeTimer;
        _reviewEnabled = reviewEnabled;
        _studyGoal = studyGoal;
        _loading = false;
      });"""
assert old in s, 'settings load anchor'
s = s.replace(old, new, 1)

# (3) if (reviewModeEnabled) -> if (_reviewEnabled)
old = "                      if (reviewModeEnabled)\n                        ListTile("
new = "                      if (_reviewEnabled)\n                        ListTile("
assert old in s, 'settings review gate anchor'
s = s.replace(old, new, 1)

# (4) 在 _exportReviewFlags 方法后加 _importBackup 和 _showImportFormat
old = """    await _exportToFile(
      'review_flags_$stamp.json',
      json,
      emptyHint: '当前没有审题标记（刷题时点击题号旁的旗子即可标记）',
      count: count,
    );
  }

  // ---------- 题库包管理操作 ----------"""
new = """    await _exportToFile(
      'review_flags_$stamp.json',
      json,
      emptyHint: '当前没有审题标记（刷题时点击题号旁的旗子即可标记）',
      count: count,
    );
  }

  /// 导入备份：从导出的 JSON 全量恢复（清空现有数据，不可撤销）
  Future<void> _importBackup() async {
    try {
      final file = await FilePicker.pickFile(
        type: FileType.custom,
        allowedExtensions: ['json'],
        dialogTitle: '选择备份文件（.json）',
      );
      if (file == null) return;
      final text = utf8.decode(await file.readAsBytes());
      final ok = await showDialog<bool>(
        context: context,
        builder: (ctx) => AlertDialog(
          title: const Text('导入备份？'),
          content: const Text(
            '将清空当前全部题目、作答记录、复习进度、错题本并恢复为备份内容，'
            '不可撤销。建议先「导出备份」留存当前数据。',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx, false),
              child: const Text('取消'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(ctx, true),
              child: const Text('导入并覆盖'),
            ),
          ],
        ),
      );
      if (ok != true) return;
      final repo = await ref.read(quizRepositoryProvider);
      await repo.restoreJson(text);
      _toast('已从备份恢复全部数据');
      await _load();
    } on FormatException catch (e) {
      _toast('备份文件无效：${e.message}');
    } catch (e) {
      _toast('导入备份失败：$e');
    }
  }

  /// 关于：题库导入格式说明弹窗
  void _showImportFormat() {
    showDialog<void>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('题库导入格式'),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: const [
              Text('支持两种题库包容器：', style: TextStyle(fontWeight: FontWeight.w700)),
              SizedBox(height: 6),
              Text('· .json：单文件，顶层含 manifest 字段 + questions 数组'),
              Text('· .zip：manifest.json + questions/ 目录（可按章节分文件）'),
              SizedBox(height: 12),
              Text('题目必填字段：', style: TextStyle(fontWeight: FontWeight.w700)),
              SizedBox(height: 6),
              Text('· id：全局唯一，如 bank-xxx:q_00001'),
              Text('· type：single_choice / multi_choice / true_false / blank / short_answer'),
              Text('· stem：题干'),
              Text('· answer：答案（选择题为选项 key 或正确项文本）'),
              Text('· options：选择题选项数组 [{"key":"A","text":"..."}]'),
              SizedBox(height: 12),
              Text('可选字段：', style: TextStyle(fontWeight: FontWeight.w700)),
              SizedBox(height: 6),
              Text('· explanation：解析、chapter：章节、purpose：basic/test'),
              Text('· formatVersion：1-4（缺省按基础格式解析）'),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('知道了'),
          ),
        ],
      ),
    );
  }

  // ---------- 题库包管理操作 ----------"""
assert old in s, 'settings import methods anchor'
s = s.replace(old, new, 1)

# (5) 导出备份 ListTile 后加导入备份
old = """                        title: const Text('导出备份'),
                        subtitle: const Text('全部题目/作答/复习进度导出为 JSON 文件'),
                        trailing: const Icon(Icons.chevron_right),
                        onTap: _exportBackup,
                      ),"""
new = """                        title: const Text('导出备份'),
                        subtitle: const Text('全部题目/作答/复习进度导出为 JSON 文件'),
                        trailing: const Icon(Icons.chevron_right),
                        onTap: _exportBackup,
                      ),
                      const Divider(height: 1, indent: 16, endIndent: 16),
                      ListTile(
                        leading: _IconBox(
                          icon: Icons.restore_outlined,
                          color: theme.colorScheme.primary,
                        ),
                        title: const Text('导入备份'),
                        subtitle: const Text('从导出的 JSON 备份恢复全部数据（覆盖当前）'),
                        trailing: const Icon(Icons.chevron_right),
                        onTap: _importBackup,
                      ),"""
assert old in s, 'settings import entry anchor'
s = s.replace(old, new, 1)

# (6) 题库包管理默认展开
old = "                      ExpansionTile(\n                        initiallyExpanded: false,"
new = "                      ExpansionTile(\n                        initiallyExpanded: true,"
assert old in s, 'settings expansion anchor'
s = s.replace(old, new, 1)

# (7) 关于区：考研刷题 ListTile 后加题库导入格式
old = """                Card(
                  child: ListTile(
                    leading: _IconBox(
                      icon: Icons.school_outlined,
                      color: theme.colorScheme.tertiary,
                    ),
                    title: const Text('考研刷题'),
                    subtitle: const Text('本地离线刷题 · 学习数据不出设备'),
                  ),
                ),"""
new = """                Card(
                  clipBehavior: Clip.antiAlias,
                  child: Column(
                    children: [
                      ListTile(
                        leading: _IconBox(
                          icon: Icons.school_outlined,
                          color: theme.colorScheme.tertiary,
                        ),
                        title: const Text('考研刷题'),
                        subtitle: const Text('本地离线刷题 · 学习数据不出设备'),
                      ),
                      const Divider(height: 1, indent: 16, endIndent: 16),
                      ListTile(
                        leading: _IconBox(
                          icon: Icons.input_outlined,
                          color: theme.colorScheme.tertiary,
                        ),
                        title: const Text('题库导入格式'),
                        subtitle: const Text('自制题库包的 .json / .zip 格式要求'),
                        trailing: const Icon(Icons.chevron_right),
                        onTap: _showImportFormat,
                      ),
                    ],
                  ),
                ),"""
assert old in s, 'settings about anchor'
s = s.replace(old, new, 1)

open(p, 'w', encoding='utf-8').write(s)
print('[5] settings_page ok')

# ============ settings_theme_panel.dart ============
p = r'D:\study_app\app\lib\ui\settings_theme_panel.dart'
s = open(p, encoding='utf-8').read()

# (a) 加 _reviewEnabled 字段
old = "  late AppThemeConfig _config;\n  bool _ready = false;"
new = ("  late AppThemeConfig _config;\n"
       "  bool _ready = false;\n"
       "  bool _reviewEnabled = false; // 审题标记开关（默认关）")
assert old in s, 'panel field anchor'
s = s.replace(old, new, 1)

# (b) _load 读 reviewModeEnabled
old = """  Future<void> _load() async {
    final config = await ref.read(themeControllerProvider.future);
    if (!mounted) return;
    setState(() {
      _config = config;
      _ready = true;
    });
  }"""
new = """  Future<void> _load() async {
    final config = await ref.read(themeControllerProvider.future);
    final repo = await ref.read(quizRepositoryProvider);
    final reviewEnabled = await repo.reviewModeEnabled();
    if (!mounted) return;
    setState(() {
      _config = config;
      _reviewEnabled = reviewEnabled;
      _ready = true;
    });
  }"""
assert old in s, 'panel load anchor'
s = s.replace(old, new, 1)

# (c) 深色模式/隐藏状态栏之后加"功能"分区：审题标记开关
old = """                const SizedBox(height: 8),
                // 隐藏状态栏
                SwitchListTile(
                  secondary: const Icon(Icons.fullscreen_outlined),
                  title: const Text('隐藏状态栏'),
                  subtitle: const Text('沉浸式全屏，下拉可临时唤出系统栏'),
                  value: _config.hideStatusBar,
                  onChanged: (v) => _apply(_config.copyWith(hideStatusBar: v)),
                ),
                const SizedBox(height: 8),"""
new = """                const SizedBox(height: 8),
                // 隐藏状态栏
                SwitchListTile(
                  secondary: const Icon(Icons.fullscreen_outlined),
                  title: const Text('隐藏状态栏'),
                  subtitle: const Text('沉浸式全屏，下拉可临时唤出系统栏'),
                  value: _config.hideStatusBar,
                  onChanged: (v) => _apply(_config.copyWith(hideStatusBar: v)),
                ),
                const SizedBox(height: 8),
                // 功能开关（审题标记）
                const AppSectionHeader(title: '功能', helperText: '按需开启的附加功能'),
                const SizedBox(height: 8),
                SwitchListTile(
                  secondary: const Icon(Icons.flag_outlined),
                  title: const Text('审题标记'),
                  subtitle: const Text('开启后刷题页显示旗子标记，设置页可导出标记清单'),
                  value: _reviewEnabled,
                  onChanged: (v) async {
                    final repo = await ref.read(quizRepositoryProvider);
                    await repo.setReviewModeEnabled(v);
                    if (mounted) setState(() => _reviewEnabled = v);
                  },
                ),
                const SizedBox(height: 8),"""
assert old in s, 'panel switch anchor'
s = s.replace(old, new, 1)

open(p, 'w', encoding='utf-8').write(s)
print('[6] settings_theme_panel ok')
