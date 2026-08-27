/**
 * 素材提取：从思源笔记本提取「可出题素材块」
 *
 * 筛选规则（与设计方案 §2.2 一致）：
 * - 内容型块：type IN ('p','h','li')（段落/标题/列表项），排除代码块/数据库等
 * - 长度过滤：length BETWEEN 20 AND 800（过短无信息量、过长需切分）
 * - 按笔记本 + 可选文档路径过滤
 * - 携带 hpath（章节语境）+ markdown 原文 + 块 id（出题后可追溯 source.blockId）
 * - 排除污染源（探查实测）：课后习题答案/题库答案/真题汇总等本身就是答案的文档，
 *   AI 据此出题会直接泄露答案；emojis 结构标记块（💡/📄/📝/🌏/🎵）无出题信息量
 */
import { querySql } from './siyuan.js';

const EXCLUDE_HPATH_PATTERNS = [
  /课后习题答案/,
  /题库\/答案/,
  /本章真题汇总/,
  /真题\/答案/,
  /真题精读\/.*\/📝/,
];

const EXCLUDE_CONTENT_PREFIX = ['💡', '📄', '📝', '🌏', '🎵'];

/** 判断块是否应排除（返回 true 表示排除） */
export function isExcluded(b) {
  const hpath = b.hpath || '';
  if (EXCLUDE_HPATH_PATTERNS.some((re) => re.test(hpath))) return true;
  const content = (b.content || '').trim();
  if (EXCLUDE_CONTENT_PREFIX.some((p) => content.startsWith(p))) return true;
  return false;
}

/** 提取某笔记本的可出题素材块 */
export async function extractBlocks(config, { notebook, minLen = 20, maxLen = 800, limit = 2000 }) {
  const stmt = `
    SELECT id, root_id, box, path, hpath, type, content, markdown, length, sort
    FROM blocks
    WHERE box = '${notebook}'
      AND type IN ('p','h','li')
      AND length BETWEEN ${minLen} AND ${maxLen}
    ORDER BY hpath, sort
    LIMIT ${limit}
  `;
  const rows = await querySql(config, stmt);
  return rows.filter((b) => !isExcluded(b));
}

/** 提取某笔记本的标题树（章节体系候选：h 块） */
export async function extractHeadings(config, notebook, limit = 500) {
  const stmt = `
    SELECT content, hpath, sort
    FROM blocks
    WHERE box = '${notebook}' AND type = 'h'
    ORDER BY hpath, sort
    LIMIT ${limit}
  `;
  return await querySql(config, stmt);
}

/** 按块 id 批量取原文（供 AI 生成时拼上下文） */
export async function fetchBlocksByIds(config, ids) {
  if (ids.length === 0) return [];
  const stmt = `
    SELECT id, box, hpath, type, content, markdown
    FROM blocks
    WHERE id IN (${ids.map((id) => `'${id}'`).join(',')})
  `;
  return await querySql(config, stmt);
}

/** 输出块类型统计（探查用） */
export async function blockTypeStats(config, notebook) {
  const stmt = `
    SELECT type, COUNT(*) AS cnt, SUM(length) AS total_len
    FROM blocks
    WHERE box = '${notebook}'
    GROUP BY type
    ORDER BY cnt DESC
  `;
  return await querySql(config, stmt);
}
