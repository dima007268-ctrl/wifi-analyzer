from _ctypes import CFuncPtr, FUNCFLAG_STDCALL, LoadLibrary, _SimpleCData

LOAD_LIBRARY_SEARCH_DEFAULT_DIRS = 0x00001000

class c_int(_SimpleCData):
	_type_ = "i"

class MyWinDll:
	def __init__(self, name):
		class _FuncPtr(CFuncPtr):
			_flags_= FUNCFLAG_STDCALL
			_restype_= c_int

		self._FuncPtr = _FuncPtr
		self._name = name
		self._handle = LoadLibrary(name, LOAD_LIBRARY_SEARCH_DEFAULT_DIRS)

	def __getattr__(self, name):
		if name.startswith("__") and name.endswith("__"):
			raise AttributeError(name)
		func = self._FuncPtr((name, self))
		func.__name__ = name
		setattr(self, name, func)
		return func



class LibraryLoader(object):
	def __init__(self, dlltype):
		self._dlltype = dlltype

	def __getattr__(self,name):
		if name[0] == '_':
			raise AttributeError(name)
		try:
			dll = self._dlltype(name)
		except OSError:
			raise AttributeError(name)
		setattr(self, name , dll)
		return dll

my_windll = LibraryLoader(MyWinDll)

if __name__ == "__main__":
	kernel32 = my_windll.kernel32
	print("Библиотека:", kernel32._name, kernel32._handle)
	print("Функция:", kernel32.GetTickCount64)
	print("Миллисекунд с включения", kernel32.GetTickCount64())
	kernel32.Beep(750,300)