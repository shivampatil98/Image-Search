import yaml

def load_config(config_path = "configs/default.yaml"):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config


def save_config(config, config_path="configs/default.yaml"):
    with open(config_path, 'w') as f:
        yaml.dump(config, f)
    