import string
import time
from datetime import datetime

from django.conf import settings
from simplecrypt import encrypt, decrypt
import random

import sys
from cryptography.fernet import Fernet


# Generate encryption key
def passkey():
    # Generate key
    key = Fernet.generate_key()
    # Decoded encryption key to be stored
    keyDecoded = key.decode("utf-8")
    return keyDecoded


# Encrypt password using key
def passencrypt(mykey, mypassword):
    # Take key from stored form and convert it back to byte form
    keyRecovered = mykey.encode("utf-8")
    encryptKeyRecovered = Fernet(keyRecovered)
    # Encrypt password from byte form with str.encode
    encryptPass = encryptKeyRecovered.encrypt(mypassword)
    # Decode encrypted password to string form to be stored
    encryptPassDecoded = encryptPass.decode("utf-8")
    return encryptPassDecoded


# Decrypt password using key
def passdecrypt(mykey, mypasswordencrypted):
    # Take key from stored form and convert it back to byte form
    keyRecovered = mykey.encode("utf-8")
    encryptKeyRecovered = Fernet(keyRecovered)
    # Using recovered key unencrypt stored password
    encryptPassEncode = mypasswordencrypted.encode("utf-8")
    originalPassByte = encryptKeyRecovered.decrypt(encryptPassEncode)
    originalPass = originalPassByte.decode("utf-8")
    return originalPass


def my_encrypt(name):
    letters = string.ascii_lowercase

    strr = (''.join(random.choice(letters) for i in range(10)) + "|" + str(time.time()) + "|" + settings.CROSS_LOGIN_SECRET + "|" + name).encode()
    return passencrypt(settings.CROSS_LOGIN_KEY, strr)


def my_decrypt(data):
    return passdecrypt(settings.CROSS_LOGIN_KEY, data)
