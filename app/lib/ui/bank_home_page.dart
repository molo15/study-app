/// 题库主页（V3 iOS 风格）：综合模拟卷 Banner + 五科列表。
///
/// 入口：底部导航「题库」。点科目进章节树，点模拟卷进模拟卷列表。
/// V3 化：大标题 + IOSCard Banner + IOSListItem 科目列表 + IOSSubjectColors 渐变。
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../data/quiz_repository.dart';
import 'responsive.dart';
import 'theme/ios_tokens.dart';
import 'widgets/ios_button.dart';
import 'widgets/ios_card.dart';
import 'theme/ios_page_route.dart';
import 'pages/v3/bank_manage_v3_page.dart';
import 'widgets/ios_list_group.dart';

class BankHomePage extends ConsumerStatefulWidget {
  const BankHomePage({super.key});

  @override
  ConsumerState<BankHomePage> createState() => BankHomePageState();
}

class BankHomePageState extends ConsumerState<BankHomePage> {
  List<BankInfo> _banks = const [];
  bool _loading = true;
  String? _error;
  int _emptyRetry = 0; // 空库自动重试（等首页内置题库导入完成）

  @override
  void initState() {
    super.initState();
    _load();
  }

  /// 外部刷新（切到题库 Tab 时调用，确保首页自动导入题库后能看到数据）
  Future<void> refresh() => _load();

  Future<void> _load() async {
    try {
      final repo = await ref.read(quizRepositoryProvider);
      var banks = await repo.banks();
      // 空库时自动重试（首页正在异步导入内置题库，最多等 3 轮）
      if (banks.isEmpty && _emptyRetry < 3) {
        _emptyRetry++;
        await Future.delayed(const Duration(milliseconds: 1500));
        if (!mounted) return;
        banks = await repo.banks();
      }
      if (!mounted) return;
      setState(() {
        _banks = banks;
        _loading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final colors = IOSColors.of(context);
    if (_loading) {
      return const Center(child: CircularProgressIndicator(strokeWidth: 2.5));
    }
    if (_error != null) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.cloud_off_outlined, size: 44, color: colors.danger),
            const SizedBox(height: IOSSpacing.s12),
            Text(_error!, style: IOSTypography.callout(color: colors.text2)),
            const SizedBox(height: IOSSpacing.s16),
            IOSButton(label: '重试', onPressed: _load),
          ],
        ),
      );
    }

    return Center(
      child: ConstrainedBox(
        constraints: BoxConstraints(maxWidth: effectiveContentWidth(context)),
        child: ListView(
          padding: const EdgeInsets.fromLTRB(
            IOSSpacing.s16,
            IOSSpacing.s8,
            IOSSpacing.s16,
            IOSFloatingBar.kTContentBottomInset,
          ),
          children: [
            Row(
              children: [
                Text('题库', style: IOSTypography.largeTitle(color: colors.text)),
                const Spacer(),
                IconButton(
                  onPressed: () => Navigator.of(context).push(
                    iosPageRoute<dynamic>((_) => const BankManageV3Page()),
                  ),
                  icon: Icon(Icons.tune_outlined, color: colors.primary, size: 24),
                  tooltip: '题库管理 · 导入',
                ),
              ],
            ),
            const SizedBox(height: IOSSpacing.s8),
            // 综合模拟卷 Banner
            IOSCard(
              padding: const EdgeInsets.all(IOSSpacing.s16),
              onTap: () => context.go('/mock'),
              child: Row(
                children: [
                  Container(
                    width: 44,
                    height: 44,
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(IOSRadius.md),
                      gradient: LinearGradient(
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                        colors: [
                          Color.lerp(colors.primary, Colors.white, 0.25)!,
                          colors.primary,
                        ],
                      ),
                    ),
                    child: const Icon(Icons.assignment_outlined,
                        color: Colors.white, size: 22),
                  ),
                  const SizedBox(width: IOSSpacing.s16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('综合模拟卷',
                            style: IOSTypography.callout(color: colors.text)
                                .copyWith(fontWeight: FontWeight.w700)),
                        const SizedBox(height: IOSSpacing.s4),
                        Text('5 科随机组卷 · 现代汉语 / 古代汉语为主',
                            style: IOSTypography.caption1(
                                color: colors.text2)),
                      ],
                    ),
                  ),
                  Icon(Icons.chevron_right,
                      color: colors.text2.withValues(alpha: 0.6)),
                ],
              ),
            ),
            const SizedBox(height: IOSSpacing.s24),
            // 五科列表
            IOSListGroup(
              title: '五科题库',
              items: [
                for (final b in _banks)
                  IOSListItem(
                    title: b.name,
                    subtitle: '${b.active} 题 · ${b.version}',
                    leading: _subjectAvatar(b),
                    showChevron: true,
                    onTap: () => context.go('/bank/${b.bankId}/chapters'),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _subjectAvatar(BankInfo bank) {
    final (a, b) = _subjectGradient(bank.name);
    final initial = bank.name.isNotEmpty ? bank.name.substring(0, 1) : '?';
    return Container(
      width: 38,
      height: 38,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(IOSRadius.sm),
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [a, b],
        ),
      ),
      alignment: Alignment.center,
      child: Text(
        initial,
        style: const TextStyle(
          color: Colors.white,
          fontSize: 16,
          fontWeight: FontWeight.w800,
        ),
      ),
    );
  }

  (Color, Color) _subjectGradient(String name) => switch (name) {
        '现代汉语' => IOSSubjectColors.modernChineseGrad,
        '古代汉语' => IOSSubjectColors.ancientChineseGrad,
        '现代文学' => IOSSubjectColors.modernLitGrad,
        '当代文学' => IOSSubjectColors.contemporaryLitGrad,
        '古代文学' => IOSSubjectColors.ancientLitGrad,
        _ => IOSSubjectColors.defaultGrad,
      };
}
