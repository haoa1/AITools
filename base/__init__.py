from typing import List, Dict, Any

def property_param(name: str, t: str, required: bool = True, description: str = "") -> dict:
    """Create a property parameter dictionary for AI function definitions.

    Args:
        name: Property name. t: Property type (string, boolean, integer, etc.).
        required: Whether the property is required. Defaults to True. description:
        Property description. Defaults to "".

    Returns:
        dict: Property dictionary with name, type, description, and required fields.

    """
    proper = dict({
        "name": name,
        "type": t,
        "description": description,
        "required": required
    })
        
    return proper


def parameters_func(properties: List[Dict[str, Any]]) -> dict:
    """Create a parameters dictionary for AI function definitions.

    Args:
        properties: List of property dictionaries.

    Returns:
        dict: Parameters dictionary with type, properties, and required fields.

    """
    requires = []
    relocationProperties = {}
    for prop in properties:
        if prop["required"]:
            requires.append(prop["name"])
        relocationProperties[prop["name"]] = dict({
            "type": prop["type"],
            "description": prop["description"],
        })
    
    params = dict({
        "type": "object",
        "properties": relocationProperties,
        "required": requires
    })

    return params


def function_ai(name: str, parameters: dict, description: str = "") -> dict:
    """Create an AI function dictionary for tool definitions.

    Args:
        name: Function name. parameters: Parameters dictionary. description: Function
        description. Defaults to "".

    Returns:
        dict: Function dictionary with type and function details.

    """
    func = dict({
        "type": "function",
        "function": {
            "name": name,
            "strict": True,
            "description": description,
            "parameters": parameters
        }
    })

    return func