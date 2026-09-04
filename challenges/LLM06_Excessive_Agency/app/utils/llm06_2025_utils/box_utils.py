"""Local file store used by the LLM06 challenge.

The challenge used to depend on a single Box account whose credentials and
folder IDs were committed to the repository.  Besides exposing credentials,
that made every checkout stop working when the account changed.  These
helpers retain the small interface used by the challenge while keeping its
public and restricted files in the repository.
"""

from pathlib import Path

DATA_ROOT = Path(__file__).with_name("data")
FOLDERS = {
    "all": DATA_ROOT,
    "accessible": DATA_ROOT / "accessible",
    "restricted": DATA_ROOT / "restricted",
    "logs": DATA_ROOT / "logs",
}


def _folder(folder_id):
    folder_key = folder_id or "all"
    try:
        return FOLDERS[folder_key]
    except KeyError as exc:
        raise ValueError(f"Unknown challenge folder: {folder_key}") from exc


def search_file_recursive(folder_id, file_name):
    """Return the first matching file below a challenge folder."""
    if not file_name:
        return False, "", "File not found in the accessible folder."

    requested_name = Path(file_name).name.casefold()
    for path in _folder(folder_id).rglob("*"):
        if path.is_file() and path.name.casefold() == requested_name:
            return True, str(path.relative_to(DATA_ROOT)), path.read_text()

    return False, "", "File not found in the accessible folder."


def _list_folder(path):
    content = {}
    for item in sorted(path.iterdir()):
        if item.is_file():
            content.setdefault(path.name, []).append(item.name)
        elif item.is_dir():
            content[item.name] = _list_folder(item)
    content.setdefault(path.name, [])
    return content


def list_all_files(folder_id):
    """List files below a challenge folder without crossing its boundary."""
    return _list_folder(_folder(folder_id))


def create_file(folder_id, filename, content):
    """Create a file in a challenge folder."""
    path = _folder(folder_id) / Path(filename).name
    if path.exists():
        return f"❌ Error creating file: '{path.name}' already exists"
    path.write_text(content)
    return f"✅ File '{path.name}' created successfully"


def update_file(folder_id, file_name, new_content):
    """Update the first matching file in a challenge folder."""
    found, file_id, _ = search_file_recursive(folder_id, file_name)
    if not found:
        return "❌ File not found"
    (DATA_ROOT / file_id).write_text(new_content)
    return f"✅ File '{Path(file_id).name}' updated successfully"


def delete_file(folder_id, file_name):
    """Delete the first matching file in a challenge folder."""
    found, file_id, _ = search_file_recursive(folder_id, file_name)
    if not found:
        return "❌ File not found"
    (DATA_ROOT / file_id).unlink()
    return f"✅ File (ID: {file_id}) deleted successfully"
