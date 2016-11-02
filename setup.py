from setuptools import setup
setup(name='CSciBox',
        version='0.11.1',
        packages = ['cscience', 
            'cscience.framework',
            'cscience.framework.samples',
            'cscience.GUI',
            'cscience.GUI.Editors',
            'cscience.GUI.graph',
            'cscience.GUI.io',
            'cscience.components',
            'cscience.components.cfiles',
            'cscience.backends',
            'calvin',
            'calvin.reasoning',
            'images'
            ],
        py_modules = ['cscibox','config','dbconversion'],
        install_requires = [
            "quantities>=0.11.1",
            "bagit>=1.5.4",
            ]
        package_dir = {'' : 'src'},
        entry_points={ "gui_scripts": [ "cscibox = cscibox:main", ] },
        include_package_data=True,
        )
