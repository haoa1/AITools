from base import function_ai, parameters_func, property_param
import os
import json
import base64
import tempfile
import subprocess
from typing import Dict, List, Optional

# 属性定义
__DIAGRAM_TYPE_PROPERTY__ = property_param(
    name="diagram_type",
    description="Type of diagram: 'architecture', 'flowchart', 'sequence', 'class', 'deployment'",
    t="string",
    required=True
)

__MERMAID_CODE_PROPERTY__ = property_param(
    name="mermaid_code",
    description="Mermaid syntax code for diagram generation",
    t="string",
    required=True
)

__DOT_CODE_PROPERTY__ = property_param(
    name="dot_code",
    description="Graphviz DOT syntax code for diagram generation",
    t="string",
    required=True
)

__OUTPUT_FORMAT_PROPERTY__ = property_param(
    name="output_format",
    description="Output format: 'png', 'svg', 'pdf', 'dot', 'mermaid'",
    t="string",
    required=False
)

__OUTPUT_PATH_PROPERTY__ = property_param(
    name="output_path",
    description="Path to save the diagram file. If not provided, returns base64 encoded image or text.",
    t="string",
    required=False
)

__COMPONENTS_PROPERTY__ = property_param(
    name="components",
    description="List of system components as JSON array of objects with 'name', 'type', 'description'",
    t="string",
    required=True
)

__CONNECTIONS_PROPERTY__ = property_param(
    name="connections",
    description="Connections between components as JSON array of objects with 'from', 'to', 'type'",
    t="string",
    required=False
)

__TITLE_PROPERTY__ = property_param(
    name="title",
    description="Title of the diagram",
    t="string",
    required=False
)

__STEPS_PROPERTY__ = property_param(
    name="steps",
    description="Flowchart steps as JSON array of objects with 'id', 'label', 'type' (start, end, process, decision, etc.)",
    t="string",
    required=True
)

__ACTORS_PROPERTY__ = property_param(
    name="actors",
    description="Actors in sequence diagram as JSON array of objects with 'name', 'type'",
    t="string",
    required=True
)

__MESSAGES_PROPERTY__ = property_param(
    name="messages",
    description="Messages in sequence diagram as JSON array of objects with 'from', 'to', 'message', 'type'",
    t="string",
    required=True
)

# 函数工具定义
__GENERATE_MERMAID_DIAGRAM_FUNCTION__ = function_ai(
    name="generate_mermaid_diagram",
    description="Generate diagram from Mermaid syntax code. Returns base64 encoded image or saves to file.",
    parameters=parameters_func([
        __MERMAID_CODE_PROPERTY__,
        __OUTPUT_FORMAT_PROPERTY__,
        __OUTPUT_PATH_PROPERTY__
    ])
)

__GENERATE_DOT_DIAGRAM_FUNCTION__ = function_ai(
    name="generate_dot_diagram",
    description="Generate diagram from Graphviz DOT syntax code. Returns base64 encoded image or saves to file.",
    parameters=parameters_func([
        __DOT_CODE_PROPERTY__,
        __OUTPUT_FORMAT_PROPERTY__,
        __OUTPUT_PATH_PROPERTY__
    ])
)

__CREATE_ARCHITECTURE_DIAGRAM_FUNCTION__ = function_ai(
    name="create_architecture_diagram",
    description="Create system architecture diagram from components and connections. Returns diagram code or image.",
    parameters=parameters_func([
        __COMPONENTS_PROPERTY__,
        __CONNECTIONS_PROPERTY__,
        __TITLE_PROPERTY__,
        __OUTPUT_FORMAT_PROPERTY__,
        __OUTPUT_PATH_PROPERTY__
    ])
)

__CREATE_FLOWCHART_FUNCTION__ = function_ai(
    name="create_flowchart",
    description="Create flowchart from steps and connections. Returns diagram code or image.",
    parameters=parameters_func([
        __STEPS_PROPERTY__,
        __TITLE_PROPERTY__,
        __OUTPUT_FORMAT_PROPERTY__,
        __OUTPUT_PATH_PROPERTY__
    ])
)

