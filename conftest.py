
import pytest
import sys

def pytest_sessionstart(session):
    session.total_test_count = 0
    session.tests_completed = 0

def pytest_collection_finish(session):
    session.total_test_count = len(session.items)
    print(f"\n[PROGRESS] Collected {session.total_test_count} tests.")

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_logreport(report):
    # Only increment on 'call' phase to avoid double counting setup/teardown phases
    if report.when == 'call':
        # Safely try to get the session. 
        # In pytest, the session is usually available via some objects, but 
        # a simpler way to track global state in a single process run is a global or a session property.
        pass

# A more reliable way to track across phases:
class ProgressPlugin:
    def __init__(self):
        self.total = 0
        self.completed = 0

    def pytest_collection_finish(self, session):
        self.total = len(session.items)
        print(f"\n[PROGRESS] Total Tests: {self.total}")

    def pytest_runtest_logreport(self, report):
        if report.when == 'call':
            self.completed += 1
            if self.total > 0:
                percent = (self.completed / self.total) * 100
                # Using sys.stderr.write often helps avoid some capture issues or just use print with flush
                print(f"[PROGRESS] {percent:.1f}% Complete ({self.completed}/{self.total}) - {report.nodeid.split('::')[-1]}", flush=True)

def pytest_configure(config):
    config.pluginmanager.register(ProgressPlugin())
