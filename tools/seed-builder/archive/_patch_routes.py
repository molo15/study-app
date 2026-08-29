# -*- coding: utf-8 -*-
"""给所有 MaterialPageRoute 加 transitionDuration，并 import app_routes.dart"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

files = [
    r'D:\study_app\app\lib\ui\bank_page.dart',
    r'D:\study_app\app\lib\ui\chapter_overview_list_page.dart',
    r'D:\study_app\app\lib\ui\chapter_overview_page.dart',
    r'D:\study_app\app\lib\ui\home_page.dart',
    r'D:\study_app\app\lib\ui\mock_exam_list_page.dart',
    r'D:\study_app\app\lib\ui\question_manage_page.dart',
    r'D:\study_app\app\lib\ui\settings_page.dart',
    r'D:\study_app\app\lib\ui\wrong_book_page.dart',
]

for f in files:
    s = open(f, encoding='utf-8').read()
    orig = s

    # 1) import app_routes（在最后一个 import 后插入）
    if "import 'app_routes.dart';" not in s:
        lines = s.split('\n')
        last_import = -1
        for i, l in enumerate(lines):
            if l.startswith('import '):
                last_import = i
        assert last_import != -1, f'no import in {f}'
        lines.insert(last_import + 1, "import 'app_routes.dart';")
        s = '\n'.join(lines)

    # 2) MaterialPageRoute<bool>( 先于 MaterialPageRoute(
    n_generic = s.count('MaterialPageRoute<bool>(')
    s = s.replace(
        'MaterialPageRoute<bool>(',
        'MaterialPageRoute<bool>(transitionDuration: routeDuration, ',
    )
    # 3) 普通 MaterialPageRoute(
    n_plain = s.count('MaterialPageRoute(')
    s = s.replace(
        'MaterialPageRoute(',
        'MaterialPageRoute(transitionDuration: routeDuration, ',
    )

    if s != orig:
        open(f, 'w', encoding='utf-8').write(s)
    print(f'{f.split(chr(92))[-1]}: 泛型{n_generic} + 普通{n_plain} 处已加 duration, import已加')
