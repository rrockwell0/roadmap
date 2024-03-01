import os
import csv
import sqlite3
from datetime import date
from lib.graphviz import GraphViz, Group, Node, Edge
from lib.db_tools import record_feature_id

# todo: find all prereqs where release <= prereq release: message and red arrow?

local_db = 'db.sqlite'

color_scheme = {
    '': 'pink',
    'Placeholder': '#c194ff',
    'Planned': '#ffd8ab',
    'In Progress': '#a6bfff',
    'Complete': '#9fd6ac',
}


def load_data(file_target_a):
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS nodes;")
    cur.execute("DROP TABLE IF EXISTS edges;")
    cur.execute("DROP TABLE IF EXISTS feature_edges;")
    cur.execute("DROP TABLE IF EXISTS feature_ids;")
    cur.execute("CREATE TABLE nodes(id text, function text, feature text, status text, theme text, target_release text);")
    cur.execute("CREATE TABLE edges(node_from text, node_to text);")
    cur.execute("CREATE TABLE feature_edges(feature_from text, feature_to text);")
    cur.execute("CREATE TABLE feature_ids(feature text, uid text);")
    conn.commit()

    with open(file_target_a) as infile:
        csvfile = csv.reader(infile, delimiter="\t")
        for row in csvfile:
            uid = row[0]
            if uid.lower() != 'id':
                theme = row[1]
                feature = row[2]
                function = row[3]
                prerequisites = row[4]
                status = row[5]
                target_release = row[6]
                cur.execute(f"INSERT INTO nodes VALUES('{uid}', '{function}' , '{feature}', '{status}', '{theme}', '{target_release}');")
                for req in prerequisites.split(','):
                    if req.strip() != '':
                        cur.execute(f"INSERT INTO edges VALUES('{req.strip()}', '{uid.strip()}');")
    conn.commit()
    conn.close()


def check_data():
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    messages = []

    # feature split across target_releases
    query = """select feature, trc from (
               select feature, count(target_release) trc
               from (select distinct feature, target_release from nodes) alpha
               group by feature) beta
               where trc > 1;"""
    for result in cur.execute(query):
        messages += [f"Feature {result[0]} is split across {result[1]} features."]
    conn.close()
    return messages


def print_messages(messages):
    print(f"There are {len(messages)} data errors.")
    if len(messages) > 0:
        print("Please resolve them to ensure correct diagrams.\n")
    for message in messages:
        print(message)


def build_double_group_diagram(grouping1=None, grouping2=None):
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()

    gv = GraphViz()
    gv.name = 'LIMS-Roadmap-Detail'
    gv.title = 'LIMS Roadmap Detail'
    if grouping1:
        gv.name += f'-by-{grouping1.title()}'
        gv.title += f' by {grouping1.title()}'
    if grouping2:
        gv.name += f'-by-{grouping2.title()}'
        gv.title += f' by {grouping2.title()}'
    gv.subtitle = f'{date.today().isoformat()} RR'
    gv.fontcolor = 'orange'
    gv.nodesep = '0.1'
    gv.directory = os.path.join('c:', os.sep, 'Users', 'Randy Rockwell', 'Desktop', 'roadmap_output')

    if grouping1:
        query1 = f"select distinct {grouping1} from nodes;"
        groups1 = list(cur.execute(query1))
        for group1 in groups1:
            g1 = Group()
            g1.fontcolor = 'black'
            g1.name = group1[0]
            g1.color = 'black'

            record_feature_id(g1)

            if grouping2:
                groups2 = list(cur.execute(f"select distinct {grouping2} from nodes;"))
                for group2 in groups2:
                    g2 = Group()
                    g2.fontcolor = 'darkorange'
                    g2.name = group2[0]
                    g2.color = 'grey'

                    nodes = cur.execute(f"select id, function, status, target_release, feature from nodes where {grouping1} "
                                        f"= '{group1[0]}' and {grouping2} = '{group2[0]}' order by id;")
                    for node in nodes:
                        n = define_node(node)
                        g2.nodes += [n]
                    g1.groups += [g2]
            gv.groups += [g1]

    else:
        nodes = cur.execute(f"select id, function, status, target_release, feature from nodes where;")
        for node in nodes:
            n = define_node(node)
            gv.ungrouped_nodes += [n]

    query = f"select distinct {grouping1} from nodes order by {grouping1};"
    last_one = None
    for item in list(cur.execute(query)):
        if last_one:
            script = f"INSERT INTO feature_edges VALUES('{last_one}', '{item[0]}');"
            cur.execute(script)
        last_one = item[0]
    conn.commit()

    def get_feature_in_release(release):
        query = f"""select id from nodes where target_release = '{release}' and feature is not '' limit 1;"""
        result = list(cur.execute(query))
        return result[0][0]

    query = """select fe.feature_from, fe.feature_to, fi1.uid feature_from, fi2.uid feature_to from feature_edges fe
               left join feature_ids fi1 on fe.feature_from = fi1.feature
               left join feature_ids fi2 on fe.feature_to = fi2.feature;"""
    for fe in list(cur.execute(query)):
        n1 = get_feature_in_release(fe[0])
        n2 = get_feature_in_release(fe[1])
        if n1 and n2:
            e = Edge()
            e.arrowhead = 'normal'
            e.color = '#4f4f4f'
            e.start = n1
            e.end = n2
            e.post_text = f"ltail={fe[2]} lhead={fe[3]} "
            gv.edges += [e]

    conn.close()

    gv.write_dot(vertical=False)
    gv.rendergraphs()


