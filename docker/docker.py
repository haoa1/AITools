from base import function_ai, parameters_func, property_param

import os
import subprocess
import sys
import json
import time
from typing import Dict, List, Optional, Any

__DOCKER_PROPERTY_ONE__ = property_param(
    name="image",
    description="Docker image name or ID.",
    t="string"
)

__DOCKER_PROPERTY_TWO__ = property_param(
    name="container",
    description="Docker container name or ID.",
    t="string"
)

__DOCKER_PROPERTY_THREE__ = property_param(
    name="name",
    description="Name for the container or resource.",
    t="string"
)

__DOCKER_PROPERTY_4__ = property_param(
    name="command",
    description="Command to run in container.",
    t="string"
)

__DOCKER_PROPERTY_5__ = property_param(
    name="ports",
    description="Port mappings (host:container).",
    t="string"
)

__DOCKER_PROPERTY_6__ = property_param(
    name="volumes",
    description="Volume mappings (host:container).",
    t="string"
)

__DOCKER_PROPERTY_7__ = property_param(
    name="environment",
    description="Environment variables (KEY=VALUE).",
    t="string"
)

__DOCKER_PROPERTY_8__ = property_param(
    name="detach",
    description="Run container in detached mode.",
    t="boolean"
)

__DOCKER_PROPERTY_9__ = property_param(
    name="force",
    description="Force the operation (use with caution).",
    t="boolean"
)

__DOCKER_PROPERTY_10__ = property_param(
    name="all",
    description="Apply operation to all containers/images.",
    t="boolean"
)

__DOCKER_PROPERTY_11__ = property_param(
    name="dockerfile",
    description="Path to Dockerfile for building images.",
    t="string"
)

__DOCKER_PROPERTY_12__ = property_param(
    name="tag",
    description="Tag for docker image.",
    t="string"
)

__DOCKER_PROPERTY_13__ = property_param(
    name="context",
    description="Build context path.",
    t="string"
)

__DOCKER_PROPERTY_14__ = property_param(
    name="network",
    description="Network name or ID.",
    t="string"
)

__DOCKER_PROPERTY_15__ = property_param(
    name="volume",
    description="Volume name or ID.",
    t="string"
)

__DOCKER_PROPERTY_16__ = property_param(
    name="follow",
    description="Follow log output.",
    t="boolean"
)

__DOCKER_PROPERTY_17__ = property_param(
    name="timeout",
    description="Timeout in seconds for command execution.",
    t="integer"
)

__DOCKER_PROPERTY_18__ = property_param(
    name="filter",
    description="Filter output (e.g., 'status=running').",
    t="string"
)

__DOCKER_PROPERTY_19__ = property_param(
    name="workdir",
    description="Working directory inside container.",
    t="string"
)

__DOCKER_PROPERTY_20__ = property_param(
    name="registry",
    description="Docker registry URL.",
    t="string"
)

__DOCKER_PROPERTY_21__ = property_param(
    name="username",
    description="Username for registry authentication.",
    t="string"
)

__DOCKER_PROPERTY_22__ = property_param(
    name="password",
    description="Password for registry authentication.",
    t="string"
)

__DOCKER_PROPERTY_23__ = property_param(
    name="compose_file",
    description="Docker Compose file path.",
    t="string"
)

__DOCKER_PROPERTY_24__ = property_param(
    name="services",
    description="Compose services to operate on.",
    t="string"
)

# Container Management Functions
__DOCKER_RUN_FUNCTION__ = function_ai(name="docker_run",
                                     description="Run a docker container.",
                                     parameters=parameters_func([__DOCKER_PROPERTY_ONE__, __DOCKER_PROPERTY_THREE__, __DOCKER_PROPERTY_4__, __DOCKER_PROPERTY_5__, __DOCKER_PROPERTY_6__, __DOCKER_PROPERTY_7__, __DOCKER_PROPERTY_8__, __DOCKER_PROPERTY_19__]))

__DOCKER_PS_FUNCTION__ = function_ai(name="docker_ps",
                                    description="List docker containers.",
                                    parameters=parameters_func([__DOCKER_PROPERTY_10__, __DOCKER_PROPERTY_18__]))

__DOCKER_START_FUNCTION__ = function_ai(name="docker_start",
                                       description="Start one or more stopped containers.",
                                       parameters=parameters_func([__DOCKER_PROPERTY_TWO__, __DOCKER_PROPERTY_10__]))

__DOCKER_STOP_FUNCTION__ = function_ai(name="docker_stop",
                                      description="Stop one or more running containers.",
                                      parameters=parameters_func([__DOCKER_PROPERTY_TWO__, __DOCKER_PROPERTY_10__, __DOCKER_PROPERTY_9__, __DOCKER_PROPERTY_17__]))

__DOCKER_RESTART_FUNCTION__ = function_ai(name="docker_restart",
                                         description="Restart one or more containers.",
                                         parameters=parameters_func([__DOCKER_PROPERTY_TWO__, __DOCKER_PROPERTY_10__, __DOCKER_PROPERTY_9__]))

__DOCKER_RM_FUNCTION__ = function_ai(name="docker_rm",
                                    description="Remove one or more containers.",
                                    parameters=parameters_func([__DOCKER_PROPERTY_TWO__, __DOCKER_PROPERTY_10__, __DOCKER_PROPERTY_9__]))

