import sys
import pytest
from pathlib import Path

# Add src to path so "maps" and "core" can be imported when running tests
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def pytest_addoption(parser):
    parser.addoption(
        "--live",
        action="store_true",
        default=False,
        help="Use real HTTP requests instead of mocks (e.g. pytest tests/ --live)",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "live: mark test to run against real API when --live is passed (deselect without it)",
    )


def pytest_collection_modifyitems(config, items):
    """With --live: run only tests marked 'live'. Without --live: skip tests marked 'live'."""
    live = config.getoption("--live", default=False)
    for item in items:
        has_live = any(m.name == "live" for m in item.iter_markers())
        if live and not has_live:
            item.add_marker(pytest.mark.skip(reason="run only with --live (mock test)"))
        elif not live and has_live:
            item.add_marker(pytest.mark.skip(reason="omit without --live (live API test)"))
