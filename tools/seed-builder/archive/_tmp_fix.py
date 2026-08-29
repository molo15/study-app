# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
p = r'D:\study_app\app\lib\ui\mock_exam_page.dart'
s = open(p, encoding='utf-8').read()
old = "import 'glass_app_bar.dart';"
new = "import 'app_routes.dart';\nimport 'glass_app_bar.dart';"
assert old in s
s = s.replace(old, new, 1)
open(p, 'w', encoding='utf-8').write(s)
print('app_routes import ok')
