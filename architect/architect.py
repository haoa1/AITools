from base import function_ai, parameters_func, property_param
import os
import json
import tempfile
from datetime import datetime
from typing import Dict, List, Optional

__PROJECT_NAME_PROPERTY__ = property_param(
    name="project_name",
    description="Name of the project.",
    t="string",
    required=True
)

__PROJECT_DESCRIPTION_PROPERTY__ = property_param(
    name="project_description",
    description="Description of the project.",
    t="string",
    required=True
)

__ARCHITECTURE_TYPE_PROPERTY__ = property_param(
    name="architecture_type",
    description="Type of architecture: 'monolith', 'microservices', 'serverless', 'event-driven', 'layered', 'hexagonal'.",
    t="string",
    required=True
)

__ARCHITECTURE_DATA_PROPERTY__ = property_param(
    name="architecture_data",
    description="Architecture data in JSON format (components, connections, etc.).",
    t="string",
    required=False
)

__CONFIRMATION_REQUIRED_PROPERTY__ = property_param(
    name="confirmation_required",
    description="Whether user confirmation is required before proceeding.",
    t="boolean",
    required=False
)

__OUTPUT_PATH_PROPERTY__ = property_param(
    name="output_path",
    description="Path to save the output file.",
    t="string",
    required=False
)

__MODULES_DATA_PROPERTY__ = property_param(
    name="modules_data",
    description="Modules data in JSON format (list of modules with names and descriptions).",
    t="string",
    required=False
)

__INTERFACES_DATA_PROPERTY__ = property_param(
    name="interfaces_data",
    description="Interfaces data in JSON format (list of interfaces between modules).",
    t="string",
    required=False
)

__PHASES_DATA_PROPERTY__ = property_param(
    name="phases_data",
    description="Project phases data in JSON format (list of phases with timeline and deliverables).",
    t="string",
    required=False
)

__FEATURES_DATA_PROPERTY__ = property_param(
    name="features_data",
    description="Features data in JSON format (list of features per phase).",
    t="string",
    required=False
)

__DIAGRAM_FORMAT_PROPERTY__ = property_param(
    name="format",
    description="Diagram output format: 'mermaid', 'png', 'svg', 'pdf'.",
    t="string",
    required=False
)

# 函数工具定义
__DESIGN_ARCHITECTURE_FUNCTION__ = function_ai(
    name="design_architecture",
    description="Design system architecture based on project requirements. Returns architecture description that needs user confirmation.",
    parameters=parameters_func([
        __PROJECT_NAME_PROPERTY__,
        __PROJECT_DESCRIPTION_PROPERTY__,
        __ARCHITECTURE_TYPE_PROPERTY__,
        __OUTPUT_PATH_PROPERTY__
    ])
)

__CONFIRM_ARCHITECTURE_FUNCTION__ = function_ai(
    name="confirm_architecture",
    description="Confirm architecture design with user. Uses interactive confirmation.",
    parameters=parameters_func([
        property_param(name="architecture_summary", description="Summary of architecture to confirm.", t="string", required=True),
        property_param(name="question", description="Question to ask user for confirmation.", t="string", required=False)
    ])
)

__GENERATE_ARCHITECTURE_DIAGRAM_FUNCTION__ = function_ai(
    name="generate_architecture_diagram",
    description="Generate visual architecture diagram from architecture data.",
    parameters=parameters_func([
        __ARCHITECTURE_DATA_PROPERTY__,
        __DIAGRAM_FORMAT_PROPERTY__,
        __OUTPUT_PATH_PROPERTY__
    ])
)

__DEFINE_MODULES_FUNCTION__ = function_ai(
    name="define_modules",
    description="Define modules and their responsibilities based on confirmed architecture.",
    parameters=parameters_func([
        __ARCHITECTURE_DATA_PROPERTY__,
        __OUTPUT_PATH_PROPERTY__
    ])
)

__DEFINE_INTERFACES_FUNCTION__ = function_ai(
    name="define_interfaces",
    description="Define interfaces between modules with contracts and protocols.",
    parameters=parameters_func([
        __MODULES_DATA_PROPERTY__,
        __OUTPUT_PATH_PROPERTY__
    ])
)

__DESIGN_FLOWCHART_FUNCTION__ = function_ai(
    name="design_flowchart",
    description="Design flowchart for key processes in the system.",
    parameters=parameters_func([
        __ARCHITECTURE_DATA_PROPERTY__,
        property_param(name="process_name", description="Name of the process to diagram.", t="string", required=True),
        __OUTPUT_PATH_PROPERTY__
    ])
)

__DESIGN_SEQUENCE_DIAGRAM_FUNCTION__ = function_ai(
    name="design_sequence_diagram",
    description="Design sequence diagram for key interactions in the system.",
    parameters=parameters_func([
        __ARCHITECTURE_DATA_PROPERTY__,
        property_param(name="interaction_scenario", description="Scenario to diagram.", t="string", required=True),
        __OUTPUT_PATH_PROPERTY__
    ])
)

__DEFINE_PROJECT_PHASES_FUNCTION__ = function_ai(
    name="define_project_phases",
    description="Define project phases, timelines, and deliverables.",
    parameters=parameters_func([
        __PROJECT_NAME_PROPERTY__,
        __ARCHITECTURE_DATA_PROPERTY__,
        __MODULES_DATA_PROPERTY__,
        __OUTPUT_PATH_PROPERTY__
    ])
)

__DEFINE_FEATURES_FUNCTION__ = function_ai(
    name="define_features",
    description="Define features for each project phase.",
    parameters=parameters_func([
        __PHASES_DATA_PROPERTY__,
        __OUTPUT_PATH_PROPERTY__
    ])
)

__CREATE_ARCHITECTURE_REPORT_FUNCTION__ = function_ai(
    name="create_architecture_report",
    description="Create comprehensive architecture report with all components.",
    parameters=parameters_func([
        __PROJECT_NAME_PROPERTY__,
        __ARCHITECTURE_DATA_PROPERTY__,
        __MODULES_DATA_PROPERTY__,
        __INTERFACES_DATA_PROPERTY__,
        __PHASES_DATA_PROPERTY__,
        __FEATURES_DATA_PROPERTY__,
        __OUTPUT_PATH_PROPERTY__
    ])
)

tools = [
    __DESIGN_ARCHITECTURE_FUNCTION__,
    __CONFIRM_ARCHITECTURE_FUNCTION__,
    __GENERATE_ARCHITECTURE_DIAGRAM_FUNCTION__,
    __DEFINE_MODULES_FUNCTION__,
    __DEFINE_INTERFACES_FUNCTION__,
    __DESIGN_FLOWCHART_FUNCTION__,
    __DESIGN_SEQUENCE_DIAGRAM_FUNCTION__,
    __DEFINE_PROJECT_PHASES_FUNCTION__,
    __DEFINE_FEATURES_FUNCTION__,
    __CREATE_ARCHITECTURE_REPORT_FUNCTION__
]

# ============================================================================
# 工具函数实现
# ============================================================================

