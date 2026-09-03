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

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../data/quiz_repository.dart';
import '../../theme/ios_page_route.dart';
import '../../theme/ios_tokens.dart';
import '../../widgets/ios_card.dart';
import '../../widgets/ios_list_group.dart';
import '../../chapter_overview_list_page.dart';

class MemorizeV3Page extends ConsumerStatefulWidget {
  const MemorizeV3Page({super.key});

  @override
  ConsumerState<MemorizeV3Page> createState() => _MemorizeV3PageState();
}

class _MemorizeV3PageState extends ConsumerState<MemorizeV3Page> {
  List<BankInfo> _banks = const [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

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
      setState(() => _loading = false);
    }
  }

  void _openBank(BankInfo bank) {
    Navigator.of(context).push(
      iosPageRoute<dynamic>(
        (_) => ChapterOverviewListPage(bankId: bank.bankId, bankName: bank.name),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final colors = IOSColors.of(context);
    if (_loading) {
      return const Center(child: CircularProgressIndicator(strokeWidth: 2.5));
    }
    return ListView(
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
        '现代汉语' => (const Color(0xFF8FB1F0), const Color(0xFF5B7FD0)),
        '古代汉语' => (IOSSubjectColors.ancientChinese,
            const Color(0xFF4BA38C)),
        '现代文学' => (const Color(0xFFE8B26B), const Color(0xFFD08A3E)),
        '当代文学' => (IOSSubjectColors.literaryTheory,
            const Color(0xFF8A5FC4)),
        '古代文学' => (const Color(0xFFE08FB0), const Color(0xFFC45F8A)),
        _ => (IOSColors.light.primary, const Color(0xFF4F7CD4)),
      };
}
