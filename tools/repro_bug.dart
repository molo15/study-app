// 复现 App 端：zip 数据 → fromBankJson 解析 → _AnswerCard 匹配，看渲染几行
import 'dart:convert';
import 'dart:io';

Set<String> decodeAnswer(dynamic raw) {
  if (raw == null) return {};
  if (raw is String) return {raw};
  if (raw is List) return raw.cast<String>().toSet();
  throw FormatException('bad answer: $raw');
}

Set<String> mapChoiceAnswer(Set<String> answer, List<Map> options) {
  if (answer.isEmpty || options.isEmpty) return answer;
  final keys = {for (final o in options) o['key'] as String};
  final allKeys = answer.every((a) => a.length == 1 && keys.contains(a));
  if (allKeys) return answer;
  final textToKey = {for (final o in options) o['text'] as String: o['key'] as String};
  return answer.map((a) => textToKey[a] ?? a).toSet();
}

void main() {
  final zips = Directory(r'D:\study_app\app\assets\banks').listSync().whereType<File>().toList();
  for (final z in zips) {
    final bytes = z.readAsBytesSync();
    // 简单 zip 解析：直接读已知文件路径不现实，改用 python 已导出的单题数据跑
    // 这里直接构造：从 zip 中解出 manifest 与 questions
    // 用 archive 不可用（无依赖），改为：仅对已知题做逻辑复现
  }
  // 直接用手动构造的这道题数据复现
  final raw = {
    'id': 'bank-gudai-hanyu:kb_00001',
    'type': 'single_choice',
    'stem': '我国古代第一部修辞专著是（　）',
    'options': [
      {'key': 'A', 'text': '《二十四诗品》'},
      {'key': 'B', 'text': '《文则》'},
      {'key': 'C', 'text': '《修辞格》'},
      {'key': 'D', 'text': '《文心雕龙》'},
    ],
    'answer': '《文则》',
  };
  final options = (raw['options'] as List).cast<Map>().toList();
  final answer = mapChoiceAnswer(decodeAnswer(raw['answer']), options);
  print('decoded answer = $answer');
  // _AnswerCard 匹配
  var rendered = 0;
  for (final o in options) {
    final key = o['key'] as String;
    final text = o['text'] as String;
    if (answer.contains(key) || answer.contains(text)) {
      rendered++;
      print('  渲染: $key. $text');
    }
  }
  print('渲染行数 = $rendered');
}