def design_architecture(project_name: str, project_description: str, 
                       architecture_type: str, output_path: str = None) -> str:
    '''
    Design system architecture based on project requirements.
    
    :param project_name: Name of the project
    :type project_name: str
    :param project_description: Description of the project
    :type project_description: str
    :param architecture_type: Type of architecture
    :type architecture_type: str
    :param output_path: Path to save the architecture design
    :type output_path: str
    :return: Architecture design that needs user confirmation
    :rtype: str
    '''
    try:
        # Generate architecture design based on inputs
        architecture_data = {
            "project_name": project_name,
            "project_description": project_description,
            "architecture_type": architecture_type,
            "generated_at": datetime.now().isoformat(),
            "components": [],
            "connections": [],
            "principles": [],
            "constraints": []
        }
        
        # Add components based on architecture type
        if architecture_type.lower() == "microservices":
            architecture_data["components"] = [
                {"id": "api_gateway", "name": "API Gateway", "type": "gateway", "description": "Entry point for all requests"},
                {"id": "service_registry", "name": "Service Registry", "type": "registry", "description": "Service discovery and registration"},
                {"id": "auth_service", "name": "Authentication Service", "type": "service", "description": "Handles user authentication"},
                {"id": "user_service", "name": "User Service", "type": "service", "description": "Manages user data"},
                {"id": "product_service", "name": "Product Service", "type": "service", "description": "Manages product catalog"},
                {"id": "order_service", "name": "Order Service", "type": "service", "description": "Handles orders"},
                {"id": "payment_service", "name": "Payment Service", "type": "service", "description": "Processes payments"},
                {"id": "database", "name": "Database Cluster", "type": "database", "description": "Distributed database"},
                {"id": "cache", "name": "Cache Layer", "type": "cache", "description": "Redis cache for performance"},
                {"id": "message_queue", "name": "Message Queue", "type": "queue", "description": "Kafka/RabbitMQ for async communication"}
            ]
            architecture_data["connections"] = [
                {"from": "api_gateway", "to": "auth_service", "type": "authenticates", "label": "validates tokens"},
                {"from": "api_gateway", "to": "service_registry", "type": "discovers", "label": "finds services"},
                {"from": "api_gateway", "to": "user_service", "type": "routes", "label": "user requests"},
                {"from": "api_gateway", "to": "product_service", "type": "routes", "label": "product requests"},
                {"from": "api_gateway", "to": "order_service", "type": "routes", "label": "order requests"},
                {"from": "order_service", "to": "payment_service", "type": "triggers", "label": "payment processing"},
                {"from": "services", "to": "database", "type": "stores", "label": "persistent data"},
                {"from": "services", "to": "cache", "type": "caches", "label": "frequent data"},
                {"from": "services", "to": "message_queue", "type": "publishes", "label": "async events"}
            ]
            architecture_data["principles"] = [
                "Single responsibility per service",
                "Independent deployability",
                "Decentralized data management",
                "API-first design",
                "Event-driven communication"
            ]
            
        elif architecture_type.lower() == "monolith":
            architecture_data["components"] = [
                {"id": "web_layer", "name": "Web Layer", "type": "presentation", "description": "Controllers and views"},
                {"id": "business_layer", "name": "Business Layer", "type": "business", "description": "Service and domain logic"},
                {"id": "data_layer", "name": "Data Layer", "type": "data", "description": "Data access and persistence"},
                {"id": "database", "name": "Database", "type": "database", "description": "Relational database"},
                {"id": "cache", "name": "Cache", "type": "cache", "description": "In-memory cache"},
                {"id": "external_apis", "name": "External APIs", "type": "integration", "description": "Third-party integrations"}
            ]
            architecture_data["connections"] = [
                {"from": "web_layer", "to": "business_layer", "type": "delegates", "label": "business logic"},
                {"from": "business_layer", "to": "data_layer", "type": "persists", "label": "data operations"},
                {"from": "data_layer", "to": "database", "type": "stores", "label": "persistent storage"},
                {"from": "business_layer", "to": "cache", "type": "caches", "label": "performance optimization"},
                {"from": "business_layer", "to": "external_apis", "type": "integrates", "label": "external services"}
            ]
            architecture_data["principles"] = [
                "Layered architecture",
                "Separation of concerns",
                "Centralized data management",
                "Simplified deployment",
                "Easier debugging and testing"
            ]
            
        elif architecture_type.lower() == "serverless":
            architecture_data["components"] = [
                {"id": "api_gateway", "name": "API Gateway", "type": "gateway", "description": "Serverless API endpoints"},
                {"id": "lambda_functions", "name": "Lambda Functions", "type": "compute", "description": "Stateless functions"},
                {"id": "event_sources", "name": "Event Sources", "type": "trigger", "description": "S3, DynamoDB streams, etc."},
                {"id": "dynamodb", "name": "DynamoDB", "type": "database", "description": "NoSQL database"},
                {"id": "s3", "name": "S3 Buckets", "type": "storage", "description": "Object storage"},
                {"id": "cloudwatch", "name": "CloudWatch", "type": "monitoring", "description": "Logging and metrics"}
            ]
            architecture_data["connections"] = [
                {"from": "api_gateway", "to": "lambda_functions", "type": "triggers", "label": "HTTP requests"},
                {"from": "event_sources", "to": "lambda_functions", "type": "triggers", "label": "event-driven"},
                {"from": "lambda_functions", "to": "dynamodb", "type": "stores", "label": "data persistence"},
                {"from": "lambda_functions", "to": "s3", "type": "stores", "label": "file storage"},
                {"from": "lambda_functions", "to": "cloudwatch", "type": "logs", "label": "monitoring"}
            ]
            architecture_data["principles"] = [
                "Event-driven execution",
                "Pay-per-use pricing",
                "Automatic scaling",
                "No server management",
                "Built-in high availability"
            ]
            
        else:  # generic architecture
            architecture_data["components"] = [
                {"id": "frontend", "name": "Frontend", "type": "presentation", "description": "User interface"},
                {"id": "backend", "name": "Backend", "type": "business", "description": "Application logic"},
                {"id": "database", "name": "Database", "type": "database", "description": "Data storage"},
                {"id": "cache", "name": "Cache", "type": "cache", "description": "Performance layer"}
            ]
            architecture_data["connections"] = [
                {"from": "frontend", "to": "backend", "type": "requests", "label": "API calls"},
                {"from": "backend", "to": "database", "type": "queries", "label": "data operations"},
                {"from": "backend", "to": "cache", "type": "caches", "label": "frequent data"}
            ]
            architecture_data["principles"] = [
                "Modular design",
                "Scalability",
                "Maintainability",
                "Security by design"
            ]
        
        # Add constraints
        architecture_data["constraints"] = [
            "Must support at least 1000 concurrent users",
            "Response time under 200ms for 95% of requests",
            "99.9% availability target",
            "GDPR compliance for user data"
        ]
        
        # Format output
        summary = f"""# Architecture Design for: {project_name}

## Project Description
{project_description}

## Architecture Type
{architecture_type}

## Key Components
"""
        
        for comp in architecture_data["components"]:
            summary += f"- **{comp['name']}** ({comp['type']}): {comp['description']}\n"
        
        summary += f"""
## Key Principles
"""
        for principle in architecture_data["principles"]:
            summary += f"- {principle}\n"
        
        summary += f"""
## Design Constraints
"""
        for constraint in architecture_data["constraints"]:
            summary += f"- {constraint}\n"
        
        summary += f"""
## Next Steps
1. **Review this architecture design carefully**
2. **Use 'confirm_architecture' tool to confirm or request changes**
3. After confirmation, proceed with:
   - generate_architecture_diagram
   - define_modules
   - define_interfaces
   - design_flowchart
   - design_sequence_diagram
   - define_project_phases
   - define_features
"""
        
        # Save to file if requested
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(architecture_data, f, indent=2, ensure_ascii=False)
                summary += f"\n## Output\nArchitecture data saved to: {output_path}"
            except Exception as e:
                summary += f"\n## Warning\nCould not save to {output_path}: {str(e)}"
        
        return summary
        
    except Exception as e:
        return f"Error: Unexpected error when designing architecture: {str(e)}"

