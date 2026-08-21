from typing import Callable, Any
import random
import SPN.permutations as permutations
import SPN.functions as functions
import SPN.spn as spn
import SPN.sphash as sphash

def rand_plaintext(n_blocks: int, size: int) -> list[bool]:
    result = []

    for _ in range(size * n_blocks):
        result.append(random.choice([False, True]))

    return result

def rand_keys(rounds: int, width: int) -> list[list[bool]]:
    result = []

    for _ in range(rounds):
        new_row = []

        for _ in range(width):
            new_row.append(random.choice([False, True]))

        result.append(new_row)

    return result

def rand_SPN(size: int, width: int, rounds: int) -> spn.SPN:
    rand_sbox = functions.rand_long_bij([False, True], width)
    rand_pbox = permutations.rand_perm_list(size)
    rand_keys_i = rand_keys(rounds, width)

    return spn.SPN(rand_sbox, rand_pbox, rand_keys_i, rounds)

def rand_bool_l(size: int) -> list[bool]:
    return [random.choice([False, True]) for _ in range(size)]

def rand_SPHash(hash_size: int, width: int, rounds: int) -> sphash.SPHash:
    cipher = rand_SPN(2 * hash_size, width, rounds)

    return sphash.SPHash(cipher)

BITS_TO_HEX = {
    (0, 0, 0, 0): '0',
    (0, 0, 0, 1): '1',
    (0, 0, 1, 0): '2',
    (0, 0, 1, 1): '3',
    (0, 1, 0, 0): '4',
    (0, 1, 0, 1): '5',
    (0, 1, 1, 0): '6',
    (0, 1, 1, 1): '7',
    (1, 0, 0, 0): '8',
    (1, 0, 0, 1): '9',
    (1, 0, 1, 0): 'A',
    (1, 0, 1, 1): 'B',
    (1, 1, 0, 0): 'C',
    (1, 1, 0, 1): 'D',
    (1, 1, 1, 0): 'E',
    (1, 1, 1, 1): 'F'
}

HEX_TO_BITS = functions.inv_dict(BITS_TO_HEX)

def hex_to_bool_l(s: str) -> list[bool]:
    result = []

    for hex in s:
        result.extend(list(HEX_TO_BITS[hex]))

    return result

def bool_l_to_hex(l: list[bool]) -> str:
    """
    Precondition:
    - len(l) % 4 == 0
    """
    bits_l = spn.split(l, 4)

    result = []

    for bits in bits_l:
        result.append(BITS_TO_HEX[tuple(bits)])

    return ''.join(result)

def sphash_to_hash_f(hash: sphash.SPHash) -> Callable[[Any], list[bool]]:
    def hash_f(message: int) -> list[bool]:
        bits = [b == '1' for b in bin(message)[2:]]

        return hash.hash(bits)

    return hash_f

BYTE_TO_BITS = {}

for n in range(256):
    byte = []

    for i in range(7, -1, -1):
        byte.append(bool(n & (1 << i)))

    BYTE_TO_BITS[n] = byte

def str_to_bool_l(s: str) -> list[bool]:
    bits = s.encode()

    result = []

    for n in bits:
        result.extend(BYTE_TO_BITS[n])

    return result

def str_to_int(s: str) -> int:
    bits = s.encode()

    return int.from_bytes(bits)