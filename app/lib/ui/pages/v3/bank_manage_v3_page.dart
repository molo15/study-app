/// V3 iOS 风格「题库管理」二级页。
///
/// 职责：
/// - 导入题库包（.json / .zip，复用 SeedLoader 解析，与首页自动导入同一入口）；
/// - 列出全部已导入题库（含被隐藏的库，includeHidden: true）；
/// - 每个题库提供：编辑题目 / 清理归档 / 隐藏（或恢复显示）/ 彻底删除；
/// - 彻底删除需输入库名二次确认（不可恢复）。
///
/// 视觉与交互全部走 V3 设计系统：IOSCard / IOSListGroup / IOSButton /
/// showIOSActionSheet / showIOSModalSheet / iosPageRoute，动效与其他二级页一致。
/// 数据层不新增 SQL，全部复用 QuizRepository 既有方法。
library;

import 'dart:convert';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../data/quiz_repository.dart';
import '../../../data/seed_loader.dart';
import '../../app_toast.dart';
import '../../responsive.dart';
import '../../theme/ios_page_route.dart';
import '../../theme/ios_tokens.dart';
import '../../widgets/ios_action_sheet.dart';
import '../../widgets/ios_button.dart';
import '../../widgets/ios_card.dart';
import '../../widgets/ios_list_group.dart';
import '../../question_manage_page.dart';

class BankManageV3Page extends ConsumerStatefulWidget {
  const BankManageV3Page({super.key});

  @override
  ConsumerState<BankManageV3Page> createState() => _BankManageV3PageState();
}

class _BankManageV3PageState extends ConsumerState<BankManageV3Page> {
  List<BankInfo> _banks = const [];
  bool _loading = true;
  bool _importing = false;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final repo = await ref.read(quizRepositoryProvider);
      final banks = await repo.banks(includeHidden: true);
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

  // ---------------- 导入题库包 ----------------

  Future<void> _importBank() async {
    if (_importing) return;
    setState(() => _importing = true);
    try {
      final file = await FilePicker.pickFile(
        type: FileType.custom,
        allowedExtensions: const ['json', 'zip'],
        dialogTitle: '选择题库包（.json 或 .zip）',
      );
      if (file == null) {
        if (mounted) setState(() => _importing = false);
        return;
      }
      final bytes = await file.readAsBytes();
      final pack = file.name.toLowerCase().endsWith('.zip')
          ? SeedLoader.parseZipBytes(bytes)
          : SeedLoader.parse(utf8.decode(bytes));
      final repo = await ref.read(quizRepositoryProvider);
      final result = await repo.importBank(pack);
      if (!mounted) return;
      showAppToast(context, '导入成功：$result');
      await _load();
    } on FormatException catch (e) {
      if (mounted) showAppToast(context, '题库包无效：${e.message}');
    } catch (e) {
      if (mounted) showAppToast(context, '导入失败：$e');
    } finally {
      if (mounted) setState(() => _importing = false);
    }
  }

  // ---------------- 单库管理操作 ----------------

  Future<void> _bankActions(BankInfo bank) async {
    final action = await showIOSActionSheet<String>(
      context: context,
      title: bank.name,
      items: [
        const IOSActionItem(
          value: 'edit',
          title: '浏览 / 编辑题目',
          icon: Icons.edit_note,
        ),
        if (bank.archived > 0)
          IOSActionItem(
            value: 'purge',
            title: '清理已归档题（${bank.archived}）',
            subtitle: '物理删除归档题及其记录',
            icon: Icons.cleaning_services_outlined,
          ),
        IOSActionItem(
          value: bank.hidden ? 'restore' : 'hide',
          title: bank.hidden ? '恢复显示' : '隐藏题库',
          subtitle: bank.hidden ? '移除隐藏标记（题目需重新导入）' : '从刷题范围移除，进度保留',
          icon: bank.hidden ? Icons.visibility_outlined : Icons.visibility_off_outlined,
        ),
        const IOSActionItem(
          value: 'delete',
          title: '彻底删除题库',
          subtitle: '题目与全部学习记录一并删除，不可恢复',
          icon: Icons.delete_outline,
          destructive: true,
        ),
      ],
    );
    if (action == null || !mounted) return;
    switch (action) {
      case 'edit':
        Navigator.of(context).push(
          iosPageRoute<dynamic>(
            (_) => QuestionManagePage(bankId: bank.bankId, bankName: bank.name),
          ),
        );
      case 'purge':
        await _purge(bank);
      case 'hide':
        await _hide(bank);
      case 'restore':
        await _restore(bank);
      case 'delete':
        await _confirmDelete(bank);
    }
  }

  Future<void> _purge(BankInfo bank) async {
    final repo = await ref.read(quizRepositoryProvider);
    final n = await repo.purgeArchived(bank.bankId);
    if (!mounted) return;
    showAppToast(context, '已清理 $n 道归档题');
    await _load();
  }

  Future<void> _hide(BankInfo bank) async {
    final repo = await ref.read(quizRepositoryProvider);
    await repo.uninstallBank(bank.bankId);
    if (!mounted) return;
    showAppToast(context, '已隐藏「${bank.name}」，学习记录保留');
    await _load();
  }

  Future<void> _restore(BankInfo bank) async {
    final repo = await ref.read(quizRepositoryProvider);
    await repo.restoreBank(bank.bankId);
    if (!mounted) return;
    showAppToast(context, '已恢复显示，重新导入题库包可恢复题目');
    await _load();
  }

