# ======================================================================= #
#  Copyright (C) 2020 - 2024 Dominik Willner <th33xitus@gmail.com>        #
#                                                                         #
#  This file is part of KIAUH - Klipper Installation And Update Helper    #
#  https://github.com/dw-0/kiauh                                          #
#                                                                         #
#  This file may be distributed under the terms of the GNU GPLv3 license  #
# ======================================================================= #

import textwrap
from typing import Type, Optional

from components.klipper_firmware.menus.klipper_build_menu import (
    KlipperBuildFirmwareMenu,
)
from components.klipper_firmware.menus.klipper_flash_menu import (
    KlipperFlashMethodMenu,
    KlipperSelectMcuConnectionMenu,
)
from core.menus import Option
from core.menus.base_menu import BaseMenu
from utils.constants import COLOR_YELLOW, RESET_FORMAT


# noinspection PyUnusedLocal
class AdvancedMenu(BaseMenu):
    def __init__(self, previous_menu: Optional[Type[BaseMenu]] = None):
        super().__init__()
        self.previous_menu = previous_menu

    def set_previous_menu(self, previous_menu: Optional[Type[BaseMenu]]) -> None:
        from core.menus.main_menu import MainMenu

        self.previous_menu: Type[BaseMenu] = (
            previous_menu if previous_menu is not None else MainMenu
        )

    def set_options(self):
        self.options = {
            "3": Option(method=self.build, menu=True),
            "4": Option(method=self.flash, menu=False),
            "6": Option(method=self.get_id, menu=False),
        }

    def print_menu(self):
        header = " [ Advanced Menu ] "
        color = COLOR_YELLOW
        count = 62 - len(color) - len(RESET_FORMAT)
        menu = textwrap.dedent(
            f"""
            /=======================================================\\
            | {color}{header:~^{count}}{RESET_FORMAT} |
            |-------------------------------------------------------|
            | Repo Rollback:                                        |
            |  1) [Klipper]                                         |
            |  2) [Moonraker]                                       |
            |                                                       |
            | Klipper Firmware:                                     |
            |  3) [Build]                                           |
            |  4) [Flash]                                           |
            |  5) [Build + Flash]                                   |
            |  6) [Get MCU ID]                                      |   
            """
        )[1:]
        print(menu, end="")

    def build(self, **kwargs):
        KlipperBuildFirmwareMenu(previous_menu=self.__class__).run()

    def flash(self, **kwargs):
        KlipperFlashMethodMenu(previous_menu=self.__class__).run()

    def get_id(self, **kwargs):
        KlipperSelectMcuConnectionMenu(
            previous_menu=self.__class__,
            standalone=True,
        ).run()
