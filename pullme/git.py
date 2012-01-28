import pullme.subprocess_wrapper as subprocess

def has_outstanding_changes():
    return bool(subprocess.check_output(['git', 'status', '--porcelain' ]))

def show_outstanding_changes():
    subprocess.check_call(['git', 'status', '--short'])

def config(key):
    command = ['git', 'config', 'pullme.%s' % key]
    return subprocess.get_output(command).strip()

def current_branch():
    return subprocess.check_output([
        'git',
        'name-rev',
        '--name-only',
        'HEAD',
    ]).rstrip()

def push_to_personal(remote, branch):
    command = ['git', 'push', remote, 'HEAD:%s' % branch]
    return subprocess.check_call(command)

def remotes():
    return subprocess.check_output(['git', 'remote', '-v']).split('\n')

def commits_since(start_ref):
    status = subprocess.Popen(
        [
            'git',
            'log',
            '--oneline',
            '--reverse',
            '%s..' % start_ref
        ],
        stdout=subprocess.PIPE
    )
    return [ line for line in status.stdout ]

def latest_commit_message():
    return subprocess.check_output(['git', 'log', '-1', '--pretty=format:%B'])

def log_with_ref_names():
# format:%d will show us all ref names for a commit.
# decorate=full ensures that we get refs/remotes in front of upstream,
# insulating us from local branches that happen to have 'upstream' in the name.
    command = "git log --decorate=full --pretty=format:%d"
    return subprocess.Popen(
        [command],
        shell=True,
        stdout=subprocess.PIPE,
    )
