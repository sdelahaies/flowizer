#python drawDAG.py ../config/template_3.yaml ../outputs/bigflow.svg svg

import yaml
from graphviz import Digraph
import sys


def draw_dag(data, output, fmt='png',view=True):
    """Generate a directed graph visualization of a workflow configuration.

    This function creates a graphical representation of a workflow using Graphviz, displaying nodes with their names and types, and connecting them according to their defined relationships.

    Args:
        data (dict): Workflow configuration containing nodes and flow information.
        output (str): File path for the output graph visualization.
        fmt (str, optional): Output file format. Defaults to 'png'.
        view (bool, optional): Whether to display the generated graph visualization. Defaults to True.

    Returns:
        None: Generates a graph visualization file and optionally displays it.

    Raises:
        FileNotFoundError: If the output directory is not accessible.
        graphviz.ExecutableNotFound: If Graphviz is not installed on the system.
    """
    # Create a mapping between node IDs and names with types
    node_mapping = {str(list(node.keys())[0]): str(
        list(node.values())[0]) for node in data['nodes']}

    # Initialize the Digraph object
    dot = Digraph()

    # Add nodes to the Digraph with names and types on new lines, displayed in red
    for ninfo in node_mapping.values():
        nname, ntype = ninfo.split(',')
        nlabel = f'{nname}\n{ntype}'
        dot.node(nname, label=nlabel, type=ntype, style='filled', color='lightblue')

    # Add edges to the Digraph
    edges = set()
    for edge in data['flow']:
        sources, targets = edge.split('>>')
        sources = [node_mapping[s.strip()].split(',')[0]
                                        for s in sources.split(',')]
        targets = [node_mapping[t.strip()].split(',')[0]
                                        for t in targets.split(',')]

        for source in sources:
            for target in targets:
                edge_tuple = (source, target)
                if edge_tuple not in edges:  # Check for duplicate edges
                    edges.add(edge_tuple)
                    dot.edge(source, target)

    # Generate the digraph
    #dot.graph_attr.update({'rankdir': 'LR'})
    dot.format = fmt
    dot.render(outfile=output, view=view)
    #dot.save(output.replace('.png', '.gv'))
    dot.save(output.split('.')[0]+'.gv')

if __name__ == "__main__":
    if len(sys.argv) <= 3:
        exit("You need 2 argument: python drawDAG.py <path-to-yaml> <path-to-output> <format>")
    filename=sys.argv[1]
    output=sys.argv[2]
    fmt=sys.argv[3] if len(sys.argv) > 3 else 'png'
    with open(filename) as f:
        data=yaml.load(f, Loader=yaml.FullLoader)
    draw_dag(data, output,fmt)
