from pullme.subprocess_wrapper import Subprocess as subprocess

class Git(object):
    @classmethod
    def has_outstanding_changes(cls):
        return bool(subprocess.check_output(['git', 'status', '--porcelain' ]))

    @classmethod
    def show_outstanding_changes(cls):
        subprocess.check_call(['git', 'status', '--short'])

    @classmethod
    def config(cls, key):
        command = ['git', 'config', 'pullme.%s' % key]
        return subprocess.get_output(command).strip()

    @classmethod
    def current_branch(cls):
        return subprocess.check_output([
            'git',
            'name-rev',
            '--name-only',
            'HEAD',
        ]).rstrip()

    @classmethod
    def push_to_personal(cls, remote, branch):
        command = ['git', 'push', remote, 'HEAD:%s' % branch]
        return subprocess.check_call(command)

    @classmethod
    def remotes(cls):
        return subprocess.check_output(['git', 'remote', '-v']).split('\n')

    @classmethod
    def commits_since(cls, start_ref):
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

    @classmethod
    def latest_commit_message(cls):
        return subprocess.check_output(['git', 'log', '-1', '--pretty=format:%B'])

    @classmethod
    def log_with_ref_names(cls):
    # format:%d will show us all ref names for a commit.
    # decorate=full ensures that we get refs/remotes in front of upstream,
    # insulating us from local branches that happen to have 'upstream' in the name.
        command = "git log --decorate=full --pretty=format:%d"
        return subprocess.Popen(
            [command],
            shell=True,
            stdout=subprocess.PIPE,
        )
