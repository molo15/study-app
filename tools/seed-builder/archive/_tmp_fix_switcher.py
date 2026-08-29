# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
p = r'D:\study_app\app\lib\ui\practice_question_view.dart'
s = open(p, encoding='utf-8').read()

old = """    return AnimatedSwitcher(
      duration: reduceMotion ? Duration.zero : AppAnim.grade,
      switchInCurve: AppAnim.standard,
      switchOutCurve: AppAnim.standard,
      transitionBuilder: (child, animation) => FadeTransition("""

new = """    return AnimatedSwitcher(
      duration: reduceMotion ? Duration.zero : AppAnim.grade,
      switchInCurve: AppAnim.standard,
      switchOutCurve: AppAnim.standard,
      // 只显示当前 child：避免新旧 ListView 叠加导致 TextField 串题（测试 P1-5）
      layoutBuilder: (currentChild, previousChildren) => currentChild!,
      transitionBuilder: (child, animation) => FadeTransition("""

s = s.replace(old, new)
open(p, 'w', encoding='utf-8', newline='').write(s)
print('AnimatedSwitcher layoutBuilder 已添加:', 'layoutBuilder:' in s)
