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


def device_settings():
    return loadcfg()["devices"]["IP2CC"][0]


def database_path():
    return loadcfg()["database"]["path"]


def settings():
    return loadcfg()["settings"]


def log_path():
    return loadcfg()["logging"]["path"]
