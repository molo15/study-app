# -*- coding: utf-8 -*-
p1 = r'D:\study_app\app\lib\ui\knowledge_memorize_page.dart'
s = open(p1, encoding='utf-8').read()
if "import 'glass_app_bar.dart';" not in s:
    s = s.replace(
        "import '../models/models.dart';",
        "import '../models/models.dart';\nimport 'glass_app_bar.dart';",
    )
    open(p1, 'w', encoding='utf-8').write(s)
    print('kmp import ok')
else:
    print('kmp already')

p2 = r'D:\study_app\app\lib\ui\memorize_tabs_page.dart'
s = open(p2, encoding='utf-8').read()
if "import '../data/quiz_repository.dart';" not in s:
    s = s.replace(
        "import '../models/models.dart';",
        "import '../data/quiz_repository.dart';\nimport '../models/models.dart';",
    )
    open(p2, 'w', encoding='utf-8').write(s)
    print('mtp import ok')
else:
    print('mtp already')
