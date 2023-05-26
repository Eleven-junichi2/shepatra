import pytest

from src.shepatra_core import (
    generate_recipe,
    hash_str_with_recipe,
    HashFuncName,
)


def test_generate_hashfunc_layers():
    with pytest.raises(ValueError):
        generate_recipe(HashFuncName.SHA3_312, HashFuncName.BLAKE2b, "あいうえお")
    hashfunc_layers = generate_recipe(
        HashFuncName.SHA3_312, HashFuncName.BLAKE2b, HashFuncName.BLAKE3
    )
    for hashfunc in hashfunc_layers:
        assert hasattr(hashfunc(), "update")  # assert whether `hashfunc` is hash object


def test_integration():
    hashed_str = hash_str_with_recipe(
        "test",
        generate_recipe(
            HashFuncName.SHA3_312, HashFuncName.BLAKE2b, HashFuncName.BLAKE3
        ),
    )
    assert hashed_str
