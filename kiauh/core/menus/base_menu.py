# ======================================================================= #
#  Copyright (C) 2020 - 2024 Dominik Willner <th33xitus@gmail.com>        #
#                                                                         #
#  This file is part of KIAUH - Klipper Installation And Update Helper    #
#  https://github.com/dw-0/kiauh                                          #
#                                                                         #
#  This file may be distributed under the terms of the GNU GPLv3 license  #
# ======================================================================= #

from __future__ import annotations

import subprocess
import sys
import textwrap
from abc import abstractmethod, ABC
from typing import Dict, Union, Callable, Type

from core.menus import FooterType, NAVI_OPTIONS
from utils.constants import (
    COLOR_GREEN,
    COLOR_YELLOW,
    COLOR_RED,
    COLOR_CYAN,
    RESET_FORMAT,
)
from utils.logger import Logger


def clear():
    subprocess.call("clear", shell=True)


def print_header():
    line1 = " [ KIAUH ] "
    line2 = "Klipper Installation And Update Helper"
    line3 = ""
    color = COLOR_CYAN
    count = 62 - len(color) - len(RESET_FORMAT)
    header = textwrap.dedent(
        f"""
        /=======================================================\\
        | {color}{line1:~^{count}}{RESET_FORMAT} |
        | {color}{line2:^{count}}{RESET_FORMAT} |
        | {color}{line3:~^{count}}{RESET_FORMAT} |
        \=======================================================/
        """
    )[1:]
    print(header, end="")


def print_quit_footer():
    text = "Q) Quit"
    color = COLOR_RED
    count = 62 - len(color) - len(RESET_FORMAT)
    footer = textwrap.dedent(
        f"""
        |-------------------------------------------------------|
        | {color}{text:^{count}}{RESET_FORMAT} |
        \=======================================================/
        """
    )[1:]
    print(footer, end="")


def print_back_footer():
    text = "B) « Back"
    color = COLOR_GREEN
    count = 62 - len(color) - len(RESET_FORMAT)
    footer = textwrap.dedent(
        f"""
        |-------------------------------------------------------|
        | {color}{text:^{count}}{RESET_FORMAT} |
        \=======================================================/
        """
    )[1:]
    print(footer, end="")


def print_back_help_footer():
    text1 = "B) « Back"
    text2 = "H) Help [?]"
    color1 = COLOR_GREEN
    color2 = COLOR_YELLOW
    count = 34 - len(color1) - len(RESET_FORMAT)
    footer = textwrap.dedent(
        f"""
        |-------------------------------------------------------|
        | {color1}{text1:^{count}}{RESET_FORMAT} | {color2}{text2:^{count}}{RESET_FORMAT} |
        \=======================================================/
        """
    )[1:]
    print(footer, end="")


Option = Union[Callable, Type["BaseMenu"], "BaseMenu"]
Options = Dict[str, Option]


class BaseMenu(ABC):
    options: Options = None
    options_offset: int = 0
    default_option: Union[Option, None] = None
    input_label_txt: str = "Perform action"
    header: bool = True
    previous_menu: Union[Type[BaseMenu], BaseMenu] = None
    footer_type: FooterType = FooterType.BACK

    def __init__(self):
        if type(self) is BaseMenu:
            raise NotImplementedError("BaseMenu cannot be instantiated directly.")

    @abstractmethod
    def print_menu(self) -> None:
        raise NotImplementedError("Subclasses must implement the print_menu method")

    def print_footer(self) -> None:
        if self.footer_type is FooterType.QUIT:
            print_quit_footer()
        elif self.footer_type is FooterType.BACK:
            print_back_footer()
        elif self.footer_type is FooterType.BACK_HELP:
            print_back_help_footer()
        else:
            raise NotImplementedError("Method for printing footer not implemented.")

    def display_menu(self) -> None:
        # clear()
        if self.header:
            print_header()
        self.print_menu()
        self.print_footer()

    def validate_user_input(self, usr_input: str) -> Union[Option, str, None]:
        """
        Validate the user input and either return an Option, a string or None
        :param usr_input: The user input in form of a string
        :return: Option, str or None
        """
        usr_input = usr_input.lower()
        option = self.options.get(usr_input, None)

        # check if usr_input contains a character used for basic navigation, e.g. b, h or q
        # and if the current menu has the appropriate footer to allow for that action
        is_valid_navigation = self.footer_type in NAVI_OPTIONS
        user_navigated = usr_input in NAVI_OPTIONS[self.footer_type]
        if is_valid_navigation and user_navigated:
            return usr_input

        # if usr_input is None or an empty string, we execute the menues default option if specified
        if option is None or option == "" and self.default_option is not None:
            return self.default_option

        # user selected a regular option
        if option is not None:
            return option

        return None

    def handle_user_input(self) -> Union[Option, str]:
        """Handle the user input, return the validated input or print an error."""
        while True:
            print(f"{COLOR_CYAN}###### {self.input_label_txt}: {RESET_FORMAT}", end="")
            usr_input = input().lower()
            validated_input = self.validate_user_input(usr_input)

            if validated_input is not None:
                return validated_input
            else:
                Logger.print_error("Invalid input!", False)

    def run(self) -> None:
        """Start the menu lifecycle. When this function returns, the lifecycle of the menu ends."""
        while True:
            self.display_menu()
            choice = self.handle_user_input()

            if choice == "q":
                Logger.print_ok("###### Happy printing!", False)
                sys.exit(0)
            elif choice == "b":
                return
            else:
                self.execute_option(choice)

    def execute_option(self, option: Option) -> None:
        if option is None:
            raise NotImplementedError(f"No implementation for {option}")

        if isinstance(option, type) and issubclass(option, BaseMenu):
            self.navigate_to_menu(option, True)
        elif isinstance(option, BaseMenu):
            self.navigate_to_menu(option, False)
        elif callable(option):
            option()

    def navigate_to_menu(self, menu, instantiate: bool) -> None:
        """
        Method for handling the actual menu switch. Can either take in a menu type or an already
        instantiated menu class. Use instantiated menu classes only if the menu requires specific input parameters
        :param menu: A menu type or menu instance
        :param instantiate: Specify if the menu requires instantiation
        :return: None
        """
        menu = menu() if instantiate else menu
        menu.previous_menu = self
        menu.run()
