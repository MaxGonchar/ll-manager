import hashlib


def hash_psw(psw: str) -> str:
    return _hash_psw(psw)


def _hash_psw(psw: str) -> str:
    hasher = hashlib.sha256()
    hasher.update(psw.encode())
    return hasher.hexdigest()


def is_psw_matching(str_psw: str, hash_psw: str) -> bool:
    return _hash_psw(str_psw) == hash_psw
