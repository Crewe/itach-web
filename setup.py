from setuptools import setup, find_packages

VERSION = '0.0.1' 
DESCRIPTION = 'iTachWeb: a stand-alone package for managing Global Caché iTach devices.'
LONG_DESCRIPTION = 'iTachWeb: a stand-alone package for managing Global Caché iTach devices.'

# Setting up
setup(
        name="itachweb", 
        version=VERSION,
        author="Ryan Edwards-Crewe",
        author_email="qtc@ve3dxv.ca",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=['black==24.3.0',
                          'fastapi==0.110.1',
                          'uvicorn==0.29.0',
                          'pyyaml==6.0.1',
                          'build==1.2.1',],
        keywords=['python', 'itach', 'webUI', 'webAPI'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Education",
            "Programming Language :: Python :: 3",
            #"Operating System :: MacOS :: MacOS X",
            #"Operating System :: Microsoft :: Windows",
        ]
)