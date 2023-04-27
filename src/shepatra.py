""" shepatra = she is password translator """
from pathlib import Path
import hashlib
import json


from blake3 import blake3
import click
import pyperclip

from scripts.utils import json_to_translation_systems, \
    translation_systems_to_json

# RUN_SCRIPT_ON_RELEASE = False

SCRIPT_DIR = Path(__file__).absolute().parent

PTS_FILENAME = "pts.json"
CONFIG_FILENAME = "config.json"
I18N_DIRNAME = "i18n"

PTS_FILEPATH = SCRIPT_DIR / PTS_FILENAME
CONFIG_FILEPATH = SCRIPT_DIR / CONFIG_FILENAME
I18N_DIRPATH = SCRIPT_DIR / I18N_DIRNAME

with open(CONFIG_FILEPATH, "r") as f:
    config = json.load(f)

LANGUAGE = config["language"]

with open(I18N_DIRPATH / f"{LANGUAGE}.json", "r", encoding="utf-8") as f:
    navigation_texts_candidates: dict = json.load(f)

navigation_style = config["navigation_style"]
if navigation_style not in navigation_texts_candidates.keys():
    navigation_style = "standard"

navi_txts = navigation_texts_candidates[navigation_style]

algorithms = {
    "sha3-512": hashlib.sha3_512,
    "blake2b": hashlib.blake2b,
    "blake3": blake3}
algorithms_reversed = dict(zip(algorithms.values(), algorithms.keys()))

translation_systems = {}
if PTS_FILEPATH.exists():
    with open(PTS_FILEPATH, "r") as f:
        translation_systems = json_to_translation_systems(
            json.load(f), algorithms)


def show_options(options_dict: dict):
    [click.echo(message=f"{id} {text}")
     for id, text in enumerate(options_dict.keys())]


def edit_password_translation_system():
    options = {navi_txts["cancel"]: "cancel",
               navi_txts["submit"]: "submit"}
    options |= algorithms
    show_options(options)
    translation_layers = []
    order_id = None
    while True:
        order_id = click.prompt(
            navi_txts["which_algorithm_add_and_layered"], type=int)
        if order_id > len(options) - 1:
            continue
        if order_id not in (0, 1):
            translation_layers.append(list(options.values())[order_id])
        layers_to_show = [algorithms_reversed[layer]
                          for layer in translation_layers
                          if layer in algorithms.values()]
        click.echo("layers: ", nl=False)
        click.secho(str(layers_to_show), bg="blue")
        if list(options.values())[order_id] == "cancel":
            return
        elif list(options.values())[order_id] == "submit":
            if translation_layers == []:
                continue
            name = click.prompt(
                navi_txts["what_name_trans_system"])
            translation_systems[name] = translation_layers
            click.echo(f"{navi_txts['trans_system_generated']}", nl=False)
            click.secho(str(name), bg="green")
            click.echo("layers: ", nl=False)
            click.secho(str(layers_to_show), bg="blue")
            with open(PTS_FILEPATH, "w") as f:
                json.dump(
                    translation_systems_to_json(
                        translation_systems, algorithms_reversed), f)
            break


def translate_password():
    if translation_systems == {}:
        click.echo(navi_txts["no_trans_system"])
        while True:
            edit_password_translation_system()
            if translation_systems == {}:
                continue
            else:
                click.echo(
                    "---finish password translation system generation---")
                break
    click.echo("--List of password translation system--")
    show_options(translation_systems)
    while True:
        order_id = click.prompt(
            navi_txts["which_trans_system_use"], type=int, default=0)
        if order_id > len(translation_systems) - 1:
            continue
        else:
            break
    password: str = click.prompt(navi_txts["input_password"])
    hashfunc_layers = translation_systems[
        list(translation_systems.keys())[order_id]]
    for hashfunc in hashfunc_layers:
        password = hashfunc(bytes(password, "utf-8")).hexdigest()
    hashed_password_hex = password
    click.secho(navi_txts['password_generated'],
                fg="green")
    click.secho(str(hashed_password_hex),
                fg="bright_green")
    click.echo(navi_txts["copy_to_clipboard"])
    pyperclip.copy(str(hashed_password_hex))


@click.command()
def cli():
    click.echo(navi_txts["welcome"])
    while True:
        options_on_title = {
            navi_txts["exit"]:
            lambda: True,
            navi_txts["go_to_pts_gen"]:
            edit_password_translation_system,
            navi_txts["make_hashed_password"]:
            translate_password}
        show_options(options_on_title)
        order_id = click.prompt(
            navi_txts["make_selection"], type=int, default=0)
        is_exit_ordered = tuple(options_on_title.values())[order_id]()
        if is_exit_ordered:
            break


if __name__ == "__main__":
    cli()
