/// 背题总览（UI v2 · 冷磨砂）：不背单词式背题模式的中枢。
///
/// 顶部说明卡介绍背题模式（按知识点推送、直到背会），下方各科知识点入口，
/// 点科目进章节概览 → 选章节 → 背题卡。
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/quiz_repository.dart';
import 'app_routes.dart';
import 'chapter_overview_list_page.dart';
import 'glass_app_bar.dart';
import 'theme_controller.dart';
import 'responsive.dart';
import 'widgets/app_card.dart';

class MemorizeHomePage extends ConsumerStatefulWidget {
  const MemorizeHomePage({super.key});

  @override
  ConsumerState<MemorizeHomePage> createState() => _MemorizeHomePageState();
}

class _MemorizeHomePageState extends ConsumerState<MemorizeHomePage> {
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

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final config = ref.watch(themeControllerProvider).asData?.value;
    final accent = config?.accent ?? const Color(0xFF4F7CD4);

    return Scaffold(
      appBar: GlassAppBar(
        title: const Text('背题'),
        centerTitle: true,
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(10),
          child: Container(),
        ),
      ),
      body: _buildBody(theme, accent),
    );
  }

  Widget _buildBody(ThemeData theme, Color accent) {
    if (_loading) {
      return const Center(child: CircularProgressIndicator());
    }

    final ink2 = theme.colorScheme.onSurfaceVariant;

    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 4, 16, 96),
      children: [
        // 背题模式说明卡
        AppCard(
          depth: 1,
          padding: EdgeInsets.zero,
          margin: const EdgeInsets.only(bottom: 18),
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(Icons.auto_awesome, color: accent, size: 22),
                    const SizedBox(width: 8),
                    const Text('背题模式', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800)),
                  ],
                ),
                const SizedBox(height: 10),
                Text(
                  '按知识点推送背诵卡，正面记知识点、背面记要点；\n没记住会反复出现，直到背会为止，不进普通复习队列。',
                  style: TextStyle(fontSize: 12.5, height: 1.55, color: theme.colorScheme.onSurfaceVariant),
                ),
              ],
            ),
          ),
        ),

        Padding(
          padding: const EdgeInsets.fromLTRB(4, 4, 4, 12),
          child: Text('按科目背诵', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: theme.colorScheme.onSurfaceVariant)),
        ),
        // 宽屏（平板/桌面）科目两列，手机单列（P3 对齐原型 memlist）
        if (isWideScreen(context))
          Wrap(
            spacing: 12,
            runSpacing: 12,
            children: [
              for (final b in _banks)
                SizedBox(
                  width: (effectiveContentWidth(context) - 32 - 12) / 2,
                  child: _bankItem(theme, accent, ink2, b),
                ),
            ],
          )
        else
          ..._banks.map((b) => _bankItem(theme, accent, ink2, b)),
      ],
    );
  }

  Widget _bankItem(ThemeData theme, Color accent, Color ink2, BankInfo bank) {
    final colors = <String, List<Color>>{
      '现代汉语': [const Color(0xFF8FB1F0), const Color(0xFF5B7FD0)],
      '古代汉语': [const Color(0xFF7FC4B2), const Color(0xFF4BA38C)],
      '现代文学': [const Color(0xFFE8B26B), const Color(0xFFD08A3E)],
      '当代文学': [const Color(0xFFB78FE0), const Color(0xFF8A5FC4)],
      '古代文学': [const Color(0xFFE08FB0), const Color(0xFFC45F8A)],
    };
    final cs = colors[bank.name] ?? [accent, accent];
    final initial = bank.name.isNotEmpty ? bank.name.substring(0, 1) : '?';

    return AppCard(
      padding: EdgeInsets.zero,
      margin: const EdgeInsets.only(bottom: 12),
      onTap: () => pushPage(
        context,
        ChapterOverviewListPage(bankId: bank.bankId, bankName: bank.name),
      ),
      child: Padding(
        padding: const EdgeInsets.all(15),
        child: Row(
          children: [
            Container(
              width: 46,
              height: 46,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(15),
                gradient: LinearGradient(begin: Alignment.topLeft, end: Alignment.bottomRight, colors: cs),
              ),
              alignment: Alignment.center,
              child: Text(initial, style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.w800)),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(bank.name, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w800)),
                  const SizedBox(height: 4),
                  Text('${bank.active} 题可背 · ${bank.version}', style: TextStyle(fontSize: 11, color: ink2)),
                ],
              ),
            ),
            Icon(Icons.chevron_right, color: ink2.withValues(alpha: 0.6)),
          ],
        ),
      ),
    );
  }
}
