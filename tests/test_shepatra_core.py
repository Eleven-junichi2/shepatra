import py  # for typehint

import pytest

from src.shepatra_core import (
    generate_hashfunclayers,
    hash_str_as_hexdigest,
    HashFuncName,
    store_recipedict_to_json,
    load_recipedict_from_json,
    HashFuncLayersRecipeDict,
    HashFuncLayersRecipe,
)


def test_generate_hashfunclayers():
    with pytest.raises(ValueError):
        generate_hashfunclayers(HashFuncName.SHA3_312, HashFuncName.BLAKE2b, "あいうえお")
    hashfunc_layers = generate_hashfunclayers(
        HashFuncName.SHA3_312, HashFuncName.BLAKE2b, HashFuncName.BLAKE3
    )
    for hashfunc in hashfunc_layers:
        assert hasattr(hashfunc(), "update")  # assert whether `hashfunc` is hash object


def test_integration():
    hashed_str = hash_str_as_hexdigest(
        "test",
        generate_hashfunclayers(
            HashFuncName.SHA3_312, HashFuncName.BLAKE2b, HashFuncName.BLAKE3
        ),
    )
    assert hashed_str


def test_store_recipedict_to_json(tmpdir: py.path.local):
    # TODO: here
    recipe_path = tmpdir.join("recipe.json")
    recipedict = HashFuncLayersRecipeDict()
    recipedict["test"] = HashFuncLayersRecipe(
        recipe=[HashFuncName.SHA3_312, HashFuncName.BLAKE2b, HashFuncName.BLAKE3],
        is_variable_length_algorithm_only=False,
    )
    store_recipedict_to_json(recipe_path, recipedict)
    assert recipe_path.exists()


def test_load_recipedict_from_json(tmpdir: py.path.local):
    recipe_path = tmpdir.join("recipe.json")
    recipedict_to_store = HashFuncLayersRecipeDict()
    recipedict_to_store["test"] = HashFuncLayersRecipe(
        recipe=[HashFuncName.SHA3_312, HashFuncName.BLAKE2b, HashFuncName.BLAKE3],
        is_variable_length_algorithm_only=False,
    )
    store_recipedict_to_json(recipe_path, recipedict_to_store)
    recipedict = load_recipedict_from_json(recipe_path)
    assert recipedict["test"]["recipe"] == [
        HashFuncName.SHA3_312,
        HashFuncName.BLAKE2b,
        HashFuncName.BLAKE3,
    ]
