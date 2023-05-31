# TODO: refactor code

from pathlib import Path
import json
import sys

import flet as ft
import pyperclip

from shepatra_core import (
    HashFuncLayersRecipe,
    HashFuncLayersRecipeDict,
    HashFuncName,
    load_recipedict_from_json,
    hash_str_as_hexdigest,
    generate_hashfunclayers,
    store_recipedict_to_json,
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


class SettingsScene(ft.UserControl):
    def build(self):
        return ft.Container(padding=10, content=ft.Column([]))


class MakingHashedPasswordScene(ft.UserControl):
    def build(self):
        self.recipe_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option(key=recipe_name, text=recipe_name)
                for recipe_name in recipedict
            ],
            hint_text=navi_texts["select_algorithm"],
        )
        self.password_textfield = ft.TextField(
            hint_text=navi_texts["submit_with_enter"],
            on_submit=lambda e: self.make_password_hashed(),
        )
        self.result_textfield = ft.TextField(
            hint_text=navi_texts["hash_value_output_is_here"], read_only=True
        )
        return ft.Container(
            padding=10,
            content=ft.Column(
                [self.recipe_dropdown, self.password_textfield, self.result_textfield]
            ),
        )

    def make_password_hashed(self):
        if not self.is_recipe_selected():
            return
        if self.password_textfield.value:
            hashed_password = hash_str_as_hexdigest(
                self.password_textfield.value,
                generate_hashfunclayers(
                    *recipedict[self.recipe_dropdown.value]["recipe"]
                ),
            )
            pyperclip.copy(hashed_password)
            self.result_textfield.value = hashed_password
            self.result_textfield.helper_text = navi_texts["copied_to_clipboard"]
            self.result_textfield.helper_style = ft.TextStyle(
                color=ft.colors.GREEN_ACCENT_200
            )
            self.result_textfield.update()
            if self.recipe_dropdown.error_text:
                self.recipe_dropdown.error_text = None
                self.recipe_dropdown.update()

    def is_recipe_selected(self) -> bool:
        if self.recipe_dropdown.value is None:
            self.recipe_dropdown.error_text = navi_texts[
                "raise_error_not_recipe_selected"
            ]
            self.recipe_dropdown.update()
            return False
        else:
            return True


def main(page: ft.Page):
    # -configure window-
    page.title = "Shepatra"
    # --
    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(
                text=navi_texts["make_hashed_password"],
                content=MakingHashedPasswordScene(),
                icon=ft.icons.KEY
            ),
            ft.Tab(
                text=navi_texts["settings"],
                content=SettingsScene(),
                icon=ft.icons.SETTINGS
            )
        ],
        expand=1,
    )
    page.add(tabs)
    page.update()


if __name__ == "__main__":
    ft.app(target=main)