def confirm_architecture(architecture_summary: str, question: str = None) -> str:
    '''
    Confirm architecture design with user.
    
    :param architecture_summary: Summary of architecture to confirm
    :type architecture_summary: str
    :param question: Question to ask user for confirmation
    :type question: str
    :return: Confirmation result
    :rtype: str
    '''
    try:
        # Use enhanced interaction for confirmation
        try:
            from interaction.enhanced_interaction import discuss_with_user
        except ImportError:
            return "Error: Enhanced interaction module not available. Cannot get user confirmation."
        
        if not question:
            question = f"Do you confirm this architecture design? Review carefully before confirming."
        
        # Display architecture summary
        print("\n" + "="*80)
        print("ARCHITECTURE DESIGN FOR CONFIRMATION")
        print("="*80)
        print(architecture_summary)
        print("="*80 + "\n")
        
        # Get user confirmation
        result = discuss_with_user(
            interaction_type="confirm",
            question=question,
            require_confirmation=True,
            blocking=True,
            continue_condition="user_input"
        )
        
        return result
        
    except Exception as e:
        return f"Error: Unexpected error when confirming architecture: {str(e)}"

def generate_architecture_diagram(architecture_data: str, format: str = "mermaid", 
                                 output_path: str = None) -> str:
    '''
    Generate visual architecture diagram from architecture data.
    
    :param architecture_data: Architecture data in JSON format
    :type architecture_data: str
    :param format: Output format: 'mermaid', 'png', 'svg', 'pdf'
    :type format: str
    :param output_path: Path to save the diagram
    :type output_path: str
    :return: Diagram generation result
    :rtype: str
    '''
    try:
        # Parse architecture data
        try:
            data = json.loads(architecture_data)
        except json.JSONDecodeError:
            # Try to interpret as file path
            if os.path.exists(architecture_data):
                try:
                    with open(architecture_data, 'r') as f:
                        data = json.load(f)
                except:
                    return f"Error: Could not parse architecture data from file: {architecture_data}"
            else:
                return f"Error: Invalid JSON architecture data"
        
        # Use diagram module to generate diagram
        try:
            from diagram.diagram import create_architecture_diagram
        except ImportError:
            return "Error: Diagram module not available. Please ensure diagram module is installed."
        
        # Extract components and connections
        components = data.get("components", [])
        connections = data.get("connections", [])
        title = f"Architecture Diagram: {data.get('project_name', 'System')}"
        
        if not components:
            return "Error: No components found in architecture data"
        
        # Convert to JSON strings for diagram module
        components_json = json.dumps(components, ensure_ascii=False)
        connections_json = json.dumps(connections, ensure_ascii=False) if connections else "[]"
        
        # Generate diagram
        result = create_architecture_diagram(
            components=components_json,
            connections=connections_json,
            title=title,
            output_format=format,
            output_path=output_path
        )
        
        return result
        
    except Exception as e:
        return f"Error: Unexpected error when generating architecture diagram: {str(e)}"

def define_modules(architecture_data: str, output_path: str = None) -> str:
    '''
    Define modules and their responsibilities based on confirmed architecture.
    
    :param architecture_data: Architecture data in JSON format
    :type architecture_data: str
    :param output_path: Path to save the modules definition
    :type output_path: str
    :return: Modules definition
    :rtype: str
    '''
    try:
        # Parse architecture data
        try:
            data = json.loads(architecture_data)
        except json.JSONDecodeError:
            if os.path.exists(architecture_data):
                try:
                    with open(architecture_data, 'r') as f:
                        data = json.load(f)
                except:
                    return f"Error: Could not parse architecture data from file: {architecture_data}"
            else:
                return f"Error: Invalid JSON architecture data"
        
        # Extract components and map to modules
        components = data.get("components", [])
        architecture_type = data.get("architecture_type", "generic").lower()
        
        modules = []
        
        if architecture_type == "microservices":
            # Group related services into modules
            service_components = [c for c in components if c.get("type") == "service"]
            infra_components = [c for c in components if c.get("type") in ["database", "cache", "queue", "gateway", "registry"]]
            
            # Create service modules
            for service in service_components:
                module = {
                    "name": service["name"].replace(" Service", "").replace(" service", ""),
                    "type": "service",
                    "responsibilities": [
                        f"Implements {service['name']} business logic",
                        "Manages its own data store",
                        "Exposes REST/gRPC APIs",
                        "Publishes domain events",
                        "Handles its own deployment"
                    ],
                    "technologies": ["Java/Go/Node.js", "Docker", "Kubernetes", "PostgreSQL/MongoDB"],
                    "team_size": "2-3 developers",
                    "dependencies": ["API Gateway", "Service Registry", "Message Queue"]
                }
                modules.append(module)
            
            # Create infrastructure modules
            infra_module = {
                "name": "Infrastructure Platform",
                "type": "platform",
                "responsibilities": [
                    "Provides shared infrastructure services",
                    "Manages service discovery",
                    "Handles API routing and rate limiting",
                    "Manages message queues",
                    "Provides monitoring and logging"
                ],
                "technologies": ["Kubernetes", "Istio/Linkerd", "Kafka/RabbitMQ", "Prometheus/Grafana"],
                "team_size": "3-4 DevOps engineers",
                "dependencies": []
            }
            modules.append(infra_module)
            
        elif architecture_type == "monolith":
            # Create layered modules
            layers = [
                {
                    "name": "Presentation Layer",
                    "type": "layer",
                    "responsibilities": [
                        "Handles HTTP requests/responses",
                        "Input validation and sanitization",
                        "Authentication and authorization",
                        "API documentation"
                    ],
                    "technologies": ["Spring MVC/Express.js/Django REST", "Swagger/OpenAPI"],
                    "team_size": "2-3 developers",
                    "dependencies": ["Business Layer"]
                },
                {
                    "name": "Business Layer",
                    "type": "layer",
                    "responsibilities": [
                        "Implements core business logic",
                        "Domain model and services",
                        "Transaction management",
                        "Business rules validation"
                    ],
                    "technologies": ["Java/Python/Node.js", "Spring/Django/NestJS"],
                    "team_size": "3-4 developers",
                    "dependencies": ["Presentation Layer", "Data Layer"]
                },
                {
                    "name": "Data Layer",
                    "type": "layer",
                    "responsibilities": [
                        "Data access and persistence",
                        "Database migrations",
                        "Caching strategy",
                        "Data integrity"
                    ],
                    "technologies": ["PostgreSQL/MySQL", "Redis", "Hibernate/TypeORM/Sequelize"],
                    "team_size": "2-3 developers",
                    "dependencies": ["Business Layer"]
                }
            ]
            modules.extend(layers)
            
        else:  # generic
            # Create modules based on component types
            type_groups = {}
            for comp in components:
                comp_type = comp.get("type", "other")
                if comp_type not in type_groups:
                    type_groups[comp_type] = []
                type_groups[comp_type].append(comp)
            
            for comp_type, comps in type_groups.items():
                module = {
                    "name": f"{comp_type.capitalize()} Module",
                    "type": comp_type,
                    "responsibilities": [
                        f"Manages all {comp_type} components",
                        f"Handles {comp_type}-specific logic"
                    ],
                    "technologies": ["To be determined based on requirements"],
                    "team_size": "2-4 developers",
                    "dependencies": [f"Other modules that interact with {comp_type}"]
                }
                modules.append(module)
        
        # Add metadata
        modules_data = {
            "project_name": data.get("project_name", "Unknown Project"),
            "architecture_type": architecture_type,
            "generated_at": datetime.now().isoformat(),
            "modules": modules
        }
        
        # Format output
        output = f"""# Module Definitions for: {modules_data['project_name']}

## Architecture Type: {architecture_type}
## Total Modules: {len(modules)}

"""
        
        for i, module in enumerate(modules, 1):
            output += f"""## Module {i}: {module['name']}

**Type**: {module['type']}

**Responsibilities**:
"""
            for resp in module['responsibilities']:
                output += f"- {resp}\n"
            
            output += f"""
**Technologies**:
"""
            for tech in module['technologies']:
                output += f"- {tech}\n"
            
            output += f"""
**Team Size**: {module['team_size']}

**Dependencies**:
"""
            for dep in module['dependencies']:
                output += f"- {dep}\n"
            
            output += "\n" + "-"*60 + "\n\n"
        
        # Save to file if requested
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(modules_data, f, indent=2, ensure_ascii=False)
                output += f"\n## Output\nModules data saved to: {output_path}"
            except Exception as e:
                output += f"\n## Warning\nCould not save to {output_path}: {str(e)}"
        
        return output
        
    except Exception as e:
        return f"Error: Unexpected error when defining modules: {str(e)}"

