import namegenerator
import names
import random

consonant = ('b', 'g', 'd', 't', 'f', 'c', 'h', 'm', 'n', 'p', 'h', 'r', 'l', 's', 'g', 'k', 'sh', 'ch')
vowel = ('a', 'e', 'i', 'o', 'u')


def set_rnd(name, count):  # returns random letter, whether consonant or vowel
    chosen_char = ''
    is_valid = False
    while not is_valid:
        if str(random.randint(1, 2)) == "1":
            chosen_char = str(random.choice(consonant))
            is_valid = True
        else:
            chosen_char = str(random.choice(vowel))
            # checks whether the chosen char (vowel) is different to previous
            if (count > 0) and (str(chosen_char) != str(name[count - 1])):
                is_valid = True
    return chosen_char


def generate_name():
    return namegenerator.gen().replace("-", " ")


def generate_full_name():
    return names.get_full_name()

# declares initial running
