import unittest
from pyDoubles.framework import spy, mock, when
import pullme
import pullme.git as git_lib
import pullme.subprocess_wrapper as subprocess_lib
import pullme.interaction as interaction_lib
import getpass as getpass_lib
import optparse as optparse_lib
import subprocess as sys_subprocess

class PullmeTest(unittest.TestCase):
    default_settings = {
        'password': 'swordfish',
        'upstream': 'origin',
        'personal': 'alorente',
        'assume': False,
        'file': None,
        'issue': None,
        'open': False,
    }
    def setUp(self):
        git_spy = spy(git_lib)
        when(git_spy.log_with_ref_names).then_return(FakeReadableLog())
        when(git_spy.remotes).then_return([
            'buckles  git@github.com:somebuckley/audience.git (fetch)',
            'origin  git@github.com:andrewlorente/audience.git (fetch)'])
        when(git_spy.commits_since).then_return([
            '6bd5f07 stub out everything that interacts with the user',
            '4bd32e0 Tests for the check_outstanding_changes method',
            '0d4eada guard against a "referenced before assignment"',
            '5a340e8 Test that critical find-a-branch regex'])
        pullme.git = git_spy
        self.git_spy = git_spy

        subprocess_spy = spy(subprocess_lib)
        pullme.subprocess = subprocess_spy
        self.subprocess_spy = subprocess_spy

        interaction_spy = spy(interaction_lib)
        pullme.interaction = interaction_spy
        self.interaction_spy = interaction_spy

        pullme.exit = lambda x: True

        pullme.edit_file = lambda x: None

        pullme.read_description_from_file = lambda x: ('foo', 'bar')

        pullme.urllib2.urlopen = lambda x: FakeApiResponse()

        pullme.load_settings = lambda: self.default_settings

class FakeFile(object):
    lines = iter([
        '(HEAD, refs/remotes/origin/testing, refs/heads/testing)',
        '',
        '(refs/tags/v-2.0.1, refs/remotes/origin/master, refs/remotes/origin/HEAD)',
        '(refs/tags/v-2.0.0)',
    ])

    def readline(self):
        return self.lines.next()

    def close(self):
        return True

class FakeReadableLog(object):
    def poll(self):
        return None
    stdout = FakeFile()

class FakeApiResponse(object):
    def read(self):
        return """
            {
                "number": 24,
                "html_url": "http://example.com/robots/24"
            }
        """
