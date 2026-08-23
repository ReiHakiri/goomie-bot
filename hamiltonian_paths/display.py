import random
import netgraph
import matplotlib.pyplot as plt

def path_edges(path: list[int]) -> list[tuple[int, int]]:
    if len(path) == 0:
        return []

    if len(path) == 1:
        raise SyntaxError()

    first = path[:-1]
    second = path[1:]

    result = []

    for e1, e2 in zip(first, second):
        result.append((e1, e2))

    return result

def graph_to_edge_list(g: list[set[int]]) -> list[tuple[int, int]]:
    result = []

    for i, s in enumerate(g):
        for e in s:
            result.append((i, e))

    return result

def graph_image(g: list[set[int]], folder: str) -> str:
    g_edges = graph_to_edge_list(g)

    node_coloring = {node: 'lightblue' for node in range(len(g))}

    netgraph.Graph(g_edges,
                   node_color = node_coloring,
                   arrows = True,
                   node_labels = True,
                   edge_width = 0.6,
                   arrowsize = 8)

    plt.axis('off')

    result = folder + f'graph{random.randrange(0, 10 ** 5)}.png'

    plt.savefig(result)
    plt.close()

    return result

def graph_path_image(g: list[set[int]],
                     path: list[int],
                     path_color: str,
                     node_color: str,
                     folder: str) -> str:
    g_edges = graph_to_edge_list(g)

    p_edges = path_edges(path)

    edge_coloring = {edge: path_color 
                   if edge in p_edges else 'lightgray'
                   for edge in g_edges}

    path_nodes = set(path)

    node_coloring = {node: node_color
                   if node in path_nodes else 'lightblue'
                   for node in range(len(g))}

    netgraph.Graph(g_edges,
                   node_color = node_coloring,
                   edge_color = edge_coloring,
                   arrows = True,
                   node_labels = True,
                   edge_width = 0.6,
                   arrowsize = 8)

    plt.axis('off')

    result = folder + f'graph{random.randrange(0, 10 ** 5)}.png'

    plt.savefig(result)
    plt.close()

    return result