__CREATE_SEQUENCE_DIAGRAM_FUNCTION__ = function_ai(
    name="create_sequence_diagram",
    description="Create sequence diagram from actors and messages. Returns diagram code or image.",
    parameters=parameters_func([
        __ACTORS_PROPERTY__,
        __MESSAGES_PROPERTY__,
        __TITLE_PROPERTY__,
        __OUTPUT_FORMAT_PROPERTY__,
        __OUTPUT_PATH_PROPERTY__
    ])
)

__EXPORT_DIAGRAM_FUNCTION__ = function_ai(
    name="export_diagram",
    description="Export diagram to file in specified format.",
    parameters=parameters_func([
        __DIAGRAM_TYPE_PROPERTY__,
        property_param(name="diagram_code", description="Diagram code in Mermaid or DOT format", t="string", required=True),
        __OUTPUT_FORMAT_PROPERTY__,
        __OUTPUT_PATH_PROPERTY__
    ])
)

tools = [
    __GENERATE_MERMAID_DIAGRAM_FUNCTION__,
    __GENERATE_DOT_DIAGRAM_FUNCTION__,
    __CREATE_ARCHITECTURE_DIAGRAM_FUNCTION__,
    __CREATE_FLOWCHART_FUNCTION__,
    __CREATE_SEQUENCE_DIAGRAM_FUNCTION__,
    __EXPORT_DIAGRAM_FUNCTION__
]

# 工具函数实现

def generate_mermaid_diagram(mermaid_code: str, output_format: str = "png", output_path: str = None) -> str:
    '''
    Generate diagram from Mermaid syntax code.
    
    :param mermaid_code: Mermaid syntax code for diagram
    :type mermaid_code: str
    :param output_format: Output format: 'png', 'svg', 'pdf', 'txt' (mermaid code)
    :type output_format: str
    :param output_path: Path to save the diagram file. If not provided, returns base64 encoded image or text.
    :type output_path: str
    :return: Base64 encoded image or text or error message
    :rtype: str
    '''
    try:
        # Clean and validate mermaid code
        mermaid_code = mermaid_code.strip()
        if not mermaid_code:
            return "Error: Mermaid code cannot be empty"
        
        if output_format.lower() == "txt" or output_format.lower() == "mermaid":
            # Just return the mermaid code
            if output_path:
                try:
                    with open(output_path, 'w') as f:
                        f.write(mermaid_code)
                    return f"Success: Mermaid code saved to {output_path}"
                except Exception as e:
                    return f"Error: Failed to save mermaid code to {output_path}: {str(e)}"
            return mermaid_code
        
        # For image formats, use mermaid.ink API
        import requests
        
        # Encode mermaid code for URL
        import urllib.parse
        encoded_code = urllib.parse.quote(mermaid_code)
        
        # Use mermaid.ink API
        url = f"https://mermaid.ink/img/{encoded_code}"
        
        # Set appropriate extension based on format
        if output_format.lower() == "svg":
            url = f"https://mermaid.ink/svg/{encoded_code}"
        elif output_format.lower() == "pdf":
            # mermaid.ink doesn't support PDF directly, return SVG instead
            url = f"https://mermaid.ink/svg/{encoded_code}"
            output_format = "svg"
        
        # Download the image
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            return f"Error: Failed to generate diagram from mermaid.ink. Status: {response.status_code}"
        
        if output_path:
            try:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return f"Success: Diagram saved to {output_path}"
            except Exception as e:
                return f"Error: Failed to save diagram to {output_path}: {str(e)}"
        else:
            # Return base64 encoded image
            import base64
            encoded_image = base64.b64encode(response.content).decode('utf-8')
            return f"data:image/{output_format};base64,{encoded_image}"
            
    except ImportError:
        return "Error: 'requests' library not installed. Please install it with 'pip install requests'"
    except Exception as e:
        return f"Error: Unexpected error when generating mermaid diagram: {str(e)}"

