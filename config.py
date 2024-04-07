import yaml
from yaml import load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


def loadcfg():
    with open("config.yml", "r") as file:
        cfg = yaml.safe_load(file)

    return cfg
