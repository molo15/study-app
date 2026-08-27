// Export 现代汉语 课后习题 3 docs to JSON for question bank building
import { loadConfig, listNotebooks, querySql } from './src/siyuan.js';
import { writeFileSync } from 'fs';
import { resolve } from 'path';

const OUT = resolve('./out/zhenti');

const docs = [
  { id: '20260730121545-204k7qp', name: 'shangbian', chapter: '语音' },
  { id: '20260730121548-vogtcyt', name: 'zhongbian', chapter: '词汇' },
  { id: '20260730121548-zb7oxgj', name: 'xiabian', chapter: '修辞' },
];

const c = loadConfig();
for (const d of docs) {
  const b = await querySql(c, `SELECT id, type, content, markdown FROM blocks WHERE root_id='${d.id}' ORDER BY sort`);
  const data = {
    bank: 'bank-xiandai-hanyu',
    chapter: d.chapter,
    docId: d.id,
    blocks: b.map(x => ({ id: x.id, t: x.type, c: x.content || '', m: x.markdown || '' })),
  };
  const file = resolve(OUT, `kehou-${d.name}.json`);
  writeFileSync(file, JSON.stringify(data, null, 1), 'utf8');
  console.log('written', file, b.length, 'blocks');
}
