/**
 * 题库骨架产出：把提取的素材组织成「题库包骨架」
 *
 * 骨架 = manifest 雏形 + 章节候选 + 素材清单（每块标注 hpath → 章节目）
 * 供结构规划使用；后续 gen 阶段把素材喂给 AI 生成题目并填充 questions。
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
export const OUT_DIR = path.join(__dirname, '..', 'out');

export function ensureOutDir() {
  if (!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR, { recursive: true });
}

/** 从素材块的 hpath 推导章节（取第一级/第二级路径段作为章） */
export function deriveChapter(hpath, { level = 1 } = {}) {
  if (!hpath) return '未分类';
  const parts = hpath.split('/').filter((p) => p.trim().length > 0);
  if (parts.length === 0) return '未分类';
  const idx = Math.min(level, parts.length - 1);
  return parts[idx] || parts[0] || '未分类';
}

/** 素材按章节聚合，产出骨架对象 */
export function buildSkeleton(bankMeta, blocks, { chapterLevel = 1 } = {}) {
  const chapters = new Map(); // chapter -> { blocks: [], ids: [] }
  const material = [];

  for (const b of blocks) {
    const chapter = deriveChapter(b.hpath, { level: chapterLevel });
    if (!chapters.has(chapter)) chapters.set(chapter, { count: 0, ids: [] });
    const c = chapters.get(chapter);
    c.count++;
    c.ids.push(b.id);
    material.push({
      id: b.id,
      docPath: b.hpath,
      chapter,
      type: b.type,
      length: b.length,
      preview: (b.content || '').slice(0, 120),
      blockId: b.id, // 出题后 source.blockId 可追溯
    });
  }

  const chapterList = [...chapters.keys()].sort();
  return {
    formatVersion: 2,
    bankId: bankMeta.bankId,
    name: bankMeta.name,
    version: bankMeta.version || '0.1.0',
    chapters: chapterList,
    mockPapers: [], // 规划后填充（gen 阶段）
    skeleton: {
      totalBlocks: material.length,
      chapterStats: chapterList.map((ch) => ({
        chapter: ch,
        count: chapters.get(ch).count,
        blockIds: chapters.get(ch).ids,
      })),
    },
    material, // 素材清单（供 AI 生成用，可含每块的完整 markdown）
    questions: [], // gen 阶段填充
  };
}

/** 保存骨架到 out/ */
export function saveSkeleton(skeleton, { markdown = false } = {}) {
  ensureOutDir();
  const base = path.join(OUT_DIR, skeleton.bankId);
  fs.writeFileSync(`${base}.skeleton.json`, JSON.stringify(skeleton, null, 2), 'utf-8');
  if (markdown) {
    const md = [
      `# ${skeleton.name}（题库骨架）`,
      `bankId: ${skeleton.bankId} · v${skeleton.version}`,
      `素材块总数: ${skeleton.skeleton.totalBlocks}`,
      '',
      '## 章节',
      ...skeleton.chapters.map((ch, i) => {
        const st = skeleton.skeleton.chapterStats.find((s) => s.chapter === ch);
        return `${i + 1}. **${ch}**（${st.count} 块）`;
      }),
      '',
      '## 素材样例（每章前 3 块）',
      ...skeleton.chapters.flatMap((ch) => {
        const st = skeleton.skeleton.chapterStats.find((s) => s.chapter === ch);
        const samples = skeleton.material.filter((m) => m.chapter === ch).slice(0, 3);
        return [
          `### ${ch}`,
          ...samples.map((m) => `- [${m.id}] ${m.preview}...`),
        ];
      }),
    ].join('\n');
    fs.writeFileSync(`${base}.skeleton.md`, md, 'utf-8');
  }
  return `${base}.skeleton.json`;
}

/** 导出完整素材（含全文 markdown，供 AI/agent 出题）——out/<bankId>.materials.json */
export function saveMaterials(skeleton, blocksById) {
  ensureOutDir();
  const base = path.join(OUT_DIR, skeleton.bankId);
  const materials = skeleton.material.map((m) => ({
    ...m,
    content: blocksById[m.id]?.content ?? '',
    markdown: blocksById[m.id]?.markdown ?? '',
  }));
  fs.writeFileSync(`${base}.materials.json`, JSON.stringify({
    bankId: skeleton.bankId,
    name: skeleton.name,
    chapters: skeleton.chapters,
    materials,
  }, null, 2), 'utf-8');
  return `${base}.materials.json`;
}
