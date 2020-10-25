import getopt
import sys
import requests
from enum import Enum

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


def print_choose_function():
    print("Choose Function:")
    print_functions()


def print_functions():
    # // 0 - 12 Hour Clock -
    # // 1 - 24 Hour Clock -
    # // 2 - Date -
    # // 3 - HourMin Countdown - offset in minutes
    # // 4 - Day Countdown  - offset
    # // 5 - HourMin timer - offset in minutes
    # // 6 - MinSec Timer - offset in seconds
    # // 7 - Alt Timezone - offset in minutes
    print("\t 0 - 12 Hour Clock")
    print("\t 1 - 24 Hour Clock")
    print("\t 2 - Date")
    print("\t 3 - Hour Minute Countdown")
    print("\t 4 - Day Countdown")
    print("\t 5 - Hour Minute Timer")
    print("\t 6 - Minute Second Timer")
    print("\t 7 - Alternate Timezone")


def get_parameter(func):

    user_input = ""

    if func == MINUTE_COUNTDOWN:
        user_input = input(" How many minutes for the countdown: ")
    elif func == DAY_COUNTDOWN:
        user_input = input(" Ordinal number of the day to count down to: ")
    elif func == MINUTE_TIMER:
        user_input = input(" How many minutes for the timer: ")
    elif func == SECOND_TIMER:
        user_input = input(" How many seconds for the timer: ")
    elif func == TIMEZONE:
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
    # static const uint8_t FunctionCodeIndex = 0;
    # static const uint8_t DutyCycleIndex = 1;
    # static const uint8_t ParameterHigh = 2;
    # static const uint8_t ParamterLow = 3;
    # static const uint8_t RGB_Red = 4;
    # static const uint8_t RGB_Green = 5;
    # static const uint8_t RGB_Blue = 6;

    if offset == "":
        offset = "0"

    command_ints = [func, int(dc), int(offset) >> 8, int(offset) & 0xFF, int(red), int(green), int(blue)]

    return bytes(command_ints)


def get_one_user_command():
    # Print menu to user
    print_choose_function()
    function_choice = int(input("> "))
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

    # build command and enqueue
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
        print("clockConfig.py -a <URL>")
        sys.exit()
    elif o in ("-a", "--address"):
        URL = a

cmd = get_command_bytes(get_user_commands())


# send or add more

headers = {'Content-Type': 'application/octet-stream'}
response = requests.post(URL, data=cmd, headers=headers)

print("\n", response.status_code)


