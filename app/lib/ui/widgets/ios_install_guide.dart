import 'package:flutter/foundation.dart'
    show kIsWeb, defaultTargetPlatform, TargetPlatform;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/quiz_repository.dart';
import 'app_card.dart';

/// 是否 iOS Web（Safari）。
///
/// 背景：sqlite3.wasm 将题库/进度/错题存入 IndexedDB；iOS WebKit 对未添加到
/// 主屏幕的网页内容，连续 7 天不访问会清除网站数据（含 IndexedDB）。
/// 添加到主屏幕（standalone）后不清理，并享受全屏无地址栏体验。
bool get isIosWeb =>
    kIsWeb && defaultTargetPlatform == TargetPlatform.iOS;

const _kSeenKey = 'ios_a2hs_seen';

/// iOS Web 首次启动「添加到主屏幕」引导（仅一次）。
///
/// 「已看过」标记写入设置表（与 DB 同存储，跨会话持久）；DB 未就绪等
/// 失败场景静默跳过，下次启动再提示。
Future<void> maybeShowIosInstallGuide(
    WidgetRef ref, BuildContext context) async {
  if (!isIosWeb) return;
  try {
    final repo = await ref.read(quizRepositoryProvider);
    final seen = await repo.setting(_kSeenKey);
    if (seen == '1') return;
    await repo.setSetting(_kSeenKey, '1');
    if (!context.mounted) return;
    await showDialog<void>(
      context: context,
      barrierDismissible: true,
      barrierColor: Colors.black38,
      builder: (_) => const IosInstallGuideDialog(),
    );
  } catch (_) {
    // DB 未就绪 / 读取失败：静默跳过，下次启动再提示
  }
}

/// 设置页 iOS 专属提示条（仅 iOS Web 返回非空）。
Widget? iosInstallGuideBanner() {
  if (!isIosWeb) return null;
  return Padding(
    padding: const EdgeInsets.only(bottom: 12),
    child: AppCard(
      padding: const EdgeInsets.all(14),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.smartphone_outlined,
              size: 20, color: Color(0xFF4F7CD4)),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'iOS 数据保护：请添加到主屏幕',
                  style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13.5),
                ),
                const SizedBox(height: 4),
                Text(
                  'Safari 会清理长期未访问的网页数据（含刷题进度）。'
                  '点底部「分享」→「添加到主屏幕」后数据不再被清理，且全屏无地址栏。',
                  style: const TextStyle(
                      fontSize: 12.5, color: Color(0xFF56647C), height: 1.5),
                ),
              ],
            ),
          ),
        ],
      ),
    ),
  );
}

/// 首次启动引导对话框（玻璃化，与 AppCard 一致）。
class IosInstallGuideDialog extends StatelessWidget {
  const IosInstallGuideDialog({super.key});

  @override
  Widget build(BuildContext context) {
    return Dialog(
      backgroundColor: Colors.transparent,
      insetPadding:
          const EdgeInsets.symmetric(horizontal: 28, vertical: 24),
      child: AppCard(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: const Color(0xFF4F7CD4).withValues(alpha: .12),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(Icons.install_mobile,
                      color: Color(0xFF4F7CD4), size: 22),
                ),
                const SizedBox(width: 10),
                const Expanded(
                  child: Text(
                    '添加到主屏幕，数据更安全',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 14),
            const Text(
              'iOS 的 Safari 会清理长时间未访问的网页数据，包括你的刷题进度、错题与存档。'
              '添加到主屏幕后，数据将不再被清理，并享受全屏无地址栏的原生体验。',
              style:
                  TextStyle(fontSize: 13, height: 1.6, color: Color(0xFF56647C)),
            ),
            const SizedBox(height: 14),
            const _StepLine(n: '1', text: '点 Safari 底部「分享」按钮'),
            const SizedBox(height: 8),
            const _StepLine(n: '2', text: '选择「添加到主屏幕」'),
            const SizedBox(height: 8),
            const _StepLine(n: '3', text: '从桌面图标打开本应用'),
            const SizedBox(height: 18),
            SizedBox(
              width: double.infinity,
              child: FilledButton(
                style: FilledButton.styleFrom(
                  backgroundColor: const Color(0xFF4F7CD4),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 12),
                ),
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('知道了', style: TextStyle(fontSize: 14.5)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _StepLine extends StatelessWidget {
  const _StepLine({required this.n, required this.text});

  final String n;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          width: 18,
          height: 18,
          alignment: Alignment.center,
          decoration: const BoxDecoration(
              color: Color(0xFF4F7CD4), shape: BoxShape.circle),
          child: Text(
            n,
            style: const TextStyle(
                color: Colors.white, fontSize: 11, fontWeight: FontWeight.w700),
          ),
        ),
        const SizedBox(width: 8),
        Expanded(child: Text(text, style: const TextStyle(fontSize: 13.5))),
      ],
    );
  }
}
