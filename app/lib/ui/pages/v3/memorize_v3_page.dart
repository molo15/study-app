/// V3 iOS 风格背题总览：背题模式中枢（中央圆钮入口页）。
///
/// 对齐 `docs/prototype/ui-v3-ios.html` 背题总览：
/// - 顶部大标题（largeTitle 34pt）"背题"
/// - 背题模式说明卡（纯白 IOSCard）
/// - 按科目背诵列表（inset grouped，科目渐变头像）
///
/// 数据层复用现有 QuizRepository.banks()，不新增 SQL、不改 repository。
/// 掌握度环待数据层确认接口后补（阶段3）。
/// 旧 V2 MemorizeHomePage 保留（lib/ui/memorize_home_page.dart）。
library;

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../data/quiz_repository.dart';
import '../../responsive.dart';
import '../../theme/ios_tokens.dart';
import '../../widgets/ios_button.dart';
import '../../widgets/ios_card.dart';
import '../../widgets/ios_list_group.dart';

class MemorizeV3Page extends ConsumerStatefulWidget {
  const MemorizeV3Page({super.key});

  @override
  MemorizeV3PageState createState() => MemorizeV3PageState();
}

class MemorizeV3PageState extends ConsumerState<MemorizeV3Page> {
  List<BankInfo> _banks = const [];
  bool _loading = true;
  bool _error = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  /// B3 审查修复：切 Tab 刷新（root_page GlobalKey 触发，IndexedStack 常驻不重建）
  void refresh() => _load();

  Future<void> _load() async {
    try {
      final repo = await ref.read(quizRepositoryProvider);
      final banks = await repo.banks();
      if (!mounted) return;
      setState(() {
        _banks = banks;
        _loading = false;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error = true;
      });
    }
  }

  void _openBank(BankInfo bank) {
    // R3 修复：原实现 Navigator.push(ChapterOverviewListPage) 与章节页内部
    // context.go('/bank/xx/chapter/xx') 混用，go_router 在栈底重建 BankPage+Chapter 两层，
    // 叠加 push 层形成"看似一层、实际多层"（右滑需多次返回）。
    // 改为统一走 go_router 嵌套路由，栈 = RootPage → BankPage → 章节列表 → 章节概览。
    context.go('/bank/${bank.bankId}/chapters');
  }

  @override
  Widget build(BuildContext context) {
    final colors = IOSColors.of(context);
    if (_loading) {
      return const Center(child: CupertinoActivityIndicator(radius: 14));
    }
    if (_error) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.cloud_off_outlined, size: 48, color: colors.text3),
            const SizedBox(height: IOSSpacing.s12),
            Text('加载失败', style: IOSTypography.body(color: colors.text2)),
            const SizedBox(height: IOSSpacing.s16),
            IOSButton(
              label: '重试',
              onPressed: () {
                setState(() {
                  _error = false;
                  _loading = true;
                });
                _load();
              },
            ),
          ],
        ),
      );
    }
    return Center(
      child: ConstrainedBox(
        constraints: BoxConstraints(maxWidth: effectiveContentWidth(context)),
        child: ListView(
      // 底部留白防悬浮 TabBar 遮挡（V3 §3.3）
      padding: const EdgeInsets.fromLTRB(
        IOSSpacing.s16,
        IOSSpacing.s8,
        IOSSpacing.s16,
        IOSFloatingBar.kTContentBottomInset,
      ),
      children: [
        // 顶部大标题 34pt
        Text('背题', style: IOSTypography.largeTitle(color: colors.text)),
        const SizedBox(height: IOSSpacing.s8),
        // 背题模式说明卡
        IOSCard(
          padding: const EdgeInsets.all(IOSSpacing.s16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(Icons.auto_awesome, color: colors.primary, size: 20),
                  const SizedBox(width: IOSSpacing.s8),
                  Text(
                    '背题模式',
                    style: IOSTypography.title3(color: colors.text),
                  ),
                ],
              ),
              const SizedBox(height: IOSSpacing.s8),
              Text(
                '按知识点推送背诵卡，正面记知识点、背面记要点；\n没记住会反复出现，直到背会为止，不进普通复习队列。',
                style: IOSTypography.footnote(
                  color: colors.text2,
                ).copyWith(height: 1.55),
              ),
            ],
          ),
        ),
        // 按科目背诵
        IOSListGroup(
          animate: true,
          title: '按科目背诵',
          items: [
            for (final bank in _banks)
              IOSListItem(
                title: bank.name,
                subtitle: '${bank.active} 题可背 · ${bank.version}',
                leading: _subjectAvatar(bank),
                showChevron: true,
                onTap: () => _openBank(bank),
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
