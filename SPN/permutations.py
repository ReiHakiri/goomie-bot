from typing import Any
import random

NITER = 10 ** 4

def two_deep_list_copy(l: list[list[Any]]) -> list[list[Any]]:
    result = []

    for row in l:
        new_row = []

        for e in row:
            new_row.append(e)
        
        result.append(new_row)
    
    return result

def rand_perm_list(n: int) -> list[int]:
    result = list(range(n))

    random.shuffle(result)

    return result

def id_perm(n: int) -> list[int]:
    return list(range(n))

def inv_perm(l: list[int]) -> list[int]:
    """
    Precondition:
    - l is a permutation list
    """
    result = id_perm(len(l))

    for i, e in enumerate(l):
        result[e] = i
    
    return result

def apply_perm(l: list[Any], perm_l: list[int]) -> None:
    """
    Precondition:
    - perm_l is a permutation list
    """
    l_c = l.copy()

    for i in range(len(l)):
        j = perm_l[i]

        l[i] = l_c[j]

def get_order(l: list[int]) -> int:
    """
    Precondition:
    - l is a permutation list
    """
    curr = id_perm(len(l))
    target = curr.copy()

    result = 1

    apply_perm(curr, l)

    while curr != target:
        apply_perm(curr, l)
        result += 1
    
    return result

def rand_large_order_perm(n: int, n_iterations: int) -> tuple[list[int], int]:
    """
    Precondition:
    - n_iterations > 0
    """
    result = id_perm(n)
    order = 1

    for _ in range(n_iterations):
        curr = rand_perm_list(n)
        curr_order = get_order(curr)

        if curr_order > order:
            result = curr
            order = curr_order
    
    return result, order

def nat_to_perm(n: int, m: int) -> list[int]:
    """
    Precondition:
    - 0 <= n < m!
    """
    factorials = []

    for i in range(m):
        if i == 0:
            factorials.append(1)
        
        else:
            factorials.append(i * factorials[i - 1])

    result = []

    selections = list(range(m))

    while len(factorials) != 0:
        factorial = factorials.pop()

        selection = n // factorial
        result.append(selections.pop(selection))

        n %= factorial
    
    return result