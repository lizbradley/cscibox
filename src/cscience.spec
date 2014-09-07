# -*- mode: python -*-
a = Analysis(['cscience.py'],
             pathex=['/Users/fernando/Projects/CScience/src'],
             hiddenimports=['scipy.special._ufuncs_cxx'],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
resources_tree = Tree('../resources', prefix='resources')
database_tree = Tree('../database', prefix='database')
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          resources_tree,
          database_tree,
          name='cscience',
          debug=False,
          strip=None,
          upx=True,
          console=False )
app = BUNDLE(exe,
             name='cscience.app',
             icon=None)
