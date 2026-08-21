from typing import Any
import SPN.permutations as permutations

def all_lists(domain: list[Any], n: int):
    if n == 0:
        yield []

    else:
        for l in all_lists(domain, n - 1):
            for element in domain:
                yield l + [element]

def rand_long_bij(domain: list[Any], n: int) -> dict[tuple[Any], tuple[Any]]:
    cycle = list(all_lists(domain, n))

    perm = permutations.rand_perm_list(len(cycle))

    permutations.apply_perm(cycle, perm)

    shifted_cycle = cycle[1:] + [cycle[0]]

    result = {}

    for key, value in zip(cycle, shifted_cycle):
        result[tuple(key)] = tuple(value)

    return result

def inv_dict(d: dict[Any, Any]) -> dict[Any, Any]:
    result = {}

    for key, value in d.items():
        result[value] = key

    return result