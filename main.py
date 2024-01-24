from neomodel import db
import pandas as pd
import numpy as np
import json

# Requirements
# Ensure that the neo4j APOC plugin is enabled in your neo4j dbms

neo4j_bolt_url = 'bolt://<username>:<password>@localhost:7687/<database_name>'
db.set_connection(neo4j_bolt_url)

rels = db.cypher_query('call apoc.meta.relTypeProperties')
props = db.cypher_query('call apoc.meta.nodeTypeProperties')

###########################################################################
# Sample of what neo4j schema output looks like
print('  ---  '.join(rels[1]))
print('  --------  '.join(map(str, rels[0][0])))
print()
print('  ---  '.join(props[1]))
print('  --------  '.join(map(str, props[0][0])))

###########################################################################
# Create nodes for arrows.app object
node_id_ind = 0

node_ids = {} # nodeLabel: node_id
types = {} # nodeLabel: label
properties = {} #nodelabel: [properties]

for row in props[0]:
    for nodeLabel in row[1]:

        # Get node.id
        if nodeLabel not in node_ids:
            cur_node_id_ind = 'n' + str(node_id_ind)
            node_ids[nodeLabel] = cur_node_id_ind
            node_id_ind+=1
        else:
            cur_node_id_ind = node_ids[nodeLabel]
    
        # Types
        label_types = list(set(row[0].replace('`','').split(':')[1:]))
        if nodeLabel not in types:
            types[nodeLabel] = label_types
        else:
            types[nodeLabel] = list(set(types[nodeLabel] + label_types))

        # properties
        if nodeLabel not in properties:
            properties[nodeLabel] = {row[2]:[row[3][0]]} # nodeLabel: {property: property_type}
        else:
            properties[nodeLabel][row[2]] = row[3][0]


# Structure nodes into arrows.app format
nodes = []
for nodeLabel in node_ids:

    arrows_row = {}

    arrows_row['id'] = node_ids[nodeLabel]
    arrows_row['position'] = {'x': np.random.random() * 4000, 'y': np.random.random() * 4000}
    arrows_row['caption'] = ''
    
    arrows_row['style'] = {"node-color": "#fcdc00", "border-color": "#fcdc00"}
    arrows_row['labels'] = types[nodeLabel]
    arrows_row['properties'] = properties[nodeLabel]
    
    nodes.append(arrows_row)


###########################################################################
# Create relationships arrows.app object

rel_id_ind = 0
rel_hierarchy = {}
for row in rels[0]:

    for sourceNode in row[1]:

        if sourceNode not in rel_hierarchy:
            rel_hierarchy[sourceNode] = {}

        for targetNode in row[2]:

            if targetNode not in rel_hierarchy[sourceNode]:
                rel_hierarchy[sourceNode][targetNode] = {}
            
            if row[0] not in rel_hierarchy[sourceNode][targetNode]:
                rel_hierarchy[sourceNode][targetNode][row[0]] = {}

            #Properties
            rel_hierarchy[sourceNode][targetNode][row[0]][row[3]] = row[4]

relationships = []
for sourceNode in rel_hierarchy:
    for targetNode in rel_hierarchy[sourceNode]:
        for relType in rel_hierarchy[sourceNode][targetNode]:

            arrows_row = {}

            # Relationship ID
            cur_rel_id_ind = 'n' + str(rel_id_ind)
            arrows_row['id'] = cur_rel_id_ind
            rel_id_ind+=1

            arrows_row['fromId'] = node_ids[sourceNode]
            arrows_row['toId'] = node_ids[targetNode]
            arrows_row['type'] = relType.replace('`','').replace(':','')
            arrows_row['properties'] = rel_hierarchy[sourceNode][targetNode][relType]

            relationships.append(arrows_row)


###########################################################################
# Takes the lists of nodes and relationships, then dumps them to json file readable by arrows
def make_arrows_json(nodes, relationships, style={}):
    arrows_import = {
        'nodes': nodes,
        'relationships': relationships,
        'style': style
    }
    outpath = "arrows_import.json"
    with open(outpath, "w") as fp:
        json.dump(arrows_import , fp)
    print(f"File saved to {outpath}")
make_arrows_json(nodes, relationships)
