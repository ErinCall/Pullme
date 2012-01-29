from tests import PullmeTest
from pyDoubles.framework import assert_that_method, when
import pullme

class OutstandingChanges(PullmeTest):
    standard_settings = {'assume': False}

    def test_checks_for_outstanding_changes(self):
        pullme.check_outstanding_changes(self.standard_settings)
        assert_that_method(self.git_spy.
                           has_outstanding_changes).was_called()
        assert_that_method(self.interaction_spy.
                           confirm_continue).was_never_called()

    def test_does_nothing_when_assuming(self):
        pullme.check_outstanding_changes({'assume': True})
        assert_that_method(self.git_spy.
                           has_outstanding_changes).was_never_called()
        assert_that_method(self.git_spy.
                           show_outstanding_changes).was_never_called()
        assert_that_method(self.interaction_spy.
                           confirm_continue).was_never_called()

    def test_shows_outstanding_changes_if_there_are_any(self):
        when(self.git_spy.has_outstanding_changes).then_return(True)
        pullme.check_outstanding_changes(self.standard_settings)
        assert_that_method(self.git_spy.
                           show_outstanding_changes).was_called()

    def test_asks_for_guidance_if_there_are_changes(self):
        when(self.git_spy.has_outstanding_changes).then_return(True)
        pullme.check_outstanding_changes(self.standard_settings)
        assert_that_method(self.interaction_spy.
                           confirm_continue).was_called(). \
                           with_args(self.standard_settings,
                                     'There are outstanding changes.')

