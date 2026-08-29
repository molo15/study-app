# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
p = r'D:\study_app\app\lib\ui\theme_controller.dart'
s = open(p, encoding='utf-8').read()
imp = "import 'package:flutter/cupertino.dart' show CupertinoPageTransitionsBuilder;\n"
s = s.replace(imp, '', 1)
open(p, 'w', encoding='utf-8').write(s)
print('OK removed import; Cupertino 剩余出现:', s.count('Cupertino'))
