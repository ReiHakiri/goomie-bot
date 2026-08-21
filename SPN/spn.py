import SPN.permutations as permutations
import SPN.functions as functions

def split(l: list[bool], size: int) -> list[list[bool]]:
    result = []

    buffer = []

    for e in l:
        buffer.append(e)

        if len(buffer) == size:
            result.append(buffer.copy())
            buffer = []

    return result

def join(l: list[list[bool]]) -> list[bool]:
    result = []

    for e in l:
        result.extend(e)

    return result

def get_block(l: list[bool], i: int, width: int) -> list[bool]:
    return l[width * i: width * (i + 1)]

def replace_block(l1: list[bool], l2: list[bool], i: int, width: int) -> None:
    for j, e in enumerate(l2):
        x = width * i + j

        l1[x] = e

def block_xor(l1: list[bool], l2: list[bool]) -> None:
    for i in range(len(l1)):
        e1, e2 = l1[i], l2[i]

        l1[i] = e1 ^ e2

def repeat_block_xor(l1: list[bool], l2: list[bool], times: int, width: int) -> None:
    for time in range(times):
        block = get_block(l1, time, width)

        block_xor(block, l2)

        replace_block(l1, block, time, width)

def do_sbox(l: list[bool], sbox: dict[tuple[bool], tuple[bool]], times: int, width: int) -> None:
    for time in range(times):
        block = get_block(l, time, width)

        replace_block(l, list(sbox[tuple(block)]), time, width)

def do_pbox(l: list[bool], pbox: list[int]) -> None:
    permutations.apply_perm(l, pbox)

class SPN:
    def __init__(self, sbox: dict[tuple[bool], tuple[bool]], pbox: list[int], keys: list[list[bool]], n_rounds: int) -> None:
        self.sbox = sbox
        self.pbox = pbox
        self.keys = permutations.two_deep_list_copy(keys)
        self.n_rounds = n_rounds

        self.size = len(self.pbox)
        self.width = len(list(self.sbox.keys())[0])
        self.times = self.size // self.width

    def encrypt(self, plaintext: list[bool]) -> list[bool]:
        states = split(plaintext, self.size)

        result = []

        for state in states:
            for key in self.keys:
                repeat_block_xor(state, key, self.times, self.width)

                do_sbox(state, self.sbox, self.times, self.width)
                do_pbox(state, self.pbox)

            result.append(state)

        return join(result)

    def decrypt(self, ciphertext: list[bool]) -> list[bool]:
        inv_sbox = functions.inv_dict(self.sbox)
        inv_pbox = permutations.inv_perm(self.pbox)

        states = split(ciphertext, self.size)

        result = []

        for state in states:
            for key in reversed(self.keys):
                do_pbox(state, inv_pbox)
                do_sbox(state, inv_sbox, self.times, self.width)

                repeat_block_xor(state, key, self.times, self.width)

            result.append(state)

        return join(result)