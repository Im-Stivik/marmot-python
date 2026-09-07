from __future__ import annotations

import pytest

from tests.db_isolation import assert_safe_test_database_name, create_test_database


def test_test_database_name_must_end_with_test() -> None:
    assert_safe_test_database_name("marmot_test")

    with pytest.raises(RuntimeError, match="_test"):
        assert_safe_test_database_name("marmot")

    with pytest.raises(RuntimeError, match="_test"):
        assert_safe_test_database_name("something_else")


def test_abort_if_test_database_already_exists(isolated_db: str) -> None:
    with pytest.raises(RuntimeError, match="already exists"):
        create_test_database(isolated_db)
