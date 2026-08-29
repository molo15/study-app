# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. 修复 practice_question_view.dart 的 AnimatedSwitcher 闭合（多了一层）
p = r'D:\study_app\app\lib\ui\practice_question_view.dart'
s = open(p, encoding='utf-8').read()

old = """      ],
        ),
      ),
    );
  }
}

class _OptionTile"""

new = """      ],
      ),
    );
  }
}

class _OptionTile"""

s = s.replace(old, new)
open(p, 'w', encoding='utf-8', newline='').write(s)
print('practice_question_view 闭合修复:', '        ),\n      ),\n    );' not in s)

# 2. 修复 app_card.dart 的 borderRadius 获取（ShapeBorder 没有 borderRadius）
p2 = r'D:\study_app\app\lib\ui\widgets\app_card.dart'
s2 = open(p2, encoding='utf-8').read()

old2 = """    final radius = theme.cardTheme.shape?.borderRadius
            as BorderRadius? ??
        BorderRadius.circular(16);"""

new2 = """    final shape = theme.cardTheme.shape;
    final radius = shape is RoundedRectangleBorder
        ? shape.borderRadius
        : BorderRadius.circular(16);"""

s2 = s2.replace(old2, new2)
open(p2, 'w', encoding='utf-8', newline='').write(s2)
print('app_card borderRadius 修复:', 'shape is RoundedRectangleBorder' in s2)
