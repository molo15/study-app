part of 'settings_page.dart';

class _ThemePanelPage extends ConsumerStatefulWidget {
  const _ThemePanelPage();

  @override
  ConsumerState<_ThemePanelPage> createState() => _ThemePanelPageState();
}

class _ThemePanelPageState extends ConsumerState<_ThemePanelPage> {
  static const _presetColors = [
    '#00696D',
    '#525E7D',
    '#7D5260',
    '#B2780A',
    '#2E7D32',
    '#006A94',
    '#8A2BE2',
    '#D81B60',
    '#546E7A',
    '#BF360C',
  ];

  static const _presetBackgrounds = [
    '#F4F7F6',
    '#FDF3E7',
    '#EAF2F8',
    '#F6F0F8',
    '#F2F8F0',
    '#FDF6EC',
    '#EBF5F5',
    '#F9F5F0',
  ];

  late AppThemeConfig _config;
  bool _ready = false;
  bool _reviewEnabled = false; // 审题标记开关（默认关）

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final config = await ref.read(themeControllerProvider.future);
    final repo = await ref.read(quizRepositoryProvider);
    final reviewEnabled = await repo.reviewModeEnabled();
    if (!mounted) return;
    setState(() {
      _config = config;
      _reviewEnabled = reviewEnabled;
      _ready = true;
    });
  }

  Future<void> _apply(AppThemeConfig next) async {
    await ref.read(themeControllerProvider.notifier).apply(next);
    if (mounted) setState(() => _config = next);
  }

  /// 选择本地图片作为全局背景（需求：全局背景图）
  Future<void> _pickBackgroundImage() async {
    try {
      final file = await FilePicker.pickFile(
        type: FileType.image,
        dialogTitle: '选择背景图片',
      );
      if (file == null) return;
      final path = file.path;
      if (path == null || path.isEmpty) {
        if (mounted) {
          ScaffoldMessenger.of(
            context,
          ).showSnackBar(const SnackBar(content: Text('无法读取该图片路径')));
        }
        return;
      }
      await _apply(_config.copyWith(backgroundImagePath: path));
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('选择背景图失败：$e')));
      }
    }
  }

  /// 颜色选择器：点击区域 ≥48dp，带 Tooltip 与 Semantics 标签（审查 P1-3）
  /// P1 主题预设卡片：主色+背景色预览 + 名称
  Widget _presetCard({
    required String name,
    required AppThemeConfig preset,
    required bool selected,
    required VoidCallback onTap,
  }) {
    final theme = Theme.of(context);
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 90,
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: theme.cardColor,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: selected ? theme.colorScheme.primary : theme.colorScheme.outlineVariant,
            width: selected ? 2 : 1,
          ),
        ),
        child: Column(
          children: [
            Container(
              height: 36,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(8),
                color: parseHexColor(preset.backgroundColor),
              ),
              child: Row(
                children: [
                  Container(
                    width: 36,
                    height: 36,
                    decoration: BoxDecoration(
                      color: parseHexColor(preset.primaryColor),
                      borderRadius: const BorderRadius.horizontal(left: Radius.circular(8)),
                    ),
                  ),
                  const Spacer(),
                  if (preset.darkMode)
                    const Padding(
                      padding: EdgeInsets.only(right: 6),
                      child: Icon(Icons.dark_mode_outlined, size: 14, color: Colors.white54),
                    ),
                ],
              ),
            ),
            const SizedBox(height: 6),
            Text(
              name,
              style: theme.textTheme.labelSmall?.copyWith(
                fontWeight: selected ? FontWeight.w700 : FontWeight.w500,
                color: selected ? theme.colorScheme.primary : null,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _colorSwatch({
    required String hex,
    required bool selected,
    required String label,
    required Color unselectedBorder,
    required VoidCallback onTap,
  }) {
    final theme = Theme.of(context);
    return Semantics(
      button: true,
      label: '$label，颜色 $hex${selected ? '，已选中' : ''}',
      child: Tooltip(
        message: '$label $hex',
        child: GestureDetector(
          onTap: onTap,
          child: Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: parseHexColor(hex),
              shape: BoxShape.circle,
              border: Border.all(
                color: selected
                    ? theme.colorScheme.onSurface
                    : unselectedBorder,
                width: 3,
              ),
            ),
          ),
        ),
      ),
    );
  }

  /// 顶部实时预览卡：随下方调整即时变化
  Widget _buildPreviewCard(ThemeData theme) {
    final bg = _config.darkMode ? const Color(0xFF101418) : _config.background;
    final cardColor =
        (_config.darkMode ? const Color(0xFF1E2428) : Colors.white).withValues(
          alpha: _config.cardOpacity,
        );
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(_config.cornerRadius),
      ),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: cardColor,
          borderRadius: BorderRadius.circular(_config.cornerRadius),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '实时预览',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              '主色 / 背景 / 卡片透明度 / 圆角 / 深色模式会随下方设置即时变化',
              style: theme.textTheme.bodySmall,
            ),
            const SizedBox(height: 16),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                FilledButton(
                  onPressed: () {},
                  style: FilledButton.styleFrom(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 20,
                      vertical: 10,
                    ),
                  ),
                  child: const Text('主按钮'),
                ),
                FilledButton.tonal(onPressed: () {}, child: const Text('次按钮')),
              ],
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: GlassAppBar(title: const Text('主题定制')),
      body: !_ready
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                // 实时预览
                const AppSectionHeader(title: '预览', helperText: '先看效果，再调整参数'),
                const SizedBox(height: 8),
                _buildPreviewCard(theme),
                const SizedBox(height: 24),
                // P1 主题预设：一键切换整套主题
                const AppSectionHeader(title: '主题预设', helperText: '一键切换整套配色与风格'),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 12,
                  runSpacing: 12,
                  children: [
                    for (final (name, preset) in AppThemeConfig.presets)
                      _presetCard(
                        name: name,
                        preset: preset,
                        selected: _config.primaryColor == preset.primaryColor &&
                            _config.backgroundColor == preset.backgroundColor,
                        onTap: () => _apply(preset.copyWith(
                          reduceMotion: _config.reduceMotion,
                          backgroundImagePath: _config.backgroundImagePath,
                          backgroundOpacity: _config.backgroundOpacity,
                          cardOpacity: _config.cardOpacity,
                          hideStatusBar: _config.hideStatusBar,
                        )),
                      ),
                  ],
                ),
                const SizedBox(height: 24),
                // 主色预设
                const AppSectionHeader(title: '主色'),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 12,
                  runSpacing: 12,
                  children: [
                    for (final hex in _presetColors)
                      _colorSwatch(
                        hex: hex,
                        label: '主色',
                        selected: _config.primaryColor == hex,
                        unselectedBorder: Colors.transparent,
                        onTap: () =>
                            _apply(_config.copyWith(primaryColor: hex)),
                      ),
                  ],
                ),
                const SizedBox(height: 24),
                // 背景色预设
                const AppSectionHeader(title: '背景色'),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 12,
                  runSpacing: 12,
                  children: [
                    for (final hex in _presetBackgrounds)
                      _colorSwatch(
                        hex: hex,
                        label: '背景色',
                        selected: _config.backgroundColor == hex,
                        unselectedBorder: theme.colorScheme.outlineVariant,
                        onTap: () =>
                            _apply(_config.copyWith(backgroundColor: hex)),
                      ),
                  ],
                ),
                const SizedBox(height: 24),
                // 背景图片（需求：全局背景图，允许用户自选本地图）
                // web 无本地文件路径概念，隐藏整块（Phase 2.2）
                if (!kIsWeb) ...[
                  const AppSectionHeader(title: '背景图片'),
                  const SizedBox(height: 8),
                  Card(
                    child: ListTile(
                      leading: _IconBox(
                        icon: Icons.image_outlined,
                        color: theme.colorScheme.secondary,
                      ),
                      title: Text(
                        _config.backgroundImagePath.isEmpty
                            ? '未设置背景图'
                            : '已设置背景图',
                      ),
                      subtitle: Text(
                        _config.backgroundImagePath.isEmpty
                            ? '选择一张本地图片作为全局背景'
                            : '点按更换',
                      ),
                      trailing: const Icon(Icons.chevron_right),
                      onTap: _pickBackgroundImage,
                    ),
                  ),
                  const SizedBox(height: 8),
                  // 背景图透明度（需求：允许用户自己调节）
                  Slider(
                    value: _config.backgroundOpacity,
                    min: 0.1,
                    max: 1.0,
                    divisions: 9,
                    label:
                        '${(_config.backgroundOpacity * 100).toStringAsFixed(0)}%',
                    onChanged: (v) => setState(
                      () => _config = _config.copyWith(backgroundOpacity: v),
                    ),
                    onChangeEnd: (_) => _apply(_config),
                  ),
                  if (_config.backgroundImagePath.isNotEmpty)
                    Center(
                      child: TextButton.icon(
                        onPressed: () =>
                            _apply(_config.copyWith(backgroundImagePath: '')),
                        icon: const Icon(Icons.remove_circle_outline),
                        label: const Text('移除背景图'),
                      ),
                    ),
                  const SizedBox(height: 8),
                ],
                // 卡片透明度
                const AppSectionHeader(title: '卡片透明度'),
                Slider(
                  value: _config.cardOpacity,
                  min: 0.3,
                  max: 1.0,
                  divisions: 7,
                  label: '${(_config.cardOpacity * 100).toStringAsFixed(0)}%',
                  onChanged: (v) => setState(
                    () => _config = _config.copyWith(cardOpacity: v),
                  ),
                  onChangeEnd: (_) => _apply(_config),
                ),
                const SizedBox(height: 8),
                // 卡片圆角
                const AppSectionHeader(title: '卡片圆角'),
                Slider(
                  value: _config.cornerRadius,
                  min: 8,
                  max: 28,
                  divisions: 10,
                  label: '${_config.cornerRadius.round()}',
                  onChanged: (v) => setState(
                    () => _config = _config.copyWith(cornerRadius: v),
                  ),
                  onChangeEnd: (_) => _apply(_config),
                ),
                const SizedBox(height: 8),
                // 深色模式
                SwitchListTile(
                  secondary: const Icon(Icons.dark_mode_outlined),
                  title: const Text('深色模式'),
                  subtitle: const Text('暗色背景，夜间护眼'),
                  value: _config.darkMode,
                  onChanged: (v) => _apply(_config.copyWith(darkMode: v)),
                ),
                const SizedBox(height: 8),
                // 隐藏状态栏
                SwitchListTile(
                  secondary: const Icon(Icons.fullscreen_outlined),
                  title: const Text('隐藏状态栏'),
                  subtitle: const Text('沉浸式全屏，下拉可临时唤出系统栏'),
                  value: _config.hideStatusBar,
                  onChanged: (v) => _apply(_config.copyWith(hideStatusBar: v)),
                ),
                const SizedBox(height: 8),
                // 减少动效（P0 手感优化）
                SwitchListTile(
                  secondary: const Icon(Icons.speed_outlined),
                  title: const Text('减少动效'),
                  subtitle: const Text('关闭判题抖动/弹性放大等装饰动效，仅保留颜色反馈，更流畅省电'),
                  value: _config.reduceMotion,
                  onChanged: (v) => _apply(_config.copyWith(reduceMotion: v)),
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
                const SizedBox(height: 8),
                // 恢复默认
                Center(
                  child: TextButton.icon(
                    onPressed: () => _apply(AppThemeConfig.defaults()),
                    icon: const Icon(Icons.restore),
                    label: const Text('恢复默认主题'),
                  ),
                ),
              ],
            ),
    );
  }
}


/// 数字步进器（学习目标每日题量加减）
