# TODO: add comments or refactor code

from pathlib import Path
import sys
import json
from typing import Sequence

import click
import pyperclip

from shepatra_core import (
    HashFuncName,
    generate_hashfunclayers,
    hash_str_as_hexdigest,
    load_recipedict_from_json,
    store_recipedict_to_json,
    HashFuncLayersRecipeDict,
    HashFuncLayersRecipe,
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


# -prepare recipedict-
recipedict = HashFuncLayersRecipeDict()
if Path(SCRIPT_DIR / HASHFUNC_LAYERS_RECIPES_FILENAME).exists():
    recipedict = load_recipedict_from_json(
        SCRIPT_DIR / HASHFUNC_LAYERS_RECIPES_FILENAME
    )
# --


def echo_sequence_items_with_index(sequence: Sequence):
    [click.echo(f"{i} {navi_text}") for i, navi_text in enumerate(sequence)]


def making_password_hashed_scene():
    if recipedict == {}:
        click.secho(navi_texts["no_recipe"], fg="bright_red")
        making_recipe_scene()
        if recipedict == {}:
            return
    cancel_flag = False
    options = (navi_texts["cancel"], *tuple(recipedict.keys()))
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
        elif options[order] in recipedict.keys():
            click.secho(
                navi_texts["given_hashfunc_layers_recipe"] + ": " + options[order],
                fg="bright_blue",
            )
            password = click.prompt(navi_texts["input_password"])
            hashed_password = hash_str_as_hexdigest(
                password,
                generate_hashfunclayers(*recipedict[options[order]]["recipe"]),
            )
            click.secho(
                navi_texts["password_generated"] + hashed_password, fg="bright_green"
            )
            click.secho(navi_texts["copied_to_clipboard"], fg="green")
            pyperclip.copy(hashed_password)
            cancel_flag = True
            click.echo()


def making_recipe_scene():
    hashfuncnames_to_display = [hashfuncname.name for hashfuncname in HashFuncName]
    options = (
        navi_texts["cancel"],
        navi_texts["submit"],
        *hashfuncnames_to_display,
    )
    recipe = HashFuncLayersRecipe(recipe=[], is_variable_length_algorithm_only=False)
    hash_func_choices_display = ""  # str to display hash func choices
    cancel_flag = False
    while not cancel_flag:
        echo_sequence_items_with_index(options)
        order = click.prompt(
            navi_texts["which_algorithm_add_and_layered"]
            + f"({click.style(hash_func_choices_display, fg='bright_blue')})",
            type=int,
            default=0,
        )
        if options[order] == navi_texts["cancel"]:
            cancel_flag = True
            click.echo()
        elif options[order] in hashfuncnames_to_display:
            recipe["recipe"].append(HashFuncName[options[order]])
            if hash_func_choices_display == "":
                hash_func_choices_display += (
                    navi_texts["given_hashfunc_layers_recipe"] + "="
                )
            hash_func_choices_display += str(order)
        elif options[order] == navi_texts["submit"] and recipe != []:
            click.secho(
                f'{navi_texts["given_hashfunc_layers_recipe"]}:', fg="bright_blue"
            )
            # -print hash func choices-
            [
                click.secho(f"  {hashfuncname.name}", fg="bright_blue")
                for hashfuncname in recipe["recipe"]
            ]
            # ---
            if click.confirm(navi_texts["confirm"], default=True):
                recipe_name = click.prompt(navi_texts["what_name_trans_system"])
                recipedict[recipe_name] = recipe
                click.secho(
                    navi_texts["recipe_generated"] + ": " + recipe_name,
                    fg="bright_green",
                )
                store_recipedict_to_json(
                    SCRIPT_DIR / HASHFUNC_LAYERS_RECIPES_FILENAME,
                    recipedict,
                )
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
            making_recipe_scene()


if __name__ == "__main__":
    title_scene()
