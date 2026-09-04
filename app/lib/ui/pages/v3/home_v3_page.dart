/// V3 iOS 风格首页：今日任务优先 + 快捷入口 + 题库列表。
///
/// 对齐 `docs/prototype/ui-v3-ios.html` 首页设计稿：
/// - 顶部大标题（largeTitle 34pt）"今日"
/// - 今日学习卡（环形正确率 + 待复习/新题/错题 + 到期复习/可新学队列）
/// - 学习目标卡（考试倒计时，P2）
/// - 快捷入口（iOS inset grouped 列表：模拟考 / 背题 / 错题本）
/// - 题库列表（科目卡：名称 + 题量 + 进度条）
///
/// 数据层复用现有 QuizRepository，不新增 SQL、不改 repository。
/// 旧 V2 HomePage 保留（lib/ui/home_page.dart），本页为 V3 替代实现。
library;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../data/quiz_repository.dart';
import '../../../data/seed_loader.dart';
import '../../../models/models.dart';
import '../../responsive.dart';
import '../../theme/ios_animations.dart';
import '../../theme/ios_page_route.dart';
import '../../theme/ios_tokens.dart';
import '../../widgets/circular_ring.dart';
import '../../widgets/ios_button.dart';
import '../../widgets/ios_card.dart';
import '../../widgets/ios_list_group.dart';
import '../../practice_page.dart';

class HomeV3Page extends ConsumerStatefulWidget {
  const HomeV3Page({super.key});

  @override
  ConsumerState<HomeV3Page> createState() => HomeV3PageState();
}

