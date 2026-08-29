# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

s = open(r'D:\study_app\app\lib\ui\chapter_overview_page.dart', encoding='utf-8').read()
checks = {
    'overview import section': "import 'widgets/app_section_header.dart';\nimport 'widgets/app_state_view.dart';" in s,
    'overview _kpName': 'String _kpName(String? id)' in s,
    'overview AppSectionHeader': s.count('AppSectionHeader(') == 1,
    'overview AppStateView.error': s.count('AppStateView.error(') == 1,
    'overview tertiary': 'color: theme.colorScheme.tertiary' in s,
    'overview 无deepOrange': 'Colors.deepOrange' not in s,
    'overview 无_SectionTitle': '_SectionTitle' not in s,
    'overview 无_ErrorView': '_ErrorView' not in s,
}
print('=== chapter_overview_page ===')
for k, v in checks.items():
    print(('OK  ' if v else 'FAIL'), k)

s = open(r'D:\study_app\app\lib\ui\settings_page.dart', encoding='utf-8').read()
checks2 = {
    'settings import toast': "import 'app_toast.dart';" in s,
    'settings import section/state': "import 'widgets/app_section_header.dart';" in s and "import 'widgets/app_state_view.dart';" in s,
    'settings AppSectionHeader x5': s.count('AppSectionHeader(') == 5,
    'settings AppStateView.error x1': s.count('AppStateView.error(') == 1,
    'settings showAppToast': s.count('showAppToast') == 1,
    'settings 无_SectionHeader/_ErrorRetry': '_SectionHeader' not in s and '_ErrorRetry' not in s,
}
print('=== settings_page ===')
for k, v in checks2.items():
    print(('OK  ' if v else 'FAIL'), k)
