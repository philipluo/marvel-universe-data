#!/usr/bin/env python3
"""Convert import_data.cypher to graphml format for visualization."""
import re
import os

CYPER_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'marvel_graph_data', 'import_data.cypher')
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'marvel_graph_data', 'marvel_graph.graphml')

def main():
    with open(CYPER_FILE, 'r') as f:
        content = f.read()
    
    # Parse nodes
    nodes = {}
    for m in re.finditer(r'MERGE \((\w+):(\w+) \{([^}]+)\}\);', content):
        var, label, props_str = m.groups()
        props = {}
        # Parse each property
        for pm in re.finditer(r'(\w+):\s*"([^"]*)"', props_str):
            key, val = pm.groups()
            props[key] = val
        nodes[var] = {
            'id': var,
            'label': label,
            'props': props
        }
    
    # Parse relationships - support both Chinese and English labels
    rels = []
    for m in re.finditer(r'MERGE \((\w+)\)-\[:([^:]+)\]->\((\w+)\)\s*;', content):
        src, rel_type, tgt = m.groups()
        if src in nodes and tgt in nodes:
            rels.append((src, rel_type, tgt))
    
    # Generate GraphML
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('''<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns
         http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
  <key id="d0" for="node" attr.name="label" attr.type="string"/>
  <key id="d1" for="node" attr.name="name" attr.type="string"/>
  <key id="d2" for="node" attr.name="name_cn" attr.type="string"/>
  <key id="d3" for="node" attr.name="species" attr.type="string"/>
  <key id="d4" for="node" attr.name="real_name" attr.type="string"/>
  <key id="d5" for="node" attr.name="abilities" attr.type="string"/>
  <key id="d6" for="node" attr.name="type" attr.type="string"/>
  <key id="d7" for="node" attr.name="year" attr.type="string"/>
  <key id="d8" for="node" attr.name="title" attr.type="string"/>
  <key id="d9" for="node" attr.name="event_name" attr.type="string"/>
  <key id="d10" for="node" attr.name="item_name" attr.type="string"/>
  <key id="d11" for="node" attr.name="first_appearance" attr.type="string"/>
  <key id="d12" for="node" attr.name="description" attr.type="string"/>
  <key id="d13" for="edge" attr.name="relation" attr.type="string"/>
''')
        
        # Write nodes
        for var, node in nodes.items():
            label = node['label']
            props = node['props']
            
            # Different node types have different attributes
            if label == 'Character':
                f.write(f'  <node id="{var}">\n')
                f.write(f'    <data key="d0">{node["label"].upper()}</data>\n')
                f.write(f'    <data key="d1">{props.get("name", "")}</data>\n')
                f.write(f'    <data key="d2">{props.get("name_cn", "")}</data>\n')
                f.write(f'    <data key="d3">{props.get("species", "")}</data>\n')
                f.write(f'    <data key="d4">{props.get("real_name", "")}</data>\n')
                f.write(f'    <data key="d5">{props.get("abilities", "")}</data>\n')
                f.write(f'  </node>\n')
            elif label == 'Team':
                f.write(f'  <node id="{var}">\n')
                f.write(f'    <data key="d0">TEAM</data>\n')
                f.write(f'    <data key="d1">{props.get("name", "")}</data>\n')
                f.write(f'    <data key="d6">{props.get("type", "")}</data>\n')
                f.write(f'  </node>\n')
            elif label == 'Location':
                f.write(f'  <node id="{var}">\n')
                f.write(f'    <data key="d0">LOCATION</data>\n')
                f.write(f'    <data key="d1">{props.get("name", "")}</data>\n')
                f.write(f'    <data key="d6">{props.get("type", "")}</data>\n')
                f.write(f'  </node>\n')
            elif label == 'Movie':
                f.write(f'  <node id="{var}">\n')
                f.write(f'    <data key="d0">MOVIE</data>\n')
                f.write(f'    <data key="d8">{props.get("title", "")}</data>\n')
                f.write(f'    <data key="d7">{props.get("year", "")}</data>\n')
                f.write(f'  </node>\n')
            elif label == 'Event':
                f.write(f'  <node id="{var}">\n')
                f.write(f'    <data key="d0">EVENT</data>\n')
                f.write(f'    <data key="d9">{props.get("event_name", "")}</data>\n')
                f.write(f'    <data key="d7">{props.get("year", "")}</data>\n')
                f.write(f'  </node>\n')
            elif label == 'Item':
                f.write(f'  <node id="{var}">\n')
                f.write(f'    <data key="d0">ITEM</data>\n')
                item_name = props.get("item_name", props.get("name", ""))
                f.write(f'    <data key="d10">{item_name}</data>\n')
                f.write(f'    <data key="d6">{props.get("type", "")}</data>\n')
                f.write(f'  </node>\n')
            else:
                f.write(f'  <node id="{var}">\n')
                f.write(f'    <data key="d0">{label.upper()}</data>\n')
                f.write(f'  </node>\n')
        
        # Write edges
        for src, rel_type, tgt in rels:
            # Translate relation label to Chinese
            rel_cn = {
                '成员': '成员', 'ENEMY_OF': '敌人', 'ALLY_OF': '盟友',
                'USES': '使用', 'FROM': '来自', 'RELATIVE_OF': '亲属',
                'HERALD_OF': '使者'
            }.get(rel_type, rel_type)
            f.write(f'  <edge source="{src}" target="{tgt}" id="e_{src}_{tgt}">\n')
            f.write(f'    <data key="d13">{rel_cn}</data>\n')
            f.write(f'  </edge>\n')
        
        f.write('</graphml>')
    
    print(f"GraphML file created: {OUTPUT_FILE}")
    print(f"Nodes: {len(nodes)}")
    print(f"Edges: {len(rels)}")
    
    # Show sample
    print("\n=== Sample nodes ===")
    for var, node in list(nodes.items())[:3]:
        print(f"  {var}: {node['label']} - {node['props'].get('name', '')}")
    
    print("\n=== Sample edges ===")
    for src, rel, tgt in rels[:3]:
        print(f"  {src} --[{rel}]-> {tgt}")

if __name__ == '__main__':
    main()