class HomeV3PageState extends ConsumerState<HomeV3Page> {
  /// 内置题库自动发现（与 home_page 同逻辑）：枚举 assets/banks/*.zip 取最高版本。
  static Future<Map<String, String>> _discoverBundledBanks() async {
    final manifest = await AssetManifest.loadFromAssetBundle(rootBundle);
    final best = <String, MapEntry<int, String>>{};
    final pattern = RegExp(
      r'^assets/banks/(bank-[a-z0-9-]+)-v(\d+)\.(\d+)\.(\d+)\.zip$',
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
  }

  bool _loading = true;
  String? _error;
  int _totalCount = 0;
  int _dueCount = 0;
  int _newCount = 0;
  int _wrongCount = 0;
  List<BankInfo> _banks = const [];
  String? _currentBankId;
  Map<String, int> _answeredByBank = const {};
  List<MockPaper> _mockPapers = const [];
  int _todayAnswered = 0;
  double _todayAccuracy = 0;
  int _streak = 0;
  StudyGoal? _studyGoal;

  @override
  void initState() {
    super.initState();
    _init();
  }

  Future<void> _init() async {
    try {
      final repo = await ref.read(quizRepositoryProvider);
      // 内置题库同步（幂等）：自动扫描 assets 最新版本，版本不一致时自动重导
      final bundledBanks = await _discoverBundledBanks();
      for (final entry in bundledBanks.entries) {
        final hidden =
            await repo.setting('bank_${entry.key}_hidden') == 'true';
        if (hidden) continue;
        final bytes = (await rootBundle
            .load(entry.value)).buffer.asUint8List();
        final installed = await repo.importedVersion(entry.key);
        if (SeedLoader.manifestVersionFromZipBytes(bytes) != installed) {
          final zipPack = SeedLoader.parseZipBytes(bytes);
          await repo.importBank(zipPack);
        }
      }
      await _refresh(repo);
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error = '加载失败：$e';
      });
    }
  }

  /// 刷新全部概览数据（首载与从子页返回/切换题库时）
  Future<void> _refresh(QuizRepository repo) async {
    final banks = await repo.banks();
    if (banks.isEmpty) {
      if (mounted) {
        setState(() {
          _loading = false;
          _error = '未导入题库包';
        });
      }
      return;
    }
    var current = await repo.currentBankId();
    if (banks.length == 1) {
      current = banks.first.bankId;
      await repo.setCurrentBankId(current);
    } else if (current != null && !banks.any((b) => b.bankId == current)) {
      current = null;
    }
    final isAll = current == null;
    final bankId = isAll ? null : current;
    final dueCount = await repo.dueCount(bankId: bankId);
    final newCount = await repo.newCount(bankId: bankId);
    final wrongCount = await repo.wrongBookCount(bankId: bankId);
    final mockPapers = await repo.mockPapers(bankId: bankId);
    final overview = await repo.todayOverview();
    final answeredByBank = await repo.answeredCountByBank();
    final studyGoal = await repo.studyGoal();
    final totalAll = banks.fold(0, (sum, b) => sum + b.active);
    if (!mounted) return;
    setState(() {
      _loading = false;
      _banks = banks;
      _currentBankId = current;
      _totalCount = totalAll;
      _dueCount = dueCount;
      _newCount = newCount;
      _wrongCount = wrongCount;
      _mockPapers = mockPapers;
      _answeredByBank = answeredByBank;
      _todayAnswered = overview.todayAnswered;
      _todayAccuracy = overview.todayAccuracy;
      _streak = overview.streak;
      _studyGoal = studyGoal;
    });
  }

  /// 供 root_page tab 切换时调用（IndexedStack 常驻页面不重建，需手动刷新）
  Future<void> refresh() async {
    final repo = await ref.read(quizRepositoryProvider);
    await _refresh(repo);
  }

  Future<void> _push(Widget page) async {
    await Navigator.of(context).push(
      iosPageRoute<dynamic>((_) => page),
    );
    if (!mounted) return;
    final repo = await ref.read(quizRepositoryProvider);
    await _refresh(repo);
  }

  @override
  Widget build(BuildContext context) {
    final colors = IOSColors.of(context);
    if (_loading) {
      return const Center(
        child: CircularProgressIndicator(strokeWidth: 2.5),
      );
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
            IOSButton(
              label: '重试',
              onPressed: () {
                setState(() {
                  _loading = true;
                  _error = null;
                });
                _init();
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
      // 底部留白防悬浮 TabBar 遮挡（V3 §3.3 kTContentBottomInset）
      padding: const EdgeInsets.fromLTRB(
        IOSSpacing.s16,
        IOSSpacing.s8,
        IOSSpacing.s16,
        IOSFloatingBar.kTContentBottomInset,
      ),
      children: [
        // 顶部大标题 34pt
        Text('今日', style: IOSTypography.largeTitle(color: colors.text)),
        const SizedBox(height: IOSSpacing.s8),
        // 今日学习卡
        _buildTodayCard(colors),
        const SizedBox(height: IOSSpacing.s12),
        // 到期复习 / 可新学 队列
        Row(
          children: [
            Expanded(
              child: _buildQueueCard(
                colors: colors,
                title: '到期复习',
                count: _dueCount,
                icon: Icons.autorenew,
                color: colors.primary,
                done: _dueCount == 0,
                onTap: _dueCount == 0
                    ? null
                    : () => _push(PracticePage(
                          mode: PracticeMode.review,
                          bankId: _currentBankId,
                        )),
              ),
            ),
            const SizedBox(width: IOSSpacing.s12),
            Expanded(
              child: _buildQueueCard(
                colors: colors,
                title: '可新学',
                count: _newCount,
                icon: Icons.bolt_outlined,
                color: IOSSystemColors.purple,
                done: _newCount == 0,
                onTap: () async {
                  final repo = await ref.read(quizRepositoryProvider);
                  final questions = await repo.newQuestions(
                    bankId: _currentBankId,
                    limit: _newCount,
                  );
                  if (!mounted || questions.isEmpty) return;
                  _push(PracticePage(
                    mode: PracticeMode.learn,
                    bankId: _currentBankId,
                    progressKey: 'home-new:${_currentBankId ?? 'all'}',
                    questions: questions,
                  ));
                },
              ),
            ),
          ],
        ),
        // 学习目标卡（考试倒计时）
        if (_studyGoal != null && _studyGoal!.enabled) ...[
          const SizedBox(height: IOSSpacing.s16),
          _buildStudyGoalCard(colors),
        ],
        // 快捷入口
        IOSListGroup(
          animate: true,
          title: '快捷入口',
          items: [
            IOSListItem(
              title: '模拟考试',
              subtitle: _mockPapers.isEmpty ? '综合卷' : '${_mockPapers.length + 1} 套',
              leading: _circleIcon(colors.primary, Icons.assignment_outlined),
              showChevron: true,
              onTap: () => context.go(
                _currentBankId != null
                    ? '/mock?bank=$_currentBankId'
                    : '/mock',
              ),
            ),
            IOSListItem(
              title: '背题',
              subtitle: '选章背诵',
              leading: _circleIcon(colors.primary, Icons.style_outlined),
              showChevron: true,
              onTap: _showBankPickerForMem,
            ),
            IOSListItem(
              title: '错题本',
              subtitle: _wrongCount == 0 ? '暂无' : '$_wrongCount 道',
              leading: _circleIcon(colors.danger, Icons.error_outline),
              showChevron: true,
              onTap: () => context.go(
                _currentBankId != null
                    ? '/wrongbook?bank=$_currentBankId'
                    : '/wrongbook',
              ),
            ),
          ],
        ),
        // 题库列表
        IOSListGroup(
          animate: true,
          title: '题库 · 共 $_totalCount 题',
          items: [
            for (final bank in _banks)
              IOSListItem(
                title: bank.name,
                subtitle:
                    '${bank.active} 题 · ${_answeredByBank[bank.bankId] ?? 0} 已答',
                leading: _circleIcon(
                  _subjectColor(bank.bankId),
                  Icons.menu_book_outlined,
                ),
                showChevron: true,
                onTap: () => context.go('/bank/${bank.bankId}'),
              ),
          ],
        ),
      ],
        ),
      ),
    );
  }

  Color _subjectColor(String bankId) => switch (bankId) {
        'education' => IOSSubjectColors.education,
        'psychology' => IOSSubjectColors.psychology,
        'ancient_chinese' => IOSSubjectColors.ancientChinese,
        'literary_theory' => IOSSubjectColors.literaryTheory,
        'politics' => IOSSubjectColors.politics,
        _ => IOSColors.light.primary,
      };

  Widget _circleIcon(Color color, IconData icon) {
    return Container(
      width: 30,
      height: 30,
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(IOSRadius.tag),
      ),
      child: Icon(icon, color: color, size: 17),
    );
  }

  /// 今日学习卡：环形正确率 + 今日学习数据竖排
  Widget _buildTodayCard(IOSColorScheme colors) {
    final accuracy = _todayAnswered > 0
        ? (_todayAccuracy / 100).clamp(0.0, 1.0)
        : 0.0;
    return IOSCard(
      padding: const EdgeInsets.all(IOSSpacing.s16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('今日学习', style: IOSTypography.title3(color: colors.text)),
          const SizedBox(height: IOSSpacing.s12),
          Row(
            children: [
              CircularRing(
                progress: accuracy,
                size: 92,
                strokeWidth: 8,
                color: colors.primary,
                center: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      _todayAnswered > 0
                          ? '${_todayAccuracy.toStringAsFixed(0)}%'
                          : '--',
                      style: TextStyle(
                        fontSize: IOSFontSize.title2,
                        fontWeight: FontWeight.w700,
                        color: colors.primary,
                      ),
                    ),
                    Text(
                      '今日正确率',
                      style: IOSTypography.caption2(color: colors.text2),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: IOSSpacing.s20),
              Expanded(
                child: Column(
                  children: [
                    _miniStat('待复习', _dueCount, colors.primary),
                    const SizedBox(height: IOSSpacing.s8),
                    _miniStat('新题', _newCount, IOSSystemColors.purple),
                    const SizedBox(height: IOSSpacing.s8),
                    _miniStat('错题', _wrongCount, colors.danger),
                    const SizedBox(height: IOSSpacing.s8),
                    _miniStat('连学', _streak, IOSSystemColors.green),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _miniStat(String label, int value, Color color) {
    final colors = IOSColors.of(context);
    return Row(
      children: [
        Container(
          width: 7,
          height: 7,
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(4),
          ),
        ),
        const SizedBox(width: IOSSpacing.s8),
        Text(label, style: IOSTypography.footnote(color: colors.text2)),
        const Spacer(),
        Text(
          '$value',
          style: IOSTypography.callout(color: colors.text)
              .copyWith(fontWeight: FontWeight.w700),
        ),
      ],
    );
  }

  /// 今日队列卡：标题 + 数量/状态，点击进入
  Widget _buildQueueCard({
    required IOSColorScheme colors,
    required String title,
    required int count,
    required IconData icon,
    required Color color,
    required bool done,
    VoidCallback? onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: IOSDuration.highlight,
        padding: const EdgeInsets.symmetric(
          horizontal: IOSSpacing.s12,
          vertical: IOSSpacing.s12,
        ),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(IOSRadius.md),
          color: color.withValues(alpha: 0.10),
          border: Border.all(color: color.withValues(alpha: 0.28)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, size: 15, color: done ? colors.success : color),
                const SizedBox(width: 6),
                Text(
                  title,
                  style: IOSTypography.footnote(
                    color: colors.text2,
                  ).copyWith(fontWeight: FontWeight.w600),
                ),
              ],
            ),
            const SizedBox(height: 7),
            Text(
              done
                  ? (title == '到期复习' ? '已完成' : '暂无新题')
                  : '$count 道',
              style: IOSTypography.title3(color: colors.text).copyWith(
                fontWeight: FontWeight.w700,
                color: done ? colors.success : colors.text,
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// 考试倒计时 + 每日目标卡（P2）
  Widget _buildStudyGoalCard(IOSColorScheme colors) {
    final goal = _studyGoal!;
    final days = goal.daysUntilExam(DateTime.now());
    return IOSCard(
      onTap: () => _push(const SettingsPagePlaceholder()),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: colors.dangerBg,
              borderRadius: BorderRadius.circular(IOSRadius.sm),
            ),
            child: Icon(Icons.event_available, color: colors.danger, size: 20),
          ),
          const SizedBox(width: IOSSpacing.s12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  days == null
                      ? (goal.examDate == null ? '未设置考试日期' : '考试日期已过')
                      : '距考试还有 $days 天',
                  style: IOSTypography.headline(
                    color: days != null && days <= 30
                        ? colors.danger
                        : colors.text,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  '考试日期 ${goal.examDate ?? '未设置'} · 今日已做 $_todayAnswered 题',
                  style: IOSTypography.footnote(color: colors.text2),
                ),
              ],
            ),
          ),
          Icon(Icons.chevron_right, color: colors.placeholder, size: 18),
        ],
      ),
    );
  }

  /// 背题入口：弹出题库选择，选科后跳章节列表
  Future<void> _showBankPickerForMem() async {
    final colors = IOSColors.of(context);
    final picked = await showModalBottomSheet<String>(
      context: context,
      builder: (ctx) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Padding(
              padding: const EdgeInsets.all(IOSSpacing.s16),
              child: Text(
                '选择科目开始背题',
                style: IOSTypography.title3(color: colors.text),
              ),
            ),
            for (final bank in _banks)
              ListTile(
                leading: Icon(
                  Icons.menu_book_outlined,
                  color: _subjectColor(bank.bankId),
                ),
                title: Text(bank.name),
                subtitle: Text('${bank.active} 题'),
                trailing: const Icon(Icons.chevron_right),
                onTap: () => Navigator.pop(ctx, bank.bankId),
              ),
            const SizedBox(height: IOSSpacing.s8),
          ],
        ),
      ),
    );
    if (picked != null && mounted) {
      context.go('/bank/$picked');
    }
  }
}

/// 临时占位：学习目标编辑入口（阶段3 接入设置页 V3 后替换）
class SettingsPagePlaceholder extends StatelessWidget {
  const SettingsPagePlaceholder({super.key});

  @override
  Widget build(BuildContext context) {
    final colors = IOSColors.of(context);
    return Scaffold(
      backgroundColor: colors.bg,
      appBar: AppBar(
        backgroundColor: colors.bg,
        title: const Text('设置'),
      ),
      body: const Center(child: Text('阶段3 接入')),
    );
  }
}
