# PyInstaller spec for EDI LLM offline assistant
# Save as edi_llm_server.spec
# Run: pyinstaller edi_llm_server.spec

block_cipher = None

import os
from PyInstaller.utils.hooks import collect_data_files

# Collect model files from Hugging Face cache
model_cache = os.path.expanduser("~/.cache/huggingface/hub")
model_data = collect_data_files(model_cache)

a = Analysis(
    ['edi_llm_server.py'],
    pathex=[],
    binaries=[],
    datas=model_data,
    hiddenimports=['transformers', 'torch', 'fastapi', 'uvicorn', 'pydantic'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='EDI_LLM_Assistant',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)
