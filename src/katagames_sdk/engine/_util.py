import re


def underscore_format(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def camel_case_format(string_ac_underscores):
    words = [word.capitalize() for word in string_ac_underscores.split('_')]
    return "".join(words)