def define_interfaces(modules_data: str, output_path: str = None) -> str:
    '''
    Define interfaces between modules with contracts and protocols.
    
    :param modules_data: Modules data in JSON format
    :type modules_data: str
    :param output_path: Path to save the interfaces definition
    :type output_path: str
    :return: Interfaces definition
    :rtype: str
    '''
    try:
        # Parse modules data
        try:
            data = json.loads(modules_data)
        except json.JSONDecodeError:
            if os.path.exists(modules_data):
                try:
                    with open(modules_data, 'r') as f:
                        data = json.load(f)
                except:
                    return f"Error: Could not parse modules data from file: {modules_data}"
            else:
                return f"Error: Invalid JSON modules data"
        
        modules = data.get("modules", [])
        if not modules:
            return "Error: No modules found in modules data"
        
        # Generate interfaces based on module dependencies
        interfaces = []
        
        for i, module1 in enumerate(modules):
            for j, module2 in enumerate(modules):
                if i >= j:  # Avoid duplicate interfaces
                    continue
                
                # Check if modules have dependencies on each other
                has_dependency = False
                if module2['name'] in module1.get('dependencies', []):
                    has_dependency = True
                    direction = f"{module1['name']} → {module2['name']}"
                elif module1['name'] in module2.get('dependencies', []):
                    has_dependency = True
                    direction = f"{module2['name']} → {module1['name']}"
                
                if has_dependency:
                    # Create interface definition
                    interface = {
                        "name": f"{module1['name']}_to_{module2['name']}",
                        "parties": [module1['name'], module2['name']],
                        "type": "API" if module1['type'] == 'service' or module2['type'] == 'service' else "Library",
                        "protocol": "REST/HTTP" if module1['type'] == 'service' or module2['type'] == 'service' else "Internal API",
                        "data_format": "JSON",
                        "authentication": "JWT/OAuth2" if module1['type'] == 'service' or module2['type'] == 'service' else "None required",
                        "rate_limiting": "Yes, 1000 req/min" if module1['type'] == 'service' or module2['type'] == 'service' else "No",
                        "versioning": "Semantic versioning",
                        "error_handling": "Standard HTTP error codes with error details"
                    }
                    interfaces.append(interface)
        
        # Add metadata
        interfaces_data = {
            "project_name": data.get("project_name", "Unknown Project"),
            "generated_at": datetime.now().isoformat(),
            "total_interfaces": len(interfaces),
            "interfaces": interfaces
        }
        
        # Format output
        output = f"""# Interface Definitions for: {interfaces_data['project_name']}

## Total Interfaces: {len(interfaces)}

"""
        
        for i, interface in enumerate(interfaces, 1):
            output += f"""## Interface {i}: {interface['name']}

**Parties**: {', '.join(interface['parties'])}

**Type**: {interface['type']}

**Protocol**: {interface['protocol']}

**Data Format**: {interface['data_format']}

**Authentication**: {interface['authentication']}

**Rate Limiting**: {interface['rate_limiting']}

**Versioning Strategy**: {interface['versioning']}

**Error Handling**: {interface['error_handling']}

**Example Request**:
```http
POST /api/v1/{interface['name'].replace('_to_', '/')}
Authorization: Bearer <token>
Content-Type: application/json

{{
  "data": "example request payload"
}}
```

**Example Response**:
```json
{{
  "status": "success",
  "data": {{}},
  "timestamp": "2024-01-01T00:00:00Z"
}}
```

""" + "-"*60 + "\n\n"
        
        # Save to file if requested
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(interfaces_data, f, indent=2, ensure_ascii=False)
                output += f"\n## Output\nInterfaces data saved to: {output_path}"
            except Exception as e:
                output += f"\n## Warning\nCould not save to {output_path}: {str(e)}"
        
        return output
        
    except Exception as e:
        return f"Error: Unexpected error when defining interfaces: {str(e)}"

def design_flowchart(architecture_data: str, process_name: str, 
                    output_path: str = None) -> str:
    '''
    Design flowchart for key processes in the system.
    
    :param architecture_data: Architecture data in JSON format
    :type architecture_data: str
    :param process_name: Name of the process to diagram
    :type process_name: str
    :param output_path: Path to save the flowchart
    :type output_path: str
    :return: Flowchart design
    :rtype: str
    '''
    try:
        # Parse architecture data
        try:
            data = json.loads(architecture_data)
        except json.JSONDecodeError:
            if os.path.exists(architecture_data):
                try:
                    with open(architecture_data, 'r') as f:
                        data = json.load(f)
                except:
                    return f"Error: Could not parse architecture data from file: {architecture_data}"
            else:
                return f"Error: Invalid JSON architecture data"
        
        # Generate flowchart based on process name
        process_name_lower = process_name.lower()
        
        # Common processes
        if "user" in process_name_lower and "registration" in process_name_lower:
            steps = [
                {"id": "start", "label": "User Registration Start", "type": "start"},
                {"id": "input", "label": "Collect User Details", "type": "input"},
                {"id": "validate", "label": "Validate Input", "type": "decision"},
                {"id": "check", "label": "Check Duplicate User", "type": "process"},
                {"id": "create", "label": "Create User Record", "type": "process"},
                {"id": "notify", "label": "Send Welcome Email", "type": "process"},
                {"id": "end", "label": "Registration Complete", "type": "end"}
            ]
            description = "User registration process with validation and notification."
            
        elif "order" in process_name_lower and "process" in process_name_lower:
            steps = [
                {"id": "start", "label": "Order Received", "type": "start"},
                {"id": "validate", "label": "Validate Order", "type": "decision"},
                {"id": "check", "label": "Check Inventory", "type": "process"},
                {"id": "payment", "label": "Process Payment", "type": "process"},
                {"id": "fulfill", "label": "Fulfill Order", "type": "process"},
                {"id": "ship", "label": "Ship Order", "type": "process"},
                {"id": "notify", "label": "Send Shipping Notification", "type": "process"},
                {"id": "end", "label": "Order Complete", "type": "end"}
            ]
            description = "Order processing workflow from validation to shipping."
            
        elif "payment" in process_name_lower:
            steps = [
                {"id": "start", "label": "Payment Initiated", "type": "start"},
                {"id": "validate", "label": "Validate Payment Details", "type": "decision"},
                {"id": "auth", "label": "Authorize Payment", "type": "process"},
                {"id": "process", "label": "Process Payment", "type": "process"},
                {"id": "record", "label": "Record Transaction", "type": "process"},
                {"id": "notify", "label": "Send Payment Confirmation", "type": "process"},
                {"id": "end", "label": "Payment Complete", "type": "end"}
            ]
            description = "Payment processing workflow with authorization and recording."
            
        else:
            # Generic flowchart
            steps = [
                {"id": "start", "label": f"Start {process_name}", "type": "start"},
                {"id": "step1", "label": "Step 1: Initial Processing", "type": "process"},
                {"id": "decision", "label": "Decision Point", "type": "decision"},
                {"id": "step2a", "label": "Path A: Alternative Process", "type": "process"},
                {"id": "step2b", "label": "Path B: Main Process", "type": "process"},
                {"id": "merge", "label": "Merge Paths", "type": "process"},
                {"id": "final", "label": "Final Processing", "type": "process"},
                {"id": "end", "label": f"End {process_name}", "type": "end"}
            ]
            description = f"Generic flowchart for {process_name} process."
        
        # Use diagram module to generate flowchart
        try:
            from diagram.diagram import create_flowchart
        except ImportError:
            return "Error: Diagram module not available. Please ensure diagram module is installed."
        
        steps_json = json.dumps(steps, ensure_ascii=False)
        
        result = create_flowchart(
            steps=steps_json,
            title=f"Flowchart: {process_name}",
            output_format="mermaid",
            output_path=output_path
        )
        
        if output_path and "saved to" in result:
            return f"""# Flowchart Design: {process_name}

## Description
{description}

## Steps
"""
        for step in steps:
            return f"- {step['label']} ({step['type']})\n" + f"\n## Diagram\n{result}"
        else:
            return f"""# Flowchart Design: {process_name}

## Description
{description}

## Steps
"""
        for step in steps:
            return f"- {step['label']} ({step['type']})\n" + f"\n## Diagram Code\n```mermaid\n{result}\n```"
        
    except Exception as e:
        return f"Error: Unexpected error when designing flowchart: {str(e)}"

