part of 'quiz_repository.dart';

/// 设置读写、当前题库选择、刷题续刷进度、题库包版本检测
mixin _SettingsMixin on RepositoryMixinBase {
  /// 当前选中的题库 id（settings 持久化；null/空 = 全部）
  Future<String?> currentBankId() async {
    final value = await setting('current_bank_id');
    return (value == null || value.isEmpty) ? null : value;
  }

  Future<void> setCurrentBankId(String? bankId) async {
    await setSetting('current_bank_id', bankId ?? '');
  }

  /// 某题库的章节分组（v3 两级：上编/中编/下编 → 章节；v2 单个"全部"分组）
  Future<List<ChapterGroup>> chapterGroups(String bankId) async {
    final raw = await setting('bank_${bankId}_groups');
    if (raw == null || raw.isEmpty) return const [];
    try {
      final decoded = const JsonDecoder().convert(raw) as List<dynamic>;
      return decoded
          .map((e) => ChapterGroup.fromJson(e as Map<String, dynamic>))
          .toList();
    } catch (_) {
      return const [];
    }
  }

  /// {bankId: name} 映射（错题本/统计标注题库名用；审查 P2-6：正则解析避免 id 含 _name 错名）
  Future<Map<String, String>> bankNameMap() async {
    final rows = await _db.query(
      'settings',
      where: "key LIKE 'bank\\_%\\_name' ESCAPE '\\'",
    );
    final result = <String, String>{};
    for (final r in rows) {
      final key = r['key'] as String;
      final match = RegExp(r'^bank_(.+)_name$').firstMatch(key);
      if (match != null) {
        result[match.group(1)!] = (r['value'] as String?) ?? '';
      }
    }
    return result;
  }

  /// 键值设置读取（题库包名称/版本、复习参数等）
  @override
  Future<String?> setting(String key) async {
    final rows = await _db.query(
      'settings',
      where: 'key = ?',
      whereArgs: [key],
      limit: 1,
    );
    return rows.isEmpty ? null : rows.first['value'] as String?;
  }

  /// 键值设置写入（upsert）
  Future<void> setSetting(String key, String value) async {
    await _db.insert('settings', {
      'key': key,
      'value': value,
    }, conflictAlgorithm: ConflictAlgorithm.replace);
  }

  /// 刷题页计时器可见性（默认关闭；计时本身不受此开关影响）
  Future<bool> practiceTimerVisible() async =>
      (await setting(QuizRepository.practiceTimerVisibleKey)) == 'true';

  /// 审题标记功能开关（默认关闭；关闭时刷题页不显示旗子、设置页不显示导出入口）
  Future<bool> reviewModeEnabled() async =>
      (await setting(QuizRepository.reviewModeEnabledKey)) == 'true';

  Future<void> setReviewModeEnabled(bool enabled) => setSetting(
        QuizRepository.reviewModeEnabledKey,
        enabled ? 'true' : 'false',
      );

  /// 模拟考存疑标记◆开关（默认开启；关闭时模拟考答题页不显示 diamond 按钮）
  Future<bool> doubtEnabled() async {
    final v = await setting(QuizRepository.mockDoubtEnabledKey);
    return v == null || v == 'true'; // 默认开启
  }

  Future<void> setDoubtEnabled(bool enabled) => setSetting(
        QuizRepository.mockDoubtEnabledKey,
        enabled ? 'true' : 'false',
      );

  Future<void> setPracticeTimerVisible(bool visible) => setSetting(
    QuizRepository.practiceTimerVisibleKey,
    visible ? 'true' : 'false',
  );

  /// 读取某刷题范围上次做到的题目 id（无记录返回 null）
  Future<String?> practiceProgress(String key) =>
      setting(QuizRepository.practiceProgressKey(key));

  /// 保存某刷题范围当前进度（下次进入从该题继续）
  Future<void> savePracticeProgress(String key, String questionId) =>
      setSetting(QuizRepository.practiceProgressKey(key), questionId);

  /// 清除某刷题范围进度（刷完/用户重新开始）
  Future<void> clearPracticeProgress(String key) async {
    await _db.delete(
      'settings',
      where: 'key = ?',
      whereArgs: [QuizRepository.practiceProgressKey(key)],
    );
  }

  /// 通用：删除单个设置键（答题卡结果表清理等）
  Future<void> clearSetting(String key) async {
    await _db.delete('settings', where: 'key = ?', whereArgs: [key]);
  }

  /// 内置题库包是否已导入（按 bank_id 版本记录）
  @override
  Future<String?> importedVersion(String bankId) async {
    final rows = await _db.query(
      'settings',
      where: 'key = ?',
      whereArgs: ['bank_${bankId}_version'],
    );
    return rows.isEmpty ? null : rows.first['value'] as String;
  }

  /// 学习目标（P2：考试日期 + 每日新题/复习量；未设返回 null）
  Future<StudyGoal?> studyGoal() async {
    final raw = await setting('study_goal');
    if (raw == null || raw.isEmpty) return null;
    try {
      return StudyGoal.fromJson(
        const JsonDecoder().convert(raw) as Map<String, dynamic>,
      );
    } catch (_) {
      return null;
    }
  }

  Future<void> setStudyGoal(StudyGoal goal) =>
      setSetting('study_goal', const JsonEncoder().convert(goal.toJson()));
}
