from random import choice

def random_line(fname):
    lines = open(fname).read().splitlines()
    return choice(lines)