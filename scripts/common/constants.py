from enum import Enum
from collections import namedtuple


class Env(Enum):
    TEST = "test"
    DEV = "dev"
    PROD = "prod"

    @classmethod
    def list_(cls):
        return [item.value for item in cls]


# ENV_MAPPING = {
#     Env.DEV.value: "../.env.dev",
#     Env.PROD.value: "../.env.prod",
#     Env.TEST.value: "../.env.test",
# }
ENV_MAPPING = {
    Env.DEV.value: ".env.dev",
    Env.PROD.value: ".env.prod",
    Env.TEST.value: ".env.test",
}
