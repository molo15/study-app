# -*- coding: utf-8 -*-
"""P1-4: 切题过渡 — AnimatedSwitcher 包裹题目 ListView"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
p = r'D:\study_app\app\lib\ui\practice_question_view.dart'
s = open(p, encoding='utf-8').read()

# 1. 把 return ListView( 替换为 AnimatedSwitcher 包裹
old_list = "    return ListView(\n      padding: const EdgeInsets.all(16),"
new_list = """    return AnimatedSwitcher(
      duration: reduceMotion ? Duration.zero : AppAnim.grade,
      switchInCurve: AppAnim.standard,
      switchOutCurve: AppAnim.standard,
      transitionBuilder: (child, animation) => FadeTransition(
        opacity: animation,
        child: SlideTransition(
          position: Tween<Offset>(
            begin: const Offset(0.06, 0),
            end: Offset.zero,
          ).animate(animation),
          child: child,
        ),
      ),
      child: ListView(
        key: ValueKey(question.id),
        padding: const EdgeInsets.all(16),"""

s = s.replace(old_list, new_list)

# 2. 找到 _QuestionView build 方法的结尾（ListView 的闭合），加 AnimatedSwitcher 闭合
# _QuestionView 的 build 结尾是：
#       ],
#     );
#   }
# }
# 
# class _OptionTile
old_end = """      ],
    );
  }
}

class _OptionTile"""
new_end = """      ],
        ),
      ),
    );
  }
}

class _OptionTile"""

s = s.replace(old_end, new_end)

open(p, 'w', encoding='utf-8', newline='').write(s)
print('切题过渡已添加')
print('  AnimatedSwitcher:', 'AnimatedSwitcher(' in s)
print('  ValueKey(question.id):', 'ValueKey(question.id)' in s)
