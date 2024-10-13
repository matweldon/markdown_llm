import pytest
import tempfile
import yaml
from pathlib import Path
from llm_tool.config_and_system import load_config_or_empty
"""
For this function, you should test the following properties:

1. It returns a dict when a valid YAML file exists.
2. It returns an empty dict when the file doesn't exist.
3. It returns an empty dict when the path is invalid.
4. It correctly loads the YAML content into a dict.
5. It handles both .yaml and .yml file extensions.
6. It returns an empty dict for non-YAML files.
"""
@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname

def test_load_config_or_empty(temp_dir):
    # Test valid YAML file
    valid_yaml = {"key": "value", "nested": {"inner": 42}}
    yaml_file = Path(temp_dir) / "test.yaml"
    with yaml_file.open('w') as f:
        yaml.dump(valid_yaml, f)
    
    result = load_config_or_empty(temp_dir, "test.yaml")
    assert result == valid_yaml

    # Test non-existent file
    result = load_config_or_empty(temp_dir, "nonexistent.yaml")
    assert result == {}

    # Test invalid path
    result = load_config_or_empty("/invalid/path", "test.yaml")
    assert result == {}

    # Test .yml extension
    yml_file = Path(temp_dir) / "test.yml"
    with yml_file.open('w') as f:
        yaml.dump(valid_yaml, f)
    
    result = load_config_or_empty(temp_dir, "test.yml")
    assert result == valid_yaml

    # Test non-YAML file
    non_yaml_file = Path(temp_dir) / "test.txt"
    non_yaml_file.touch()
    
    result = load_config_or_empty(temp_dir, "test.txt")
    assert result == {}

def test_yaml_content(temp_dir):
    # Test correct loading of YAML content
    complex_yaml = {
        "string": "value",
        "integer": 42,
        "float": 3.14,
        "list": [1, 2, 3],
        "nested": {
            "inner": "nested value",
            "inner_list": ["a", "b", "c"]
        }
    }
    yaml_file = Path(temp_dir) / "complex.yaml"
    with yaml_file.open('w') as f:
        yaml.dump(complex_yaml, f)
    
    result = load_config_or_empty(temp_dir, "complex.yaml")
    assert result == complex_yaml
