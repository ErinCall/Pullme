import subprocess

check_call = subprocess.check_call
Popen = subprocess.Popen
PIPE = subprocess.PIPE

def check_output(*args):
    return_code, output = read_subprocess(*args)
    if return_code == 0:
        return output
    else:
        raise subprocess.CalledProcessError(return_code, args)

def get_output(*args):
    return_code, output = read_subprocess(*args)
    return output

def read_subprocess(*args):
    subp = subprocess.Popen(*args, stdout=subprocess.PIPE)
    return_code = subp.wait()
    return return_code, subp.stdout.read()


