/// 首页：今日任务优先 + 快捷入口 + 题库列表（设计方案 §3.2）
///
/// 改版（阶段 B）：
/// - 顶部今日状态改为「短文本胶囊 + Tooltip」，避免 320dp 窄屏与标题/错题按钮挤占；
/// - 今日任务区保持「开始今日复习」为页面唯一主按钮（FilledButton 样式与禁用逻辑不变），
///   无待复习时展示完成态，并提供次级「刷新题」入口；
/// - 错题本、模拟考试降级为快捷入口次级卡片；模拟卷为空时保留入口占位（轻量空态），
///   不破坏现有 mockPapers 判断逻辑；
/// - 题库列表卡仅使用现有 BankInfo 字段做视觉强化（一行标题 + 两行辅助信息、题量弱化），
///   不新增 SQL、不改 repository。
library;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/quiz_repository.dart';
import '../data/seed_loader.dart';
import '../models/models.dart';
import '../services/app_log.dart';
import 'theme_controller.dart';
import 'glass_app_bar.dart';
import 'bank_page.dart';
import 'mock_exam_list_page.dart';
import 'practice_page.dart';
import 'settings_page.dart';
import 'wrong_book_page.dart';
import 'app_routes.dart';
import 'widgets/app_card.dart';
import 'widgets/circular_ring.dart';
import 'widgets/staggered_item.dart';

class HomePage extends ConsumerStatefulWidget {
  const HomePage({super.key});

  @override
  ConsumerState<HomePage> createState() => _HomePageState();
}

class _HomePageState extends ConsumerState<HomePage> {
  /// 内置题库自动发现（v1.1.3）：枚举 assets/banks/*.zip，每科取版本号最高的包。
  ///
  /// 替代硬编码版本路径——此前 v0.12 已打包但 home_page 仍引用 v0.11，导致
  /// "新题库未附带"事故；自动扫描后未来题库升级（v0.13+）只需替换 zip，无需改代码。
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
  List<BankInfo> _banks = const []; // 多题库切换（需求）
  String? _currentBankId; // null = 全部
  Map<String, int> _answeredByBank = const {}; // 各题库已作答题数（首页题库卡进度）
  List<MockPaper> _mockPapers = const []; // 模拟卷（需求）
  int _todayAnswered = 0; // 今日已答（需求：右上角提示增强）
  double _todayAccuracy = 0;
  int _streak = 0;
  StudyGoal? _studyGoal; // 学习目标（P2：考试倒计时/每日目标）

  @override
  void initState() {
    super.initState();
    _init();
  }

