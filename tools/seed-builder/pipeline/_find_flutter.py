# -*- coding: utf-8 -*-
import io, sys, os, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print('=== 当前进程 PATH 中的 flutter 候选 ===')
for p in os.environ.get('PATH', '').split(';'):
    if 'flutter' in p.lower():
        print('  PATH:', p)

print('=== 用户/机器 PATH ===')
import winreg
for scope, hive, key in [('USER', winreg.HKEY_CURRENT_USER, r'Environment'),
                         ('MACHINE', winreg.HKEY_LOCAL_MACHINE, r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment')]:
    try:
        with winreg.OpenKey(hive, key) as k:
            val, _ = winreg.QueryValueEx(k, 'Path')
            for p in val.split(';'):
                if 'flutter' in p.lower():
                    print('  {} PATH: {}'.format(scope, p))
    except Exception as e:
        print('  {}: {}'.format(scope, e))

print('=== 常见安装位置 ===')
for pat in [r'C:\flutter\bin\flutter.bat', r'C:\src\flutter\bin\flutter.bat',
            r'D:\flutter\bin\flutter.bat', r'C:\tools\flutter\bin\flutter.bat',
            r'C:\Program Files\flutter\bin\flutter.bat',
            r'C:\Users\*\flutter\bin\flutter.bat',
            r'C:\Users\*\*\flutter\bin\flutter.bat']:
    for f in glob.glob(pat):
        print('  FOUND:', f)

print('=== where flutter（当前 PATH）===')
# 用 cmd where 可靠一点
import subprocess
r = subprocess.run('where flutter', shell=True, capture_output=True, text=True)
print(r.stdout or r.stderr)
