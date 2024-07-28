import bpy
import os

def export_geometry_nodes_to_code(obj_name, modifier_name, file_path):
    # Get the object
    obj = bpy.data.objects.get(obj_name)
    if not obj:
        print(f"Object '{obj_name}' not found.")
        return
    
    # Get the geometry nodes modifier
    geom_nodes_modifier = obj.modifiers.get(modifier_name)
    if not geom_nodes_modifier or geom_nodes_modifier.type != 'NODES':
        print(f"Geometry Nodes modifier '{modifier_name}' not found on object '{obj_name}'.")
        return
    
    # Get the node tree
    node_tree = geom_nodes_modifier.node_group
    if not node_tree:
        print(f"Node group not found in the modifier '{modifier_name}'.")
        return

    print(f"Exporting geometry nodes from object '{obj_name}' with modifier '{modifier_name}' to '{file_path}'")

    try:
        with open(file_path, 'w') as f:
            f.write(f"import bpy\n\n")
            f.write(f"def create_geometry_nodes():\n")
            f.write(f"    # Create a new node group\n")
            f.write(f"    node_group = bpy.data.node_groups.new(type='GeometryNodeTree', name='{node_tree.name}')\n")
            f.write(f"    node_group.nodes.clear()\n")
            
            # Create nodes
            for node in node_tree.nodes:
                node_name = node.name.replace(' ', '_')
                f.write(f"    # Create node: {node.name}\n")
                f.write(f"    {node_name} = node_group.nodes.new(type='{node.bl_idname}')\n")
                f.write(f"    {node_name}.location = ({node.location.x}, {node.location.y})\n")
                
                # Write node inputs (assuming the input is not linked and is a primitive type)
                for input in node.inputs:
                    if input.is_linked or input.type in ['GEOMETRY', 'OBJECT', 'COLLECTION', 'TEXTURE', 'MATERIAL', 'IMAGE']:
                        continue
                    try:
                        default_value = input.default_value
                        if isinstance(default_value, str):
                            f.write(f"    {node_name}.inputs['{input.name}'].default_value = '{default_value}'\n")
                        else:
                            f.write(f"    {node_name}.inputs['{input.name}'].default_value = {default_value}\n")
                    except AttributeError:
                        print(f"Skipping input '{input.name}' of node '{node.name}' as it has no 'default_value' attribute.")
                
                f.write("\n")
            
            # Create links
            f.write(f"    # Create links\n")
            for link in node_tree.links:
                from_node = link.from_node.name.replace(' ', '_')
                to_node = link.to_node.name.replace(' ', '_')
                from_socket = link.from_socket.name
                to_socket = link.to_socket.name
                f.write(f"    node_group.links.new({from_node}.outputs['{from_socket}'], {to_node}.inputs['{to_socket}'])\n")
            
            f.write(f"\n    return node_group\n\n")
            
            f.write(f"# Usage example:\n")
            f.write(f"node_group = create_geometry_nodes()\n")
            f.write(f"obj = bpy.data.objects['{obj_name}']\n")
            f.write(f"geom_nodes_modifier = obj.modifiers.new(name='{modifier_name}', type='NODES')\n")
            f.write(f"geom_nodes_modifier.node_group = node_group\n")
        print(f"Geometry nodes exported to {file_path}")

    except Exception as e:
        print(f"Failed to write file: {e}")

# Usage
export_geometry_nodes_to_code("Plane", "GeometryNodes", "./exported_geometry_nodes_code.py")