def design_sequence_diagram(architecture_data: str, interaction_scenario: str,
                           output_path: str = None) -> str:
    '''
    Design sequence diagram for key interactions in the system.
    
    :param architecture_data: Architecture data in JSON format
    :type architecture_data: str
    :param interaction_scenario: Scenario to diagram
    :type interaction_scenario: str
    :param output_path: Path to save the sequence diagram
    :type output_path: str
    :return: Sequence diagram design
    :rtype: str
    '''
    try:
        # Parse architecture data
        try:
            data = json.loads(architecture_data)
        except json.JSONDecodeError:
            if os.path.exists(architecture_data):
                try:
                    with open(architecture_data, 'r') as f:
                        data = json.load(f)
                except:
                    return f"Error: Could not parse architecture data from file: {architecture_data}"
            else:
                return f"Error: Invalid JSON architecture data"
        
        # Generate sequence diagram based on scenario
        scenario_lower = interaction_scenario.lower()
        
        # Common scenarios
        if "user" in scenario_lower and "login" in scenario_lower:
            actors = [
                {"name": "User", "type": "actor"},
                {"name": "Frontend", "type": "participant"},
                {"name": "AuthService", "type": "participant"},
                {"name": "Database", "type": "database"}
            ]
            messages = [
                {"from": "User", "to": "Frontend", "message": "Enter credentials", "type": "sync"},
                {"from": "Frontend", "to": "AuthService", "message": "POST /api/login", "type": "sync"},
                {"from": "AuthService", "to": "Database", "message": "Query user credentials", "type": "sync"},
                {"from": "Database", "to": "AuthService", "message": "Return user data", "type": "return"},
                {"from": "AuthService", "to": "AuthService", "message": "Validate password", "type": "self"},
                {"from": "AuthService", "to": "AuthService", "message": "Generate JWT token", "type": "self"},
                {"from": "AuthService", "to": "Frontend", "message": "Return JWT token", "type": "return"},
                {"from": "Frontend", "to": "User", "message": "Display success & store token", "type": "sync"}
            ]
            description = "User login sequence with authentication and token generation."
            
        elif "place" in scenario_lower and "order" in scenario_lower:
            actors = [
                {"name": "Customer", "type": "actor"},
                {"name": "Frontend", "type": "participant"},
                {"name": "OrderService", "type": "participant"},
                {"name": "InventoryService", "type": "participant"},
                {"name": "PaymentService", "type": "participant"},
                {"name": "NotificationService", "type": "participant"}
            ]
            messages = [
                {"from": "Customer", "to": "Frontend", "message": "Submit order", "type": "sync"},
                {"from": "Frontend", "to": "OrderService", "message": "POST /api/orders", "type": "sync"},
                {"from": "OrderService", "to": "InventoryService", "message": "Check product availability", "type": "sync"},
                {"from": "InventoryService", "to": "OrderService", "message": "Availability status", "type": "return"},
                {"from": "OrderService", "to": "PaymentService", "message": "Process payment", "type": "sync"},
                {"from": "PaymentService", "to": "OrderService", "message": "Payment confirmation", "type": "return"},
                {"from": "OrderService", "to": "InventoryService", "message": "Reserve items", "type": "sync"},
                {"from": "OrderService", "to": "NotificationService", "message": "Send order confirmation", "type": "async"},
                {"from": "OrderService", "to": "Frontend", "message": "Order confirmation", "type": "return"},
                {"from": "Frontend", "to": "Customer", "message": "Display order confirmation", "type": "sync"}
            ]
            description = "Order placement sequence with inventory check, payment processing, and notifications."
            
        else:
            # Generic sequence diagram
            actors = [
                {"name": "Client", "type": "actor"},
                {"name": "API Gateway", "type": "participant"},
                {"name": "Service A", "type": "participant"},
                {"name": "Service B", "type": "participant"},
                {"name": "Database", "type": "database"}
            ]
            messages = [
                {"from": "Client", "to": "API Gateway", "message": "Request data", "type": "sync"},
                {"from": "API Gateway", "to": "Service A", "message": "Forward request", "type": "sync"},
                {"from": "Service A", "to": "Service B", "message": "Get additional data", "type": "sync"},
                {"from": "Service B", "to": "Database", "message": "Query database", "type": "sync"},
                {"from": "Database", "to": "Service B", "message": "Return data", "type": "return"},
                {"from": "Service B", "to": "Service A", "message": "Return processed data", "type": "return"},
                {"from": "Service A", "to": "API Gateway", "message": "Return response", "type": "return"},
                {"from": "API Gateway", "to": "Client", "message": "Final response", "type": "return"}
            ]
            description = f"Generic sequence diagram for {interaction_scenario} interaction."
        
        # Use diagram module to generate sequence diagram
        try:
            from diagram.diagram import create_sequence_diagram
        except ImportError:
            return "Error: Diagram module not available. Please ensure diagram module is installed."
        
        actors_json = json.dumps(actors, ensure_ascii=False)
        messages_json = json.dumps(messages, ensure_ascii=False)
        
        result = create_sequence_diagram(
            actors=actors_json,
            messages=messages_json,
            title=f"Sequence Diagram: {interaction_scenario}",
            output_format="mermaid",
            output_path=output_path
        )
        
        if output_path and "saved to" in result:
            return f"""# Sequence Diagram Design: {interaction_scenario}

## Description
{description}

## Actors
"""
        for actor in actors:
            return f"- {actor['name']} ({actor['type']})\n" + f"\n## Interaction Flow\n" + f"\n## Diagram\n{result}"
        else:
            return f"""# Sequence Diagram Design: {interaction_scenario}

## Description
{description}

## Actors
"""
        for actor in actors:
            return f"- {actor['name']} ({actor['type']})\n" + f"\n## Interaction Flow\n" + f"\n## Diagram Code\n```mermaid\n{result}\n```"
        
    except Exception as e:
        return f"Error: Unexpected error when designing sequence diagram: {str(e)}"

