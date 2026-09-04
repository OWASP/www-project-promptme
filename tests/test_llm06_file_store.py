import importlib.util
from pathlib import Path

MODULE_PATH = (
    Path(__file__).parents[1]
    / "challenges/LLM06_Excessive_Agency/app/utils/llm06_2025_utils/box_utils.py"
)
SPEC = importlib.util.spec_from_file_location("llm06_box_utils", MODULE_PATH)
box_utils = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(box_utils)


def test_regular_users_cannot_find_restricted_flag():
    found, _, content = box_utils.search_file_recursive("accessible", "flag.txt")

    assert not found
    assert content == "File not found in the accessible folder."


def test_admin_view_can_find_restricted_flag():
    found, file_id, content = box_utils.search_file_recursive("all", "flag.txt")

    assert found
    assert file_id == "restricted/flag.txt"
    assert content.startswith("FLAG{")


def test_regular_file_listing_does_not_disclose_restricted_names():
    listing = box_utils.list_all_files("accessible")

    assert "welcome.txt" in repr(listing)
    assert "flag.txt" not in repr(listing)
    assert "secret_data.txt" not in repr(listing)


def test_unknown_folder_ids_fail_closed():
    try:
        box_utils.list_all_files("external-folder-id")
    except ValueError as exc:
        assert "Unknown challenge folder" in str(exc)
    else:
        raise AssertionError("unknown folders must not fall back to the full store")
