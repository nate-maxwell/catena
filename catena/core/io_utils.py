import json
from pathlib import Path
from typing import Optional


def export_data_to_json(path: Path, data: dict, overwrite: bool = False) -> None:
    """
    Export dict to JSON file path.

    Args:
        path (Path): the file path to place the .json file.
        data (dict): the data to export into the .json file.
        overwrite (bool): to overwrite JSON file if it already exists in path.
            Defaults to False.
    """
    if not path.exists() or overwrite:
        with open(path, "w") as outfile:
            json.dump(data, outfile, indent=4)
    else:
        return


def import_data_from_json(filepath: Path) -> Optional[dict]:
    """
    Import data from a .json file.

    Args:
        filepath (Path): the filepath to the JSON file to extract data from.
    Returns:
        Optional[dict]: will return data if JSON file exists, else None.
    """
    if filepath.exists():
        with open(filepath) as file:
            data = json.load(file)
            return data

    return None