def define_project_phases(project_name: str, architecture_data: str, 
                         modules_data: str, output_path: str = None) -> str:
    '''
    Define project phases, timelines, and deliverables.
    
    :param project_name: Name of the project
    :type project_name: str
    :param architecture_data: Architecture data in JSON format
    :type architecture_data: str
    :param modules_data: Modules data in JSON format
    :type modules_data: str
    :param output_path: Path to save the phases definition
    :type output_path: str
    :return: Project phases definition
    :rtype: str
    '''
    try:
        # Parse data
        arch_data = {}
        if architecture_data:
            try:
                arch_data = json.loads(architecture_data)
            except json.JSONDecodeError:
                if os.path.exists(architecture_data):
                    try:
                        with open(architecture_data, 'r') as f:
                            arch_data = json.load(f)
                    except:
                        pass
        
        mod_data = {}
        if modules_data:
            try:
                mod_data = json.loads(modules_data)
            except json.JSONDecodeError:
                if os.path.exists(modules_data):
                    try:
                        with open(modules_data, 'r') as f:
                            mod_data = json.load(f)
                    except:
                        pass
        
        # Determine architecture type
        arch_type = arch_data.get("architecture_type", "generic").lower()
        modules = mod_data.get("modules", [])
        
        # Define phases based on architecture type and modules
        phases = []
        
        if arch_type == "microservices":
            phases = [
                {
                    "name": "Phase 1: Foundation & Core Services",
                    "duration": "6-8 weeks",
                    "deliverables": [
                        "Setup development environment and CI/CD pipeline",
                        "Implement API Gateway and Service Registry",
                        "Build Authentication & User services",
                        "Setup basic monitoring and logging",
                        "Deploy to development environment"
                    ],
                    "success_criteria": [
                        "All developers can run services locally",
                        "CI/CD pipeline is operational",
                        "Basic authentication works",
                        "Services can communicate via API Gateway"
                    ]
                },
                {
                    "name": "Phase 2: Business Domain Services",
                    "duration": "8-10 weeks",
                    "deliverables": [
                        "Implement Product and Order services",
                        "Setup message queue for async communication",
                        "Implement payment service integration",
                        "Add comprehensive testing",
                        "Performance testing setup"
                    ],
                    "success_criteria": [
                        "All core business services are implemented",
                        "Services communicate via events",
                        "Test coverage > 80%",
                        "Performance meets baseline requirements"
                    ]
                },
                {
                    "name": "Phase 3: Advanced Features & Optimization",
                    "duration": "6-8 weeks",
                    "deliverables": [
                        "Implement caching layer",
                        "Add advanced monitoring and alerting",
                        "Implement rate limiting and circuit breakers",
                        "Security hardening",
                        "Documentation completion"
                    ],
                    "success_criteria": [
                        "System handles expected load",
                        "Comprehensive monitoring in place",
                        "Security audit passed",
                        "Documentation is complete"
                    ]
                },
                {
                    "name": "Phase 4: Production Readiness & Launch",
                    "duration": "4-6 weeks",
                    "deliverables": [
                        "Load testing and optimization",
                        "Disaster recovery planning",
                        "Production deployment",
                        "Team training and handover",
                        "Post-launch support plan"
                    ],
                    "success_criteria": [
                        "System passes production readiness review",
                        "Successful production deployment",
                        "Support team trained",
                        "Launch metrics tracking in place"
                    ]
                }
            ]
        elif arch_type == "monolith":
            phases = [
                {
                    "name": "Phase 1: Foundation & Core Structure",
                    "duration": "4-6 weeks",
                    "deliverables": [
                        "Project setup and development environment",
                        "Database schema design and implementation",
                        "Core domain models and business logic",
                        "Basic API endpoints",
                        "Authentication and authorization"
                    ],
                    "success_criteria": [
                        "Development environment is working",
                        "Database schema is finalized",
                        "Core business logic is implemented",
                        "Basic CRUD operations work"
                    ]
                },
                {
                    "name": "Phase 2: Feature Development",
                    "duration": "8-10 weeks",
                    "deliverables": [
                        "Implement main application features",
                        "User interface development",
                        "Integration with external services",
                        "Comprehensive testing suite",
                        "Performance optimization"
                    ],
                    "success_criteria": [
                        "All planned features are implemented",
                        "UI is functional and user-friendly",
                        "Integration tests pass",
                        "Performance meets requirements"
                    ]
                },
                {
                    "name": "Phase 3: Refinement & Deployment",
                    "duration": "4-6 weeks",
                    "deliverables": [
                        "Security audit and fixes",
                        "Final testing and bug fixes",
                        "Deployment pipeline setup",
                        "Documentation completion",
                        "User acceptance testing"
                    ],
                    "success_criteria": [
                        "Security audit passed",
                        "All critical bugs resolved",
                        "Deployment process automated",
                        "Documentation is complete"
                    ]
                }
            ]
        else:
            # Generic phases
            num_modules = len(modules)
            phase_duration = max(4, num_modules * 2)  # 2 weeks per module minimum
            
            phases = [
                {
                    "name": "Phase 1: Planning & Setup",
                    "duration": "2-3 weeks",
                    "deliverables": [
                        "Project requirements finalization",
                        "Architecture design completion",
                        "Development environment setup",
                        "Team onboarding"
                    ],
                    "success_criteria": [
                        "Requirements document approved",
                        "Architecture design finalized",
                        "All team members can build and run the project"
                    ]
                },
                {
                    "name": "Phase 2: Core Implementation",
                    "duration": f"{phase_duration} weeks",
                    "deliverables": [
                        f"Implement {num_modules} core modules",
                        "Database design and implementation",
                        "Basic API and UI",
                        "Integration between modules"
                    ],
                    "success_criteria": [
                        "All modules are implemented",
                        "Database is operational",
                        "Basic functionality works end-to-end"
                    ]
                },
                {
                    "name": "Phase 3: Testing & Refinement",
                    "duration": "3-4 weeks",
                    "deliverables": [
                        "Comprehensive testing",
                        "Performance optimization",
                        "Security implementation",
                        "User documentation"
                    ],
                    "success_criteria": [
                        "Test coverage > 80%",
                        "Performance meets requirements",
                        "Security audit passed"
                    ]
                },
                {
                    "name": "Phase 4: Deployment & Launch",
                    "duration": "2-3 weeks",
                    "deliverables": [
                        "Production deployment",
                        "Monitoring setup",
                        "Team training",
                        "Launch support"
                    ],
                    "success_criteria": [
                        "Successful production deployment",
                        "Monitoring is operational",
                        "Support team is ready"
                    ]
                }
            ]
        
        # Add metadata
        phases_data = {
            "project_name": project_name,
            "architecture_type": arch_type,
            "total_phases": len(phases),
            "total_duration": sum(int(p["duration"].split("-")[0].split()[0]) for p in phases if p["duration"][0].isdigit()),
            "generated_at": datetime.now().isoformat(),
            "phases": phases
        }
        
        # Format output
        output = f"""# Project Phases for: {project_name}

## Architecture Type: {arch_type}
## Total Phases: {len(phases)}

"""
        
        for i, phase in enumerate(phases, 1):
            output += f"""## Phase {i}: {phase['name']}

**Duration**: {phase['duration']}

**Key Deliverables**:
"""
            for deliverable in phase['deliverables']:
                output += f"- {deliverable}\n"
            
            output += f"""
**Success Criteria**:
"""
            for criterion in phase['success_criteria']:
                output += f"- {criterion}\n"
            
            output += "\n" + "-"*60 + "\n\n"
        
        output += f"""
## Overall Timeline
Total estimated duration: {phases_data['total_duration']} weeks

## Recommendations
1. **Phase Gates**: Review and approve each phase before proceeding to the next
2. **Risk Management**: Identify risks early and have mitigation plans
3. **Stakeholder Communication**: Regular updates to stakeholders
4. **Quality Assurance**: Continuous testing throughout all phases
"""
        
        # Save to file if requested
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(phases_data, f, indent=2, ensure_ascii=False)
                output += f"\n## Output\nPhases data saved to: {output_path}"
            except Exception as e:
                output += f"\n## Warning\nCould not save to {output_path}: {str(e)}"
        
        return output
        
    except Exception as e:
        return f"Error: Unexpected error when defining project phases: {str(e)}"