def generate_dot_diagram(dot_code: str, output_format: str = "png", output_path: str = None) -> str:
    '''
    Generate diagram from Graphviz DOT syntax code.
    
    :param dot_code: Graphviz DOT syntax code for diagram
    :type dot_code: str
    :param output_format: Output format: 'png', 'svg', 'pdf', 'dot' (DOT code)
    :type output_format: str
    :param output_path: Path to save the diagram file. If not provided, returns base64 encoded image or text.
    :type output_path: str
    :return: Base64 encoded image or text or error message
    :rtype: str
    '''
    try:
        # Clean and validate DOT code
        dot_code = dot_code.strip()
        if not dot_code:
            return "Error: DOT code cannot be empty"
        
        if output_format.lower() == "dot":
            # Just return the DOT code
            if output_path:
                try:
                    with open(output_path, 'w') as f:
                        f.write(dot_code)
                    return f"Success: DOT code saved to {output_path}"
                except Exception as e:
                    return f"Error: Failed to save DOT code to {output_path}: {str(e)}"
            return dot_code
        
        # Check if graphviz is installed
        try:
            import graphviz
            has_graphviz = True
        except ImportError:
            has_graphviz = False
        
        if not has_graphviz:
            # Return DOT code with instructions
            return f"Error: Graphviz not installed. Please install with 'pip install graphviz' and ensure Graphviz binaries are installed on system.\\n\\nDOT code:\\n{dot_code}"
        
        # Create graph from DOT code
        import graphviz
        from graphviz import Source
        
        # Create temporary file for DOT code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dot', delete=False) as tmp:
            tmp.write(dot_code)
            tmp_path = tmp.name
        
        try:
            # Render the graph
            format_map = {
                'png': 'png',
                'svg': 'svg',
                'pdf': 'pdf'
            }
            
            fmt = format_map.get(output_format.lower(), 'png')
            
            # Use graphviz Source to render
            src = Source(dot_code, format=fmt)
            
            if output_path:
                # Render to file
                src.render(filename=output_path.replace(f'.{fmt}', ''), cleanup=True)
                return f"Success: Diagram saved to {output_path}"
            else:
                # Render to temporary file and read as base64
                temp_output = src.render(filename=tempfile.mktemp(), cleanup=False)
                
                with open(temp_output, 'rb') as f:
                    image_data = f.read()
                
                # Clean up
                os.unlink(temp_output)
                
                # Return base64 encoded image
                import base64
                encoded_image = base64.b64encode(image_data).decode('utf-8')
                return f"data:image/{fmt};base64,{encoded_image}"
                
        finally:
            # Clean up temporary DOT file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                
    except Exception as e:
        return f"Error: Unexpected error when generating DOT diagram: {str(e)}"

