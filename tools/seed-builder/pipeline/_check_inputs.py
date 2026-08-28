# -*- coding: utf-8 -*-
import io, sys, os, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
spec = importlib.util.spec_from_file_location('pv', r'D:\study_app\tools\seed-builder\pipeline\pack_v012.py')
pv = importlib.util.module_from_spec(spec)
sys.path.insert(0, r'D:\study_app\tools\seed-builder\pipeline')
spec.loader.exec_module(pv)
for b, (nm, label, rel) in pv.BANKS.items():
    full = os.path.normpath(os.path.join(r'D:\study_app\tools\seed-builder', rel))
    print(('OK ' if os.path.exists(full) else 'MISS'), b,
          (os.path.getsize(full) if os.path.exists(full) else 'NOT FOUND: ' + rel))
