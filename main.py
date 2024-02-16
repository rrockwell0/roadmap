import os
import csv
from lib.graphviz import GraphViz, Group, Node, Edge

local_db = 'db.sqlite'


def build_full_diagram():
    data = {}
    gv = GraphViz()
    gv.name = 'rd'
    gv.title = 'LIMS Roadmap Detail'
    gv.fontcolor = 'orange'
    gv.directory = os.path.join('c:', os.sep, 'Users', 'Randy Rockwell', 'Desktop', 'roadmap_output')

    folder = os.path.join('c:', os.sep, 'Users', 'Randy Rockwell', 'Downloads')
    for file in os.listdir(folder):
        if '.tsv' in file and 'LIMS Roadmap Function List' in file:
            file_target = os.path.join(folder, file)
            with open(file_target) as infile:
                csvfile = csv.reader(infile, delimiter="\t")
                for row in csvfile:
                    uid = row[0]
                    if uid.lower() != 'id':
                        feature = row[1]
                        function = row[2]
                        prerequisites = row[3]
                        if feature == '':
                            gv.ungrouped_nodes += [define_node(uid, function)]
                        if feature not in data:
                            g = Group()
                            g.fontcolor = 'darkorange'
                            g.name = feature
                            g.color = 'grey'
                            data[feature] = g
                        g = data[feature]
                        g.nodes += [define_node(uid, function)]
                        for req in prerequisites.split(','):
                            if req.strip() != '':
                                e = Edge()
                                e.start = req.strip()
                                e.end = uid
                                e.arrowhead = 'normal'
                                e.color = 'orange'
                                gv.edges += [e]
            os.remove(file_target)
    for name, group in data.items():
        gv.groups += [group]
    gv.write_dot(vertical=False)
    gv.rendergraphs()


def define_node(uid, function):
    n = Node()
    n.id = uid
    n.label = function
    n.color = 'orange'
    n.fillcolor = 'white'
    n.fontcolor = 'black'
    return n


def main():
    build_full_diagram()


if __name__ == '__main__':
    main()
