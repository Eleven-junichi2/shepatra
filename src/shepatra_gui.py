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
    def __init__(self):
        super().__init__()
        self.recipe_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option(key=recipe_name, text=recipe_name)
                for recipe_name in recipedict
            ],
            hint_text=navi_texts["which_recipe_would_you_like"],
        )

    def build(self):
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
        if not self.check_recipe_selected():
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

    def check_recipe_selected(self) -> bool:
        if self.recipe_dropdown.value is None:
            self.recipe_dropdown.error_text = navi_texts[
                "raise_error_not_recipe_selected"
            ]
            self.recipe_dropdown.update()
            return False
        else:
            return True


class MakingRecipeScene(ft.UserControl):
    def build(self):
        self.algorithm_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option(hashfunc.value, hashfunc.name)
                for hashfunc in HashFuncName
            ],
            hint_text=navi_texts["select_algorithm"],
            expand=1,
        )
        self.append_to_recipe_btn = ft.FloatingActionButton(
            icon=ft.icons.ADD, on_click=lambda e: self.add_algorithm_to_recipe()
        )
        self.algorithm_listview = ft.Column(expand=1, scroll="always")
        return ft.Container(
            padding=10,
            content=ft.Column(
                [
                    ft.Row(
                        [self.algorithm_dropdown, self.append_to_recipe_btn],
                        self.algorithm_listview,
                    )
                ]
            ),
        )

    @staticmethod
    def find_option_for_key_from_dropdown(
        dropdown: ft.Dropdown, key
    ) -> ft.dropdown.Option | None:
        for option in dropdown.options:
            if key == option.key:
                return option

    def add_algorithm_to_recipe(self):
        if self.check_algorithm_selected():
            listitem = ft.TextButton(
                text=self.find_option_for_key_from_dropdown(
                    self.algorithm_dropdown, self.algorithm_dropdown.value
                ),
                on_click=lambda: self.algorithm_listview.controls.remove(listitem),
            )
            self.algorithm_listview.controls.append(listitem)
            # self.algorithm_listview.update()

    def check_algorithm_selected(self) -> bool:
        if self.algorithm_dropdown.value is None:
            self.algorithm_dropdown.error_text = navi_texts[
                "error_no_algorithm_selected"
            ]
            self.algorithm_dropdown.update()
            return False
        else:
            return True


def main(page: ft.Page):
    def reload_recipedict(display_control: ft.Control):
        RECIPE_FILEPATH = Path(SCRIPT_DIR / HASHFUNC_LAYERS_RECIPES_FILENAME)
        if RECIPE_FILEPATH.exists():
            global recipedict
            recipedict = load_recipedict_from_json(RECIPE_FILEPATH)
            display_control.update()

    # -configure window-
    page.title = "Shepatra"
    # --
    making_hasheed_password_scene = MakingHashedPasswordScene()

    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(
                text=navi_texts["make_hashed_password"],
                content=making_hasheed_password_scene,
                icon=ft.icons.KEY,
            ),
            ft.Tab(
                text=navi_texts["go_to_recipe_making"],
                content=MakingRecipeScene(),
                icon=ft.icons.EDIT_NOTE,
            ),
            ft.Tab(
                text=navi_texts["settings"],
                content=SettingsScene(),
                icon=ft.icons.SETTINGS,
            ),
        ],
        on_change=lambda e: reload_recipedict(
            making_hasheed_password_scene.recipe_dropdown
        ),
        expand=1,
    )
    page.add(tabs)
    page.update()


if __name__ == "__main__":
    ft.app(target=main)
