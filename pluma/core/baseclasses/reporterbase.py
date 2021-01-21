
import datetime
from abc import ABC
from typing import Optional, Sequence
from pluma.test.testbase import TestBase

# TODO: The session parameter should be an instance of a metadata class (such as Session, which
# is currently WIP) instead of a TestBase iterable.
# TODO: the result_pass and result_message should be collected into a result object. This result
# object should also include other possible states for the test (ignored, skipped, etc.)
# TODO: Should there be a session_result paramter in report_session_end?


class ReporterBase(ABC):
    def report_session_start(self, time: datetime.datetime, session: Sequence[TestBase]) -> None:
        """Report the start of a testing session"""
        pass

    def report_session_end(self, time: datetime.datetime, session: Sequence[TestBase]) -> None:
        """Report the end of a testing session"""
        pass

    def report_test_start(self, time: datetime.datetime, session: Sequence[TestBase], test: TestBase) -> None:
        """Report the start of a single test"""
        pass

    def report_test_end(self, time: datetime.datetime, session: Sequence[TestBase], test: TestBase, result_passed: bool, result_message: str) -> None:
        """Report the end of a single test"""
        pass
