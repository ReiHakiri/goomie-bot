import SPN.spn as spn

def pad(message: list[bool], width: int) -> list[bool]:
    """
    Based on SHA256 padding
    """
    result = message.copy()

    l_message = len(message)

    l_message = [b == '1' for b in bin(l_message)[2:]]

    result.append(True)

    while len(result) < width:
        result.append(False)

    for _ in range((len(result) + len(l_message)) % width):
        result.append(False)

    result.extend(l_message)

    return result

class SPHash:
    def __init__(self, cipher: spn.SPN) -> None:
        """
        Precondition:
        - cipher.size % 2 == 0
        """
        self.cipher = cipher

    def hash(self, message: list[bool]) -> list[bool]:
        stack = pad(message, self.cipher.size)
        stack = spn.split(stack, self.cipher.size // 2)
        stack.reverse()

        result = stack.pop()

        while len(stack) != 0:
            block = stack.pop()

            result.extend(block)

            result = self.cipher.encrypt(result)
            result = result[: len(result) // 2]

        return result