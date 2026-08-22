import random

def empty_graph(n: int) -> list[set[int]]:
    """
    Precondition:
    - n > 0
    """
    return [set() for _ in range(n)]

def rand_graph(n: int, p: float) -> list[set[int]]:
    """
    Precondition:
    - n > 0
    - 0 <= p <= 1
    """
    result = empty_graph(n)

    for i in range(n):
        for j in range(n):
            if i == j:
                continue

            sample = random.random()

            if sample <= p:
                result[i].add(j)
    
    return result

def rand_k_out_graph(n: int, k: int) -> list[set[int]]:
    """
    Precondition:
    - n > 0
    - n > k
    - k >= 0
    """
    nodes = list(range(n))

    result = empty_graph(n)

    for i in range(n):
        result[i] = set(random.sample(nodes[:i] + nodes[i + 1:], k))
    
    return result

def rand_undirected_graph(n: int, p: float) -> list[set[int]]:
    """
    Precondition:
    - n > 0
    - 0 <= p <= 1
    """
    result = empty_graph(n)

    for i in range(n):
        for j in range(i):
            sample = random.random()

            if sample <= p:
                result[i].add(j)
                result[j].add(i)

    return result

def rand_walk(graph: list[set[int]], n: int) -> list[int]:
    result = []

    curr = random.randrange(0, len(graph))

    for _ in range(n):
        result.append(curr)

        curr = random.choice(result[curr])
    
    return result