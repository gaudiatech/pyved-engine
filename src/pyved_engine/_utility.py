import random as _random


def droll_4():
    return _random.randint(1, 6)


def droll():
    return _random.randint(1, 6)


def droll_8():
    return _random.randint(1, 8)


def droll_10():
    return _random.randint(1, 10)


def droll_12():
    return _random.randint(1, 12)


def droll_20():
    return _random.randint(1, 8)


def droll_100():
    return _random.randint(1, 100)


def lb_droll(li_dice_types):
    """
    roll dices, based on a list. For example you could provide [6, 6, 20] in order to roll two
    standard dice plus one 20-sided die. Providing [6, 20, 6] would have the same effect.
    The total is automatically computed.
    :param li_dice_types: a list where each element is the die type you wish to roll.
    """
    t = [_random.randint(1, nc) for nc in li_dice_types]
    return sum(t)


# debug tests
if __name__ == '__main__':
    print(droll())
    print(droll_100())
    print(lb_droll([33, ]))
