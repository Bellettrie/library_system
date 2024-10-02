import re
import unicodedata

_ligature_re = re.compile(r'LATIN (?:(CAPITAL)|SMALL) LIGATURE ([A-Z]{2,})')


def split_ligatures(s):
    """
    Split the ligatures in `s` into their component letters.
    """

    def untie(letter):
        try:
            m = _ligature_re.match(unicodedata.name(letter))
            if not m:
                return letter
            elif m.group(1):
                return m.group(2)
            else:
                return m.group(2)
        except ValueError:
            return ""

    return ''.join(untie(c) for c in s)


def normalize_str(strs):
    """ Normalizes string in such a way that when sorted it's in the order we want. It destroys accents and merges IJ. Only works for western-like names"""
    strs = split_ligatures(strs).upper().replace("IJ", "Y").replace("ø".upper(), "O")
    data = strs
    normal = unicodedata.normalize('NFKD', data).encode('ASCII', 'ignore')
    return normal.decode('ASCII')


def normalize_number(num):
    """
    Normalize the number. Due to dirty type magics this works both on integers, and strings.
    *Example*: 370 --> 37
    """
    return str(float('0.' + str(num)))[2:]


def get_number_for_code(code: str):
    """
    Get the number from a book_code
    :param code: A book_code
    :return: Eg. 37 from SF-T-37-lr1
    """
    code_parts = code.split("-")
    if len(code_parts) > 2:
        try:
            return int(str(float("0." + code_parts[2])).split(".")[1])
        except ValueError:
            try:
                return int(str(float("0." + code_parts[1])).split(".")[1])
            except ValueError:
                if "ABC" not in code_parts:
                    print("ERROR" + code)
                pass



def standardize_code(cc: str):
    """
    Turn code with strange numbers into standardized numbers:
    SF-T-370-lr1 ==> SF-T-37-lr1
    """
    if len(cc) > 0 and cc[0] == "V":
        cc = "N" + cc[1:]
    code = cc.replace(" ", "").replace(".", "")
    code_parts = code.split("-")
    if len(code_parts) > 2:
        try:
            code_parts[2] = str(float("0." + code_parts[2])).split(".")[1]
        except ValueError:
            pass
    return_value = code_parts[0]
    for i in range(1, len(code_parts)):
        c = code_parts[i]
        if i == len(code_parts) - 1:
            num = 0
            c = ""
            for char in code_parts[i]:
                if char in "0123456789":
                    num *= 10
                    num += int(char)
                else:
                    if num > 0:
                        c += str.rjust(str(num), 6, "0")
                    c += char
            if num > 0:
                c += str.rjust(str(num), 6, "0")
        return_value = return_value + "-" + c
    return return_value
