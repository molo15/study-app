# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

p = r'D:\study_app\app\lib\ui\home_page.dart'
s = open(p, encoding='utf-8').read()

# ---------- 1) 替换硬编码常量 → 自动发现方法 ----------
old_const = """  /// 内置 T1 题库包（5 个 zip，formatVersion=4，v0.11.0：知识点树+章节概览+背题+学习目标）
  static const _bundledBanks = <String, String>{
    'bank-gudai-hanyu': 'assets/banks/bank-gudai-hanyu-v0.11.0.zip',
    'bank-xiandai-hanyu': 'assets/banks/bank-xiandai-hanyu-v0.11.0.zip',
    'bank-zhongguo-gudai-wenxue':
        'assets/banks/bank-zhongguo-gudai-wenxue-v0.11.0.zip',
    'bank-zhongguo-xiandai-wenxue':
        'assets/banks/bank-zhongguo-xiandai-wenxue-v0.11.0.zip',
    'bank-zhongguo-dangdai-wenxue':
        'assets/banks/bank-zhongguo-dangdai-wenxue-v0.11.0.zip',
  };"""

new_const = """  /// 内置题库自动发现（v1.1.3）：枚举 assets/banks/*.zip，每科取版本号最高的包。
  ///
  /// 替代硬编码版本路径——此前 v0.12 已打包但 home_page 仍引用 v0.11，导致
  /// "新题库未附带"事故；自动扫描后未来题库升级（v0.13+）只需替换 zip，无需改代码。
  static Future<Map<String, String>> _discoverBundledBanks() async {
    final manifest = await AssetManifest.loadFromAssetBundle(rootBundle);
    final best = <String, MapEntry<int, String>>{};
    final pattern = RegExp(
      r'^assets/banks/(bank-[a-z0-9-]+)-v(\\d+)\\.(\\d+)\\.(\\d+)\\.zip$',
    );
    for (final asset in manifest.listAssets()) {
      final m = pattern.firstMatch(asset);
      if (m == null) continue;
      final bank = m.group(1)!;
      final ver = int.parse(m.group(2)!) * 1000000 +
          int.parse(m.group(3)!) * 1000 +
          int.parse(m.group(4)!);
      final cur = best[bank];
      if (cur == null || ver > cur.key) {
        best[bank] = MapEntry(ver, asset);
      }
    }
    return best.map((k, v) => MapEntry(k, v.value));
  }"""

if old_const not in s:
    print('ERROR: _bundledBanks const block not found')
    sys.exit(1)
s = s.replace(old_const, new_const, 1)

# ---------- 2) _init 改用扫描结果 ----------
old_init = """      final repo = await ref.read(quizRepositoryProvider);
      // 内置题库同步（幂等）：用户卸载/隐藏的库跳过；
      // 内置包 version 与已导入版本不一致时自动重导（覆盖旧内容、保留用户本地修改）。
      // 先轻量读 manifest 版本比对，不一致才全量解析导入（性能优化：避免每次启动解析全部题目）。
      for (final entry in _bundledBanks.entries) {"""

new_init = """      final repo = await ref.read(quizRepositoryProvider);
      // 内置题库同步（幂等）：自动扫描 assets 最新版本（v1.1.3）；
      // 用户卸载/隐藏的库跳过；版本不一致时自动重导（覆盖旧内容、保留用户本地修改）。
      // 先轻量读 manifest 版本比对，不一致才全量解析导入（性能优化：避免每次启动解析全部题目）。
      final bundledBanks = await _discoverBundledBanks();
      for (final entry in bundledBanks.entries) {"""

if old_init not in s:
    print('ERROR: _init loop block not found')
    sys.exit(1)
s = s.replace(old_init, new_init, 1)

open(p, 'w', encoding='utf-8').write(s)
print('OK: home_page.dart updated (B1+B2)')
