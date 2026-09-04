/// UI v2 侧边栏导航（平板 / 桌面形态，对齐原型 .sidebar）
///
/// 三态：
/// - medium（平板 600–1200）：66px 图标栏，可点 ≡ 展开 200px（显示文字 + 脚注）
/// - expanded（桌面 ≥1200）：232px 全宽侧栏，含考试倒计时脚注
///
/// compact（手机）不渲染侧边栏（由 RootPage 决定显示 dock）。
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/quiz_repository.dart';
import '../theme/ios_animations.dart';
import '../theme/ios_tokens.dart';
import '../responsive.dart';

/// 侧边栏导航项（今日 / 题库 / 背题 / 统计 / 我的）
class _SideItem {
  const _SideItem(this.icon, this.label);
  final IconData icon;
  final String label;
}

const _items = [
  _SideItem(Icons.today_outlined, '今日'),
  _SideItem(Icons.folder_outlined, '题库'),
  _SideItem(Icons.auto_awesome, '背题'),
  _SideItem(Icons.insights_outlined, '统计'),
  _SideItem(Icons.person_outline, '我的'),
];

class AppSidebar extends ConsumerStatefulWidget {
  const AppSidebar({super.key, required this.index, required this.onSelect});

  final int index;
  final ValueChanged<int> onSelect;

  @override
  ConsumerState<AppSidebar> createState() => _AppSidebarState();
}

class _AppSidebarState extends ConsumerState<AppSidebar> {
  bool _expanded = false; // 平板展开态（≡）
  int? _days;

  @override
  void initState() {
    super.initState();
    _loadGoal();
  }

  Future<void> _loadGoal() async {
    try {
      final repo = await ref.read(quizRepositoryProvider);
      final goal = await repo.studyGoal();
      if (!mounted) return;
      setState(() => _days = goal?.daysUntilExam(DateTime.now()));
    } catch (_) {
      // 读取失败静默（脚注显示占位）
    }
  }

  @override
  Widget build(BuildContext context) {
    final colors = IOSColors.of(context);
    final anim = IOSAnimations.of(context);
    final accent = colors.primary;
    final ink = colors.text2;
    final ink3 = colors.text3;

    final layout = appLayoutOf(context);
    final isDesktop = layout == AppLayout.expanded;
    final showText = isDesktop || _expanded;
    // 宽度：桌面 232 / 平板 66（展开 200）
    final width = isDesktop
        ? 232.0
        : (_expanded ? 200.0 : 66.0);

    return AnimatedContainer(
      duration: anim.effectiveDuration(IOSDuration.standard),
      curve: anim.effectiveCurve(IOSCurve.standard),
      width: width,
      decoration: BoxDecoration(
        color: colors.card,
        border: Border(
          right: BorderSide(color: colors.separator),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // 平板展开开关（桌面不显示）
          if (!isDesktop)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 8),
              child: Center(
                child: GestureDetector(
                  behavior: HitTestBehavior.opaque,
                  onTap: () => setState(() => _expanded = !_expanded),
                  child: Container(
                    width: 40,
                    height: 40,
                    decoration: BoxDecoration(
                      color: colors.fill,
                      borderRadius: BorderRadius.circular(IOSRadius.sm),
                      border: Border.all(color: colors.cardBorder),
                    ),
                    child: Icon(Icons.menu, size: 18, color: colors.text2),
                  ),
                ),
              ),
            ),
          // Brand：研
          Padding(
            padding: EdgeInsets.only(
              top: 14,
              bottom: 16,
              left: isDesktop ? 14 : 0,
            ),
            child: Center(
              child: Container(
                width: 42,
                height: 42,
                decoration: BoxDecoration(
                  color: colors.primary,
                  borderRadius: BorderRadius.circular(IOSRadius.md),
                  boxShadow: [
                    BoxShadow(
                      color: colors.cardBorder,
                      blurRadius: 20,
                      offset: const Offset(0, 6),
                    ),
                  ],
                ),
                child: const Center(
                  child: Text(
                    '研',
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.w800,
                      fontSize: 17,
                    ),
                  ),
                ),
              ),
            ),
          ),
          // 导航项
          Expanded(
            child: Column(
              children: [
                for (var i = 0; i < _items.length; i++)
                  _buildItem(context, i, _items[i], accent, ink, showText, isDesktop),
              ],
            ),
          ),
          // 脚注：距考试天数（原型 .s-foot）
          if (showText && !isDesktop)
            Padding(
              padding: const EdgeInsets.all(8),
              child: _buildFoot(colors, ink, ink3),
            )
          else if (isDesktop)
            Padding(
              padding: const EdgeInsets.all(14),
              child: _buildFoot(colors, ink, ink3),
            ),
        ],
      ),
    );
  }

  Widget _buildFoot(IOSColorScheme colors, Color ink, Color ink3) {
    final days = _days;
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 10),
      decoration: BoxDecoration(
        color: colors.fill,
        borderRadius: BorderRadius.circular(IOSRadius.md),
        border: Border.all(color: colors.cardBorder),
      ),
      child: Column(
        children: [
          Text(
            days != null ? '距考试' : '未设考试日期',
            style: TextStyle(fontSize: 11, color: ink, height: 1.6),
            textAlign: TextAlign.center,
          ),
          if (days != null)
            Text(
              '$days 天',
              style: TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.w800,
                color: colors.danger,
                height: 1.4,
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildItem(
    BuildContext context,
    int i,
    _SideItem item,
    Color accent,
    Color ink,
    bool showText,
    bool isDesktop,
  ) {
    final on = widget.index == i;
    return Padding(
      padding: EdgeInsets.symmetric(
        horizontal: isDesktop ? 8 : 4,
        vertical: 3,
      ),
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: () => widget.onSelect(i),
        child: Container(
          padding: EdgeInsets.symmetric(
            horizontal: showText ? 12 : 0,
            vertical: 12,
          ),
          alignment: showText ? Alignment.centerLeft : Alignment.center,
          decoration: BoxDecoration(
            color: on ? accent.withValues(alpha: 0.10) : Colors.transparent,
            borderRadius: BorderRadius.circular(IOSRadius.md),
            border: on
                ? Border.all(color: accent.withValues(alpha: 0.30))
                : null,
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            mainAxisAlignment: showText ? MainAxisAlignment.start : MainAxisAlignment.center,
            children: [
              Icon(item.icon, size: 19, color: on ? accent : ink),
              if (showText) ...[
                const SizedBox(width: 12),
                Text(
                  item.label,
                  style: TextStyle(
                    fontSize: 13.5,
                    fontWeight: FontWeight.w700,
                    color: on ? accent : ink,
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
