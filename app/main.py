import ctypes
ctypes.windll.kernel32.SetConsoleTitleW("Warframe Relic Picker")
print(
    f"""

    ░██╗░░░░░░░██╗███████╗  ██████╗░███████╗██╗░░░░░██╗░█████╗░  ██████╗░██╗░█████╗░██╗░░██╗███████╗██████╗░
    ░██║░░██╗░░██║██╔════╝  ██╔══██╗██╔════╝██║░░░░░██║██╔══██╗  ██╔══██╗██║██╔══██╗██║░██╔╝██╔════╝██╔══██╗
    ░╚██╗████╗██╔╝█████╗░░  ██████╔╝█████╗░░██║░░░░░██║██║░░╚═╝  ██████╔╝██║██║░░╚═╝█████═╝░█████╗░░██████╔╝
    ░░████╔═████║░██╔══╝░░  ██╔══██╗██╔══╝░░██║░░░░░██║██║░░██╗  ██╔═══╝░██║██║░░██╗██╔═██╗░██╔══╝░░██╔══██╗
    ░░╚██╔╝░╚██╔╝░██║░░░░░  ██║░░██║███████╗███████╗██║╚█████╔╝  ██║░░░░░██║╚█████╔╝██║░╚██╗███████╗██║░░██║
    ░░░╚═╝░░░╚═╝░░╚═╝░░░░░  ╚═╝░░╚═╝╚══════╝╚══════╝╚═╝░╚════╝░  ╚═╝░░░░░╚═╝░╚════╝░╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝
    v1.0.0
"""
)

from time import sleep
from traceback import format_exc

import pygetwindow as gw

import mouse
import keyboard

from module.utils import take_screenshot, print_error
from module.ocr import get_recommended_relic, recommended_relic_box_lines
from module.find_position_on_image import (
    kmeans_v2 as find_position_on_image,
)


reference_image_path_dict = {
    "Lith": {
        "Intact": r"app/model/image/relic/lith/0_intact.png",
        "Exceptional": r"app/model/image/relic/lith/1_exceptional.png",
        "Flawless": r"app/model/image/relic/lith/2_flawless.png",
        "Radiant": r"app/model/image/relic/lith/3_radiant.png",
    },
    "Meso": {
        "Intact": r"app/model/image/relic/meso/0_intact.png",
        "Exceptional": r"app/model/image/relic/meso/1_exceptional.png",
        "Flawless": r"app/model/image/relic/meso/2_flawless.png",
        "Radiant": r"app/model/image/relic/meso/3_radiant.png",
    },
    "Neo": {
        "Intact": r"app/model/image/relic/neo/0_intact.png",
        "Exceptional": r"app/model/image/relic/neo/1_exceptional.png",
        "Flawless": r"app/model/image/relic/neo/2_flawless.png",
        "Radiant": r"app/model/image/relic/neo/3_radiant.png",
    },
    "Axi": {
        "Intact": r"app/model/image/relic/axi/0_intact.png",
        "Exceptional": r"app/model/image/relic/axi/1_exceptional.png",
        "Flawless": r"app/model/image/relic/axi/2_flawless.png",
        "Radiant": r"app/model/image/relic/axi/3_radiant.png",
    },
    "search_box": {
        "magnifly_glass": r"app/model/image/warframe_ui/search_box_1.png",
        "x": r"app/model/image/warframe_ui/search_box_2.png",
    },
    "button": {
        "yes": r"app/model/image/warframe_ui/yes_button.png",
    },
}


def click():
    sleep(0.05)
    mouse.press(button="left")
    sleep(0.05)
    mouse.release(button="left")


def relic_picker(relic):
    ## Check if Warframe window is active
    active_window = gw.getActiveWindow()
    if active_window and "Warframe" not in active_window.title:
        print_error("Error: Warframe window is inactive.")  # TODO: logging
        return

    ## Check for recommended relics overlay is pressent, retry 5 times
    max_retry = 5
    for i in range(max_retry + 1):
        ## Move cursor away
        mouse.move(0, 0)
        click()
        sleep(0.01)

        ## Take a screenshot (recommended relics overlay)
        screenshot = take_screenshot()

        ## OCR relic name selected one
        try:
            selected_relic = get_recommended_relic(screenshot=screenshot, relic=relic)
        except ValueError as err:
            print_error(f"Error: {str(err)}")  # TODO: logging
            return
        if selected_relic is not None:
            selected_relic = selected_relic.split(" ")
            break
        elif i < max_retry:
            print(
                f"Error: Unable to get recommended relic from overlay, retrying ({i+1}/{max_retry})"
            )  # TODO: loggin
            sleep(0.1)
        else:
            print_error("Error: Failed. (Is AlecaFrame running?)")  # TODO: logging
            return

    ## Find position of search box move mouse, click write selected relic era and name
    try:
        search_box_postiton = find_position_on_image(
            reference_image_path=reference_image_path_dict["search_box"][
                "magnifly_glass"
            ],
            search_image=screenshot,
            # debug_window=True,
        )
    except ValueError:
        try:
            search_box_postiton = find_position_on_image(
                reference_image_path=reference_image_path_dict["search_box"]["x"],
                search_image=screenshot,
                # debug_window=True,
            )
        except ValueError as err:
            print_error(
                f"Error: {str(err).format(thing_to_find='search box')}"
            )  # TODO: logging
            return
    mouse.move(round(search_box_postiton[0]), round(search_box_postiton[1]))
    click()
    keyboard.write(f"{selected_relic[0]} {selected_relic[1]}")

    ## Take a screenshot (relic search result)
    sleep(0.08)
    screenshot = take_screenshot()

    ## Find selected relic position and double click
    select_ref = reference_image_path_dict[selected_relic[0]][selected_relic[2]]
    try:
        relic_coordinate = find_position_on_image(
            reference_image_path=select_ref,
            search_image=screenshot,
            # debug_window=True,
        )
    except ValueError as err:
        print_error(
            f"Error: {str(err).format(thing_to_find='selected relic')}"
        )  # TODO: logging
        return
    mouse.move(round(relic_coordinate[0]), round(relic_coordinate[1]))
    click()
    click()

    print(
        f"Info: Selected {selected_relic[0]} {selected_relic[1]} {selected_relic[2]}"
    )  # TODO: logging


def exception_handeler(function, **args):
    try:
        function(**args)
    except Exception:
        print(format_exc())  # TODO: logging


def main():
    print("Info: Ready!")  # TODO: logging
    keyboard.add_hotkey(
        "F1", lambda: exception_handeler(function=relic_picker, relic=relic_1)
    )
    keyboard.add_hotkey(
        "F2", lambda: exception_handeler(function=relic_picker, relic=relic_2)
    )
    keyboard.add_hotkey(
        "F3", lambda: exception_handeler(function=relic_picker, relic=relic_3)
    )
    keyboard.add_hotkey(
        "F4", lambda: exception_handeler(function=relic_picker, relic=relic_4)
    )

    keyboard.wait()


if __name__ == "__main__":
    relic_1, relic_2, relic_3, relic_4 = recommended_relic_box_lines()
    main()
