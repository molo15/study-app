/**
 * 真题块流导出：把真题文档的完整块流（type+content+markdown）原样导出，
 * 供转换 agent 按"题干块→加粗答案块顺序配对"解析成题目。
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadConfig, listNotebooks, querySql } from './siyuan.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.join(__dirname, '..', 'out', 'zhenti');

const SOURCES = [
  { nb: '古代汉语', bank: 'bank-gudai-hanyu', chapters: ['绪论','工具书简介','古书的标点','词汇','文字（上）','文字（下）','语法（上）','语法（下）','音韵','诗词格律','训诂'] },
  { nb: '现代汉语', bank: 'bank-xiandai-hanyu', chapters: ['绪论','语音','文字','词汇','语法','修辞'] },
  { nb: '中国现代文学史', bank: 'bank-zhongguo-xiandai-wenxue', chapters: ['鲁迅（一）'] },
];

export async function exportZhenti(config) {
  fs.mkdirSync(OUT, { recursive: true });
  const nbs = await listNotebooks(config);
  const all = [];
  for (const src of SOURCES) {
    const nb = nbs.find((n) => n.name === src.nb);
    if (!nb) continue;
    for (const chapter of src.chapters) {
      // 精确匹配：hpath 以 /<chapter>/ 结尾或含 /<chapter>/xxx 且含 真题汇总
      const docs = await querySql(config, `
        SELECT id, hpath FROM blocks
        WHERE box = '${nb.id}' AND type = 'd'
          AND hpath LIKE '%${chapter}%' AND hpath LIKE '%真题汇总%'
          AND hpath NOT LIKE '%${chapter}%${chapter}%'
        ORDER BY hpath
      `);
      // 去重（同名章可能跨编，取与 chapter 精确匹配的）
      const seen = new Set();
      for (const doc of docs) {
        const h = doc.hpath;
        if (seen.has(h)) continue;
        seen.add(h);
        const blocks = await querySql(config, `
          SELECT type, content, markdown, sort FROM blocks
          WHERE root_id = '${doc.id}' ORDER BY sort
          LIMIT 100000
        `);
        const stream = blocks.map((b) => ({
          t: b.type === 'h' ? 'H' : b.type === 'p' ? 'P' : b.type,
          c: (b.content || '').trim(),
          m: b.markdown || '',
        }));
        all.push({ bank: src.bank, chapter, docPath: h, blocks: stream });
        console.log(`${src.bank}·${chapter}: 块流 ${stream.length} 块`);
      }
    }
  }
  fs.writeFileSync(path.join(OUT, 'zhenti-streams.json'), JSON.stringify(all, null, 1), 'utf-8');
  console.log(`\n导出 ${all.length} 个真题文档块流 → out/zhenti/zhenti-streams.json`);
}

const config = loadConfig();
exportZhenti(config).catch((e) => { console.error(e.message); process.exit(1); });
