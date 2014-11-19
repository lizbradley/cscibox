# -*- mode: python -*-
a = Analysis(['cscience.py'],
             pathex=['C:\\Users\\Fernando Nobre\\Documents\\CScience\\src'],
             hiddenimports=['scipy.special._ufuncs_cxx'],
             hookspath=None,
             runtime_hooks=None)
for d in a.datas:
    if 'pyconfig' in d[0]: 
        a.datas.remove(d)
        break
pyz = PYZ(a.pure)
resources_tree = Tree('../resources', prefix='resources')
database_tree = Tree('../database_win32', prefix='database')
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          resources_tree,
          database_tree,
          name='cscience.exe',
          debug=False,
          strip=None,
          upx=True,
          console=False )
