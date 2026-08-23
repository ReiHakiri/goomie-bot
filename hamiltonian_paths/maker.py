import hamiltonian_paths.graphs as graphs
import hamiltonian_paths.permutations as permutations

def get_full_path(n: int) -> list[int]:
    result = list(range(n))

    perm = permutations.rand_perm_list(n)

    permutations.apply_perm(result, perm)

    return result

def path_graph(path: list[int]) -> list[set[int]]:
    if len(path) == 0:
        return []

    result = graphs.empty_graph(len(path))

    for i in range(len(path) - 1):
        result[path[i]].add(path[i + 1])

    return result

def graph_union(g1: list[set[int]], g2: list[set[int]]) -> list[set[int]]:
    """
    Precondition:
    - len(g1) == len(g2)
    """
    result = []

    for edges1, edges2 in zip(g1, g2):
        result.append(edges1 | edges2)

    return result

def rand_hp_graph(n: int, p: float) -> tuple[list[int], list[set[int]]]:
    path = get_full_path(n)

    graph = path_graph(path)

    rand_graph = graphs.rand_graph(n, p)

    graph = graph_union(graph, rand_graph)

    return path, graph

def shift_up(g: list[set[int]]) -> list[set[int]]:
    result = []

    for s in g:
        new_neighbors = set()

        for e in s:
            new_neighbors.add(e + 1)

        result.append(new_neighbors)

    return result

def for_pasting(g: list[set[int]], name: str = 'g') -> str:
    return f'array [1.. {len(g)}] of set of 1..{len(g)}: {name} = {shift_up(g)};'

def is_path(g: list[set[int]], start: int, end: int, path: list[int]) -> bool:
    if len(path) == 0:
        return False

    if path[0] != start:
        return False

    if path[-1] != end:
        return False

    for e in path:
        if not (0 <= e < len(g)):
            return False

    for i in range(len(path) - 1):
        if path[i + 1] not in g[path[i]]:
            return False

    return True

def is_hamiltonian_path(g: list[set[int]], start: int, end: int, path: list[int]) -> bool:
    if not is_path(g, start, end, path):
        return False

    if len(set(path)) != len(g):
        return False

    return True