def build_full_diagram(dependencies=True, grouping=None):
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()

    gv = GraphViz()
    gv.name = 'LIMS-Roadmap-Detail'
    gv.title = 'LIMS Roadmap Detail'
    if grouping:
        gv.name += f'-by-{grouping.title()}'
        gv.title += f' by {grouping.title()}'
    gv.subtitle = f'{date.today().isoformat()} RR'
    gv.fontcolor = 'orange'
    gv.nodesep = '0.1'
    gv.directory = os.path.join('c:', os.sep, 'Users', 'Randy Rockwell', 'Desktop', 'roadmap_output')

    if grouping:
        groups = list(cur.execute(f"select distinct {grouping} from nodes;"))
        for group in groups:
            g = Group()
            g.fontcolor = 'darkorange'
            g.name = group[0]
            g.color = 'grey'

            releases = []
            nodes = cur.execute(f"select id, function, status, target_release, feature from nodes where {grouping} = '{group[0]}' order by id;")
            for node in nodes:
                n = define_node(node)
                if grouping == 'target_release':
                    n.label = n.feature + n.label
                g.nodes += [n]
                if n.target_release not in releases:
                    releases += [n.target_release]
            gv.groups += [g]

            if releases != [''] and grouping != 'target_release':
                g.name += f' [{",".join(releases)}]'



    else:
        nodes = cur.execute(f"select id, function, status, target_release, feature from nodes where;")
        for node in nodes:
            n = define_node(node)
            gv.ungrouped_nodes += [n]

    if dependencies:
        for edge in cur.execute(f"select node_from, node_to from edges order by node_from, node_to;"):
            e = Edge()
            e.arrowhead = 'normal'
            e.color = '#4f4f4f'
            e.start = edge[0]
            e.end = edge[1]
            gv.edges += [e]

    conn.close()

    gv.write_dot(vertical=False)
    gv.rendergraphs()


def build_feature_dependency(grouping=None):
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()

    gv = GraphViz()
    gv.name = 'LIMS-Roadmap-Feature-Dependency'
    gv.title = 'LIMS Roadmap Feature Dependency'
    if grouping:
        gv.name += f'-by-{grouping.title()}'
        gv.title += f' by {grouping.title()}'
    gv.subtitle = f'{date.today().isoformat()} RR'
    gv.fontcolor = 'orange'
    gv.nodesep = '0.5'
    gv.directory = os.path.join('c:', os.sep, 'Users', 'Randy Rockwell', 'Desktop', 'roadmap_output')

    if grouping:
        groups = list(cur.execute(f"select distinct {grouping} from nodes;"))
        for group in groups:
            g = Group()
            g.fontcolor = 'darkorange'
            g.name = group[0]
            g.color = 'grey'

            query = f"""select distinct feature, status 
                        from nodes where feature is not null and {grouping} = '{group[0]}' 
                        order by feature, status;"""
            for node in cur.execute(query):
                n = define_node((node[0], None, node[1], None, None))
                g.nodes += [n]
            gv.groups += [g]

    else:
        query = f"""select distinct feature, status 
                    from nodes where feature is not null
                    order by feature, status;"""
        for node in cur.execute(query):
            n = define_node((node[0], None, node[1], None, None))
            gv.ungrouped_nodes += [n]

    for edge in cur.execute("""
        select distinct * from (select n1.feature n1g, n2.feature n2g
               from edges e
                        left join nodes n1 on e.node_from = n1.id
                        left join nodes n2 on e.node_to = n2.id) alpha
        where n1g is not null and n2g is not null
        order by n1g, n2g; """):
        e = Edge()
        e.arrowhead = 'normal'
        e.color = 'orange'
        e.start = edge[0]
        e.end = edge[1]
        gv.edges += [e]

    conn.close()

    gv.write_dot(vertical=False)
    gv.rendergraphs()


def define_node(node):
    uid, function, status, target_release, feature = node
    n = Node()
    n.id = uid
    if function:
        desc = function.replace('|', '\n')
        n.label = f"{uid} - {desc}"
    else:
        n.label = uid
    n.color = color_scheme[status]
    n.fillcolor = color_scheme[status]
    n.fontcolor = 'black'
    n.target_release = target_release
    n.feature = feature
    return n


def main():
    file_a = os.path.join('c:', os.sep, 'Users', 'Randy Rockwell', 'Downloads', 'LIMS Roadmap Function List - Function List.tsv')
    load_data(file_a)
    os.remove(file_a)
    messages = check_data()

    build_feature_dependency()
    build_feature_dependency(grouping='theme')
    build_full_diagram(dependencies=True, grouping='feature')
    build_double_group_diagram(grouping1='target_release', grouping2='feature')

    print_messages(messages)


if __name__ == '__main__':
    main()


