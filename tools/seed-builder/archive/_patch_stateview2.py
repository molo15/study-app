# -*- coding: utf-8 -*-
f = r'D:\study_app\app\lib\ui\widgets\app_state_view.dart'
s = open(f, encoding='utf-8').read()

old = """import 'package:flutter/material.dart';

import '../theme_controller.dart' show AppSpacing;

class AppStateView extends StatelessWidget {"""
new = """import 'package:flutter/material.dart';

import '../theme_controller.dart' show AppSpacing;

// 公开命名参数(message/onRetry/icon/...)→私有字段(_message/_onRetry/...) 的必要映射，
// 无法用 initializing formal 表达，豁免 prefer_initializing_formals 提示。
// ignore_for_file: prefer_initializing_formals

class AppStateView extends StatelessWidget {"""
assert old in s, 'anchor not found'
s = s.replace(old, new)
open(f, 'w', encoding='utf-8').write(s)
print('app_state_view: 已加 ignore_for_file')