def create_architecture_diagram(components: str, connections: str = None, title: str = None, 
                                output_format: str = "png", output_path: str = None) -> str:
    '''
    Create system architecture diagram from components and connections.
    
    :param components: JSON array of component objects with 'name', 'type', 'description'
    :type components: str
    :param connections: JSON array of connection objects with 'from', 'to', 'type'
    :type connections: str
    :param title: Title of the diagram
    :type title: str
    :param output_format: Output format: 'png', 'svg', 'pdf', 'mermaid', 'dot'
    :type output_format: str
    :param output_path: Path to save the diagram file
    :type output_path: str
    :return: Diagram code or image or error message
    :rtype: str
    '''
    try:
        # Parse components JSON
        try:
            comp_list = json.loads(components)
            if not isinstance(comp_list, list):
                return "Error: Components must be a JSON array"
        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON in components: {str(e)}"
        
        # Parse connections JSON if provided
        conn_list = []
        if connections:
            try:
                conn_list = json.loads(connections)
                if not isinstance(conn_list, list):
                    return "Error: Connections must be a JSON array"
            except json.JSONDecodeError as e:
                return f"Error: Invalid JSON in connections: {str(e)}"
        
        # Create Mermaid code for architecture diagram
        mermaid_code = "graph TD\\n"
        
        if title:
            mermaid_code += f"    title {title}\\n"
        
        # Add components as nodes
        for comp in comp_list:
            node_id = comp.get('id', comp.get('name', '')).replace(' ', '_').replace('-', '_')
            node_label = comp.get('label', comp.get('name', 'Node'))
            node_type = comp.get('type', 'component').lower()
            
            # Map component types to Mermaid shapes
            shape_map = {
                'database': '[(Database)]',
                'service': '([Service])',
                'api': '[[API]]',
                'queue': '>Queue]',
                'storage': '[(Storage)]',
                'loadbalancer': '{{Load Balancer}}',
                'cache': '[(Cache)]',
                'component': '[Component]'
            }
            
            shape = shape_map.get(node_type, '[Component]')
            mermaid_code += f"    {node_id}{shape}{node_label}\\n"
        
        # Add connections
        for conn in conn_list:
            from_node = conn.get('from', '').replace(' ', '_').replace('-', '_')
            to_node = conn.get('to', '').replace(' ', '_').replace('-', '_')
            conn_type = conn.get('type', '-->').lower()
            
            # Map connection types to Mermaid arrows
            arrow_map = {
                'http': '-->',
                'https': '==>',
                'grpc': '-.->',
                'message': '-.->',
                'database': '--->',
                'async': '-.->',
                'sync': '-->'
            }
            
            arrow = arrow_map.get(conn_type, '-->')
            label = conn.get('label', '')
            
            if label:
                mermaid_code += f"    {from_node} {arrow}|{label}| {to_node}\\n"
            else:
                mermaid_code += f"    {from_node} {arrow} {to_node}\\n"
        
        # Generate diagram based on output format
        if output_format.lower() in ['mermaid', 'txt']:
            if output_path:
                try:
                    with open(output_path, 'w') as f:
                        f.write(mermaid_code)
                    return f"Success: Mermaid code saved to {output_path}"
                except Exception as e:
                    return f"Error: Failed to save mermaid code: {str(e)}"
            return mermaid_code
        elif output_format.lower() == 'dot':
            # Convert to DOT format (simplified)
            dot_code = convert_mermaid_to_dot(mermaid_code)
            if output_path:
                try:
                    with open(output_path, 'w') as f:
                        f.write(dot_code)
                    return f"Success: DOT code saved to {output_path}"
                except Exception as e:
                    return f"Error: Failed to save DOT code: {str(e)}"
            return dot_code
        else:
            # Generate image
            return generate_mermaid_diagram(mermaid_code, output_format, output_path)
            
    except Exception as e:
        return f"Error: Unexpected error when creating architecture diagram: {str(e)}"

