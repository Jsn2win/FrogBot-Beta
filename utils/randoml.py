def random_line(fname):
    lines = open(fname).read().splitlines()
    return random.choice(lines)