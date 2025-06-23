from django import template

register = template.Library()

def before_last_dash(my_string: str):
    return "-".join(my_string.split("-")[:-1])


def num_get(my_string: str):
    return my_string.split("-")[-2]




register.filter('before_last_dash', before_last_dash)
register.filter('num_get', num_get)