def create_flowchart(steps: str, title: str = None, output_format: str = "png", output_path: str = None) -> str:
    '''
    Create flowchart from steps and connections.
    
    :param steps: JSON array of step objects with 'id', 'label', 'type'
    :type steps: str
    :param title: Title of the diagram
    :type title: str
    :param output_format: Output format: 'png', 'svg', 'pdf', 'mermaid', 'dot'
    :type output_format: str
    :param output_path: Path to save the diagram file
    :type output_path: str
    :return: Diagram code or image or error message
    :rtype: str
    '''
    try:
        # Parse steps JSON
        try:
            steps_list = json.loads(steps)
            if not isinstance(steps_list, list):
                return "Error: Steps must be a JSON array"
        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON in steps: {str(e)}"
        
        # Create Mermaid code for flowchart
        mermaid_code = "graph TD\\n"
        
        if title:
            mermaid_code += f"    title {title}\\n"
        
        # Add steps as nodes with appropriate shapes
        for step in steps_list:
            step_id = step.get('id', '').replace(' ', '_').replace('-', '_')
            step_label = step.get('label', 'Step')
            step_type = step.get('type', 'process').lower()
            
            # Map step types to Mermaid shapes
            shape_map = {
                'start': '([Start])',
                'end': '([End])',
                'process': '[Process]',
                'decision': '{Decision}',
                'input': '[/Input/]',
                'output': '[\\\\Output\\\\]',
                'predefined': '[Predefined Process]',
                'storage': '[(Database)]',
                'document': '[(Document)]',
                'manual': '[(Manual)]',
                'delay': '[(Delay)]'
            }
            
            shape = shape_map.get(step_type, '[Process]')
            mermaid_code += f"    {step_id}{shape}{step_label}\\n"
        
        # Add connections (assuming steps are in order)
        for i in range(len(steps_list) - 1):
            current_id = steps_list[i].get('id', '').replace(' ', '_').replace('-', '_')
            next_id = steps_list[i + 1].get('id', '').replace(' ', '_').replace('-', '_')
            
            # Check for decision branches
            current_type = steps_list[i].get('type', '').lower()
            if current_type == 'decision':
                # Decision node should have yes/no branches
                # This is simplified - in real implementation would need more complex logic
                mermaid_code += f"    {current_id} -->|Yes| {next_id}\\n"
                # Add a "No" branch to end or another node
                mermaid_code += f"    {current_id} -->|No| End\\n"
            else:
                mermaid_code += f"    {current_id} --> {next_id}\\n"
        
        # Generate diagram based on output format
        if output_format.lower() in ['mermaid', 'txt']:
            if output_path:
                try:
                    with open(output_path, 'w') as f:
                        f.write(mermaid_code)
                    return f"Success: Mermaid code saved to {output_path}"
                except Exception as e:
                    return f"Error: Failed to save mermaid code: {str(e)}"
            return mermaid_code
        elif output_format.lower() == 'dot':
            dot_code = convert_mermaid_to_dot(mermaid_code)
            if output_path:
                try:
                    with open(output_path, 'w') as f:
                        f.write(dot_code)
                    return f"Success: DOT code saved to {output_path}"
                except Exception as e:
                    return f"Error: Failed to save DOT code: {str(e)}"
            return dot_code
        else:
            return generate_mermaid_diagram(mermaid_code, output_format, output_path)
            
    except Exception as e:
        return f"Error: Unexpected error when creating flowchart: {str(e)}"

def create_sequence_diagram(actors: str, messages: str, title: str = None, 
                           output_format: str = "png", output_path: str = None) -> str:
    '''
    Create sequence diagram from actors and messages.
    
    :param actors: JSON array of actor objects with 'name', 'type'
    :type actors: str
    :param messages: JSON array of message objects with 'from', 'to', 'message', 'type'
    :type messages: str
    :param title: Title of the diagram
    :type title: str
    :param output_format: Output format: 'png', 'svg', 'pdf', 'mermaid', 'dot'
    :type output_format: str
    :param output_path: Path to save the diagram file
    :type output_path: str
    :return: Diagram code or image or error message
    :rtype: str
    '''
    try:
        # Parse actors JSON
        try:
            actors_list = json.loads(actors)
            if not isinstance(actors_list, list):
                return "Error: Actors must be a JSON array"
        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON in actors: {str(e)}"
        
        # Parse messages JSON
        try:
            messages_list = json.loads(messages)
            if not isinstance(messages_list, list):
                return "Error: Messages must be a JSON array"
        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON in messages: {str(e)}"
        
        # Create Mermaid code for sequence diagram
        mermaid_code = "sequenceDiagram\\n"
        
        if title:
            mermaid_code += f"    title {title}\\n"
        
        # Add participants (actors)
        for actor in actors_list:
            actor_name = actor.get('name', 'Actor')
            actor_type = actor.get('type', 'participant').lower()
            
            # Map actor types to Mermaid participant types
            if actor_type == 'actor':
                mermaid_code += f"    actor {actor_name}\\n"
            elif actor_type == 'database':
                mermaid_code += f"    participant {actor_name} as Database\\n"
            elif actor_type == 'service':
                mermaid_code += f"    participant {actor_name} as Service\\n"
            else:
                mermaid_code += f"    participant {actor_name}\\n"
        
        # Add messages
        for msg in messages_list:
            from_actor = msg.get('from', '')
            to_actor = msg.get('to', '')
            message_text = msg.get('message', '')
            msg_type = msg.get('type', 'sync').lower()
            
            # Map message types to Mermaid arrows
            if msg_type == 'async':
                mermaid_code += f"    {from_actor} ->> {to_actor}: {message_text}\\n"
            elif msg_type == 'return':
                mermaid_code += f"    {to_actor} -->> {from_actor}: {message_text}\\n"
            elif msg_type == 'self':
                mermaid_code += f"    {from_actor} ->> {from_actor}: {message_text}\\n"
            else:  # sync
                mermaid_code += f"    {from_actor} ->> {to_actor}: {message_text}\\n"
        
        # Generate diagram based on output format
        if output_format.lower() in ['mermaid', 'txt']:
            if output_path:
                try:
                    with open(output_path, 'w') as f:
                        f.write(mermaid_code)
                    return f"Success: Mermaid code saved to {output_path}"
                except Exception as e:
                    return f"Error: Failed to save mermaid code: {str(e)}"
            return mermaid_code
        elif output_format.lower() == 'dot':
            dot_code = convert_mermaid_to_dot(mermaid_code)
            if output_path:
                try:
                    with open(output_path, 'w') as f:
                        f.write(dot_code)
                    return f"Success: DOT code saved to {output_path}"
                except Exception as e:
                    return f"Error: Failed to save DOT code: {str(e)}"
            return dot_code
        else:
            return generate_mermaid_diagram(mermaid_code, output_format, output_path)
            
    except Exception as e:
        return f"Error: Unexpected error when creating sequence diagram: {str(e)}"

