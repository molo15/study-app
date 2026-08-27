/**
 * 真题提取：把「本章真题汇总」文档解析为结构化题目
 *
 * 源（探查确认）：
 * - 古汉 11 章、现汉 6 章、现文 1 章，格式：按题型分节
 *   （一、填空题 / 二、判断题 / 三、选择题 / 四、名词解释 / 五、简答题），
 *   题干 p 块带（年份）标注，末尾有"答案"标题 + 答案块（markdown 加粗）
 *
 * 输出：out/zhenti/<bank>.zhenti.json —— { chapter, section, year, rawStem, rawAnswer, source }
 * 供后续转换（真题题目规范化、答案配对）。
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadConfig, listNotebooks, querySql } from './siyuan.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(__dirname, '..', 'out', 'zhenti');

// 笔记本 → bankId + 真题文档章节（探查结果）
const SOURCES = [
  { nb: '古代汉语', bank: 'bank-gudai-hanyu', chapters: ['绪论','工具书简介','古书的标点','词汇','文字（上）','文字（下）','语法（上）','语法（下）','音韵','诗词格律','训诂'] },
  { nb: '现代汉语', bank: 'bank-xiandai-hanyu', chapters: ['绪论','语音','文字','词汇','语法','修辞'] },
  { nb: '中国现代文学史', bank: 'bank-zhongguo-xiandai-wenxue', chapters: ['鲁迅（一）'] },
];

const SECTION_RE = /^(一|二|三|四|五|六|七|八|九|十)、(填空题|判断题|选择题|名词解释|简答题|简答|论述题)/;

export async function extractZhenti(config) {
  fs.mkdirSync(OUT, { recursive: true });
  const nbs = await listNotebooks(config);
  const results = [];

  for (const src of SOURCES) {
    const nb = nbs.find((n) => n.name === src.nb);
    if (!nb) { console.log('跳过（无笔记本）', src.nb); continue; }
    for (const chapter of src.chapters) {
      // 真题文档名：本章真题汇总 / 本单元真题汇总（hpath 含该章名且以真题汇总结尾）
      const rows = await querySql(config, `
        SELECT id, type, content, hpath, sort FROM blocks
        WHERE box = '${nb.id}' AND type = 'd'
          AND hpath LIKE '%${chapter}%'
          AND (hpath LIKE '%真题汇总%' OR hpath LIKE '%单元真题%')
        ORDER BY sort
      `);
      for (const doc of rows) {
        const docBlocks = await querySql(config, `
          SELECT id, type, content, markdown, sort FROM blocks
          WHERE root_id = '${doc.id}' ORDER BY sort
        `);
        const parsed = parseZhentiDoc(docBlocks, src.bank, chapter, doc.hpath);
        results.push(...parsed);
        console.log(`  ${src.bank}·${chapter}: ${parsed.length} 题`);
      }
    }
  }

  const outFile = path.join(OUT, 'all.zhenti.json');
  fs.writeFileSync(outFile, JSON.stringify(results, null, 2), 'utf-8');
  console.log(`\n真题提取完成：${results.length} 题 → ${outFile}`);
}

/** 解析单个真题文档：分节 → 题干/答案配对 */
export function parseZhentiDoc(blocks, bankId, chapter, docPath) {
  const items = []; // {section, year, rawStem, rawAnswer, blockId}
  let currentSection = null;
  let answers = []; // 答案区块（"答案"标题之后的块）
  let inAnswerZone = false;

  for (const b of blocks) {
    const content = (b.content || '').trim();
    const isHeading = b.type === 'h';
    const secMatch = isHeading ? content.match(SECTION_RE) : null;
    if (secMatch) {
      currentSection = secMatch[2];
      continue;
    }
    if (isHeading && /^答案/.test(content)) { inAnswerZone = true; continue; }
    if (isHeading && inAnswerZone) { inAnswerZone = false; } // 新节标题退出答案区
    if (isHeading) continue;

    if (inAnswerZone) {
      answers.push({ content, blockId: b.id });
      continue;
    }
    if (!currentSection) continue;
    // 题干块：带（年份）
    const yearMatch = content.match(/（(\d{2})年）|\((\d{2})年\)/);
    const year = yearMatch ? (yearMatch[1] || yearMatch[2]) : null;
    if (content.length < 4) continue; // 空块
    items.push({
      bankId, chapter, docPath,
      section: currentSection,
      year: year ? `20${year}` : null,
      rawStem: content,
      rawAnswer: null,
      blockId: b.id,
    });
  }

  // 答案配对：按序号顺序，答案区块数 == 该节题干数时按序配；否则存 rawAnswers 列表
  // 简化：把整个答案区按顺序存到同节最后一个题目标记（由转换阶段细化配对）
  const sectionAnswers = {};
  for (const a of answers) {
    // 答案块通常带序号前缀（1. 2.）或直接内容；先按序收集
    sectionAnswers[sectionAnswers.length] = a;
  }
  // 把答案区块按出现顺序贴到题目上（index 对齐该文档内题目顺序）
  // 说明：真题文档题目在前、答案区在后，题目顺序与答案顺序一致（探查确认）
  const qs = items; // 题干（去重节标题后的纯题目块，含填空/判断/选择/名解/简答）
  // 答案区去掉第一个"答案"标签块（已在 inAnswerZone 前跳过），answers 即答案块序列
  const ansList = answers.filter((a) => !/^答案/.test(a.content));
  // 配对：若题目数与答案块数匹配则按序；否则把整段答案区文本附到末题（转换阶段再拆）
  if (ansList.length === qs.length) {
    for (let i = 0; i < qs.length; i++) {
      qs[i].rawAnswer = ansList[i].content;
    }
  } else {
    const allAns = ansList.map((a) => a.content).join('\n');
    if (allAns) qs.forEach((q) => (q.rawAnswer = q.rawAnswer ?? allAns));
  }
  return qs;
}

// CLI
const config = loadConfig();
extractZhenti(config).catch((e) => { console.error(e.message); process.exit(1); });
