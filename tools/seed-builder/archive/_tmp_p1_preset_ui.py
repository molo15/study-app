# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
p = r'D:\study_app\app\lib\ui\settings_theme_panel.dart'
s = open(p, encoding='utf-8').read()

# 在预览卡之后、主色之前插入主题预设选择器
old_anchor = """                _buildPreviewCard(theme),
                const SizedBox(height: 24),
                // 主色预设
                const AppSectionHeader(title: '主色'),"""

new_anchor = """                _buildPreviewCard(theme),
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
                const AppSectionHeader(title: '主色'),"""

s = s.replace(old_anchor, new_anchor)

# 在 State 类末尾（build 方法之后）加 _presetCard 方法
# 找到 _colorSwatch 方法之前插入
old_method_anchor = "  Widget _colorSwatch({"
new_method = """  /// P1 主题预设卡片：主色+背景色预览 + 名称
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

  Widget _colorSwatch({"""

s = s.replace(old_method_anchor, new_method)

open(p, 'w', encoding='utf-8', newline='').write(s)
print('主题预设选择器已添加')
print('  presets UI:', '_presetCard' in s)
print('  预设列表:', 'AppThemeConfig.presets' in s)
