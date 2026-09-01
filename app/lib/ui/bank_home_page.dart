/// 题库主页（UI v2 · 冷磨砂）：搜索框 + 综合模拟卷 Banner + 五科列表。
///
/// 入口：底部导航「题库」。点科目进章节概览，点模拟卷进模拟卷列表。
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/quiz_repository.dart';
import 'app_routes.dart';
import 'chapter_overview_list_page.dart';
import 'glass_app_bar.dart';
import 'mock_exam_list_page.dart';
import 'theme_controller.dart';
import 'responsive.dart';
import 'widgets/glass_card.dart';

class BankHomePage extends ConsumerStatefulWidget {
  const BankHomePage({super.key});

  @override
  ConsumerState<BankHomePage> createState() => _BankHomePageState();
}

class _BankHomePageState extends ConsumerState<BankHomePage> {
  List<BankInfo> _banks = const [];
  bool _loading = true;
  String? _error;

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
    final theme = Theme.of(context);
    final config = ref.watch(themeControllerProvider).asData?.value;
    final accent = config?.accent ?? const Color(0xFF4F7CD4);
    final ink2 = theme.colorScheme.onSurfaceVariant;

    return Scaffold(
      appBar: GlassAppBar(
        title: const Text('题库'),
        centerTitle: true,
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(10),
          child: Container(),
        ),
      ),
      body: _buildBody(theme, accent, ink2),
    );
  }

  Widget _buildBody(ThemeData theme, Color accent, Color ink2) {
    if (_loading) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_error != null) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('加载失败：$_error', style: TextStyle(color: theme.colorScheme.error)),
            const SizedBox(height: 12),
            FilledButton(onPressed: _load, child: const Text('重试')),
          ],
        ),
      );
    }

    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 4, 16, 96),
      children: [
        // 综合模拟卷 Banner
        GlassCard(
          margin: const EdgeInsets.only(bottom: 18),
          onTap: () => pushPage(context, const MockExamListPage()),
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Row(
              children: [
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(16),
                    gradient: LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [Color.lerp(accent, Colors.white, 0.25)!, accent],
                    ),
                  ),
                  child: const Icon(Icons.assignment_outlined, color: Colors.white, size: 24),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('综合模拟卷', style: TextStyle(fontSize: 15.5, fontWeight: FontWeight.w800, color: theme.colorScheme.onSurface)),
                      const SizedBox(height: 3),
                      Text('5 科随机组卷 · 现代汉语 / 古代汉语为主', style: TextStyle(fontSize: 11.5, color: ink2)),
                    ],
                  ),
                ),
                Icon(Icons.chevron_right, color: ink2.withValues(alpha: 0.6)),
              ],
            ),
          ),
        ),

        _sectionTitle('五科题库', accent),
        // 宽屏（平板/桌面）题库两列，手机单列（P2 响应式）
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

  Widget _sectionTitle(String title, Color accent) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(4, 4, 4, 12),
      child: Row(
        children: [
          Text(
            title,
            style: TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w700,
              color: Theme.of(context).colorScheme.onSurfaceVariant,
            ),
          ),
        ],
      ),
    );
  }

  Widget _bankItem(ThemeData theme, Color accent, Color ink2, BankInfo bank) {
    // 科目首字 + 主题色
    final colors = <String, List<Color>>{
      '现代汉语': [const Color(0xFF8FB1F0), const Color(0xFF5B7FD0)],
      '古代汉语': [const Color(0xFF7FC4B2), const Color(0xFF4BA38C)],
      '现代文学': [const Color(0xFFE8B26B), const Color(0xFFD08A3E)],
      '当代文学': [const Color(0xFFB78FE0), const Color(0xFF8A5FC4)],
      '古代文学': [const Color(0xFFE08FB0), const Color(0xFFC45F8A)],
    };
    final cs = colors[bank.name] ?? [accent, accent];
    final initial = bank.name.isNotEmpty ? bank.name.substring(0, 1) : '?';

    return GlassCard(
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
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: cs,
                ),
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
                  Text('${bank.active} 题 · ${bank.version}', style: TextStyle(fontSize: 11, color: ink2)),
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
