import random as _random


def droll():
    return _random.randint(1, 6)


def droll_4():
    return _random.randint(1, 4)


def droll_8():
    return _random.randint(1, 8)


def droll_10():
    return _random.randint(1, 10)


def droll_12():
    return _random.randint(1, 12)


def droll_20():
    return _random.randint(1, 20)


def droll_100():
    return _random.randint(1, 100)


def custom_droll(li_dice_types) -> list:
    """
    Rolls several dices, based on a list. For example you can provide [6, 6, 20] in order to roll two
    standard dices plus one 20-sided die
    :param li_dice_types: for example you can provide [6, 6, 20]
    :return: a list of values
    """
    per_dice_values = [_random.randint(1, nc) for nc in li_dice_types]
    return per_dice_values


# debug tests
if __name__ == '__main__':
    print(droll())
    print(droll_20())
    print(custom_droll([20, 6, 4]))
