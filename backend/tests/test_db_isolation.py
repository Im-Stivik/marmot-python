from __future__ import annotations

import pytest

from tests.db_isolation import assert_safe_test_database_name, create_test_database


def test_protected_database_names_are_rejected() -> None:
    with pytest.raises(RuntimeError, match="protected"):
        assert_safe_test_database_name("marmot")

    with pytest.raises(RuntimeError, match="protected"):
        assert_safe_test_database_name("metastore")

    with pytest.raises(RuntimeError, match="_test"):
        assert_safe_test_database_name("something_else")


def test_abort_if_test_database_already_exists(isolated_db: str) -> None:
    """While a test holds marmot_test, a second create must refuse to proceed."""
    with pytest.raises(RuntimeError, match="already exists"):
        create_test_database(isolated_db)
