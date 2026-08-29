# -*- coding: utf-8 -*-
"""回退无效的 transitionDuration 参数，统一 MaterialPageRoute -> AppPageRoute"""
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
    # 移除无效参数
    s = s.replace(
        'MaterialPageRoute(transitionDuration: routeDuration, ',
        'AppPageRoute(',
    )
    s = s.replace(
        'MaterialPageRoute(transitionDuration: routeDuration,\n        ',
        'AppPageRoute(\n        ',
    )
    # 兜底：任何残留的 MaterialPageRoute(transitionDuration:
    if 'transitionDuration: routeDuration' in s:
        print(f'  !! {f} 残留 transitionDuration，需人工检查')
    # 兜底：未加参数的 MaterialPageRoute 也统一替换（保持一致性）
    s = s.replace('MaterialPageRoute<bool>(', 'AppPageRoute<bool>(')
    s = s.replace('MaterialPageRoute(', 'AppPageRoute(')
    if s != orig:
        open(f, 'w', encoding='utf-8').write(s)
    n = s.count('AppPageRoute(')
    print(f'{f.split(chr(92))[-1]}: AppPageRoute 共 {n} 处')
