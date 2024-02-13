import os
from lib.tstrings import Tstr


class GraphViz:
    """
    Automated flowchart graphing using Graphviz. Basic structure:

    GraphVis
        |- .groups = [Group, Group, ...]
        |- .ungrouped_nodes = [Node, Node, ...]
        |- .edges = [Edge, Edge, ...]

    Call write_dot to create the GraphViz dot file.
    Call rendergraphs afterwords to create the png image.
    """
    def __init__(self):
        self.directory = ''
        self.name = ''
        self.title = ''
        self.ungrouped_nodes = []
        self.groups = []
        self.edges = []
        self.fontsize = {
            'title': 48,
            'node': 10,
            'group': 6,
        }
        self.outfile_contents = ''
        self.fontcolor = "black"

    def write_dot(self, vertical=True):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        orientation = ''
        if not vertical:
            orientation = '\trankdir="LR";\n'
        graphviz_start = Tstr('./lib/graphviz_template.txt')
        label = self.title
        fontcolor = self.fontcolor
        fontsize_title = str(self.fontsize['title'])
        fontsize_node = str(self.fontsize['node'])
        graphviz_start.eval(locals())
        self.outfile_contents = str(graphviz_start)

        id = 1
        for group in self.groups:
            group.id = id
            self.outfile_contents += str(group)
            id += 1

        for node in self.ungrouped_nodes:
            self.outfile_contents += str(node)

        self.outfile_contents += '\n\n//edges:\n'
        for edge in self.edges:
            self.outfile_contents += str(edge)

        self.outfile_contents += '\n}'

        target = self.directory + self.name + '.dot'
        with open(target, 'w') as outfile:
            outfile.write(self.outfile_contents)

    def rendergraphs(self):
        target = 'dot -Tpng -v -O ' + self.directory + self.name + '.dot'
        print(target)
        os.system(target)


class Group:
    """Group of Nodes"""
    def __init__(self):
        self.id = 0
        self.name = "missingname"
        self.fontcolor = "#92d0c1"
        self.color = "#92d0c1"
        self.fontsize = 24
        self.style = "rounded"
        self.nodes = []

    def __str__(self):
        nodestring = ''
        for node in self.nodes:
            nodestring += str(node)
        return (
            f'subgraph cluster{self.id} {{\n'
            f'label = "{self.name}";\n'
            f'fontsize={self.fontsize};\n'
            f'style="{self.style}";\n'
            f'color="{self.color}";\n'
            f'fontcolor="{self.fontcolor}";\n'
            f'{nodestring}'
            '}\n\n'
        )


class Node:
    def __init__(self):
        self.id = 'missingid'
        self.label = 'missinglabel'
        self.color = '#2d635b'
        self.fontcolor = '#2d635b'
        self.fillcolor = '#d2e7f2'
        self.fontname = 'Arial'
        self.shape = 'box'
        self.style = 'filled'
        self.width = 1
        self.height = 0.25

    def __str__(self):
        if len(self.label) > 0 and self.label[0] == "<":
            label = f'<{self.label}>'
        else:
            label = f'"{self.label}"'
        return (
            f'"{self.id}" [label={label} '
            f'color="{self.color}" fillcolor="{self.fillcolor}" fontcolor="{self.fontcolor}" '
            f'fontname="{self.fontname}" width="{self.width}" height="{self.height}" '
            f'shape="{self.shape}" style="{self.style}"];\n'
        )


class Edge:
    """Connection between Nodes"""
    def __init__(self):
        self.start = None
        self.end = None
        self.color = '#2d635b'
        self.arrowhead = 'none'
        self.double = False

    def __str__(self):
        double = ''
        if self.double:
            double = f' dir="both" arrowtail={self.arrowhead}'
        return (
            f'"{self.start}" -> "{self.end}" [color="{self.color}" arrowhead={self.arrowhead}{double}]\n'
        )
