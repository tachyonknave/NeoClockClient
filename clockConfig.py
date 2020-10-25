import getopt
import sys
from enum import Enum

import requests


class FuncEnum(Enum):
    TWELVE_CLOCK = 0
    TWENTY_FOUR_CLOCK = 1
    DATE_CLOCK = 2
    MINUTE_COUNTDOWN = 3
    DAY_COUNTDOWN = 4
    MINUTE_TIMER = 5
    SECOND_TIMER = 6
    TIMEZONE = 7


class MenuEnum(Enum):
    ANOTHER = 0
    LIST = 1
    DISPLAY = 2
    SEND = 3
    QUIT = 4


def get_function_choice():
    print("Choose Function:")
    print("\t 0 - 12 Hour Clock")
    print("\t 1 - 24 Hour Clock")
    print("\t 2 - Date")
    print("\t 3 - Hour Minute Countdown")
    print("\t 4 - Day Countdown")
    print("\t 5 - Hour Minute Timer")
    print("\t 6 - Minute Second Timer")
    print("\t 7 - Alternate Timezone")

    return int(input("> "))


def get_parameter(func):

    func_code = FuncEnum(func)
    user_input = ""

    if func_code == FuncEnum.MINUTE_COUNTDOWN:
        user_input = input(" How many minutes for the countdown: ")
    elif func_code == FuncEnum.DAY_COUNTDOWN:
        user_input = input(" Ordinal number of the day to count down to: ")
    elif func_code == FuncEnum.MINUTE_TIMER:
        user_input = input(" How many minutes for the timer: ")
    elif func_code == FuncEnum.SECOND_TIMER:
        user_input = input(" How many seconds for the timer: ")
    elif func_code == FuncEnum.TIMEZONE:
        user_input = input(" How many minutes offset for the timezone: ")

    return user_input


def get_colors():
    red = input(" Red: ")
    green = input(" Green: ")
    blue = input(" Blue: ")

    return red, green, blue


def get_duty_cycle():
    return input(" For how many seconds to display this function: ")


def get_menu_option():
    print("\t0 - Add another function")
    print("\t1 - List functions")
    print("\t2 - Display current command")
    print("\t3 - Send Command")
    print("\t4 - Quit")

    return int(input(" >"))


def build_command(func, dc, red, green, blue, offset):
    # From server code:
    #  FunctionCodeIndex = 0;
    #  DutyCycleIndex = 1;
    #  ParameterHigh = 2;
    #  ParameterLow = 3;
    #  RGB_Red = 4;
    #  RGB_Green = 5;
    #  RGB_Blue = 6;

    if offset == "":
        offset = "0"

    command_ints = [func, int(dc), int(offset) >> 8, int(offset) & 0xFF, int(red), int(green), int(blue)]

    return bytes(command_ints)


def get_one_user_command():

    # Print menu to user
    function_choice = get_function_choice

    # user selects

    # ask parameters
    # value
    parameter = ""
    if function_choice in range(3, 7):
        parameter = get_parameter(function_choice)
    # time
    duty_cycle = get_duty_cycle()

    # color
    r, g, b = get_colors()

    # build command
    return build_command(function_choice, duty_cycle, r, g, b, parameter)


def get_user_commands():

    # Get First Command
    command_list = [get_one_user_command()]

    menu_loop = True

    while menu_loop:
        menu_option = MenuEnum(get_menu_option())

        if menu_option == MenuEnum.QUIT:
            sys.exit()
        elif menu_option == MenuEnum.ANOTHER:
            command_list.append(get_one_user_command())
        elif menu_option == MenuEnum.SEND:
            menu_loop = False

    return command_list


def get_command_bytes(cmd_list):

    body_bytes = []

    for c in cmd_list:
        body_bytes.extend(c)

    return bytes(body_bytes)


def send_commands(web_address, command_bytes):
    headers = {'Content-Type': 'application/octet-stream'}
    response = requests.post(web_address, data=command_bytes, headers=headers)

    print("\n", response.status_code)


###############################################################################
###############################################################################
# get URL from args
if len(sys.argv) < 2:
    print("Need URL parameter")
    exit(1)

URL = ""
try:
    opts, args = getopt.getopt(sys.argv[1:], "ha:", ["help", "address="])
except getopt.GetoptError:
    print("clockConfig.py -a <URL>")
    sys.exit(2)

for o, a in opts:
    if o == "-h":
        print("clockConfig.py -a http://<URL>")
        sys.exit()
    elif o in ("-a", "--address"):
        URL = a

send_commands(URL, get_command_bytes(get_user_commands()))
