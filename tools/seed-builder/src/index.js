/**
 * seed-builder 入口（开发期工具链）
 *
 * 用法：
 *   node src/index.js explore [notebookId]   # 探查某笔记本：块类型统计 + 标题树 + 素材抽样
 *   node src/index.js plan                   # 为全部学习笔记本生成题库骨架（out/*.skeleton.json）
 *   node src/index.js gen                    # （预留）AI 生成题目——待接入 LLM
 */
import { loadConfig, listNotebooks } from './siyuan.js';
import { extractBlocks, extractHeadings, blockTypeStats } from './extract.js';
import { buildSkeleton, saveSkeleton, saveMaterials } from './skeleton.js';

const config = loadConfig();

/** 学习笔记本（用户确定范围：三本文学史 + 两本语言学；考研英语不出题） */
const STUDY_NOTEBOOKS = [
  '古代汉语',
  '现代汉语',
  '中国古代文学史',
  '中国现代文学史',
  '中国当代文学史',
];

async function cmdExplore(notebookName) {
  const notebooks = await listNotebooks(config);
  const nb = notebookName
    ? notebooks.find((n) => n.name.includes(notebookName))
    : notebooks[0];
  if (!nb) throw new Error(`笔记本未找到: ${notebookName ?? '(第一个)'}`);
  console.log(`\n=== 笔记本: ${nb.name} (${nb.id}) ===`);

  console.log('\n[块类型统计]');
  const stats = await blockTypeStats(config, nb.id);
  for (const s of stats) {
    console.log(`  ${s.type}: ${s.cnt} 块, 总长 ${s.total_len ?? 0}`);
  }

  console.log('\n[标题树（前 30）]');
  const headings = await extractHeadings(config, nb.id, 30);
  for (const h of headings) {
    console.log(`  ${h.hpath} | ${(h.content || '').slice(0, 40)}`);
  }

  console.log('\n[素材抽样（每章前 3 块）]');
  const blocks = await extractBlocks(config, { notebook: nb.id, limit: 100 });
  const byChapter = new Map();
  for (const b of blocks) {
    const parts = (b.hpath || '').split('/').filter(Boolean);
    const ch = parts[1] || parts[0] || '未分类';
    if (!byChapter.has(ch)) byChapter.set(ch, []);
    if (byChapter.get(ch).length < 3) byChapter.get(ch).push(b);
  }
  for (const [ch, items] of byChapter) {
    console.log(`\n  — ${ch} —`);
    for (const it of items) {
      console.log(`    [${it.type}] ${(it.content || '').slice(0, 80)}`);
    }
  }
}

async function cmdPlan() {
  const notebooks = await listNotebooks(config);
  for (const target of STUDY_NOTEBOOKS) {
    const nb = notebooks.find((n) => n.name === target);
    if (!nb) {
      console.log(`跳过（笔记本不存在）: ${target}`);
      continue;
    }
    console.log(`\n生成骨架: ${nb.name}...`);
    const blocks = await extractBlocks(config, { notebook: nb.id, limit: 2000 });
    const bankId = `bank-${nb.name.replace(/[^\u4e00-\u9fa5a-zA-Z0-9]/g, '').toLowerCase()}`;
    const skeleton = buildSkeleton(
      { bankId, name: `考研·${nb.name}`, version: '0.1.0' },
      blocks,
    );
    const file = saveSkeleton(skeleton, { markdown: true });
    // 导出完整素材（含全文，供 AI/agent 出题）
    const blocksById = Object.fromEntries(blocks.map((b) => [b.id, b]));
    const mfile = saveMaterials(skeleton, blocksById);
    console.log(`  → ${skeleton.skeleton.totalBlocks} 块素材, ${skeleton.chapters.length} 章节`);
    console.log(`  → ${file}`);
    console.log(`  → ${mfile}`);
  }
  console.log('\n骨架生成完成（gen 阶段待接入 AI 生成题目）');
}

async function cmdGen() {
  console.log('gen 阶段：预留——将素材块喂给 LLM 生成题目（JSON Schema 校验 + 人工审核）');
  console.log('当前骨架已产出到 out/*.skeleton.json，请先 review 章节规划再接入 AI。');
}

const [cmd, arg] = process.argv.slice(2);
const handlers = { explore: cmdExplore, plan: cmdPlan, gen: cmdGen };
const handler = handlers[cmd];
if (!handler) {
  console.log('用法: node src/index.js <explore|plan|gen> [notebookId]');
  process.exit(1);
}
handler(arg).catch((e) => {
  console.error('错误:', e.message);
  process.exit(1);
});
