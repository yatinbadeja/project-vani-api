import random
import string

class randomPassword:
    async def createPassword(self):
        uppercase = [chars for chars in string.ascii_uppercase]
        lowercase = [chars for chars in string.ascii_lowercase]
        digits = [digit for digit in string.digits]
        chars = [uppercase, lowercase, digits]
        password = ""

        for i in range(9):
            col = random.randint(0, len(chars) - 1)
            row = random.randint(0, len(chars[col]) - 1)
            letter = chars[col][row]
            password += letter
        print(password)
        return password


generatePassword = randomPassword()