def define_features(phases_data: str, output_path: str = None) -> str:
    '''
    Define features for each project phase.
    
    :param phases_data: Phases data in JSON format
    :type phases_data: str
    :param output_path: Path to save the features definition
    :type output_path: str
    :return: Features definition
    :rtype: str
    '''
    try:
        # Parse phases data
        try:
            data = json.loads(phases_data)
        except json.JSONDecodeError:
            if os.path.exists(phases_data):
                try:
                    with open(phases_data, 'r') as f:
                        data = json.load(f)
                except:
                    return f"Error: Could not parse phases data from file: {phases_data}"
            else:
                return f"Error: Invalid JSON phases data"
        
        phases = data.get("phases", [])
        if not phases:
            return "Error: No phases found in phases data"
        
        # Generate features for each phase
        features_by_phase = []
        
        for phase in phases:
            phase_name = phase['name']
            deliverables = phase.get('deliverables', [])
            
            # Extract features from deliverables
            features = []
            for deliverable in deliverables:
                # Simple heuristic to extract features
                if "implement" in deliverable.lower() or "build" in deliverable.lower() or "create" in deliverable.lower():
                    # This deliverable likely contains features
                    feature_desc = deliverable
                    
                    # Try to extract specific features
                    if "authentication" in deliverable.lower():
                        features.extend([
                            {
                                "name": "User Registration",
                                "description": "Allow users to create new accounts",
                                "priority": "High",
                                "estimate": "3-5 days"
                            },
                            {
                                "name": "User Login",
                                "description": "Allow existing users to log in",
                                "priority": "High",
                                "estimate": "2-3 days"
                            },
                            {
                                "name": "Password Management",
                                "description": "Password reset and change functionality",
                                "priority": "Medium",
                                "estimate": "2-3 days"
                            }
                        ])
                    elif "product" in deliverable.lower() and "service" in deliverable.lower():
                        features.extend([
                            {
                                "name": "Product Catalog",
                                "description": "Display list of available products",
                                "priority": "High",
                                "estimate": "3-4 days"
                            },
                            {
                                "name": "Product Search",
                                "description": "Search products by name, category, etc.",
                                "priority": "Medium",
                                "estimate": "2-3 days"
                            },
                            {
                                "name": "Product Details",
                                "description": "Detailed view of individual products",
                                "priority": "High",
                                "estimate": "2-3 days"
                            }
                        ])
                    elif "order" in deliverable.lower() and "service" in deliverable.lower():
                        features.extend([
                            {
                                "name": "Order Creation",
                                "description": "Create new orders",
                                "priority": "High",
                                "estimate": "3-4 days"
                            },
                            {
                                "name": "Order Management",
                                "description": "View and manage existing orders",
                                "priority": "Medium",
                                "estimate": "2-3 days"
                            },
                            {
                                "name": "Order History",
                                "description": "View past orders",
                                "priority": "Low",
                                "estimate": "1-2 days"
                            }
                        ])
                    elif "payment" in deliverable.lower():
                        features.extend([
                            {
                                "name": "Payment Processing",
                                "description": "Process credit card payments",
                                "priority": "High",
                                "estimate": "4-5 days"
                            },
                            {
                                "name": "Payment Gateway Integration",
                                "description": "Integrate with Stripe/PayPal",
                                "priority": "High",
                                "estimate": "3-4 days"
                            },
                            {
                                "name": "Payment History",
                                "description": "View payment transactions",
                                "priority": "Medium",
                                "estimate": "2-3 days"
                            }
                        ])
                    elif "api" in deliverable.lower() and "gateway" in deliverable.lower():
                        features.extend([
                            {
                                "name": "API Routing",
                                "description": "Route requests to appropriate services",
                                "priority": "High",
                                "estimate": "3-4 days"
                            },
                            {
                                "name": "Rate Limiting",
                                "description": "Limit requests per client",
                                "priority": "Medium",
                                "estimate": "2-3 days"
                            },
                            {
                                "name": "Request Logging",
                                "description": "Log all API requests",
                                "priority": "Medium",
                                "estimate": "2-3 days"
                            }
                        ])
                    else:
                        # Generic feature
                        features.append({
                            "name": deliverable.split(":")[0] if ":" in deliverable else deliverable.split()[0],
                            "description": deliverable,
                            "priority": "Medium",
                            "estimate": "3-5 days"
                        })
            
            # If no specific features extracted, create generic ones
            if not features:
                features = [
                    {
                        "name": f"Core Feature {i+1} for {phase_name.split(':')[0]}",
                        "description": f"Implementation of key functionality for {phase_name}",
                        "priority": "High" if i == 0 else "Medium",
                        "estimate": "3-5 days"
                    }
                    for i in range(min(3, len(deliverables)))
                ]
            
            features_by_phase.append({
                "phase": phase_name,
                "features": features
            })
        
        # Add metadata
        features_data = {
            "project_name": data.get("project_name", "Unknown Project"),
            "total_phases": len(features_by_phase),
            "total_features": sum(len(phase["features"]) for phase in features_by_phase),
            "generated_at": datetime.now().isoformat(),
            "phases_with_features": features_by_phase
        }
        
        # Format output
        output = f"""# Feature Definitions for: {features_data['project_name']}

## Summary
- Total Phases: {features_data['total_phases']}
- Total Features: {features_data['total_features']}

"""
        
        for phase_data in features_by_phase:
            phase_name = phase_data['phase']
            features = phase_data['features']
            
            output += f"""## {phase_name}

**Features in this phase**: {len(features)}

"""
            
            for i, feature in enumerate(features, 1):
                output += f"""### Feature {i}: {feature['name']}

**Description**: {feature['description']}

**Priority**: {feature['priority']}

**Estimate**: {feature['estimate']}

**Acceptance Criteria**:
- Feature meets all requirements
- Code is properly tested
- Documentation is complete
- Performance meets expectations

**Dependencies**:
- Completion of previous phase features
- Necessary infrastructure in place

"""
            
            output += "-"*60 + "\n\n"
        
        output += f"""
## Feature Development Guidelines

### 1. Prioritization
- **High priority**: Must be completed in current phase
- **Medium priority**: Important but can be deferred if needed
- **Low priority**: Nice-to-have features

### 2. Estimation Guidelines
- **Small**: 1-2 days
- **Medium**: 3-5 days  
- **Large**: 6-10 days
- **Extra Large**: 10+ days (should be broken down)

### 3. Quality Standards
- All features must have unit tests
- Code review is required before merging
- Documentation must be updated
- Performance must be measured
"""
        
        # Save to file if requested
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(features_data, f, indent=2, ensure_ascii=False)
                output += f"\n## Output\nFeatures data saved to: {output_path}"
            except Exception as e:
                output += f"\n## Warning\nCould not save to {output_path}: {str(e)}"
        
        return output
        
    except Exception as e:
        return f"Error: Unexpected error when defining features: {str(e)}"

