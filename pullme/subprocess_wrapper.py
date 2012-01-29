import subprocess

class Subprocess(object):
    PIPE = subprocess.PIPE

    @classmethod
    def check_call(cls, *args, **kwargs):
        return subprocess.check_call(*args, **kwargs)

    @classmethod
    def Popen(cls, *args, **kwargs):
        return subprocess.Popen(*args, **kwargs)

    @classmethod
    def check_output(cls, *args, **kwargs):
        if hasattr(subprocess, 'check_output'):
            return subprocess.check_output(*args, **kwargs)

        # subprocess.check_output is not available in python 2.6
        return_code, output = cls.read_subprocess(*args)
        if return_code == 0:
            return output
        else:
            raise subprocess.CalledProcessError(return_code, args)

    @classmethod
    def get_output(cls, *args):
        return_code, output = cls.read_subprocess(*args)
        return output

    @classmethod
    def read_subprocess(cls, *args):
        subp = subprocess.Popen(*args, stdout=subprocess.PIPE)
        return_code = subp.wait()
        return return_code, subp.stdout.read()


