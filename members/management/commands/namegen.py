import namegenerator
import names

consonant=('b','g','d','t','f','c','h','m','n','p','h','r','l','s','g','k','sh', 'ch')
vowel=('a','e','i','o','u')

import random

def SetRnd(name, count): #returns random letter, whether consonant or vowel
    IsValid = False
    while IsValid == False:
        if str(random.randint(1,2)) == "1":
            chosenChar = str(random.choice(consonant))
            IsValid = True
        else:
            chosenChar = str(random.choice(vowel))
            #checks whether the chosen char (vowel) is different to previous
            if (count > 0) and (str(chosenChar) != str(name[count-1])):
                IsValid = True
    return chosenChar


def generate_name():
    return namegenerator.gen().replace("-", " " )


def generate_full_name():
    return names.get_full_name()

#declares initial running
