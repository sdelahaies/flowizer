#python svg2reactflow.py ../outputs/bigflow.svg >bigflow.json

import xml.etree.ElementTree as ET
import json
import sys


path=sys.argv[1]
# load svg file with ET
root = ET.parse(path).getroot()

# Register namespaces
namespaces = {'svg': 'http://www.w3.org/2000/svg'}

nodes = []
edges = []
node_map = {}

# Extract nodes
for g in root.findall(".//svg:g[@class='node']", namespaces):
    title = g.find("svg:title", namespaces).text
    text_elements = g.findall("svg:text", namespaces)
    node_type = text_elements[1].text
    position_x = float(g.find("svg:ellipse", namespaces).attrib['cx'])
    position_y = float(g.find("svg:ellipse", namespaces).attrib['cy'])
    
    node = {
        "id": title,
        "type": "Custom",
        "position": {
            "x": position_x,
            "y": position_y
        },
        "data": {"label": title},
        # "style": {
        #             "background": "#201f21",
        #             "color": "#ea580c",
        #             "border": "1px solid #ea580c",
        #             "padding": 5,
        #             "borderRadius": 5,
        #             "height": 40,
        #             "width": 110
        #         },
        "selected": False,
        "positionAbsolute": {
            "x": position_x,
            "y": position_y
        },
        "dragging": False
    }
    nodes.append(node)
    node_map[title] = node_type

# Extract edges
for g in root.findall(".//svg:g[@class='edge']", namespaces):
    title = g.find("svg:title", namespaces).text
    #print(title)
    if len(title.split("->")) == 2:
        source, target = title.split("->")
        #print(f"Source: {source}, Target: {target}")
    
        edge = {
            "source": source,
            "sourceHandle": "b",
            "target": target,
            "targetHandle": None,
            "type": "custom-edge",
            "deletable": True,
            "id": f"reactflow__edge-{source}-{target}"
        }
        edges.append(edge)

# Create the final JSON structure
output_json = {
    "input": {
        "nodes": nodes,
        "edges": edges,
        "viewport": {
            "x": 670.1413230441351,
            "y": 255.34751684975103,
            "zoom": 0.5921495954782059
        }
    }
}

# Print the resulting JSON
print(json.dumps(output_json, indent=4))
