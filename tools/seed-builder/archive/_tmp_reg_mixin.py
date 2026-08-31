# -*- coding: utf-8 -*-
"""背题存档：quiz_repository.dart 注册 _MemorizeMixin"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
p = r'D:\study_app\app\lib\data\quiz_repository.dart'
s = open(p, encoding='utf-8').read()

old = """part 'quiz_repository_settings.dart';
part 'quiz_repository_questions.dart';
part 'quiz_repository_knowledge.dart';
part 'quiz_repository_srs.dart';
part 'quiz_repository_mock.dart';
part 'quiz_repository_export.dart';"""
new = """part 'quiz_repository_settings.dart';
part 'quiz_repository_questions.dart';
part 'quiz_repository_knowledge.dart';
part 'quiz_repository_memorize.dart';
part 'quiz_repository_srs.dart';
part 'quiz_repository_mock.dart';
part 'quiz_repository_export.dart';"""
assert old in s, 'part anchor missing'
s = s.replace(old, new)

old2 = """    _SettingsMixin,
    _QuestionsMixin,
    _KnowledgeMixin,
    _SrsMixin,"""
new2 = """    _SettingsMixin,
    _QuestionsMixin,
    _KnowledgeMixin,
    _MemorizeMixin,
    _SrsMixin,"""
assert old2 in s, 'mixin anchor missing'
s = s.replace(old2, new2)

open(p, 'w', encoding='utf-8', newline='').write(s)
print('quiz_repository 注册 _MemorizeMixin 完成')
print('  part:', "quiz_repository_memorize.dart" in s)
print('  mixin:', '_MemorizeMixin,' in s)