  Future<void> _init() async {
    try {
      final repo = await ref.read(quizRepositoryProvider);
      // 内置题库同步（幂等）：自动扫描 assets 最新版本（v1.1.3）；
      // 用户卸载/隐藏的库跳过；版本不一致时自动重导（覆盖旧内容、保留用户本地修改）。
      // 先轻量读 manifest 版本比对，不一致才全量解析导入（性能优化：避免每次启动解析全部题目）。
      final bundledBanks = await _discoverBundledBanks();
      for (final entry in bundledBanks.entries) {
        final hidden =
            await repo.setting('bank_${entry.key}_hidden') == 'true';
        if (hidden) continue;
        final bytes = (await rootBundle.load(
          entry.value,
        )).buffer.asUint8List();
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
    // 当前题库：上次选择（持久化）；单题库自动回退到唯一库；所选已消失回退（审查 P0-3）
    var current = await repo.currentBankId();
    if (banks.length == 1) {
      current = banks.first.bankId; // 单题库直接用唯一库，保证章节/随机刷可达
      await repo.setCurrentBankId(current);
    } else if (current != null && !banks.any((b) => b.bankId == current)) {
      current = null; // 所选题库已不存在（如被清理）
    }
    final isAll = current == null;
    final bankId = isAll ? null : current;
    final dueCount = await repo.dueCount(bankId: bankId);
    final newCount = await repo.newCount(bankId: bankId);
    final wrongCount = await repo.wrongBookCount(bankId: bankId);
    final mockPapers = await repo.mockPapers(bankId: bankId); // 模拟卷入口
    final overview = await repo.todayOverview(); // 今日概览（需求：右上角更多提示）
    final answeredByBank = await repo.answeredCountByBank(); // 首页题库卡已答进度
    final studyGoal = await repo.studyGoal(); // 学习目标（P2）
    final totalAll = banks.fold(0, (sum, b) => sum + b.active); // 全部题库总题数
    AppLog.page(
      '首页刷新: bank=${current ?? '全部'} 到期$dueCount 新题$newCount 错题$wrongCount',
    );
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

  Future<void> _push(Widget page) async {
    await Navigator.of(context).push(AppPageRoute(builder: (_) => page));
    final repo = await ref.read(quizRepositoryProvider);
    await _refresh(repo);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      appBar: GlassAppBar(
        title: const Text('考研刷题'),
        centerTitle: true, // 需求：标题居中
        actions: [
          // 今日状态：短文本胶囊 + Tooltip（需求：避免窄屏长文本挤占标题/错题按钮）
          if (_todayAnswered > 0)
            Tooltip(
              message:
                  '今日 $_todayAnswered 题 · 正确率 ${_todayAccuracy.toStringAsFixed(0)}%'
                  '${_streak > 1 ? ' · 连学 $_streak 天' : ''}',
              child: Center(
                child: Container(
                  margin: const EdgeInsets.only(right: 4),
                  padding: const EdgeInsets.symmetric(
                    horizontal: 10,
                    vertical: 6,
                  ),
                  decoration: BoxDecoration(
                    color: theme.colorScheme.primaryContainer.withValues(
                      alpha: 0.6,
                    ),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        Icons.today,
                        size: 14,
                        color: theme.colorScheme.onPrimaryContainer,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        '今日 $_todayAnswered 题',
                        style: theme.textTheme.labelMedium?.copyWith(
                          color: theme.colorScheme.onPrimaryContainer,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          // 错题本入口收敛到下方快捷入口卡（唯一入口，避免与今日胶囊/统计重复）
        ],
      ),
      body: _buildBody(theme),
    );
  }

  Widget _buildBody(ThemeData theme) {
    if (_loading) return const Center(child: CircularProgressIndicator());
    if (_error != null) {
      return _ErrorView(
        message: _error!,
        onRetry: () {
          setState(() {
            _loading = true;
            _error = null;
          });
          _init();
        },
      );
    }
    return ListView(
      // 底部留 96 安全空间，防沉浸式导航遮挡（需求）
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 96),
      children: [
        // 考试倒计时 + 每日目标（P2；未设置/未启用时不显示）
        if (_studyGoal != null && _studyGoal!.enabled)
          _buildStudyGoalCard(theme),
        // 今日任务区（主视觉区，设计方案 §3.2）
        _SectionTitle(title: '今日任务'),
        const SizedBox(height: 8),
        _buildTodayCard(theme),
        const SizedBox(height: 16),
        // 快捷入口区：错题本 + 模拟考试（次级入口）
        _buildQuickEntries(theme),
        const SizedBox(height: 20),
        // 题库区
        _SectionTitle(
          title: '题库',
          trailing: Text(
            '共 $_totalCount 题',
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.outline,
            ),
          ),
        ),
        const SizedBox(height: 8),
        for (var i = 0; i < _banks.length; i++)
          StaggeredItem(
            index: i,
            child: _buildBankCard(theme, _banks[i]),
          ),
        const SizedBox(height: 16),
      ],
    );
  }

  /// 考试倒计时 + 每日目标卡（P2）：距考试天数为主视觉，每日新题/复习目标为辅助。
  /// 点击进入设置页编辑学习目标（用户可自由覆盖/开关）。
  Widget _buildStudyGoalCard(ThemeData theme) {
    final goal = _studyGoal!;
    final days = goal.daysUntilExam(DateTime.now());
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () => _push(const SettingsPage()),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: theme.colorScheme.errorContainer.withValues(alpha: 0.5),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  Icons.event_available,
                  color: theme.colorScheme.onErrorContainer,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      days == null
                          ? (goal.examDate == null
                                ? '未设置考试日期'
                                : '考试日期已过')
                          : '距考试还有 $days 天',
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w700,
                        color: days != null && days <= 30
                            ? theme.colorScheme.error
                            : null,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      '考试日期 ${goal.examDate ?? '未设置'} · 今日已做 $_todayAnswered 题',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right),
            ],
          ),
        ),
      ),
    );
  }

  /// 今日任务卡：三项计数 + 唯一主按钮（禁用逻辑不变）+ 无任务时的次级入口
  Widget _buildTodayCard(ThemeData theme) {
    final config = ref.watch(themeControllerProvider).asData?.value;
    final accent = config?.accent ?? const Color(0xFF4F7CD4);
    final ink2 = theme.colorScheme.onSurfaceVariant;
    final accuracy = _todayAnswered > 0
        ? (_todayAccuracy / 100).clamp(0.0, 1.0)
        : 0.0;

    return AppCard(
      depth: 1,
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          children: [
            // Hero：今日学习环形进度（今日正确率，生长动画）
            Row(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                CircularRing(
                  progress: accuracy,
                  size: 108,
                  strokeWidth: 9,
                  color: accent,
                  center: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        _todayAnswered > 0
                            ? '${_todayAccuracy.toStringAsFixed(0)}%'
                            : '--',
                        style: TextStyle(
                          fontSize: 21,
                          fontWeight: FontWeight.w800,
                          color: accent,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        '今日正确率',
                        style: TextStyle(fontSize: 10, color: ink2),
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 20),
                // 右侧：今日数据竖排
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '今日学习',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w800,
                          color: theme.colorScheme.onSurface,
                        ),
                      ),
                      const SizedBox(height: 12),
                      _miniStat('待复习', _dueCount, theme.colorScheme.primary),
                      const SizedBox(height: 8),
                      _miniStat('新题', _newCount, theme.colorScheme.tertiary),
                      const SizedBox(height: 8),
                      _miniStat('错题', _wrongCount, theme.colorScheme.error),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            // 页面唯一主行动：开始今日复习（FilledButton 样式与禁用逻辑不变）
            SizedBox(
              width: double.infinity,
              child: FilledButton.icon(
                onPressed: _dueCount == 0
                    ? null
                    : () => _push(
                          PracticePage(
                            mode: PracticeMode.review,
                            bankId: _currentBankId,
                          ),
                        ),
                icon: const Icon(Icons.autorenew),
                label: Text(_dueCount == 0 ? '今日任务已完成' : '开始今日复习（$_dueCount）'),
              ),
            ),
            // 无待复习但仍有新题：给出次级「刷新题」入口（设计方案 §3.2 空态）
            if (_dueCount == 0 && _newCount > 0) ...[
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  // 取"新题"（尚未建立调度记录）作为本轮范围，与按钮题量一致；
                  // 否则会刷整库全部 active 题，把已做过的题混进来（审查修复）
                  onPressed: () async {
                    final repo = await ref.read(quizRepositoryProvider);
                    final questions = await repo.newQuestions(
                      bankId: _currentBankId,
                      limit: _newCount,
                    );
                    if (!mounted || questions.isEmpty) return;
                    _push(
                      PracticePage(
                        mode: PracticeMode.learn,
                        bankId: _currentBankId,
                        // 固定顺序刷题记住进度：当前题库下「新题顺序刷」范围
                        progressKey: 'home-new:${_currentBankId ?? 'all'}',
                        questions: questions,
                      ),
                    );
                  },
                  icon: const Icon(Icons.bolt_outlined),
                  label: Text('刷 $_newCount 道新题'),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  /// Hero 竖排数据项
  Widget _miniStat(String label, int value, Color color) {
    return Row(
      children: [
        Container(
          width: 8,
          height: 8,
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(4),
          ),
        ),
        const SizedBox(width: 8),
        Text(label, style: const TextStyle(fontSize: 12.5, color: Color(0xFF56647C))),
        const Spacer(),
        Text('$value', style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w800)),
      ],
    );
  }

  /// P1.5 快捷入口：三并排卡（模拟考 / 背题 / 错题本）
  Widget _buildQuickEntries(ThemeData theme) {
    return Row(
      children: [
        Expanded(
          child: _quickEntryCard(
            icon: Icons.assignment_outlined,
            iconColor: theme.colorScheme.tertiary,
            title: '模拟考',
            subtitle: _mockPapers.isEmpty
                ? '综合卷'
                : '${_mockPapers.length + 1} 套',
            onTap: () => _push(MockExamListPage(bankId: _currentBankId)),
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: _quickEntryCard(
            icon: Icons.style_outlined,
            iconColor: theme.colorScheme.primary,
            title: '背题',
            subtitle: '选章背诵',
            onTap: _showBankPickerForMem,
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: _quickEntryCard(
            icon: Icons.error_outline,
            iconColor: theme.colorScheme.error,
            title: '错题本',
            subtitle: _wrongCount == 0 ? '暂无' : '$_wrongCount 道',
            onTap: () => _push(WrongBookPage(bankId: _currentBankId)),
          ),
        ),
      ],
    );
  }

  /// 背题入口：弹出题库选择，选科后跳转到该科章节列表（用户选章进入背题）
  Future<void> _showBankPickerForMem() async {
    final theme = Theme.of(context);
    final picked = await showModalBottomSheet<String>(
      context: context,
      builder: (ctx) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Padding(
              padding: const EdgeInsets.all(16),
              child: Text('选择科目开始背题', style: theme.textTheme.titleMedium),
            ),
            for (final bank in _banks)
              ListTile(
                leading: const Icon(Icons.menu_book_outlined),
                title: Text(bank.name),
                subtitle: Text('${bank.active} 题'),
                trailing: const Icon(Icons.chevron_right),
                onTap: () => Navigator.pop(ctx, bank.bankId),
              ),
            const SizedBox(height: 8),
          ],
        ),
      ),
    );
    if (picked != null && mounted) {
      _push(BankPage(bankId: picked));
    }
  }

  /// P1.5 快捷入口小卡：图标 + 标题 + 副标题
  Widget _quickEntryCard({
    required IconData icon,
    required Color iconColor,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    final theme = Theme.of(context);
    return AppCard(
      padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 8),
      onTap: onTap,
      child: Column(
        children: [
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              color: iconColor.withValues(alpha: 0.12),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: iconColor, size: 20),
          ),
          const SizedBox(height: 8),
          Text(
            title,
            style: theme.textTheme.labelLarge?.copyWith(fontWeight: FontWeight.w700),
          ),
          const SizedBox(height: 2),
          Text(
            subtitle,
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
        ],
      ),
    );
  }

  /// 题库列表卡：一行标题 + 两行辅助信息，题量弱化（仅用 BankInfo 现有字段）
  Widget _buildBankCard(ThemeData theme, BankInfo bank) {
    return AppCard(
      padding: EdgeInsets.zero,
      margin: const EdgeInsets.only(bottom: 10),
      onTap: () => _push(BankPage(bankId: bank.bankId)),
      child: ListTile(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        leading: Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: theme.colorScheme.primary.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(
            Icons.menu_book_outlined,
            color: theme.colorScheme.primary,
            size: 22,
          ),
        ),
        title: Text(
          bank.name,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: const TextStyle(fontWeight: FontWeight.w600),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '共 ${bank.active} 题',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 6),
            _BankProgress(
              answered: _answeredByBank[bank.bankId] ?? 0,
              total: bank.active,
            ),
          ],
        ),
        isThreeLine: true,
        trailing: const Icon(Icons.chevron_right),
      ),
    );
  }
}