__DOCKER_LOGS_FUNCTION__ = function_ai(name="docker_logs",
                                      description="Fetch the logs of a container.",
                                      parameters=parameters_func([__DOCKER_PROPERTY_TWO__, __DOCKER_PROPERTY_16__, __DOCKER_PROPERTY_17__]))

__DOCKER_EXEC_FUNCTION__ = function_ai(name="docker_exec",
                                      description="Run a command in a running container.",
                                      parameters=parameters_func([__DOCKER_PROPERTY_TWO__, __DOCKER_PROPERTY_4__, __DOCKER_PROPERTY_8__, __DOCKER_PROPERTY_19__]))

__DOCKER_INSPECT_FUNCTION__ = function_ai(name="docker_inspect",
                                         description="Return low-level information on Docker objects.",
                                         parameters=parameters_func([__DOCKER_PROPERTY_TWO__]))

# Image Management Functions
__DOCKER_IMAGES_FUNCTION__ = function_ai(name="docker_images",
                                        description="List docker images.",
                                        parameters=parameters_func([]))

__DOCKER_PULL_FUNCTION__ = function_ai(name="docker_pull",
                                      description="Pull an image from a registry.",
                                      parameters=parameters_func([__DOCKER_PROPERTY_ONE__, __DOCKER_PROPERTY_20__, __DOCKER_PROPERTY_21__, __DOCKER_PROPERTY_22__]))

__DOCKER_BUILD_FUNCTION__ = function_ai(name="docker_build",
                                       description="Build an image from a Dockerfile.",
                                       parameters=parameters_func([__DOCKER_PROPERTY_11__, __DOCKER_PROPERTY_12__, __DOCKER_PROPERTY_13__, __DOCKER_PROPERTY_ONE__]))

__DOCKER_PUSH_FUNCTION__ = function_ai(name="docker_push",
                                      description="Push an image to a registry.",
                                      parameters=parameters_func([__DOCKER_PROPERTY_ONE__, __DOCKER_PROPERTY_20__, __DOCKER_PROPERTY_21__, __DOCKER_PROPERTY_22__]))

__DOCKER_RMI_FUNCTION__ = function_ai(name="docker_rmi",
                                     description="Remove one or more images.",
                                     parameters=parameters_func([__DOCKER_PROPERTY_ONE__, __DOCKER_PROPERTY_9__, __DOCKER_PROPERTY_10__]))

# Network Management Functions
__DOCKER_NETWORK_LS_FUNCTION__ = function_ai(name="docker_network_ls",
                                            description="List docker networks.",
                                            parameters=parameters_func([]))

__DOCKER_NETWORK_CREATE_FUNCTION__ = function_ai(name="docker_network_create",
                                                description="Create a docker network.",
                                                parameters=parameters_func([__DOCKER_PROPERTY_THREE__, __DOCKER_PROPERTY_14__]))

__DOCKER_NETWORK_RM_FUNCTION__ = function_ai(name="docker_network_rm",
                                            description="Remove one or more docker networks.",
                                            parameters=parameters_func([__DOCKER_PROPERTY_14__, __DOCKER_PROPERTY_9__]))

# Volume Management Functions
__DOCKER_VOLUME_LS_FUNCTION__ = function_ai(name="docker_volume_ls",
                                           description="List docker volumes.",
                                           parameters=parameters_func([]))

__DOCKER_VOLUME_CREATE_FUNCTION__ = function_ai(name="docker_volume_create",
                                               description="Create a docker volume.",
                                               parameters=parameters_func([__DOCKER_PROPERTY_THREE__, __DOCKER_PROPERTY_15__]))

__DOCKER_VOLUME_RM_FUNCTION__ = function_ai(name="docker_volume_rm",
                                           description="Remove one or more docker volumes.",
                                           parameters=parameters_func([__DOCKER_PROPERTY_15__, __DOCKER_PROPERTY_9__]))

# System Functions
__DOCKER_INFO_FUNCTION__ = function_ai(name="docker_info",
                                      description="Display system-wide information.",
                                      parameters=parameters_func([]))

__DOCKER_VERSION_FUNCTION__ = function_ai(name="docker_version",
                                         description="Show the Docker version information.",
                                         parameters=parameters_func([]))

# Compose Functions
__DOCKER_COMPOSE_UP_FUNCTION__ = function_ai(name="docker_compose_up",
                                            description="Create and start containers from compose file.",
                                            parameters=parameters_func([__DOCKER_PROPERTY_23__, __DOCKER_PROPERTY_24__, __DOCKER_PROPERTY_8__]))

__DOCKER_COMPOSE_DOWN_FUNCTION__ = function_ai(name="docker_compose_down",
                                              description="Stop and remove containers, networks from compose file.",
                                              parameters=parameters_func([__DOCKER_PROPERTY_23__, __DOCKER_PROPERTY_9__]))

__DOCKER_COMPOSE_PS_FUNCTION__ = function_ai(name="docker_compose_ps",
                                            description="List containers from compose file.",
                                            parameters=parameters_func([__DOCKER_PROPERTY_23__]))

