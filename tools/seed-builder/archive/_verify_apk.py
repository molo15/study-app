# -*- coding: utf-8 -*-
"""APK 内题库抽样复核：验证关键修复点真实生效。"""
import io, sys, json, os, re, zipfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

APK = r'D:\study_app\app\build\app\outputs\flutter-apk\app-release.apk'
z = zipfile.ZipFile(APK)

def load_bank(apk_bank_name):
    n = 'assets/flutter_assets/assets/banks/' + apk_bank_name
    zz = zipfile.ZipFile(io.BytesIO(z.read(n)))
    qs = []
    for nn in zz.namelist():
        if nn.startswith('questions/') and nn.endswith('.json'):
            qs.extend(json.loads(zz.read(nn)))
    return qs

# 关键修复点抽查
checks = {
    '现代汉语-联绵词': ('bank-xiandai-hanyu-v0.14.0.zip', 'q_000009'),
    '现代汉语-主谓式': ('bank-xiandai-hanyu-v0.14.0.zip', 'z_000109'),
    '现代汉语-展览馆变调': ('bank-xiandai-hanyu-v0.14.0.zip', 'q_000004'),
    '古汉-兼词': ('bank-gudai-hanyu-v0.14.0.zip', 'q_000136'),
    '古汉-康熙字典': ('bank-gudai-hanyu-v0.14.0.zip', 'q_000172'),
    '当代-悲悼散文': ('bank-zhongguo-dangdai-wenxue-v0.14.0.zip', 'b_000318'),
    '现代文学-何其芳': ('bank-zhongguo-xiandai-wenxue-v0.14.0.zip', 'q_000088'),
    '现代文学-田汉': ('bank-zhongguo-xiandai-wenxue-v0.14.0.zip', 'q_000163'),
    '现代文学-左联': ('bank-zhongguo-xiandai-wenxue-v0.14.0.zip', 'q_000142'),
    '现代文学-小剧场': ('bank-zhongguo-xiandai-wenxue-v0.14.0.zip', 'c_000034'),
}
print('=== APK 内题库关键修复点复核 ===')
for label, (bank, suffix) in checks.items():
    qs = load_bank(bank)
    for q in qs:
        if q['id'].endswith(suffix):
            t = q.get('type')
            if t in ('single_choice', 'multi_choice'):
                opts = q.get('options', [])
                ans = q.get('answer')
                if isinstance(ans, list):
                    at = set(ans)
                    ok = [o['key'] for o in opts if o['text'] in at]
                else:
                    ok = [o['key'] for o in opts if o['text'] == ans]
                expl = re.sub(r'\s+', '', q.get('explanation', ''))
                print(f"[{label}] {q['id']} 正确项key={ok} 解析尾={expl[-26:]}")
            else:
                print(f"[{label}] {q['id']} type={t} 解析尾={(re.sub(chr(92)+'s+','',q.get('explanation') or ''))[-30:]}")
            break
