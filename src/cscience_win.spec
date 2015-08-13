# -*- mode: python -*-
a = Analysis(['cscience.py'],
             pathex=['C:\\Users\\Fernando Nobre\\Projects\\CSciBox\\src'],
             hiddenimports=['scipy.special._ufuncs_cxx'],
             hookspath=None,
             runtime_hooks=None)
             
a.binaries += [('_baconc.so', 'cscience/components/cfiles/_baconc.so', 'BINARY')]
             
for d in a.datas:
    if 'pyconfig' in d[0]:
        a.datas.remove(d)
        break
pyz = PYZ(a.pure)
resources_tree = Tree('../resources', prefix='resources')
database_tree = Tree('../mongo_win32', prefix='database')
dump_tree = Tree('../database_dump', prefix='database_dump')
components_tree = Tree('cscience/components', prefix='cscience/components')
cfiles_tree = Tree('cscience/components/cfiles', prefix='cscience/components/cfiles')
backend_tree = Tree('cscience/backends', prefix='cscience/backends')
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          resources_tree,
          database_tree,
          dump_tree,
          components_tree,
          cfiles_tree,
          backend_tree,
          name='cscience.exe',
          debug=False,
          strip=None,
          upx=True,
          console=False )
