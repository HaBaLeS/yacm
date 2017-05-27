import os
#for color addon see
#https://en.wikipedia.org/wiki/ANSI_escape_code#Colors
debug_enabled = False
info_enabled = True

def print_with_prefix(prefix, msg):
    print(prefix +" " + msg)

def debug(msg):
    if debug_enabled:
        print_with_prefix("[d]", msg)

def error(msg):
    print_with_prefix("[e]", msg)

def success(msg):
    print_with_prefix("[X]", msg)

def info(msg):
    if info_enabled:
        print_with_prefix("[i]", msg)


def newline():
    print ""


def reset_screen():
    os.system('tput reset')

if __name__ == "__main__":
    #test stuff

    debug("Service Info Message")
    error("Service Error")
    success("tis is a success")