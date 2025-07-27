import os


def is_feature_flag_enabled(name: str) -> bool:
    positive_values = {"1", "true", "yes", "on"}
    return os.getenv(name, "").lower() in positive_values
