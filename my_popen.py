import _winapi
import msvcrt

PIPE = -1


class StartupInfo:
	def __init__(self):
		self.dwFlags = 0
		self.hStdInput = None
		self.hStdOutput = None
		self.hStdError = None
		self.wShowWindow = 0
		self.lpAttributeList = {"handle_list": []}
 

class MyPopen:
	def __init__(self, args, stdin = None, stdout = None , stderr = None, encoding = None):

		self.args = args
		self.encoding = encoding

		(p2cread, p2cwrite,
		c2pread, c2pwrite,
		errread, errwrite) = self._get_handles(stdin, stdout, stderr)

		self._c2pread = c2pread
		self._errread = errread

		self._execute_child(args, p2cread, c2pwrite, errwrite)


	def _get_handles(self, stdin , stdout , stderr):
		if stdin is None and stdout is None and stderr is None:
			return(-1, -1, -1, -1, -1, -1 )

		p2cread, p2cwrite = -1, -1 
		c2pread, c2pwrite = -1, -1
		errread, errwrite = -1, -1

		if stdin is None:
			p2cread = _winapi.GetStdHandle(_winapi.STD_INPUT_HANDLE)
			if p2cread is None:
				p2cread, _ = _winapi.CreatePipe(None, 0)
				_winapi.CloseHandle(_)
		elif stdin == PIPE:
			p2cread, p2cwrite = _winapi.CreatePipe(None, 0)
		original = p2cread
		p2cread = self._make_inheritable(p2cread)
		if stdin == PIPE:
			_winapi.CloseHandle(original)


		if stdout is None:
			c2pwrite = _winapi.GetStdHandle(_winapi.STD_OUTPUT_HANDLE)
			if c2pwrite is None:
				_, c2pwrite = _winapi.CreatePipe(None, 0)
				_winapi.CloseHandle(_)
		elif stdout == PIPE:
			c2pread , c2pwrite = _winapi.CreatePipe(None,0)
		original = c2pwrite
		c2pwrite = self._make_inheritable(c2pwrite)
		if stdout == PIPE:
			_winapi.CloseHandle(original)


		if stderr is None:
			errwrite = _winapi.GetStdHandle(_winapi.STD_ERROR_HANDLE)
			if errwrite is None:
				_, errwrite = _winapi.CreatePipe(None, 0)
				_winapi.CloseHandle(_)
		elif stderr == PIPE:
			errread, errwrite = _winapi.CreatePipe(None, 0)
		original = errwrite
		errwrite = self._make_inheritable(errwrite)
		if stderr == PIPE:
			_winapi.CloseHandle(original)



		return(p2cread , p2cwrite, c2pread, c2pwrite, errread, errwrite)

	def _make_inheritable(self , handle):
		h = _winapi.DuplicateHandle(
			_winapi.GetCurrentProcess(), handle,
			_winapi.GetCurrentProcess(), 0, True,
			_winapi.DUPLICATE_SAME_ACCESS)
		return h

	def _execute_child(self, args, p2cread, c2pwrite,errwrite):
		cmdline = " ".join(args)

		startupinfo = StartupInfo()
		if - 1 not in (p2cread, c2pwrite, errwrite):

			startupinfo.dwFlags = _winapi.STARTF_USESTDHANDLES
			startupinfo.hStdInput = p2cread
			startupinfo.hStdOutput = c2pwrite
			startupinfo.hStdError = errwrite

		hp, ht, pid, tid = _winapi.CreateProcess(
			None, cmdline, None, None, True, 0, None, None, startupinfo) # pyright: ignore

		_winapi.CloseHandle(p2cread)
		_winapi.CloseHandle(c2pwrite)
		_winapi.CloseHandle(errwrite)

		self._handle = hp
		self.pid = pid
		_winapi.CloseHandle(ht)

	def communicate(self, input = None):
		fd = msvcrt.open_osfhandle(self._c2pread, 0)
		with open(fd, "rb") as f:
			stdout = f.read()
		fd = msvcrt.open_osfhandle(self._errread, 0)
		with open (fd, "rb") as f:
			stderr = f.read()

		_winapi.WaitForSingleObject(self._handle,_winapi.INFINITE)

		out = stdout.decode(self.encoding).replace("\r\n", "\n")  # pyright: ignore
		err = stderr.decode(self.encoding).replace("\r\n", "\n")  # pyright: ignore
		
		return out, err

	def poll(self):
		return _winapi.GetExitCodeProcess(self._handle)


	def __enter__(self):
		return self

	def __exit__(self, exc_type, value, traceback):
		_winapi.CloseHandle(self._handle)







