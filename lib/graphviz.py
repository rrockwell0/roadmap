import os
from lib.tstrings import Tstr

from random import randint


class GraphViz:
    """
    Automated flowchart graphing using Graphviz. Basic structure:

    GraphVis
        |- .groups = [Group, Group, ...]
        |- .ungrouped_nodes = [Node, Node, ...]
        |- .edges = [Edge, Edge, ...]

    Call write_dot to create the GraphViz dot file.
    Call rendergraphs afterwords to create the png image.

    Developed personally by Randy Rockwell copyright April 5th, 2020
    """
    def __init__(self):
        self.directory = ''
        self.name = ''
        self.title = ''
        self.subtitle = ''
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
        self.nodesep = '1'

    def write_dot(self, vertical=True):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        orientation = ''
        if not vertical:
            orientation = '\trankdir="LR";\n'
        graphviz_start = Tstr('./lib/graphviz_template.txt')
        label = self.title + '\n' + self.subtitle
        fontcolor = self.fontcolor
        fontsize_title = str(self.fontsize['title'])
        fontsize_node = str(self.fontsize['node'])
        nodesep = self.nodesep
        graphviz_start.eval(locals())
        self.outfile_contents = str(graphviz_start)

        for group in self.groups:
            self.outfile_contents += str(group)

        for node in self.ungrouped_nodes:
            self.outfile_contents += str(node)

        self.outfile_contents += '\n\n//edges:\n'
        for edge in self.edges:
            self.outfile_contents += str(edge)

        self.outfile_contents += '\n}'

        target = os.path.join(self.directory, self.name + '.dot')
        with open(target, 'w') as outfile:
            outfile.write(self.outfile_contents)

    def rendergraphs(self):
        target = f'dot -Tpng -v -O "{os.path.join(self.directory, self.name + ".dot")}"'
        print(target)
        os.system(target)


class Group:
    """Group of Nodes"""
    def __init__(self):
        self.id = randint(100000, 999999)
        self.name = "missingname"
        self.fontcolor = "#92d0c1"
        self.color = "#92d0c1"
        self.fontsize = 24
        self.style = "rounded"
        self.nodes = []
        self.groups = []

    def __str__(self):
        nodestring = ''
        groupstring = ''
        for node in self.nodes:
            nodestring += str(node)
        for group in self.groups:
            groupstring += str(group)
        return (
            f'subgraph cluster_{self.id} {{\n'
            f'label = "{self.name}";\n'
            f'fontsize={self.fontsize};\n'
            f'style="{self.style}";\n'
            f'color="{self.color}";\n'
            f'fontcolor="{self.fontcolor}";\n'
            f'{nodestring}'
            
            f'{groupstring}'
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
        self.post_text = ''

    def __str__(self):
        double = ''
        if self.double:
            double = f' dir="both" arrowtail={self.arrowhead}'
        return (
            f'"{self.start}" -> "{self.end}" [color="{self.color}" arrowhead={self.arrowhead}{double} {self.post_text}]\n'
        )
