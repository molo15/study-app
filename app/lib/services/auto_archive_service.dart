import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/quiz_repository.dart';
import 'archive_store.dart';

/// 自动存档服务（多端同步方案 §2.2）
///
/// - 定时（默认 30 分钟）自动导出用户状态到本地 `archives/`；
/// - App 生命周期暂停/销毁时触发一次（尽力而为，移动端后台可能被系统杀掉）；
/// - 保留最近 N 份（默认 5），超出删除最旧（覆盖压缩）；
/// - 开关与保留份数读自 settings（`auto_archive_enabled` / `auto_archive_keep`）。
class AutoArchiveService {
  AutoArchiveService({
    this.interval = const Duration(minutes: 30),
  });

  final Duration interval;

  Timer? _timer;
  AppLifecycleListener? _lifecycle;
  bool _started = false;
  bool _enabled = false;
  bool _triggering = false;

  QuizRepository? _repo;
  ArchiveStore? _store;

  /// 是否已启动
  bool get isStarted => _started;

  /// 自动存档开关当前状态
  bool get autoArchiveEnabled => _enabled;

  /// 启动：读开关 → 定时器 + 生命周期监听
  Future<void> start(QuizRepository repo, ArchiveStore store) async {
    _repo = repo;
    _store = store;
    _enabled = await _isEnabled();
    _started = true;
    _sync();
  }

  /// 停止全部监听（开关关闭时调用）
  void stop() {
    _started = false;
    _enabled = false;
    _timer?.cancel();
    _timer = null;
    _lifecycle?.dispose();
    _lifecycle = null;
  }

  void _sync() {
    if (!_started) return;
    _timer?.cancel();
    _timer = null;
    _lifecycle?.dispose();
    _lifecycle = null;
    if (!_enabled) return;
    _timer = Timer.periodic(interval, (_) => _autoTrigger());
    _lifecycle = AppLifecycleListener(
      onStateChange: (state) {
        if (state == AppLifecycleState.paused ||
            state == AppLifecycleState.detached) {
          _autoTrigger();
        }
      },
    );
  }

  /// 定时/生命周期自动触发（受开关控制）
  Future<void> _autoTrigger() async {
    if (!_enabled) return;
    await trigger();
  }

  Future<bool> _isEnabled() async {
    final v = await _repo?.setting('auto_archive_enabled');
    return v != 'false'; // 默认开
  }

  /// 开关设置变更后调用（保持 _enabled 与设置一致）
  Future<void> setEnabled(bool enabled) async {
    await _repo?.setSetting('auto_archive_enabled', '$enabled');
    _enabled = enabled;
    _sync();
  }

  /// 保留份数设置变更（立即执行一次清理）
  Future<void> setKeepCount(int count) async {
    await _repo?.setSetting('auto_archive_keep', '$count');
    await _prune();
  }

  /// 立即触发一次自动存档（保留策略后清理）
  Future<String?> trigger() async {
    if (_triggering) return null;
    _triggering = true;
    try {
      final repo = _repo;
      final store = _store;
      if (repo == null || store == null) return null;
      final bytes = await repo.exportArchive(kind: ArchiveKind.auto);
      final fileName = 'auto_${_stamp()}.zip';
      final path = await store.saveAutoArchive(fileName, bytes);
      await _prune();
      return path;
    } catch (e) {
      debugPrint('自动存档失败: $e');
      return null;
    } finally {
      _triggering = false;
    }
  }

  Future<void> _prune() async {
    final store = _store;
    if (store == null) return;
    final keepRaw = await _repo?.setting('auto_archive_keep');
    final keep = int.tryParse(keepRaw ?? '') ?? 5;
    final list = await store.listAutoArchives();
    if (list.length <= keep) return;
    for (final f in list.skip(keep)) {
      await store.deleteAutoArchive(f.fileName);
    }
  }

  static String _stamp() {
    final n = DateTime.now();
    String two(int v) => v.toString().padLeft(2, '0');
    return '${n.year}${two(n.month)}${two(n.day)}_'
        '${two(n.hour)}${two(n.minute)}${two(n.second)}';
  }

  void dispose() {
    _timer?.cancel();
    _timer = null;
    _lifecycle?.dispose();
    _lifecycle = null;
    _started = false;
  }
}

/// 全局自动存档服务 provider（在 RootPage 挂载时 start）
final autoArchiveServiceProvider = Provider<AutoArchiveService>(
  (ref) {
    final service = AutoArchiveService();
    ref.onDispose(service.dispose);
    return service;
  },
);
