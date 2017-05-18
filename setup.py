from distutils.core import setup
import py2exe
import sys
import glob

sys.argv.append("py2exe")

py2exe_options = {"includes": ["decimal","sip","matplotlib.backends","dateutil", "matplotlib.figure","pylab","numpy","matplotlib.backends.backend_tkagg"],
            "excludes":["_gtkagg", "_tkagg", "_agg2", "_cairo", "_cocoaagg","_fltkagg","_gtk", "_gtkcairo",],
            "dll_excludes":["MSVCP90.dll","libiomp5md.dll",'libgdk-win32-2.0-0.dll', 'libgobject-2.0-0.dll'],
            "compressed": 1,"optimize": 2,"ascii": 0}

data_files= [
(r'cascades',glob.glob(r'.\cascades\*.*')),
(r'Temp',glob.glob(r'.\Temp\*.*')),
(r'image',glob.glob(r'.\image\*.*')),
(r'sys\img',glob.glob(r'.\sys\img\*.*')),
(r'imageformats',glob.glob(r'.\imageformats\*.*')),
(r'mpl-data',glob.glob(r'C:\Python27\Lib\site-packages\matplotlib\mpl-data\*.*')),
(r'mpl-data',[r'C:\Python27\Lib\site-packages\matplotlib\mpl-data\matplotlibrc']),
(r'mpl-data\stylelib',glob.glob(r'C:\Python27\Lib\site-packages\matplotlib\mpl-data\stylelib\*.*')),
(r'mpl-data\images',glob.glob(r'C:\Python27\Lib\site-packages\matplotlib\mpl-data\images\*.*')),
(r'mpl-data\fonts',glob.glob(r'C:\Python27\Lib\site-packages\matplotlib\mpl-data\fonts\*.*'))
]

setup(name = "GLAHF",
      version = "0.8.1",
      windows=["main.py"],
      zipfile = None,
      options={"py2exe":py2exe_options},
      data_files=data_files
      )
