import os

import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt

def create_graph(input_path_nodes,input_path_lines):
 
    df_nodes = pd.read_csv(input_path_nodes)
    df_lines = pd.read_csv(input_path_lines)

    graph = nx.Graph()

    nodes = list(df_nodes['Nodes'])
    edges = list(zip(df_lines['From'],df_lines['To']))
    pos = df_nodes.set_index('Nodes')[['pos_x', 'pos_y']].T.apply(tuple).to_dict()
    pos= {x: tuple(y.values()) for x, y in pos.items()}

    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)

    nx.draw(graph, pos=pos, with_labels = True)
    plt.show()

    return graph


if __name__ == '__main__':

    # Get the root directory path
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_data_dir = os.path.join(root_dir, '..')

    input_path_nodes = os.path.join(raw_data_dir, 'data', 'processed', 'nodes_33.csv')
    input_path_lines = os.path.join(raw_data_dir, 'data', 'processed', 'lines_33.csv')

    create_graph(input_path_nodes,input_path_lines)