  Future<void> _confirmDelete(BankInfo bank) async {
    var typed = '';
    final ok = await showIOSModalSheet<bool>(
      context: context,
      builder: (sheetCtx) {
        final c = IOSColors.of(sheetCtx);
        return StatefulBuilder(
          builder: (ctx, setSheet) => Padding(
            padding: const EdgeInsets.all(IOSSpacing.s20),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('彻底删除「${bank.name}」？',
                    style: IOSTypography.headline(color: c.danger)),
                const SizedBox(height: IOSSpacing.s12),
                Text(
                  '将删除该题库全部题目及作答记录、复习进度、错题本、模拟卷，'
                  '不可恢复。请输入题库名称确认：',
                  style: IOSTypography.footnote(color: c.text2)
                      .copyWith(height: 1.5),
                ),
                const SizedBox(height: IOSSpacing.s12),
                TextField(
                  autofocus: true,
                  onChanged: (v) => setSheet(() => typed = v.trim()),
                  decoration: InputDecoration(
                    hintText: '输入「${bank.name}」以确认',
                    isDense: true,
                  ),
                ),
                const SizedBox(height: IOSSpacing.s16),
                Row(
                  children: [
                    Expanded(
                      child: IOSButton(
                        label: '取消',
                        type: IOSButtonType.text,
                        expand: true,
                        onPressed: () => Navigator.of(ctx).pop(false),
                      ),
                    ),
                    const SizedBox(width: IOSSpacing.s12),
                    Expanded(
                      child: IOSButton(
                        label: '删除',
                        type: IOSButtonType.danger,
                        expand: true,
                        enabled: typed == bank.name,
                        onPressed: () => Navigator.of(ctx).pop(true),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
    if (ok != true || !mounted) return;
    final repo = await ref.read(quizRepositoryProvider);
    await repo.deleteBankCompletely(bank.bankId);
    if (!mounted) return;
    showAppToast(context, '已彻底删除「${bank.name}」');
    await _load();
  }

  // ---------------- 视图 ----------------

  @override
  Widget build(BuildContext context) {
    final colors = IOSColors.of(context);
    return Scaffold(
      backgroundColor: colors.bg,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        scrolledUnderElevation: 0,
        centerTitle: true,
        title: Text('题库管理',
            style: IOSTypography.title2(color: colors.text)),
        leading: const BackButton(color: IOSSystemColors.blue),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(strokeWidth: 2.5))
          : Center(
              child: ConstrainedBox(
                constraints:
                    BoxConstraints(maxWidth: effectiveContentWidth(context)),
                child: ListView(
                  padding: const EdgeInsets.fromLTRB(
                    IOSSpacing.s16,
                    IOSSpacing.s8,
                    IOSSpacing.s16,
                    IOSFloatingBar.kTContentBottomInset,
                  ),
                  children: [
                    IOSButton(
                      label: _importing ? '正在导入…' : '导入题库包（.json / .zip）',
                      icon: Icons.file_upload_outlined,
                      expand: true,
                      loading: _importing,
                      onPressed: _importBank,
                    ),
                    const SizedBox(height: IOSSpacing.s16),
                    if (_banks.isEmpty)
                      _emptyState(colors)
                    else
                      IOSListGroup(
                        title: '已导入题库（${_banks.length}）',
                        animate: true,
                        items: [
                          for (final bank in _banks)
                            IOSListItem(
                              title: bank.hidden
                                  ? '${bank.name}（已隐藏）'
                                  : bank.name,
                              subtitle: _subtitle(bank),
                              leading: _bankIcon(bank, colors),
                              showChevron: true,
                              onTap: () => _bankActions(bank),
                            ),
                        ],
                      ),
                  ],
                ),
              ),
            ),
    );
  }

  String _subtitle(BankInfo bank) {
    final parts = <String>[
      '共 ${bank.total} 题',
      '可用 ${bank.active}',
    ];
    if (bank.archived > 0) parts.add('归档 ${bank.archived}');
    if (bank.userEdited > 0) parts.add('已编辑 ${bank.userEdited}');
    if (bank.version.isNotEmpty) parts.add('v${bank.version}');
    return parts.join(' · ');
  }

  Widget _bankIcon(BankInfo bank, IOSColorScheme colors) {
    return Container(
      width: 34,
      height: 34,
      decoration: BoxDecoration(
        color: (bank.hidden ? colors.text3 : colors.primary)
            .withValues(alpha: 0.14),
        borderRadius: BorderRadius.circular(IOSRadius.sm),
      ),
      alignment: Alignment.center,
      child: Icon(
        bank.hidden ? Icons.visibility_off_outlined : Icons.menu_book_outlined,
        size: 19,
        color: bank.hidden ? colors.text3 : colors.primary,
      ),
    );
  }

  Widget _emptyState(IOSColorScheme colors) {
    return IOSCard(
      padding: const EdgeInsets.symmetric(
        vertical: IOSSpacing.s32,
        horizontal: IOSSpacing.s20,
      ),
      child: Column(
        children: [
          Icon(Icons.inbox_outlined, size: 40, color: colors.text3),
          const SizedBox(height: IOSSpacing.s12),
          Text('还没有导入任何题库包',
              style: IOSTypography.callout(color: colors.text2)),
          const SizedBox(height: IOSSpacing.s4),
          Text('点击上方按钮选择 .json 或 .zip 题库包',
              style: IOSTypography.footnote(color: colors.text3)),
        ],
      ),
    );
  }
}
