import unittest
from pyDoubles.framework import stub, mock, spy
import pullme
import pullme.git as git_lib
import pullme.subprocess_wrapper as subprocess_lib
import pullme.interaction as interaction_lib

class PullmeTest(unittest.TestCase):
    def setUp(self):
        git_spy = spy(git_lib)
        pullme.git = git_spy
        self.git_spy = git_spy

        subprocess_spy = spy(subprocess_lib)
        pullme.subprocess = subprocess_spy
        self.subprocess_spy = subprocess_spy

        interaction_spy = spy(interaction_lib)
        pullme.interaction = interaction_spy
        self.interaction_spy = interaction_spy

        pullme.exit = lambda x: True
