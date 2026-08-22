import random
import netgraph
import matplotlib.pyplot as plt

def path_edges(path: list[int]) -> set[tuple[int, int]]:
    if len(path) == 0:
        return []

    if len(path) == 1:
        raise SyntaxError()

    first = path[:-1]
    second = path[1:]

    result = set()

    for e1, e2 in zip(first, second):
        result.add((e1, e2))

    return result

def graph_to_edge_set(g: list[set[int]]) -> set[tuple[int, int]]:
    result = set()

    for i, s in enumerate(g):
        for e in s:
            result.add((i, e))

    return result

def graph_path_image(g: list[set[int]],
                     path: list[int],
                     path_color: str,
                     node_color: str) -> None:
    g_edges = graph_to_edge_set(g)

    p_edges = path_edges(path)

    edge_coloring = {edge: path_color 
                   if edge in p_edges else 'lightgray'
                   for edge in g_edges}

    path_nodes = set(path)

    node_coloring = {node: node_color
                   if node in path_nodes else 'blue'
                   for node in range(len(g))}

    netgraph.Graph(g_edges,
                   node_color = node_coloring,
                   edge_color = edge_coloring)

    plt.axis('off')
    plt.savefig(f'graph{random.randrange(0, 10 ** 5)}.png')