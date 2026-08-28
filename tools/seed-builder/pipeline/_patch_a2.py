# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ---------- 1) theme_controller.dart：清理不再使用的 cupertino import ----------
p1 = r'D:\study_app\app\lib\ui\theme_controller.dart'
s1 = open(p1, encoding='utf-8').read()
imp = "import 'package:flutter/cupertino.dart' show CupertinoPageTransitionsBuilder;\n"
if 'CupertinoPageTransitionsBuilder' not in s1 and imp in s1:
    s1 = s1.replace(imp, '', 1)
    open(p1, 'w', encoding='utf-8').write(s1)
    print('OK: removed unused cupertino import')
else:
    print('SKIP: import cleanup (checked)')

# ---------- 2) root_page.dart：Tab 切换去透底（去掉 FadeTransition 0.3 淡入） ----------
p2 = r'D:\study_app\app\lib\ui\root_page.dart'
s2 = open(p2, encoding='utf-8').read()

old_block = """    return FadeTransition(
      opacity: Tween<double>(begin: 0.3, end: 1).animate(curved),
      child: SlideTransition(
        position: Tween<Offset>(
          begin: const Offset(0, 0.012),
          end: Offset.zero,
        ).animate(curved),
        child: IndexedStack(index: widget.index, children: widget.children),
      ),
    );"""

new_block = """    // 仅轻微上滑过渡（v1.1.3：去掉透明度淡入，避免切换瞬间背景透出，显得卡顿）
    return SlideTransition(
      position: Tween<Offset>(
        begin: const Offset(0, 0.012),
        end: Offset.zero,
      ).animate(curved),
      child: IndexedStack(index: widget.index, children: widget.children),
    );"""

if old_block not in s2:
    print('ERROR: root_page fade block not found')
    sys.exit(1)
s2 = s2.replace(old_block, new_block, 1)

# 更新相关注释
s2 = s2.replace(
    '// IndexedStack 常驻三页（状态保留、切换零重建）+ 慢速淡入上滑过渡',
    '// IndexedStack 常驻三页（状态保留、切换零重建）+ 慢速轻微上滑过渡（v1.1.3）')
s2 = s2.replace(
    '/// 相比 AnimatedSwitcher + ValueKey 重建整页，IndexedStack 避免切 Tab 时\n'
    '/// 重复读库/重建，动画期间无卡顿；切换时新页淡入并轻微上滑（300ms 慢速档）。',
    '/// 相比 AnimatedSwitcher + ValueKey 重建整页，IndexedStack 避免切 Tab 时\n'
    '/// 重复读库/重建，动画期间无卡顿；切换时新页轻微上滑（300ms 慢速档，\n'
    '/// 无透明度变化，切换不露背景）。')

open(p2, 'w', encoding='utf-8').write(s2)
print('OK: root_page.dart updated (tab transition cleaned)')