__DOCKER_COMPOSE_LOGS_FUNCTION__ = function_ai(name="docker_compose_logs",
                                              description="View output from containers from compose file.",
                                              parameters=parameters_func([__DOCKER_PROPERTY_23__, __DOCKER_PROPERTY_24__, __DOCKER_PROPERTY_16__]))

# Additional Functions Definitions
__DOCKER_STATS_FUNCTION__ = function_ai(name="docker_stats",
                                       description="Display a live stream of container(s) resource usage statistics.",
                                       parameters=parameters_func([__DOCKER_PROPERTY_TWO__, __DOCKER_PROPERTY_10__]))

__DOCKER_TOP_FUNCTION__ = function_ai(name="docker_top",
                                     description="Display the running processes of a container.",
                                     parameters=parameters_func([__DOCKER_PROPERTY_TWO__]))

__DOCKER_LOGIN_FUNCTION__ = function_ai(name="docker_login",
                                       description="Log in to a Docker registry.",
                                       parameters=parameters_func([__DOCKER_PROPERTY_20__, __DOCKER_PROPERTY_21__, __DOCKER_PROPERTY_22__]))

__DOCKER_LOGOUT_FUNCTION__ = function_ai(name="docker_logout",
                                        description="Log out from a Docker registry.",
                                        parameters=parameters_func([__DOCKER_PROPERTY_20__]))

__DOCKER_SYSTEM_PRUNE_FUNCTION__ = function_ai(name="docker_system_prune",
                                              description="Remove unused Docker data.",
                                              parameters=parameters_func([__DOCKER_PROPERTY_10__, __DOCKER_PROPERTY_15__, __DOCKER_PROPERTY_9__]))

__DOCKER_CONTAINER_PRUNE_FUNCTION__ = function_ai(name="docker_container_prune",
                                                 description="Remove all stopped containers.",
                                                 parameters=parameters_func([__DOCKER_PROPERTY_9__]))

__DOCKER_IMAGE_PRUNE_FUNCTION__ = function_ai(name="docker_image_prune",
                                             description="Remove unused images.",
                                             parameters=parameters_func([__DOCKER_PROPERTY_10__, __DOCKER_PROPERTY_9__]))

tools = [
    # Container Management
    __DOCKER_RUN_FUNCTION__,
    __DOCKER_PS_FUNCTION__,
    __DOCKER_START_FUNCTION__,
    __DOCKER_STOP_FUNCTION__,
    __DOCKER_RESTART_FUNCTION__,
    __DOCKER_RM_FUNCTION__,
    __DOCKER_LOGS_FUNCTION__,
    __DOCKER_EXEC_FUNCTION__,
    __DOCKER_INSPECT_FUNCTION__,
    
    # Image Management
    __DOCKER_IMAGES_FUNCTION__,
    __DOCKER_PULL_FUNCTION__,
    __DOCKER_BUILD_FUNCTION__,
    __DOCKER_PUSH_FUNCTION__,
    __DOCKER_RMI_FUNCTION__,
    
    # Network Management
    __DOCKER_NETWORK_LS_FUNCTION__,
    __DOCKER_NETWORK_CREATE_FUNCTION__,
    __DOCKER_NETWORK_RM_FUNCTION__,
    
    # Volume Management
    __DOCKER_VOLUME_LS_FUNCTION__,
    __DOCKER_VOLUME_CREATE_FUNCTION__,
    __DOCKER_VOLUME_RM_FUNCTION__,
    
    # System Functions
    __DOCKER_INFO_FUNCTION__,
    __DOCKER_VERSION_FUNCTION__,
    
    # Compose Functions
    __DOCKER_COMPOSE_UP_FUNCTION__,
    __DOCKER_COMPOSE_DOWN_FUNCTION__,
    __DOCKER_COMPOSE_PS_FUNCTION__,
    __DOCKER_COMPOSE_LOGS_FUNCTION__,
    
    # Additional Functions
    __DOCKER_STATS_FUNCTION__,
    __DOCKER_TOP_FUNCTION__,
    __DOCKER_LOGIN_FUNCTION__,
    __DOCKER_LOGOUT_FUNCTION__,
    __DOCKER_SYSTEM_PRUNE_FUNCTION__,
    __DOCKER_CONTAINER_PRUNE_FUNCTION__,
    __DOCKER_IMAGE_PRUNE_FUNCTION__,
]

