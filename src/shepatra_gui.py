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


def recipedict_options_for_dropdown() -> list[ft.dropdown.Option]:
    return [
        ft.dropdown.Option(key=recipe_name, text=recipe_name)
        for recipe_name in recipedict.keys()
    ]


recipedict_dropdown = ft.Dropdown(
    options=recipedict_options_for_dropdown(),
    bgcolor=ft.colors.WHITE12,
    border_color=ft.colors.WHITE,
    expand=True,
)

new_recipe = HashFuncLayersRecipe(recipe=[], is_variable_length_algorithm_only=False)

# --


def making_hashed_password_tab(page: ft.Page) -> ft.Tab:
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
    password_inputfield_header = ft.Text(navi_texts["submit_with_enter"] + ":")
    password_inputfield = ft.TextField(
        hint_text=navi_texts["input_password"],
        bgcolor=ft.colors.WHITE10,
        border_color=ft.colors.WHITE,
        expand=True,
        on_submit=make_password_hashed_on_enter,
    )
    hash_outputfield = ft.TextField(
        hint_text=navi_texts["hash_value_output_is_here"],
        read_only=True,
        multiline=True,
        expand=True,
    )
    return ft.Tab(
        text=navi_texts["make_hashed_password"],
        content=ft.Column(
            [
                ft.Column(
                    [
                        ft.Row(
                            controls=[
                                recipedict_dropdown_header,
                                recipedict_dropdown,
                            ],
                        ),
                        ft.Row(
                            controls=[
                                password_inputfield_header,
                                password_inputfield,
                            ],
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),
                hash_outputfield,
            ],
        ),
    )


def making_recipe_tab(page: ft.Page) -> ft.Tab:
    def add_algorithm_on_click(e):
        if algorithm_dropdown.value is None:
            algorithm_dropdown.error_text = navi_texts["error_no_algorithm_selected"]
            algorithm_dropdown.update()
            return
        else:
            algorithm_dropdown.error_text = None
            algorithm_dropdown.update()
        new_recipe["recipe"].append(HashFuncName[algorithm_dropdown.value])
        recipelist_item = ft.TextButton((algorithm_dropdown.value))

        def remove_recipelist_item(e):
            listview_for_recipe.controls.remove(recipelist_item)
            new_recipe["recipe"].remove(HashFuncName[recipelist_item.text])
            listview_for_recipe.update()

        recipelist_item.on_click = remove_recipelist_item
        listview_for_recipe.controls.append(recipelist_item)
        listview_for_recipe.update()

    def recipe_confirmed_on_click(e):
        print(recipe_name_inputfield.value)
        if recipe_name_inputfield.value:
            recipedict[recipe_name_inputfield.value] = new_recipe
            store_recipedict_to_json(
                SCRIPT_DIR / HASHFUNC_LAYERS_RECIPES_FILENAME,
                recipedict,
            )
            recipedict_dropdown.options = recipedict_options_for_dropdown()
            recipedict_dropdown.update()
            update_to_recipe_confirmed_dialog(submit_dialog)
            page.update()

    recipe_name_inputfield = ft.TextField(
        hint_text=navi_texts["name_of_recipe"], on_submit=recipe_confirmed_on_click
    )

    def make_submit_dialog() -> ft.AlertDialog:
        return ft.AlertDialog(
            title=ft.Text(navi_texts["give_name_to_recipe"]),
            actions=[
                recipe_name_inputfield,
                ft.ElevatedButton(
                    navi_texts["submit"],
                    expand=True,
                    on_click=recipe_confirmed_on_click,
                ),
            ],
        )

    def update_to_submit_dialog(dialog: ft.AlertDialog):
        dialog = make_submit_dialog()
        dialog.update

    submit_dialog = make_submit_dialog()

    def open_submit_dialog_on_click(e):
        if new_recipe["recipe"]:
            page.dialog = submit_dialog
            submit_dialog.open = True
            page.update()

    def close_submit_dialog_on_click(e):
        submit_dialog.open = False
        update_to_submit_dialog(submit_dialog)
        page.update()

    def update_to_recipe_confirmed_dialog(dialog: ft.AlertDialog) -> ft.AlertDialog:
        dialog.title = ft.Text(
            navi_texts["recipe_generated"], color=ft.colors.GREEN_ACCENT_200
        )
        dialog.actions = [
            ft.ElevatedButton(
                navi_texts["close"],
                expand=True,
                on_click=close_submit_dialog_on_click,
            ),
        ]
        dialog.update()

    algorithm_dropdown = ft.Dropdown(
        options=[
            ft.dropdown.Option(hashfuncname.name) for hashfuncname in HashFuncName
        ],
        expand=True,
        bgcolor=ft.colors.WHITE12,
        border_color=ft.colors.WHITE,
        hint_text=navi_texts["select_algorithm"],
    )
    btn_to_add_algorithm = ft.IconButton(
        icon=ft.icons.ADD,
        icon_color="blue400",
        tooltip=navi_texts["add_algorithm"],
        on_click=add_algorithm_on_click,
    )
    btn_to_submit = ft.ElevatedButton(
        navi_texts["submit_recipe"], on_click=open_submit_dialog_on_click
    )
    listview_for_recipe = ft.ListView(
        height=200,
        auto_scroll=True,
    )
    return ft.Tab(
        text=navi_texts["go_to_recipe_making"],
        content=ft.Column(
            [
                ft.Row(
                    [
                        algorithm_dropdown,
                        btn_to_add_algorithm,
                    ]
                ),
                listview_for_recipe,
                btn_to_submit,
            ],
        ),
    )


def main(page: ft.Page):
    # -configure window-
    page.title = "Shepatra"
    page.window_width = 522
    page.window_height = 440
    page.window_resizable = False
    # --

    tabs = ft.Tabs(
        indicator_padding=11,
        selected_index=1,
        tabs=[making_hashed_password_tab(page), making_recipe_tab(page)],
        expand=1,
    )

    page.add(tabs)
    page.update()


if __name__ == "__main__":
    ft.app(target=main)
