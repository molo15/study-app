import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../data/quiz_repository.dart';
import 'bank_page.dart';
import 'chapter_overview_list_page.dart';
import 'chapter_overview_page.dart';
import 'mock_exam_list_page.dart';
import 'question_manage_page.dart';
import 'root_page.dart';
import 'wrong_book_page.dart';

/// 全局路由（URL 路由，hash 策略 → 静态托管零配置，无需服务器 fallback）。
///
/// 设计原则（iOS/桌面优先 · URL 路由）：
/// - `/` 为应用根（RootPage：5 tab + dock/侧边栏）；二级页以嵌套子路由挂在根下，
///   导航用 `context.go`（go_router 的 go 会同步 URL，push 不会；嵌套保留 RootPage
///   在栈底，返回不重建父页面）；
/// - 二级页（科目/章节/错题本/模拟考/题库管理）可深链、刷新保持、前进后退；
/// - 会话页（刷题/背题/考试/回顾）为进行中状态页，保持 Navigator 推栈（不占 URL，
///   刷新即回到根，与原有行为一致；对象参数经构造传递，避免 URL 序列化复杂度）。
///
/// 分享链接示例：
/// - `/bank/bank-gudai-hanyu/chapter/修辞` → 直达章节概览
/// - `/bank/bank-gudai-hanyu/chapters` → 直达章节列表
/// - `/wrongbook` / `/mock` → 直达错题本 / 模拟考
final appRouter = GoRouter(
  initialLocation: '/',
  routes: [
    GoRoute(
      path: '/',
      builder: (_, _) => const RootPage(),
      routes: [
        GoRoute(
          path: 'bank/:bankId',
          builder: (_, s) => BankPage(bankId: s.pathParameters['bankId']!),
          routes: [
            GoRoute(
              path: 'chapters',
              builder: (_, s) => ChapterOverviewListPage(
                bankId: s.pathParameters['bankId']!,
              ),
            ),
            GoRoute(
              path: 'chapter/:chapterId',
              builder: (_, s) => ChapterOverviewPage(
                bankId: s.pathParameters['bankId']!,
                // chapter 参数即章名（String）；go_router 已自动解码 path 参数，
                // 页面内部自行反查概览
                chapter: s.pathParameters['chapterId']!,
              ),
            ),
          ],
        ),
        GoRoute(
          path: 'mock',
          builder: (_, s) => MockExamListPage(
            bankId: s.uri.queryParameters['bank'],
          ),
        ),
        GoRoute(
          path: 'wrongbook',
          builder: (_, s) => WrongBookPage(
            bankId: s.uri.queryParameters['bank'],
          ),
        ),
        GoRoute(
          path: 'me/questions/:bankId',
          builder: (_, s) => QuestionManageDeepLinkPage(
            bankId: s.pathParameters['bankId']!,
          ),
        ),
      ],
    ),
  ],
);

/// 题库管理深链页：由 bankId 反查 bankName 后渲染 QuestionManagePage。
class QuestionManageDeepLinkPage extends ConsumerStatefulWidget {
  const QuestionManageDeepLinkPage({super.key, required this.bankId});

  final String bankId;

  @override
  ConsumerState<QuestionManageDeepLinkPage> createState() =>
      _QuestionManageDeepLinkPageState();
}

class _QuestionManageDeepLinkPageState
    extends ConsumerState<QuestionManageDeepLinkPage> {
  late final Future<String> _future;

  @override
  void initState() {
    super.initState();
    _future = _load();
  }

  Future<String> _load() async {
    try {
      final repo = await ref.read(quizRepositoryProvider);
      final banks = await repo.banks(includeHidden: true);
      for (final b in banks) {
        if (b.bankId == widget.bankId) return b.name;
      }
    } catch (_) {}
    return widget.bankId;
  }

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<String>(
      future: _future,
      builder: (context, snap) {
        if (snap.connectionState != ConnectionState.done) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }
        return QuestionManagePage(
          bankId: widget.bankId,
          bankName: snap.data ?? widget.bankId,
        );
      },
    );
  }
}
