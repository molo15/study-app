# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
p = r'D:\study_app\app\lib\ui\practice_page.dart'
s = open(p, encoding='utf-8').read()
s = s.replace(
    'ref.watch(themeControllerProvider).valueOrNull?.reduceMotion',
    'ref.watch(themeControllerProvider).value?.reduceMotion'
)
s = s.replace("import 'widgets/pressable_card.dart';\n", '')
open(p, 'w', encoding='utf-8', newline='').write(s)
print('valueOrNull 已修复:', 'valueOrNull' not in s)
print('pressable_card import 已删:', "import 'widgets/pressable_card.dart'" not in s)
