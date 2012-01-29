from tests import PullmeTest
from nose.tools import eq_
import pullme
# We have a line that looks something like this:
#
# (refs/remotes/origin/devel, refs/remotes/alorente/devel)
# (refs/remotes/origin/master)
#
# Git's rules on legal ref names are somewhat laxer than we might hope here.
# the name-terminating tokens, parens and commas, are both legal within names.
# This forces us into a rather awkward regex. So it goes...

class OutstandingChanges(PullmeTest):
    def test_returns_none_on_none(self):
        eq_(pullme.extract_branch_name(None, 'origin'),
            None)

    def test_returns_none_on_empty_string(self):
        eq_(pullme.extract_branch_name('', 'origin'),
            None)

    def test_find_branch_name_in_the_easy_case(self):
        ref_lines = [
            '(refs/remotes/origin/master)',
            '(refs/remotes/origin/master, refs/remotes/rontoms/master)',
            '(refs/remotes/origin/master, refs/remotes/origin/HEAD)',
            '(refs/remotes/origin/master, robat)',
        ]
        for ref_line in ref_lines:
            branch_name = pullme.extract_branch_name(ref_line, 'origin')
            eq_(branch_name,
                'master',
                "failed on '%s': got %s" % (ref_line, branch_name))

    def test_find_branch_name_with_a_comma_in_it(self):
        pairs = [
            ('(refs/remotes/origin/master,)', 'master,', ),
            ('(refs/remotes/origin/ma,ster,)', 'ma,ster,', ),
            ('(refs/remotes/origin/master,, refs/remotes/rontoms/master)',
                                                                'master,', ),
        ]
        for ref_line, expected in pairs:
            branch_name = pullme.extract_branch_name(ref_line, 'origin')
            eq_(branch_name, expected,
                "failed on '%s': expected '%s', got '%s'" %
                        (ref_line, branch_name, expected))

    def test_find_branch_name_with_a_paren_in_it(self):
        pairs = [
            ('(refs/remotes/origin/master))', 'master)', ),
            ('(refs/remotes/origin/ma)ster))', 'ma)ster)', ),
            ('(refs/remotes/origin/master), refs/remotes/rontoms/master)',
                                                                'master)', ),
        ]
        for ref_line, expected in pairs:
            branch_name = pullme.extract_branch_name(ref_line, 'origin')
            eq_(branch_name, expected,
                "failed on '%s': expected '%s', got '%s'" %
                        (ref_line, branch_name, expected))

class MultipleBranches(PullmeTest):
    def test_returns_false_on_none(self):
        assert not pullme.has_multiple_branches(None, 'origin')

    def test_returns_false_on_empty_string(self):
        assert not pullme.has_multiple_branches('', 'origin')

    def test_ignores_remote_head(self):
        assert not pullme.has_multiple_branches(
                '(refs/remotes/origin/master, refs/remotes/origin/HEAD)',
                'origin')

    def test_finds_multiple_remotes(self):
        assert pullme.has_multiple_branches(
                '(refs/remotes/origin/master, refs/remotes/origin/devel)',
                'origin')

    def test_same_branch_on_multiple_remotes(self):
        assert not pullme.has_multiple_branches(
                '(refs/remotes/origin/master, refs/remotes/upstream/master)',
                'origin')

    def test_one_branch_on_one_remote(self):
        assert not pullme.has_multiple_branches(
                '(refs/remotes/origin/master)',
                'origin')
