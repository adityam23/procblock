from cx_Freeze import setup, Executable
import os.path

PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')

include_files = [os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll'),
		 os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll'),
		 ]

setup(
    name='ProcBlock',
    description='Process Blocker',
    version='1.0',
    options={'build_exe': {'include_files': include_files}},
    executables=[Executable('my_ui.py', 
			    targetName='ProcessBlocker.exe',  
			    copyright='Copyright (C) Aditya Menon 2019', 
			    base='Win32GUI')]
)