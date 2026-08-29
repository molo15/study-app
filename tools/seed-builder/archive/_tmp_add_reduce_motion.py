# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
p = r'D:\study_app\app\lib\ui\theme_controller.dart'
s = open(p, encoding='utf-8').read()

# 1. 构造函数加 reduceMotion
s = s.replace(
    '    this.hideStatusBar = false,\n  });',
    '    this.hideStatusBar = false,\n    this.reduceMotion = false,\n  });'
)
# 2. 字段声明
s = s.replace(
    '  final bool hideStatusBar;',
    '  final bool hideStatusBar;\n\n'
    '  /// 减少动效（P0 手感优化）：开启后非必要动效时长减半或跳过，\n'
    '  /// 仅保留判题颜色反馈，照顾低性能设备与专注用户。默认关。\n'
    '  final bool reduceMotion;'
)
# 3. copyWith 参数
s = s.replace(
    '    bool? hideStatusBar,\n  }) => AppThemeConfig(',
    '    bool? hideStatusBar,\n    bool? reduceMotion,\n  }) => AppThemeConfig('
)
# 4. copyWith 体
s = s.replace(
    '    hideStatusBar: hideStatusBar ?? this.hideStatusBar,\n  );',
    '    hideStatusBar: hideStatusBar ?? this.hideStatusBar,\n'
    '    reduceMotion: reduceMotion ?? this.reduceMotion,\n  );'
)
# 5. toJson
s = s.replace(
    "    'hideStatusBar': hideStatusBar,\n  };",
    "    'hideStatusBar': hideStatusBar,\n    'reduceMotion': reduceMotion,\n  };"
)
# 6. fromJson
s = s.replace(
    "    hideStatusBar: json['hideStatusBar'] as bool? ?? false,\n  );",
    "    hideStatusBar: json['hideStatusBar'] as bool? ?? false,\n"
    "    reduceMotion: json['reduceMotion'] as bool? ?? false,\n  );"
)

open(p, 'w', encoding='utf-8', newline='').write(s)
print('构造函数:', 'this.reduceMotion = false' in s)
print('字段:', 'final bool reduceMotion;' in s)
print('copyWith参数:', 'bool? reduceMotion,' in s)
print('copyWith体:', 'reduceMotion ?? this.reduceMotion' in s)
print('toJson:', "'reduceMotion': reduceMotion" in s)
print('fromJson:', "json['reduceMotion']" in s)
