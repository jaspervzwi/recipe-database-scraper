import pytest
import os
import json
from tempfile import TemporaryDirectory
from recipe_database_scraper._utils import FileHandler


@pytest.mark.util
def test_load_exclusion_json_file_existing():
    """Test loading an existing exclusion JSON file."""
    with TemporaryDirectory() as tmp_dir:
        exclusion_file = os.path.join(tmp_dir, "_recipe_scraper_exclusions.json")

        sample_data = {
            "http://example.com": [
                "http://example.com/page1",
                "http://example.com/page2",
            ]
        }
        with open(exclusion_file, "w") as f:
            json.dump(sample_data, f)

        loaded_data = FileHandler(
            os.path.join(tmp_dir, "input.json")
        ).load_exclusion_json_file()

        assert loaded_data == sample_data, "Loaded data does not match expected content"


@pytest.mark.util
def test_load_exclusion_json_file_missing():
    """Test behavior when the exclusion JSON file is missing."""
    with TemporaryDirectory() as tmp_dir:
        loaded_data = FileHandler(
            os.path.join(tmp_dir, "input.json")
        ).load_exclusion_json_file()

        assert loaded_data is None, "Expected None when exclusion file is missing"


@pytest.mark.util
def test_write_exclusion_json_file_new_file():
    """Test writing to a new exclusion JSON file."""
    with TemporaryDirectory() as tmp_dir:
        file_handler = FileHandler(filename=os.path.join(tmp_dir, "output.json"))
        sample_data = {
            "http://example.com": [
                "http://example.com/page1",
                "http://example.com/page2",
            ]
        }

        file_handler.write_exclusion_json_file(sample_data)

        exclusion_file = os.path.join(tmp_dir, "_recipe_scraper_exclusions.json")
        with open(exclusion_file) as f:
            content = json.load(f)

        assert (
            content == sample_data
        ), "Exclusion file content does not match expected data"


@pytest.mark.util
def test_write_exclusion_json_file_existing_key_update():
    """Test updating an existing key in the exclusion JSON file."""
    with TemporaryDirectory() as tmp_dir:
        exclusion_file = os.path.join(tmp_dir, "_recipe_scraper_exclusions.json")
        initial_data = {
            "http://example.com": [
                "http://example.com/page1",
                "http://example.com/page2",
            ]
        }

        with open(exclusion_file, "w") as f:
            json.dump(initial_data, f)

        file_handler = FileHandler(filename=os.path.join(tmp_dir, "input.json"))
        updated_data = {
            "http://example.com": [
                "http://example.com/different-page1",
                "http://example.com/different-page2",
            ]
        }

        # Write to the exclusion file, which should update the existing key
        file_handler.write_exclusion_json_file(updated_data)

        with open(exclusion_file) as f:
            content = json.load(f)

        assert (
            content == updated_data
        ), "Exclusion file content does not match updated data"


@pytest.mark.util
def test_write_exclusion_json_file_new_key_append():
    """Test appending a new key to an existing exclusion JSON file."""
    with TemporaryDirectory() as tmp_dir:
        exclusion_file = os.path.join(tmp_dir, "_recipe_scraper_exclusions.json")
        initial_data = {
            "http://example.com": [
                "http://example.com/page1",
                "http://example.com/page2",
            ]
        }

        with open(exclusion_file, "w") as f:
            json.dump(initial_data, f)

        file_handler = FileHandler(filename=os.path.join(tmp_dir, "input.json"))
        new_data = {
            "http://another-example.com": [
                "http://another-example.com/page1",
                "http://another-example.com/page2",
            ]
        }

        # Write to the exclusion file, which should add the new key
        file_handler.write_exclusion_json_file(new_data)

        with open(exclusion_file) as f:
            content = json.load(f)

        expected_content = {**initial_data, **new_data}

        assert (
            content == expected_content
        ), "Exclusion file content does not match expected appended data"


@pytest.mark.util
def test_load_json_file():
    """Test loading a JSON file with the load_json_file method."""
    with TemporaryDirectory() as tmp_dir:
        json_file = os.path.join(tmp_dir, "test.json")
        data = {"test_key": "test_value"}

        with open(json_file, "w") as f:
            json.dump(data, f)

        file_handler = FileHandler(filename=json_file)
        loaded_data = file_handler.load_json_file()

        assert loaded_data == data, "Loaded JSON data does not match expected content"


@pytest.mark.util
def test_write_json_file():
    """Test writing data to a JSON file with the write_json_file method."""
    with TemporaryDirectory() as tmp_dir:
        json_file = os.path.join(tmp_dir, "test.json")
        data = {"write_key": "write_value"}

        file_handler = FileHandler(filename=json_file)
        file_handler.write_json_file(data)

        with open(json_file) as f:
            written_data = json.load(f)

        assert written_data == data, "Written JSON data does not match expected content"
