/**
 * 思源笔记内核 API 客户端（开发期工具链）
 * - 直连 http://127.0.0.1:6806，鉴权头 Authorization: Token <token>
 * - 全部接口 POST + JSON
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export function loadConfig() {
  const configPath = path.join(__dirname, '..', 'config.json');
  if (fs.existsSync(configPath)) {
    return JSON.parse(fs.readFileSync(configPath, 'utf-8'));
  }
  // 默认值（与思源默认一致）
  return {
    siyuanApiUrl: process.env.SIYUAN_API_URL || 'http://127.0.0.1:6806',
    siyuanToken: process.env.SIYUAN_API_TOKEN || '',
  };
}

export async function api(config, endpoint, payload = {}) {
  const url = `${config.siyuanApiUrl}${endpoint}`;
  const resp = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(config.siyuanToken ? { Authorization: `Token ${config.siyuanToken}` } : {}),
    },
    body: JSON.stringify(payload),
  });
  const text = await resp.text();
  let data;
  try {
    data = text ? JSON.parse(text) : {};
  } catch {
    throw new Error(`思源 API ${endpoint} 返回非 JSON: ${text.slice(0, 200)}`);
  }
  if (!resp.ok || data.code !== 0) {
    throw new Error(`思源 API ${endpoint} 失败: HTTP ${resp.status}, code ${data.code}, msg ${data.msg || ''}`);
  }
  return data.data;
}

/** 列出所有笔记本 */
export async function listNotebooks(config) {
  const data = await api(config, '/api/notebook/lsNotebooks', {});
  return data.notebooks || [];
}

/** 执行只读 SQL（查 blocks 表） */
export async function querySql(config, stmt) {
  return await api(config, '/api/query/sql', { stmt });
}

/** 取笔记本文档树（返回 {doc, subFile} 结构，含子文档递归） */
export async function getDocByPath(config, notebook, path = '/') {
  return await api(config, '/api/filetree/getDocByPath', { notebook, path });
}
