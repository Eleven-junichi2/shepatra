from pathlib import Path
import json
import sys

import flet as ft
import pyperclip

from shepatra_core import (
    HashFuncLayersRecipeDict,
    load_recipedict_from_json,
    hash_str_as_hexdigest,
    generate_hashfunclayers,
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
with open(
    SCRIPT_DIR / I18N_DIRNAME / "gui" / f"{LANGUAGE}.json", "r", encoding="utf-8"
) as f:
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


def making_hashed_password_view(route) -> ft.View:
    def make_password_hashed_on_enter(e):
        if recipedict_dropdown.value is None:
            recipedict_dropdown.error_text = navi_texts[
                "raise_error_not_recipe_selected"
            ]
            recipedict_dropdown.update()
            return
        if password_inputfield.value:
            hexdigested_password = hash_str_as_hexdigest(
                password_inputfield.value,
                generate_hashfunclayers(
                    *recipedict[recipedict_dropdown.value]["recipe"]
                ),
            )
            pyperclip.copy(hexdigested_password)
            hash_outputfield.value = hexdigested_password
            hash_outputfield.helper_text = navi_texts["copied_to_clipboard"]
            hash_outputfield.helper_style = ft.TextStyle(
                color=ft.colors.GREEN_ACCENT_200
            )
            hash_outputfield.update()
            if recipedict_dropdown.error_text:
                recipedict_dropdown.error_text = None
                recipedict_dropdown.update()

    recipedict_dropdown_header = ft.Text(
        navi_texts["which_recipe_would_you_like"] + ":"
    )
    recipedict_dropdown = ft.Dropdown(
        options=[
            ft.dropdown.Option(key=recipe_name, text=recipe_name)
            for recipe_name in recipedict.keys()
        ],
        bgcolor=ft.colors.WHITE12,
        border_color=ft.colors.WHITE,
        width=278,
    )
    password_inputfield_header = ft.Text(navi_texts["submit_with_enter"] + ":")
    password_inputfield = ft.TextField(
        hint_text=navi_texts["input_password"],
        bgcolor=ft.colors.WHITE10,
        border_color=ft.colors.WHITE,
        width=378,
        on_submit=make_password_hashed_on_enter,
    )
    hash_outputfield = ft.TextField(
        hint_text=navi_texts["hash_value_output_is_here"],
        read_only=True,
        multiline=True,
        expand=True,
    )
    return ft.View(
        route=route,
        controls=[
            ft.Column(
                controls=[
                    ft.Row(
                        controls=[recipedict_dropdown_header, recipedict_dropdown],
                    ),
                    ft.Row(
                        controls=[password_inputfield_header, password_inputfield],
                    ),
                ],
                alignment=ft.MainAxisAlignment.END,
            ),
            hash_outputfield,
        ],
    )


def making_recipe_view(route) -> ft.View:
    # TODO: make this
    return ft.View(route=route, controls=[])


def main(page: ft.Page):
    # -configure window-
    page.title = "Shepatra"
    page.window_width = 522
    page.window_height = 378
    page.window_resizable = False
    # --

    VIEW_LIST = [
        making_hashed_password_view("/making_hashed_password"),
        making_recipe_view("/making_recipe"),
    ]

    page.add(*VIEW_LIST)

    def on_route_change(handler: ft.RouteChangeEvent):
        troute = ft.TemplateRoute(handler.route)
        page.views.clear()
        for view in VIEW_LIST:
            if troute.match(view.route):
                page.views.append(view)
        page.update()

    page.on_route_change = on_route_change
    # page.go("/making_hashed_password")
    page.go("/making_recipe")
    page.update()


if __name__ == "__main__":
    ft.app(target=main)
