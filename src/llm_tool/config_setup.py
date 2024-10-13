from pathlib import Path
from platformdirs import user_config_dir


def create_config() -> None:
    config_dir = os.getenv("llmd_config_dir",user_config_dir("llmd"))
    config_dir = Path(config_dir)
    config_dir.mkdir(parents=True, exist_ok=True)
    
    config_path = config_dir / "config.yaml"
    if config_path.exists():
        print(f"User config is at {config_path}")
    else:
        config_path.write_text("# User config file")
        print(f"User config is at {config_path}")
    


if __name__ == "__main__":
    create_config()