def export_diagram(diagram_type: str, diagram_code: str, output_format: str = "png", output_path: str = None) -> str:
    '''
    Export diagram to file in specified format.
    
    :param diagram_type: Type of diagram: 'mermaid' or 'dot'
    :type diagram_type: str
    :param diagram_code: Diagram code in Mermaid or DOT format
    :type diagram_code: str
    :param output_format: Output format: 'png', 'svg', 'pdf', 'txt'
    :type output_format: str
    :param output_path: Path to save the diagram file
    :type output_path: str
    :return: Success message or error
    :rtype: str
    '''
    try:
        diagram_type = diagram_type.lower()
        
        if diagram_type == 'mermaid':
            return generate_mermaid_diagram(diagram_code, output_format, output_path)
        elif diagram_type == 'dot':
            return generate_dot_diagram(diagram_code, output_format, output_path)
        else:
            return f"Error: Unsupported diagram type '{diagram_type}'. Use 'mermaid' or 'dot'."
            
    except Exception as e:
        return f"Error: Unexpected error when exporting diagram: {str(e)}"

# Helper functions
def convert_mermaid_to_dot(mermaid_code: str) -> str:
    '''
    Convert Mermaid code to Graphviz DOT format (simplified conversion).
    
    :param mermaid_code: Mermaid code to convert
    :type mermaid_code: str
    :return: DOT code
    :rtype: str
    '''
    # This is a simplified conversion for basic graphs
    # In production, use a proper Mermaid to DOT converter
    
    lines = mermaid_code.split('\\n')
    dot_code = "digraph G {\\n"
    dot_code += "    rankdir=TB;\\n"
    dot_code += "    node [shape=box, style=rounded];\\n"
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('title'):
            continue
            
        # Very basic conversion - in reality this would need to parse Mermaid syntax properly
        if '-->' in line or '==>' in line or '-.->' in line:
            # It's a connection line
            # Extract nodes and connection
            parts = line.replace('|', ' ').split()
            if len(parts) >= 3:
                from_node = parts[0].strip()
                to_node = parts[-1].strip()
                dot_code += f'    "{from_node}" -> "{to_node}";\\n'
        elif '[' in line and ']' in line:
            # It's a node definition
            # Simple extraction - not robust
            pass
    
    dot_code += "}\\n"
    return dot_code

TOOL_CALL_MAP = {
    "generate_mermaid_diagram": generate_mermaid_diagram,
    "generate_dot_diagram": generate_dot_diagram,
    "create_architecture_diagram": create_architecture_diagram,
    "create_flowchart": create_flowchart,
    "create_sequence_diagram": create_sequence_diagram,
    "export_diagram": export_diagram
}