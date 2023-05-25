from enum import Enum
import hashlib
from typing import Any, Generator, Callable

from blake3 import blake3


class HashFuncName(Enum):
    SHA3_312 = "sha3-512"
    BLAKE2b = "blake2b"
    BLAKE3 = "blake3"


HASHFUNC_DICT = {
    HashFuncName.SHA3_312: hashlib.sha3_512,
    HashFuncName.BLAKE2b: hashlib.blake2b,
    HashFuncName.BLAKE3: blake3,
}

HashFuncLayers = Generator[Callable, Callable, Any]


def generate_hashfunc_layers(*hashfunc_names: HashFuncName) -> HashFuncLayers:
    if set(HASHFUNC_DICT.keys()).issuperset(set(hashfunc_names)):
        return (HASHFUNC_DICT[hashfunc_name] for hashfunc_name in hashfunc_names)
    else:
        raise ValueError(
            f"hashfunc_names(={hashfunc_names}) includes invalid hashfunc name"
        )


def hash_str_with_hashfunc_layers(
    str_to_be_hashed: str, hashfunc_layers: HashFuncLayers
) -> str:
    for hashfunc in hashfunc_layers:
        str_to_be_hashed = hashfunc(bytes(str_to_be_hashed, "utf-8")).hexdigest()
    return str_to_be_hashed
