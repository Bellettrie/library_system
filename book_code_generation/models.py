def standardize_code(cc: str):
    code = cc.replace(" ", "").replace(".", "")
    code_parts = code.split("-")
    if len(code_parts) > 2:
        try:
            code_parts[2] = str(float("0." + code_parts[2])).split(".")[1]
        except ValueError:
            pass
    return_value = code_parts[0]
    if len(code_parts) == 1:
        num = 0
        return_value = ""
        for char in code_parts[0]:
            if char in "0123456789":
                num *= 10
                num += int(char)
            else:
                if num > 0:
                    return_value += str.rjust(str(num), 6, "0")
                return_value += char
        if num > 0:
            return_value += str.rjust(str(num), 6, "0")
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
