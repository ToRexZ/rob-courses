import ctypes
import os

dll = ctypes.CDLL(os.path.join('Mikey', 'DLLs', 'MichelangeloComLib.dll'))

print(dll)