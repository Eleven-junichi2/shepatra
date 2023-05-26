from enum import Enum, auto
import hashlib
import json
from typing import Any, Generator, Callable, TypedDict

from blake3 import blake3


class HashFuncName(Enum):
    SHA3_312 = auto()
    BLAKE2b = auto()
    BLAKE3 = auto()
    SHAKE_128 = auto()
    SHAKE_256 = auto()


HASHFUNC_DICT = {
    HashFuncName.SHA3_312: hashlib.sha3_512,
    HashFuncName.BLAKE2b: hashlib.blake2b,
    HashFuncName.BLAKE3: blake3,
}

HashFuncLayers = Generator[Callable, Callable, Any]


class HashFuncLayersRecipe(TypedDict):
    recipe: list[HashFuncName]
    is_variable_length_algorithm_only: bool


class HashFuncLayersRecipeDict(dict[str, HashFuncLayersRecipe]):
    pass


def store_recipedict_to_json(filepath, recipes: HashFuncLayersRecipeDict):
    dict_to_store = {}
    for recipe_name, hashfunclayers_recipe in recipes.items():
        dict_to_store[recipe_name] = {
            "recipe": [
                hashfuncname.name for hashfuncname in hashfunclayers_recipe["recipe"]
            ],
            "is_variable_length_algorithm_only": hashfunclayers_recipe[
                "is_variable_length_algorithm_only"
            ],
        }
    with open(filepath, "w") as f:
        json.dump(dict_to_store, f)


def load_recipedict_from_json(filepath) -> HashFuncLayersRecipeDict:
    with open(filepath, "r") as f:
        recipes_in_jsondict: dict = json.load(f)
    recipes = {}
    for recipe_name, hashfunclayers_recipe in recipes_in_jsondict.items():
        recipes[recipe_name] = {
            "recipe": [
                HashFuncName[hashfuncname]
                for hashfuncname in hashfunclayers_recipe["recipe"]
            ],
            "is_variable_length_algorithm_only": hashfunclayers_recipe[
                "is_variable_length_algorithm_only"
            ],
        }
    return recipes


def generate_recipe(*hashfunc_names: HashFuncName) -> HashFuncLayers:
    if set(HASHFUNC_DICT.keys()).issuperset(set(hashfunc_names)):
        return (HASHFUNC_DICT[hashfunc_name] for hashfunc_name in hashfunc_names)
    else:
        raise ValueError(
            f"hashfunc_names(={hashfunc_names}) includes invalid hashfunc name"
        )


def hash_str_with_recipe(
    str_to_be_hashed: str, hashfunc_layers_recipe: HashFuncLayers
) -> str:
    """return hexdigest() of hash value from given str"""
    for hashfunc in hashfunc_layers_recipe:
        str_to_be_hashed = hashfunc(bytes(str_to_be_hashed, "utf-8")).hexdigest()
    return str_to_be_hashed
