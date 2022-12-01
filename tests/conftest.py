"""Conftest."""
import pytest


# do not import any module from the code base directly here, instead import the modules
# inside the functions. importing here will corrupt the patch.

def pytest_configure(config):
    """pytest_configure.

    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest
    file after command line options have been parsed.
    """
    pass


def pytest_sessionstart(session):
    """pytest_sessionstart.

    Called after the Session object has been created and
    before performing collection and entering the run test loop.
    """
    pass


def pytest_sessionfinish(session, exitstatus):
    """pytest_sessionfinish.

    Called after whole test run finished, right before
    returning the exit status to the system.
    """
    pass


def pytest_unconfigure(config):
    """pytest_unconfigure.

    called before test process is exited.
    """
    pass
