from pathlib import Path
from collections import namedtuple
from enum import Enum
import os

from dotenv import load_dotenv

PROD_ENV_BRANCH = "master"

Environ = namedtuple("Environ", "name envvars_file")


class Env(Enum):
    PROD = Environ("PROD", ".env.prod")
    DEV = Environ("DEV", ".env.dev")
    TEST = Environ("TEST", ".env.test")


def _get_active_branch_name():

    head_dir = Path(".", ".git", "HEAD")
    with head_dir.open("r") as f:
        content = f.read().splitlines()

    for line in content:
        if line[0:4] == "ref:":
            return line.partition("refs/heads/")[2]


def _get_env_name():

    if os.getenv("LL_TESTING") == "1":
        return Env.TEST

    current_branch_name = _get_active_branch_name()
    return Env.PROD if current_branch_name == PROD_ENV_BRANCH else Env.DEV


def load_env():
    env = _get_env_name()
    print(f"Load env vars for {env.value.name} ...")
    load_dotenv(env.value.envvars_file)
    print("Succeed")
