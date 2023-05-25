# TODO: add comments or refactor code

from pathlib import Path
import sys
import json
from typing import Sequence, TypedDict

import click

from shepatra_core import (
    HashFuncName,
    generate_hashfunc_layers,
    hash_str_with_hashfunc_layers,
)

# -prepare consts for file path-
SCRIPT_DIR = Path(sys.argv[0]).absolute().parent
HASHFUNC_LAYERS_RECIPES_FILENAME = "recipes.json"
CONFIG_FILENAME = "config.json"
I18N_DIRNAME = "i18n"
# --

# -load config-
with open(SCRIPT_DIR / CONFIG_FILENAME, "r") as f:
    config = json.load(f)
# --

# -load i18n text-
LANGUAGE = config["language"]
with open(SCRIPT_DIR / I18N_DIRNAME / f"{LANGUAGE}.json", "r", encoding="utf-8") as f:
    navi_texts_candidates: dict = json.load(f)
# --

# -prepare navigation texts-
navi_speaker_style = config["navigation_style"]
if navi_speaker_style not in navi_texts_candidates.keys():
    # check whether navi_texts has the specified speaker style
    navi_speaker_style = "standard"
navi_texts = navi_texts_candidates[navi_speaker_style]
# --


class HashFuncLayersRecipe(TypedDict):
    recipe: list[HashFuncName]
    is_variable_length_algorithm_only: bool


def store_hashfunc_layers_recipes_to_json(recipes: dict[str, HashFuncLayersRecipe]):
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
    with open(SCRIPT_DIR / HASHFUNC_LAYERS_RECIPES_FILENAME, "w") as f:
        json.dump(dict_to_store, f)


def load_hashfunc_layers_recipes_from_json() -> dict[str, HashFuncLayersRecipe]:
    with open(SCRIPT_DIR / HASHFUNC_LAYERS_RECIPES_FILENAME, "r") as f:
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


# -prepare hashfunc_layers_recipes-
hashfunc_layers_recipes: dict[str, HashFuncLayersRecipe] = {}
if Path(SCRIPT_DIR / HASHFUNC_LAYERS_RECIPES_FILENAME).exists():
    hashfunc_layers_recipes = load_hashfunc_layers_recipes_from_json()
# --


def echo_sequence_items_with_index(sequence: Sequence):
    [click.echo(f"{i} {navi_text}") for i, navi_text in enumerate(sequence)]


def making_password_hashed_scene():
    if hashfunc_layers_recipes == {}:
        click.secho(navi_texts["no_recipe"], fg="bright_red")
        making_hashfunc_layers_scene()
        if hashfunc_layers_recipes == {}:
            return
    cancel_flag = False
    options = (navi_texts["cancel"], *tuple(hashfunc_layers_recipes.keys()))
    while not cancel_flag:
        echo_sequence_items_with_index(options)
        order = click.prompt(
            navi_texts["which_recipe_would_you_like"],
            type=int,
            default=0,
        )
        if options[order] == navi_texts["cancel"]:
            cancel_flag = True
            click.echo()
        elif options[order] in hashfunc_layers_recipes.keys():
            click.secho(
                navi_texts["given_hashfunc_layers_recipe"] + ": " + options[order],
                fg="bright_blue",
            )
            password = click.prompt(navi_texts["input_password"])
            hashed_password = hash_str_with_hashfunc_layers(
                password,
                generate_hashfunc_layers(
                    *hashfunc_layers_recipes[options[order]]["recipe"]
                ),
            )
            click.secho(
                navi_texts["password_generated"] + hashed_password, fg="bright_green"
            )
            click.secho(navi_texts["copied_to_clipboard"], fg="green")
            cancel_flag = True
            click.echo()


def making_hashfunc_layers_scene():
    hashfuncnames = [hashfuncname.name for hashfuncname in HashFuncName]
    options = (
        navi_texts["cancel"],
        navi_texts["submit"],
        *hashfuncnames,
    )
    recipe = []
    display_ordered_layers = ""
    cancel_flag = False
    while not cancel_flag:
        echo_sequence_items_with_index(options)
        order = click.prompt(
            navi_texts["which_algorithm_add_and_layered"]
            + f"({click.style(display_ordered_layers, fg='bright_blue')})",
            type=int,
            default=0,
        )
        if options[order] == navi_texts["cancel"]:
            cancel_flag = True
            click.echo()
        elif options[order] in hashfuncnames:
            recipe.append(options[order])
            if display_ordered_layers == "":
                display_ordered_layers += (
                    navi_texts["given_hashfunc_layers_recipe"] + "="
                )
            display_ordered_layers += str(order)
        elif options[order] == navi_texts["submit"] and recipe != []:
            click.secho(
                f'{navi_texts["given_hashfunc_layers_recipe"]}:', fg="bright_blue"
            )
            [
                click.secho(f"  {hashfuncname}", fg="bright_blue")
                for hashfuncname in recipe
            ]
            if click.confirm(navi_texts["confirm"], default=True):
                recipe_name = click.prompt(navi_texts["what_name_trans_system"])
                hashfunc_layers_recipe = [
                    HashFuncName[hashfuncname] for hashfuncname in recipe
                ]
                hashfunc_layers_recipes[recipe_name] = {
                    "recipe": hashfunc_layers_recipe,
                    "is_variable_length_algorithm_only": False,
                }
                click.secho(
                    navi_texts["recipe_generated"] + ": " + recipe_name,
                    fg="bright_green",
                )
                store_hashfunc_layers_recipes_to_json(hashfunc_layers_recipes)
            cancel_flag = True
            click.echo()


@click.command()
def title_scene():
    click.echo(navi_texts["welcome"])
    options = (
        navi_texts["exit"],
        navi_texts["make_hashed_password"],
        navi_texts["go_to_recipe_making"],
    )
    exit_flag = False
    while not exit_flag:
        echo_sequence_items_with_index(options)
        order = click.prompt(navi_texts["make_selection"], type=int, default=0)
        if options[order] == navi_texts["exit"]:
            exit_flag = True
        elif options[order] == navi_texts["make_hashed_password"]:
            click.echo()
            making_password_hashed_scene()
        elif options[order] == navi_texts["go_to_recipe_making"]:
            click.echo()
            making_hashfunc_layers_scene()


if __name__ == "__main__":
    title_scene()
