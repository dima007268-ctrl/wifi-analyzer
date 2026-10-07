from my_popen import MyPopen, PIPE


class CompletedProcess:
    def __init__(self, args, returncode, stdout=None, stderr=None):
        self.args = args
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

class CalledProcessError(Exception):
    def __init__(self , returncode, cmd , output , stderr = None):
        self.returncode = returncode
        self.cmd = cmd 
        self.output = output
        self.stderr = stderr

    def __str__(self):
        return f"Команда {self.cmd} завершилась с кодом {self.returncode}"


def my_run(*popenargs, input=None, capture_output=False, timeout=None, check=False, **kwargs): # передает параметры сюда 

    if input is not None: #вводимые данные попадаюст сюда, проверяет на правильность и дает тунель
        if kwargs.get('stdin') is not None:
            raise ValueError('stdin and input arguments may not both be used.')
        kwargs['stdin'] = PIPE

    if capture_output: # ввыводит данные или выдает ошибку 
        if kwargs.get('stdout') is not None or kwargs.get('stderr') is not None:
            raise ValueError('stdout and stderr arguments may not be used with capture_output')
        kwargs['stdout'] = PIPE
        kwargs['stderr'] = PIPE

    with MyPopen(*popenargs , **kwargs) as process:
            stdout,stderr = process.communicate(input)
            retcode = process.poll()
            if check and retcode:
                raise CalledProcessError(retcode , process.args, output = stdout , stderr = stderr)
    return CompletedProcess(process.args, retcode, stdout, stderr)