/// 题库卡已答进度：百分比 + 细进度条（已答为独立题目数，作答次数不计入）
class _BankProgress extends StatelessWidget {
  const _BankProgress({required this.answered, required this.total});

  final int answered;
  final int total;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final ratio = total <= 0 ? 0.0 : (answered / total).clamp(0.0, 1.0);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          answered == 0
              ? '未开始'
              : '已答 $answered / $total 题 · ${(ratio * 100).toStringAsFixed(0)}%',
          style: theme.textTheme.bodySmall?.copyWith(
            color: theme.colorScheme.outline,
          ),
        ),
        const SizedBox(height: 4),
        ClipRRect(
          borderRadius: BorderRadius.circular(3),
          child: LinearProgressIndicator(
            value: ratio,
            minHeight: 4,
            backgroundColor: theme.colorScheme.surfaceContainerHighest,
          ),
        ),
      ],
    );
  }
}

/// 区块标题（标题 + 可选右侧辅助信息）
class _SectionTitle extends StatelessWidget {
  const _SectionTitle({required this.title, this.trailing});

  final String title;
  final Widget? trailing;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Row(
      children: [
        Text(
          title,
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.w700,
          ),
        ),
        const Spacer(),
        ?trailing,
      ],
    );
  }
}

/// 通用错误态：图标 + 说明 + 重试按钮（页面内私有组件）
class _ErrorView extends StatelessWidget {
  const _ErrorView({required this.message, required this.onRetry});

  final String message;
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.cloud_off_outlined,
              size: 44,
              color: theme.colorScheme.error,
            ),
            const SizedBox(height: 12),
            Text(
              message,
              textAlign: TextAlign.center,
              style: theme.textTheme.bodyMedium,
            ),
            const SizedBox(height: 16),
            FilledButton.tonalIcon(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh),
              label: const Text('重试'),
            ),
          ],
        ),
      ),
    );
  }
}

/// 统计数字单元：待复习 / 新题 / 错题


/// 题库切换胶囊（多题库，需求）