def _run_docker_command(args, timeout=30, check_docker=True):
    """Internal helper function to run docker commands."""
    try:
        if check_docker:
            # Check if docker is available
            try:
                subprocess.run(['docker', '--version'], 
                              capture_output=True, check=True, timeout=5)
            except (subprocess.CalledProcessError, FileNotFoundError):
                return "Error: Docker is not installed or not in PATH"
        
        # Run docker command
        result = subprocess.run(
            ['docker'] + args,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        output = result.stdout.strip()
        error = result.stderr.strip()
        
        if result.returncode != 0:
            if "permission denied" in error.lower():
                return f"Error: Permission denied - you might need to run with sudo or add user to docker group: {error}"
            elif "connection refused" in error.lower():
                return f"Error: Docker daemon not running: {error}"
            else:
                return f"Docker command failed: {error}"
        
        return output if output else "Command executed successfully (no output)"
    
    except subprocess.TimeoutExpired:
        return f"Error: Docker command timed out after {timeout} seconds"
    except PermissionError as e:
        return f"Error: Permission error: {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error executing docker command: {str(e)}"

def _parse_mappings(mapping_str, mapping_type="port"):
    """Parse port or volume mapping strings."""
    if not mapping_str:
        return []
    
    mappings = []
    try:
        # Split by comma or newline
        if ',' in mapping_str:
            items = mapping_str.split(',')
        else:
            items = mapping_str.split('\n')
        
        for item in items:
            item = item.strip()
            if item:
                if mapping_type == "port":
                    # Validate port mapping format
                    if ':' in item:
                        host_port, container_port = item.split(':', 1)
                        # Basic validation
                        if host_port and container_port:
                            mappings.append(f"-p {item}")
                    else:
                        # Just container port
                        mappings.append(f"-p {item}:{item}")
                elif mapping_type == "volume":
                    # Volume mapping
                    if ':' in item:
                        mappings.append(f"-v {item}")
                    else:
                        # Just container path
                        mappings.append(f"-v {item}:{item}")
                elif mapping_type == "env":
                    # Environment variable
                    if '=' in item:
                        mappings.append(f"-e {item}")
                    else:
                        # Just key
                        mappings.append(f"-e {item}=")
    except Exception:
        # If parsing fails, return as is
        if mapping_type == "port":
            return [f"-p {mapping_str}"]
        elif mapping_type == "volume":
            return [f"-v {mapping_str}"]
        elif mapping_type == "env":
            return [f"-e {mapping_str}"]
    
    return mappings

# Container Management Functions
def docker_run(image: str, name: str = None, command: str = None, ports: str = None,
               volumes: str = None, environment: str = None, detach: bool = False,
               workdir: str = None) -> str:
    '''
    Run a docker container.
    
    :param image: Docker image name or ID
    :type image: str
    :param name: Container name
    :type name: str
    :param command: Command to run in container
    :type command: str
    :param ports: Port mappings (host:container)
    :type ports: str
    :param volumes: Volume mappings (host:container)
    :type volumes: str
    :param environment: Environment variables (KEY=VALUE)
    :type environment: str
    :param detach: Run container in detached mode
    :type detach: bool
    :param workdir: Working directory inside container
    :type workdir: str
    :return: Container run output
    :rtype: str
    '''
    try:
        args = ["run"]
        
        if detach:
            args.append("-d")
        
        if name:
            args.extend(["--name", name])
        
        # Add port mappings
        if ports:
            port_mappings = _parse_mappings(ports, "port")
            for mapping in port_mappings:
                args.extend(mapping.split())
        
        # Add volume mappings
        if volumes:
            volume_mappings = _parse_mappings(volumes, "volume")
            for mapping in volume_mappings:
                args.extend(mapping.split())
        
        # Add environment variables
        if environment:
            env_mappings = _parse_mappings(environment, "env")
            for mapping in env_mappings:
                args.extend(mapping.split())
        
        if workdir:
            args.extend(["-w", workdir])
        
        args.append(image)
        
        if command:
            args.extend(command.split())
        
        return _run_docker_command(args, timeout=60)
        
    except Exception as e:
        return f"Error running container: {str(e)}"

def docker_ps(all: bool = False, filter: str = None) -> str:
    '''
    List docker containers.
    
    :param all: Show all containers (default shows just running)
    :type all: bool
    :param filter: Filter output (e.g., 'status=running')
    :type filter: str
    :return: Container list output
    :rtype: str
    '''
    args = ["ps"]
    
    if all:
        args.append("-a")
    
    if filter:
        args.extend(["--filter", filter])
    
    args.extend(["--format", "table {{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"])
    
    return _run_docker_command(args)

def docker_start(container: str = None, all: bool = False) -> str:
    '''
    Start one or more stopped containers.
    
    :param container: Container name or ID
    :type container: str
    :param all: Start all stopped containers
    :type all: bool
    :return: Start operation output
    :rtype: str
    '''
    if all:
        # Get all stopped containers
        args = ["ps", "-a", "--filter", "status=exited", "--format", "{{.ID}}"]
        result = _run_docker_command(args, check_docker=False)
        
        if result.startswith("Error:"):
            return result
        
        containers = result.split()
        if not containers:
            return "No stopped containers found"
        
        args = ["start"] + containers
        return _run_docker_command(args)
    
    elif container:
        return _run_docker_command(["start", container])
    
    else:
        return "Error: Either container name or 'all=True' must be specified"

def docker_stop(container: str = None, all: bool = False, force: bool = False, 
                timeout: int = 10) -> str:
    '''
    Stop one or more running containers.
    
    :param container: Container name or ID
    :type container: str
    :param all: Stop all running containers
    :type all: bool
    :param force: Force stop (kill)
    :type force: bool
    :param timeout: Stop timeout in seconds
    :type timeout: int
    :return: Stop operation output
    :rtype: str
    '''
    args = ["stop"]
    
    if force:
        args = ["kill"]  # Use kill instead of stop for force
    
    if all:
        # Get all running containers
        list_args = ["ps", "--filter", "status=running", "--format", "{{.ID}}"]
        result = _run_docker_command(list_args, check_docker=False)
        
        if result.startswith("Error:"):
            return result
        
        containers = result.split()
        if not containers:
            return "No running containers found"
        
        args.extend(containers)
        if "kill" not in args and timeout:
            args.extend(["-t", str(timeout)])
        
        return _run_docker_command(args)
    
    elif container:
        if not force and timeout:
            args.extend(["-t", str(timeout)])
        args.append(container)
        return _run_docker_command(args)
    
    else:
        return "Error: Either container name or 'all=True' must be specified"

def docker_restart(container: str = None, all: bool = False, force: bool = False) -> str:
    '''
    Restart one or more containers.
    
    :param container: Container name or ID
    :type container: str
    :param all: Restart all containers
    :type all: bool
    :param force: Force restart
    :type force: bool
    :return: Restart operation output
    :rtype: str
    '''
    if all:
        # Get all containers
        list_args = ["ps", "-a", "--format", "{{.ID}}"]
        result = _run_docker_command(list_args, check_docker=False)
        
        if result.startswith("Error:"):
            return result
        
        containers = result.split()
        if not containers:
            return "No containers found"
        
        args = ["restart"]
        if force:
            args.append("--force")
        args.extend(containers)
        return _run_docker_command(args)
    
    elif container:
        args = ["restart"]
        if force:
            args.append("--force")
        args.append(container)
        return _run_docker_command(args)
    
    else:
        return "Error: Either container name or 'all=True' must be specified"

def docker_rm(container: str = None, all: bool = False, force: bool = False) -> str:
    '''
    Remove one or more containers.
    
    :param container: Container name or ID
    :type container: str
    :param all: Remove all containers
    :type all: bool
    :param force: Force removal
    :type force: bool
    :return: Remove operation output
    :rtype: str
    '''
    if all:
        # Get all containers
        list_args = ["ps", "-a", "--format", "{{.ID}}"]
        result = _run_docker_command(list_args, check_docker=False)
        
        if result.startswith("Error:"):
            return result
        
        containers = result.split()
        if not containers:
            return "No containers found"
        
        args = ["rm"]
        if force:
            args.append("-f")
        args.extend(containers)
        return _run_docker_command(args)
    
    elif container:
        args = ["rm"]
        if force:
            args.append("-f")
        args.append(container)
        return _run_docker_command(args)
    
    else:
        return "Error: Either container name or 'all=True' must be specified"

def docker_logs(container: str, follow: bool = False, timeout: int = 30) -> str:
    '''
    Fetch the logs of a container.
    
    :param container: Container name or ID
    :type container: str
    :param follow: Follow log output
    :type follow: bool
    :param timeout: Timeout in seconds
    :type timeout: int
    :return: Container logs
    :rtype: str
    '''
    args = ["logs"]
    
    if follow:
        args.append("--follow")
        # For follow mode, use shorter timeout or no timeout
        if timeout > 0:
            args.extend(["--tail", "50"])
    
    args.append(container)
    
    # For follow mode, we might want a different approach
    if follow:
        try:
            process = subprocess.Popen(
                ['docker'] + args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Read for specified timeout
            start_time = time.time()
            output_lines = []
            
            while time.time() - start_time < timeout:
                line = process.stdout.readline()
                if line:
                    output_lines.append(line.strip())
                else:
                    time.sleep(0.1)
                
                if len(output_lines) > 1000:  # Limit output
                    output_lines.append("... (output truncated)")
                    break
            
            process.terminate()
            return "\n".join(output_lines)
        except Exception as e:
            return f"Error reading logs: {str(e)}"
    else:
        return _run_docker_command(args, timeout=timeout)

def docker_exec(container: str, command: str, detach: bool = False, workdir: str = None) -> str:
    '''
    Run a command in a running container.
    
    :param container: Container name or ID
    :type container: str
    :param command: Command to execute
    :type command: str
    :param detach: Detach from the command (run in background)
    :type detach: bool
    :param workdir: Working directory inside container
    :type workdir: str
    :return: Command output
    :rtype: str
    '''
    args = ["exec"]
    
    if detach:
        args.append("-d")
    
    if workdir:
        args.extend(["-w", workdir])
    
    args.append(container)
    args.extend(command.split())
    
    return _run_docker_command(args)

def docker_inspect(container: str) -> str:
    '''
    Return low-level information on Docker objects.
    
    :param container: Container name or ID
    :type container: str
    :return: Inspection output
    :rtype: str
    '''
    args = ["inspect", container]
    result = _run_docker_command(args)
    
    if not result.startswith("Error:"):
        try:
            # Try to format JSON output
            data = json.loads(result)
            return json.dumps(data, indent=2, ensure_ascii=False)
        except:
            pass
    
    return result

# Image Management Functions
def docker_images() -> str:
    '''
    List docker images.
    
    :return: Images list output
    :rtype: str
    '''
    args = ["images", "--format", "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.CreatedAt}}\t{{.Size}}"]
    return _run_docker_command(args)

def docker_pull(image: str, registry: str = None, username: str = None, 
                password: str = None) -> str:
    '''
    Pull an image from a registry.
    
    :param image: Image name to pull
    :type image: str
    :param registry: Docker registry URL
    :type registry: str
    :param username: Username for registry authentication
    :type username: str
    :param password: Password for registry authentication
    :type password: str
    :return: Pull operation output
    :rtype: str
    '''
    # Construct full image name
    full_image = image
    if registry:
        # Remove any existing registry from image name
        if '/' in image and not image.startswith(registry):
            # Image might already have a registry
            parts = image.split('/')
            if len(parts) > 1 and '.' in parts[0] or ':' in parts[0]:
                # First part looks like a registry
                image = '/'.join(parts[1:])
        
        # Add registry prefix
        full_image = f"{registry}/{image}" if image else registry
    
    args = ["pull", full_image]
    
    # Note: For authentication, Docker usually uses docker login command
    # or credentials from config. We could implement docker_login function.
    
    return _run_docker_command(args, timeout=300)  # Longer timeout for pull

def docker_build(dockerfile: str = "Dockerfile", tag: str = None, 
                 context: str = ".", image: str = None) -> str:
    '''
    Build an image from a Dockerfile.
    
    :param dockerfile: Path to Dockerfile
    :type dockerfile: str
    :param tag: Tag for the built image
    :type tag: str
    :param context: Build context path
    :type context: str
    :param image: Image name (alternative to tag)
    :type image: str
    :return: Build output
    :rtype: str
    '''
    args = ["build"]
    
    if dockerfile:
        args.extend(["-f", dockerfile])
    
    # Use tag or image parameter
    final_tag = tag or image
    if final_tag:
        args.extend(["-t", final_tag])
    
    args.append(context)
    
    return _run_docker_command(args, timeout=600)  # Long timeout for build

def docker_push(image: str, registry: str = None, username: str = None, 
                password: str = None) -> str:
    '''
    Push an image to a registry.
    
    :param image: Image name to push
    :type image: str
    :param registry: Docker registry URL
    :type registry: str
    :param username: Username for registry authentication
    :type username: str
    :param password: Password for registry authentication
    :type password: str
    :return: Push operation output
    :rtype: str
    '''
    # Construct full image name
    full_image = image
    if registry:
        # Remove any existing registry from image name
        if '/' in image and not image.startswith(registry):
            parts = image.split('/')
            if len(parts) > 1 and ('.' in parts[0] or ':' in parts[0]):
                image = '/'.join(parts[1:])
        
        # Add registry prefix
        full_image = f"{registry}/{image}" if image else registry
    
    args = ["push", full_image]
    
    # Note: Authentication handled by docker login
    
    return _run_docker_command(args, timeout=300)  # Longer timeout for push

def docker_rmi(image: str = None, force: bool = False, all: bool = False) -> str:
    '''
    Remove one or more images.
    
    :param image: Image name or ID
    :type image: str
    :param force: Force removal
    :type force: bool
    :param all: Remove all unused images
    :type all: bool
    :return: Remove operation output
    :rtype: str
    '''
    if all:
        # Remove all unused images
        return _run_docker_command(["image", "prune", "-a", "-f" if force else ""])
    
    elif image:
        args = ["rmi"]
        if force:
            args.append("-f")
        args.append(image)
        return _run_docker_command(args)
    
    else:
        return "Error: Either image name or 'all=True' must be specified"

# Network Management Functions
def docker_network_ls() -> str:
    '''
    List docker networks.
    
    :return: Network list output
    :rtype: str
    '''
    args = ["network", "ls", "--format", "table {{.ID}}\t{{.Name}}\t{{.Driver}}\t{{.Scope}}"]
    return _run_docker_command(args)

def docker_network_create(name: str = None, network: str = None) -> str:
    '''
    Create a docker network.
    
    :param name: Network name
    :type name: str
    :param network: Network driver or options (deprecated, use name)
    :type network: str
    :return: Network creation output
    :rtype: str
    '''
    # Use name parameter primarily
    network_name = name or network
    if not network_name:
        return "Error: Network name is required"
    
    return _run_docker_command(["network", "create", network_name])

def docker_network_rm(network: str, force: bool = False) -> str:
    '''
    Remove one or more docker networks.
    
    :param network: Network name or ID
    :type network: str
    :param force: Force removal
    :type force: bool
    :return: Network removal output
    :rtype: str
    '''
    args = ["network", "rm"]
    if force:
        args.append("--force")
    args.append(network)
    return _run_docker_command(args)

# Volume Management Functions
def docker_volume_ls() -> str:
    '''
    List docker volumes.
    
    :return: Volume list output
    :rtype: str
    '''
    args = ["volume", "ls", "--format", "table {{.Name}}\t{{.Driver}}\t{{.Scope}}"]
    return _run_docker_command(args)

def docker_volume_create(name: str = None, volume: str = None) -> str:
    '''
    Create a docker volume.
    
    :param name: Volume name
    :type name: str
    :param volume: Volume driver or options (deprecated, use name)
    :type volume: str
    :return: Volume creation output
    :rtype: str
    '''
    # Use name parameter primarily
    volume_name = name or volume
    if not volume_name:
        return "Error: Volume name is required"
    
    return _run_docker_command(["volume", "create", volume_name])

def docker_volume_rm(volume: str, force: bool = False) -> str:
    '''
    Remove one or more docker volumes.
    
    :param volume: Volume name or ID
    :type volume: str
    :param force: Force removal
    :type force: bool
    :return: Volume removal output
    :rtype: str
    '''
    args = ["volume", "rm"]
    if force:
        args.append("-f")
    args.append(volume)
    return _run_docker_command(args)

# System Functions
def docker_info() -> str:
    '''
    Display system-wide information.
    
    :return: Docker system information
    :rtype: str
    '''
    return _run_docker_command(["info"])

def docker_version() -> str:
    '''
    Show the Docker version information.
    
    :return: Docker version information
    :rtype: str
    '''
    return _run_docker_command(["version"])

# Compose Functions
def docker_compose_up(compose_file: str = "docker-compose.yml", services: str = None, 
                      detach: bool = False) -> str:
    '''
    Create and start containers from compose file.
    
    :param compose_file: Docker Compose file path
    :type compose_file: str
    :param services: Specific services to start (comma-separated)
    :type services: str
    :param detach: Run in detached mode
    :type detach: bool
    :return: Compose up output
    :rtype: str
    '''
    # Check if docker-compose is available
    try:
        subprocess.run(['docker-compose', '--version'], 
                      capture_output=True, check=True, timeout=5)
        compose_cmd = 'docker-compose'
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Try docker compose (v2)
        try:
            subprocess.run(['docker', 'compose', '--version'],
                          capture_output=True, check=True, timeout=5)
            compose_cmd = 'docker compose'
        except:
            return "Error: Neither docker-compose nor docker compose is available"
    
    args = compose_cmd.split()
    args.extend(["-f", compose_file, "up"])
    
    if detach:
        args.append("-d")
    
    if services:
        services_list = services.split(',')
        args.extend(services_list)
    
    # Run the command
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        output = result.stdout.strip()
        error = result.stderr.strip()
        
        if result.returncode != 0:
            return f"Compose command failed: {error}"
        
        return output if output else "Compose services started successfully"
        
    except subprocess.TimeoutExpired:
        return "Error: Compose command timed out after 300 seconds"
    except Exception as e:
        return f"Error executing compose command: {str(e)}"

def docker_compose_down(compose_file: str = "docker-compose.yml", force: bool = False) -> str:
    '''
    Stop and remove containers, networks from compose file.
    
    :param compose_file: Docker Compose file path
    :type compose_file: str
    :param force: Force removal (remove volumes too)
    :type force: bool
    :return: Compose down output
    :rtype: str
    '''
    # Check compose availability (simplified version)
    try:
        subprocess.run(['docker-compose', '--version'], capture_output=True, timeout=5)
        compose_cmd = 'docker-compose'
    except:
        try:
            subprocess.run(['docker', 'compose', '--version'], capture_output=True, timeout=5)
            compose_cmd = 'docker compose'
        except:
            return "Error: Neither docker-compose nor docker compose is available"
    
    args = compose_cmd.split()
    args.extend(["-f", compose_file, "down"])
    
    if force:
        args.extend(["-v", "--remove-orphans"])
    
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        output = result.stdout.strip()
        error = result.stderr.strip()
        
        if result.returncode != 0:
            return f"Compose down failed: {error}"
        
        return output if output else "Compose services stopped and removed"
        
    except subprocess.TimeoutExpired:
        return "Error: Compose down command timed out"
    except Exception as e:
        return f"Error executing compose down: {str(e)}"

def docker_compose_ps(compose_file: str = "docker-compose.yml") -> str:
    '''
    List containers from compose file.
    
    :param compose_file: Docker Compose file path
    :type compose_file: str
    :return: Compose ps output
    :rtype: str
    '''
    # Check compose availability
    try:
        subprocess.run(['docker-compose', '--version'], capture_output=True, timeout=5)
        compose_cmd = 'docker-compose'
    except:
        try:
            subprocess.run(['docker', 'compose', '--version'], capture_output=True, timeout=5)
            compose_cmd = 'docker compose'
        except:
            return "Error: Neither docker-compose nor docker compose is available"
    
    args = compose_cmd.split()
    args.extend(["-f", compose_file, "ps"])
    
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout.strip()
        error = result.stderr.strip()
        
        if result.returncode != 0:
            return f"Compose ps failed: {error}"
        
        return output if output else "No compose services running"
        
    except subprocess.TimeoutExpired:
        return "Error: Compose ps command timed out"
    except Exception as e:
        return f"Error executing compose ps: {str(e)}"

def docker_compose_logs(compose_file: str = "docker-compose.yml", services: str = None, 
                        follow: bool = False) -> str:
    '''
    View output from containers from compose file.
    
    :param compose_file: Docker Compose file path
    :type compose_file: str
    :param services: Specific services to show logs for (comma-separated)
    :type services: str
    :param follow: Follow log output
    :type follow: bool
    :return: Compose logs output
    :rtype: str
    '''
    # Check compose availability
    try:
        subprocess.run(['docker-compose', '--version'], capture_output=True, timeout=5)
        compose_cmd = 'docker-compose'
    except:
        try:
            subprocess.run(['docker', 'compose', '--version'], capture_output=True, timeout=5)
            compose_cmd = 'docker compose'
        except:
            return "Error: Neither docker-compose nor docker compose is available"
    
    args = compose_cmd.split()
    args.extend(["-f", compose_file, "logs"])
    
    if follow:
        args.append("--follow")
        # Limit initial output
        args.extend(["--tail", "50"])
    
    if services:
        services_list = services.split(',')
        args.extend(services_list)
    
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=30 if not follow else 10
        )
        
        output = result.stdout.strip()
        error = result.stderr.strip()
        
        if result.returncode != 0:
            return f"Compose logs failed: {error}"
        
        return output if output else "No logs available"
        
    except subprocess.TimeoutExpired:
        return "Error: Compose logs command timed out"
    except Exception as e:
        return f"Error executing compose logs: {str(e)}"



# Additional Functions

def docker_stats(container: str = None, all: bool = False) -> str:
    '''
    Display a live stream of container(s) resource usage statistics.
    
    :param container: Container name or ID
    :type container: str
    :param all: Show all containers (default shows just running)
    :type all: bool
    :return: Stats output
    :rtype: str
    '''
    args = ["stats", "--no-stream"]  # Get one snapshot instead of streaming
    
    if all:
        args.append("--all")
    
    if container:
        args.append(container)
    
    return _run_docker_command(args)

def docker_top(container: str) -> str:
    '''
    Display the running processes of a container.
    
    :param container: Container name or ID
    :type container: str
    :return: Top output
    :rtype: str
    '''
    return _run_docker_command(["top", container])

def docker_login(registry: str = None, username: str = None, password: str = None) -> str:
    '''
    Log in to a Docker registry.
    
    :param registry: Docker registry URL
    :type registry: str
    :param username: Username for registry authentication
    :type username: str
    :param password: Password for registry authentication
    :type password: str
    :return: Login output
    :rtype: str
    '''
    # Note: This function has security implications
    # In production, consider using Docker's credential store instead
    
    args = ["login"]
    
    if registry:
        args.append(registry)
    
    # For username/password, we could use --username flag
    # But passing password via command line is insecure
    # Better approach: let docker prompt for password
    
    if username:
        args.extend(["--username", username])
        # Don't include password in command line for security
        # Docker will prompt for password
    
    return _run_docker_command(args)

def docker_logout(registry: str = None) -> str:
    '''
    Log out from a Docker registry.
    
    :param registry: Docker registry URL
    :type registry: str
    :return: Logout output
    :rtype: str
    '''
    args = ["logout"]
    
    if registry:
        args.append(registry)
    
    return _run_docker_command(args)

def docker_system_prune(all: bool = False, volumes: bool = False, force: bool = False) -> str:
    '''
    Remove unused Docker data.
    
    :param all: Remove all unused images not just dangling ones
    :type all: bool
    :param volumes: Prune volumes
    :type volumes: bool
    :param force: Do not prompt for confirmation
    :type force: bool
    :return: Prune output
    :rtype: str
    '''
    args = ["system", "prune"]
    
    if force:
        args.append("-f")
    
    if all:
        args.append("-a")
    
    if volumes:
        args.append("--volumes")
    
    return _run_docker_command(args)

def docker_container_prune(force: bool = False) -> str:
    '''
    Remove all stopped containers.
    
    :param force: Do not prompt for confirmation
    :type force: bool
    :return: Prune output
    :rtype: str
    '''
    args = ["container", "prune"]
    
    if force:
        args.append("-f")
    
    return _run_docker_command(args)

def docker_image_prune(all: bool = False, force: bool = False) -> str:
    '''
    Remove unused images.
    
    :param all: Remove all unused images not just dangling ones
    :type all: bool
    :param force: Do not prompt for confirmation
    :type force: bool
    :return: Prune output
    :rtype: str
    '''
    args = ["image", "prune"]
    
    if force:
        args.append("-f")
    
    if all:
        args.append("-a")
    
    return _run_docker_command(args)

TOOL_CALL_MAP = {
    # Container Management
    "docker_run": docker_run,
    "docker_ps": docker_ps,
    "docker_start": docker_start,
    "docker_stop": docker_stop,
    "docker_restart": docker_restart,
    "docker_rm": docker_rm,
    "docker_logs": docker_logs,
    "docker_exec": docker_exec,
    "docker_inspect": docker_inspect,
    
    # Image Management
    "docker_images": docker_images,
    "docker_pull": docker_pull,
    "docker_build": docker_build,
    "docker_push": docker_push,
    "docker_rmi": docker_rmi,
    
    # Network Management
    "docker_network_ls": docker_network_ls,
    "docker_network_create": docker_network_create,
    "docker_network_rm": docker_network_rm,
    
    # Volume Management
    "docker_volume_ls": docker_volume_ls,
    "docker_volume_create": docker_volume_create,
    "docker_volume_rm": docker_volume_rm,
    
    # System Functions
    "docker_info": docker_info,
    "docker_version": docker_version,
    
    # Compose Functions
    "docker_compose_up": docker_compose_up,
    "docker_compose_down": docker_compose_down,
    "docker_compose_ps": docker_compose_ps,
    "docker_compose_logs": docker_compose_logs,
    
    # Additional Functions
    "docker_stats": docker_stats,
    "docker_top": docker_top,
    "docker_login": docker_login,
    "docker_logout": docker_logout,
    "docker_system_prune": docker_system_prune,
    "docker_container_prune": docker_container_prune,
    "docker_image_prune": docker_image_prune,
}
