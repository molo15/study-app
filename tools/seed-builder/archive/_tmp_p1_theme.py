# -*- coding: utf-8 -*-
"""P1-1: 主题预设 + 修复 P0 _OptionTile shakeCtrl 残留问题"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ===== 1. 修复 P0：_OptionTile didUpdateWidget 检测 question 变化重置 shakeCtrl =====
p = r'D:\study_app\app\lib\ui\practice_question_view.dart'
s = open(p, encoding='utf-8').read()

old_did = """  @override
  void didUpdateWidget(covariant _OptionTile oldWidget) {
    super.didUpdateWidget(oldWidget);
    final isCorrect = widget.question.answer.contains(widget.option.key);
    if (!oldWidget.submitted &&
        widget.submitted &&
        widget.selected &&
        !isCorrect &&
        !widget.reduceMotion) {
      _shakeCtrl.forward(from: 0);
    }
  }"""

new_did = """  @override
  void didUpdateWidget(covariant _OptionTile oldWidget) {
    super.didUpdateWidget(oldWidget);
    // P0 修复：切题时 question.id 变化，重置抖动控制器，避免偏移残留
    if (oldWidget.question.id != widget.question.id) {
      _shakeCtrl.value = 0;
    }
    final isCorrect = widget.question.answer.contains(widget.option.key);
    if (!oldWidget.submitted &&
        widget.submitted &&
        widget.selected &&
        !isCorrect &&
        !widget.reduceMotion) {
      _shakeCtrl.forward(from: 0);
    }
  }"""

s = s.replace(old_did, new_did)
open(p, 'w', encoding='utf-8', newline='').write(s)
print('P0 修复: _OptionTile 切题重置 shakeCtrl:', 'oldWidget.question.id != widget.question.id' in s)

# ===== 2. 主题预设：AppThemeConfig 加静态 presets =====
p2 = r'D:\study_app\app\lib\ui\theme_controller.dart'
s2 = open(p2, encoding='utf-8').read()

# 在 AppThemeConfig.defaults() 之后加 presets 静态常量
old_defaults = """  factory AppThemeConfig.defaults() => const AppThemeConfig();"""

new_defaults = """  factory AppThemeConfig.defaults() => const AppThemeConfig();

  /// P1 主题预设：一键切换整套主题（墨绿/纸米/经典蓝/夜间）
  static const List<(String, AppThemeConfig)> presets = [
    ('墨绿', AppThemeConfig(
      primaryColor: '#00696D',
      backgroundColor: '#F4F7F6',
      cornerRadius: 16,
    )),
    ('纸米', AppThemeConfig(
      primaryColor: '#8B6F47',
      backgroundColor: '#F5EFE3',
      cornerRadius: 18,
    )),
    ('经典蓝', AppThemeConfig(
      primaryColor: '#1A56DB',
      backgroundColor: '#F5F7FA',
      cornerRadius: 14,
    )),
    ('夜间', AppThemeConfig(
      primaryColor: '#4DB6AC',
      backgroundColor: '#101418',
      darkMode: true,
      cornerRadius: 16,
    )),
  ];"""

s2 = s2.replace(old_defaults, new_defaults)
open(p2, 'w', encoding='utf-8', newline='').write(s2)
print('P1-1: AppThemeConfig.presets 已添加:', 'static const List<(String, AppThemeConfig)> presets' in s2)
