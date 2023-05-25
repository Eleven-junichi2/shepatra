import pytest

from src.shepatra_core import (
    generate_hashfunc_layers,
    hash_str_with_hashfunc_layers,
    HashFuncName,
)


def test_generate_hashfunc_layers():
    with pytest.raises(ValueError):
        generate_hashfunc_layers(HashFuncName.SHA3_312, HashFuncName.BLAKE2b, "あいうえお")
    hashfunc_layers = generate_hashfunc_layers(
        HashFuncName.SHA3_312, HashFuncName.BLAKE2b, HashFuncName.BLAKE3
    )
    for hashfunc in hashfunc_layers:
        assert hasattr(hashfunc(), "update")  # assert whether `hashfunc` is hash object


def test_integration():
    hashfunc_layers = generate_hashfunc_layers(
        HashFuncName.SHA3_312, HashFuncName.BLAKE2b, HashFuncName.BLAKE3
    )
    hashed_str = hash_str_with_hashfunc_layers("test", hashfunc_layers=hashfunc_layers)
    assert hashed_str