def create_architecture_report(project_name: str, architecture_data: str,
                             modules_data: str, interfaces_data: str,
                             phases_data: str, features_data: str,
                             output_path: str = None) -> str:
    '''
    Create comprehensive architecture report with all components.
    
    :param project_name: Name of the project
    :type project_name: str
    :param architecture_data: Architecture data in JSON format
    :type architecture_data: str
    :param modules_data: Modules data in JSON format
    :type modules_data: str
    :param interfaces_data: Interfaces data in JSON format
    :type interfaces_data: str
    :param phases_data: Phases data in JSON format
    :type phases_data: str
    :param features_data: Features data in JSON format
    :type features_data: str
    :param output_path: Path to save the report
    :type output_path: str
    :return: Comprehensive architecture report
    :rtype: str
    '''
    try:
        # Try to parse all data
        data_sources = {
            "architecture": architecture_data,
            "modules": modules_data,
            "interfaces": interfaces_data,
            "phases": phases_data,
            "features": features_data
        }
        
        parsed_data = {}
        for key, data_str in data_sources.items():
            if data_str:
                try:
                    parsed_data[key] = json.loads(data_str)
                except json.JSONDecodeError:
                    if os.path.exists(data_str):
                        try:
                            with open(data_str, 'r') as f:
                                parsed_data[key] = json.load(f)
                        except:
                            parsed_data[key] = {"error": f"Could not parse {key} data"}
                    else:
                        parsed_data[key] = {"error": f"Invalid {key} data"}
            else:
                parsed_data[key] = {"info": f"No {key} data provided"}
        
        # Create comprehensive report
        report = f"""# COMPREHENSIVE ARCHITECTURE REPORT

## Project: {project_name}
## Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'='*80}

## 1. EXECUTIVE SUMMARY

This document provides a complete architecture overview for the {project_name} project.
It includes system architecture, module definitions, interfaces, project phases,
and feature specifications.

{'='*80}

## 2. SYSTEM ARCHITECTURE
"""
        
        arch_data = parsed_data.get("architecture", {})
        if "error" not in arch_data and "info" not in arch_data:
            report += f"""
### 2.1 Architecture Type
{arch_data.get('architecture_type', 'Not specified')}

### 2.2 Key Components
"""
            for comp in arch_data.get("components", []):
                report += f"- **{comp.get('name', 'Unknown')}**: {comp.get('description', 'No description')} ({comp.get('type', 'Unknown type')})\n"
            
            report += f"""
### 2.3 Architecture Principles
"""
            for principle in arch_data.get("principles", []):
                report += f"- {principle}\n"
        else:
            report += f"\n*Architecture data: {arch_data.get('error', arch_data.get('info', 'Not available'))}*\n"
        
        report += f"""
{'='*80}

## 3. MODULE DEFINITIONS
"""
        
        mod_data = parsed_data.get("modules", {})
        if "error" not in mod_data and "info" not in mod_data:
            modules = mod_data.get("modules", [])
            report += f"""
### 3.1 Module Overview
Total modules: {len(modules)}

### 3.2 Module Details
"""
            for i, module in enumerate(modules, 1):
                report += f"""
#### Module {i}: {module.get('name', 'Unknown')}
- **Type**: {module.get('type', 'Not specified')}
- **Team Size**: {module.get('team_size', 'Not specified')}

**Responsibilities**:
"""
                for resp in module.get("responsibilities", []):
                    report += f"  - {resp}\n"
                
                report += f"""
**Technologies**:
"""
                for tech in module.get("technologies", []):
                    report += f"  - {tech}\n"
        else:
            report += f"\n*Module data: {mod_data.get('error', mod_data.get('info', 'Not available'))}*\n"
        
        report += f"""
{'='*80}

## 4. INTERFACE DEFINITIONS
"""
        
        int_data = parsed_data.get("interfaces", {})
        if "error" not in int_data and "info" not in int_data:
            interfaces = int_data.get("interfaces", [])
            report += f"""
### 4.1 Interface Overview
Total interfaces: {len(interfaces)}

### 4.2 Key Interfaces
"""
            for i, interface in enumerate(interfaces[:5], 1):  # Limit to 5 interfaces
                report += f"""
#### Interface {i}: {interface.get('name', 'Unknown')}
- **Parties**: {', '.join(interface.get('parties', []))}
- **Type**: {interface.get('type', 'Not specified')}
- **Protocol**: {interface.get('protocol', 'Not specified')}
- **Authentication**: {interface.get('authentication', 'Not specified')}
"""
        else:
            report += f"\n*Interface data: {int_data.get('error', int_data.get('info', 'Not available'))}*\n"
        
        report += f"""
{'='*80}

## 5. PROJECT PHASES
"""
        
        phases_data = parsed_data.get("phases", {})
        if "error" not in phases_data and "info" not in phases_data:
            phases = phases_data.get("phases", [])
            report += f"""
### 5.1 Phase Overview
Total phases: {len(phases)}
Total duration: {phases_data.get('total_duration', 'Unknown')} weeks

### 5.2 Phase Schedule
"""
            for i, phase in enumerate(phases, 1):
                report += f"""
#### Phase {i}: {phase.get('name', 'Unknown')}
- **Duration**: {phase.get('duration', 'Not specified')}

**Key Deliverables**:
"""
                for deliverable in phase.get("deliverables", []):
                    report += f"  - {deliverable}\n"
        else:
            report += f"\n*Phase data: {phases_data.get('error', phases_data.get('info', 'Not available'))}*\n"
        
        report += f"""
{'='*80}

## 6. FEATURE SPECIFICATIONS
"""
        
        features_data = parsed_data.get("features", {})
        if "error" not in features_data and "info" not in features_data:
            phases_with_features = features_data.get("phases_with_features", [])
            report += f"""
### 6.1 Feature Overview
Total features: {features_data.get('total_features', 0)}

### 6.2 Features by Phase
"""
            for phase_data in phases_with_features:
                phase_name = phase_data.get("phase", "Unknown Phase")
                features = phase_data.get("features", [])
                
                report += f"""
#### {phase_name}
Features in this phase: {len(features)}

**Key Features**:
"""
                for i, feature in enumerate(features[:3], 1):  # Limit to 3 features per phase
                    report += f"{i}. **{feature.get('name', 'Unknown')}** ({feature.get('priority', 'Not specified')} priority, {feature.get('estimate', 'Not specified')} estimate)\n"
        else:
            report += f"\n*Feature data: {features_data.get('error', features_data.get('info', 'Not available'))}*\n"
        
        report += f"""
{'='*80}

## 7. RECOMMENDATIONS & NEXT STEPS

### 7.1 Immediate Actions
1. Review and validate architecture decisions
2. Confirm resource allocation for each phase
3. Establish communication channels for stakeholders
4. Set up project tracking and monitoring

### 7.2 Risk Mitigation
1. **Technical Risks**: Regular architecture reviews, proof of concepts for complex features
2. **Schedule Risks**: Buffer time in estimates, regular progress tracking
3. **Resource Risks**: Cross-training, knowledge sharing, documentation
4. **Quality Risks**: Automated testing, code reviews, quality gates

### 7.3 Success Metrics
- **Technical**: System performance, scalability, maintainability
- **Project**: On-time delivery, within budget, stakeholder satisfaction
- **Quality**: Defect rate, test coverage, security compliance

{'='*80}

## 8. APPENDICES

### 8.1 Glossary
- **Architecture**: High-level structure of the system
- **Module**: Self-contained unit of functionality
- **Interface**: Contract between modules or systems
- **Phase**: Time-bound segment of project work
- **Feature**: Distinct piece of functionality delivering value

### 8.2 References
- Architecture decision records (if available)
- Requirements documents
- Stakeholder agreements
- Technical standards and guidelines

{'='*80}

## 9. DOCUMENT HISTORY

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | {datetime.now().strftime('%Y-%m-%d')} | Architecture Tool | Initial version |

{'='*80}

**END OF REPORT**
"""
        
        # Save to file if requested
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(report)
                return f"Success: Comprehensive architecture report saved to {output_path}\\n\\nReport generated successfully with all available data."
            except Exception as e:
                return f"Error: Failed to save report to {output_path}: {str(e)}\\n\\nReport content:\\n\\n{report}"
        
        return report
        
    except Exception as e:
        return f"Error: Unexpected error when creating architecture report: {str(e)}"

TOOL_CALL_MAP = {
    "design_architecture": design_architecture,
    "confirm_architecture": confirm_architecture,
    "generate_architecture_diagram": generate_architecture_diagram,
    "define_modules": define_modules,
    "define_interfaces": define_interfaces,
    "design_flowchart": design_flowchart,
    "design_sequence_diagram": design_sequence_diagram,
    "define_project_phases": define_project_phases,
    "define_features": define_features,
    "create_architecture_report": create_architecture_report
}