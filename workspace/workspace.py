from base import function_ai, parameters_func, property_param

import os
import sys
import subprocess
import venv
import json
import shutil
from pathlib import Path

__WORKSPACE_PROPERTY_ONE__ = property_param(
    name="workspace_path",
    description="The path for the workspace or virtual environment.",
    t="string",
    required=True
)

__WORKSPACE_PROPERTY_TWO__ = property_param(
    name="venv_name",
    description="The name of the virtual environment.",
    t="string"
)

__WORKSPACE_PROPERTY_THREE__ = property_param(
    name="python_version",
    description="Python version for the virtual environment.",
    t="string"
)

__WORKSPACE_PROPERTY_4__ = property_param(
    name="requirements",
    description="Path to requirements.txt file or list of packages.",
    t="string"
)

__WORKSPACE_PROPERTY_5__ = property_param(
    name="force",
    description="Force the operation (overwrite existing files/directories).",
    t="boolean"
)

__WORKSPACE_PROPERTY_6__ = property_param(
    name="system_site_packages",
    description="Allow access to system site packages in virtual environment.",
    t="boolean"
)

__WORKSPACE_PROPERTY_7__ = property_param(
    name="packages",
    description="List of packages to install in virtual environment.",
    t="array"
)

__WORKSPACE_PROPERTY_8__ = property_param(
    name="venv_type",
    description="Type of virtual environment (venv, conda, virtualenv).",
    t="string"
)

__WORKSPACE_PROPERTY_9__ = property_param(
    name="parent_dir",
    description="Parent directory for workspace creation.",
    t="string"
)

__WORKSPACE_PROPERTY_10__ = property_param(
    name="template",
    description="Template structure for workspace.",
    t="string"
)

__WORKSPACE_PROPERTY_11__ = property_param(
    name="description",
    description="Description for the workspace.",
    t="string"
)

# 添加虚拟环境路径属性
__VENV_PATH_PROPERTY__ = property_param(
    name="venv_path",
    description="The path for the virtual environment.",
    t="string",
    required=True
)

__WORKSPACE_CREATE_FUNCTION__ = function_ai(name="create_workspace",
                                           description="Create a new workspace directory with optional template structure.",
                                           parameters=parameters_func([__WORKSPACE_PROPERTY_ONE__, __WORKSPACE_PROPERTY_9__, __WORKSPACE_PROPERTY_10__, __WORKSPACE_PROPERTY_11__, __WORKSPACE_PROPERTY_5__]))

__WORKSPACE_DELETE_FUNCTION__ = function_ai(name="delete_workspace",
                                           description="Delete a workspace directory and all its contents.",
                                           parameters=parameters_func([__WORKSPACE_PROPERTY_ONE__, __WORKSPACE_PROPERTY_5__]))

__WORKSPACE_LIST_FUNCTION__ = function_ai(name="list_workspaces",
                                         description="List all workspaces in a directory.",
                                         parameters=parameters_func([__WORKSPACE_PROPERTY_9__]))

__WORKSPACE_INFO_FUNCTION__ = function_ai(name="get_workspace_info",
                                         description="Get information about a workspace.",
                                         parameters=parameters_func([__WORKSPACE_PROPERTY_ONE__]))

__VENV_CREATE_FUNCTION__ = function_ai(name="create_virtualenv",
                                       description="Create a new Python virtual environment.",
                                       parameters=parameters_func([__VENV_PATH_PROPERTY__, __WORKSPACE_PROPERTY_THREE__, __WORKSPACE_PROPERTY_6__, __WORKSPACE_PROPERTY_8__, __WORKSPACE_PROPERTY_5__]))

__VENV_DELETE_FUNCTION__ = function_ai(name="delete_virtualenv",
                                       description="Delete a virtual environment.",
                                       parameters=parameters_func([__VENV_PATH_PROPERTY__, __WORKSPACE_PROPERTY_5__]))

__VENV_LIST_FUNCTION__ = function_ai(name="list_virtualenvs",
                                     description="List all virtual environments in a directory.",
                                     parameters=parameters_func([__WORKSPACE_PROPERTY_9__]))

__VENV_ACTIVATE_FUNCTION__ = function_ai(name="activate_virtualenv",
                                         description="Get activation commands for a virtual environment.",
                                         parameters=parameters_func([__VENV_PATH_PROPERTY__]))

__VENV_INSTALL_FUNCTION__ = function_ai(name="install_packages",
                                        description="Install packages in a virtual environment.",
                                        parameters=parameters_func([__VENV_PATH_PROPERTY__, __WORKSPACE_PROPERTY_4__, __WORKSPACE_PROPERTY_7__, __WORKSPACE_PROPERTY_5__]))

__VENV_DEACTIVATE_FUNCTION__ = function_ai(name="deactivate_virtualenv",
                                          description="Deactivate a virtual environment.",
                                          parameters=parameters_func([__VENV_PATH_PROPERTY__]))

__VENV_CHECK_FUNCTION__ = function_ai(name="check_virtualenv",
                                      description="Check if a virtual environment exists and is valid.",
                                      parameters=parameters_func([__VENV_PATH_PROPERTY__]))

__VENV_UPGRADE_FUNCTION__ = function_ai(name="upgrade_pip",
                                        description="Upgrade pip in a virtual environment.",
                                        parameters=parameters_func([__VENV_PATH_PROPERTY__]))

__VENV_EXPORT_FUNCTION__ = function_ai(name="export_requirements",
                                       description="Export installed packages to requirements.txt.",
                                       parameters=parameters_func([__VENV_PATH_PROPERTY__]))

tools = [
    __WORKSPACE_CREATE_FUNCTION__,
    __WORKSPACE_DELETE_FUNCTION__,
    __WORKSPACE_LIST_FUNCTION__,
    __WORKSPACE_INFO_FUNCTION__,
    __VENV_CREATE_FUNCTION__,
    __VENV_DELETE_FUNCTION__,
    __VENV_LIST_FUNCTION__,
    __VENV_ACTIVATE_FUNCTION__,
    __VENV_INSTALL_FUNCTION__,
    __VENV_DEACTIVATE_FUNCTION__,
    __VENV_CHECK_FUNCTION__,
    __VENV_UPGRADE_FUNCTION__,
    __VENV_EXPORT_FUNCTION__
]

def create_workspace(workspace_path: str, parent_dir: str = None, template: str = "basic", 
                     description: str = "", force: bool = False) -> str:
    '''
    Create a new workspace directory with optional template structure.
    
    :param workspace_path: Full path or name of workspace
    :type workspace_path: str
    :param parent_dir: Parent directory for workspace
    :type parent_dir: str
    :param template: Template type (basic, python, data_science, web, empty)
    :type template: str
    :param description: Description of workspace
    :type description: str
    :param force: Overwrite existing workspace
    :type force: bool
    :return: Creation status message
    :rtype: str
    '''
    try:
        # Determine full path
        if parent_dir and not os.path.isabs(workspace_path):
            full_path = os.path.join(parent_dir, workspace_path)
        else:
            full_path = workspace_path
        
        # Check if workspace already exists
        if os.path.exists(full_path):
            if not force:
                return f"Error: Workspace already exists: {full_path}. Use force=True to overwrite."
            else:
                # Remove existing workspace
                shutil.rmtree(full_path)
                print(f"Removed existing workspace: {full_path}")
        
        # Create workspace directory
        os.makedirs(full_path, exist_ok=True)
        
        # Create workspace info file
        info = {
            "name": os.path.basename(full_path),
            "path": full_path,
            "created": str(Path(full_path).stat().st_ctime),
            "template": template,
            "description": description
        }
        
        with open(os.path.join(full_path, ".workspace.json"), "w") as f:
            json.dump(info, f, indent=2)
        
        # Create template structure
        templates = {
            "basic": [
                "src/",
                "tests/",
                "docs/",
                "data/",
                "notebooks/",
                "config/",
                "logs/",
                "README.md",
                ".gitignore"
            ],
            "python": [
                "src/__init__.py",
                "src/main.py",
                "tests/__init__.py",
                "tests/test_main.py",
                "requirements.txt",
                "setup.py",
                "README.md",
                ".gitignore",
                ".env.example"
            ],
            "data_science": [
                "data/raw/",
                "data/processed/",
                "notebooks/exploratory/",
                "notebooks/reports/",
                "src/data/",
                "src/models/",
                "src/features/",
                "src/visualization/",
                "requirements.txt",
                "README.md",
                ".gitignore"
            ],
            "web": [
                "templates/",
                "static/css/",
                "static/js/",
                "static/images/",
                "src/routes/",
                "src/models/",
                "src/templates/",
                "config/",
                "requirements.txt",
                "README.md",
                ".gitignore",
                "dockerfile"
            ],
            "empty": []
        }
        
        # Create directories and files based on template
        if template in templates:
            for item in templates[template]:
                item_path = os.path.join(full_path, item)
                if item.endswith("/"):
                    os.makedirs(item_path, exist_ok=True)
                else:
                    # Create empty file
                    os.makedirs(os.path.dirname(item_path), exist_ok=True)
                    with open(item_path, "w") as f:
                        if item == "README.md":
                            f.write(f"# {os.path.basename(full_path)}\n\n{description}\n")
                        elif item == ".gitignore":
                            f.write("__pycache__/\n*.py[cod]\n*$py.class\n*.so\n.Python\n")
        
        return f"Successfully created workspace at: {full_path} (template: {template})"
    
    except PermissionError as e:
        return f"Error: Permission denied when creating workspace: {str(e)}"
    except OSError as e:
        return f"Error: OS error when creating workspace: {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error when creating workspace: {str(e)}"

def delete_workspace(workspace_path: str, force: bool = False) -> str:
    '''
    Delete a workspace directory and all its contents.
    
    :param workspace_path: Path to workspace directory
    :type workspace_path: str
    :param force: Force deletion without confirmation
    :type force: bool
    :return: Deletion status message
    :rtype: str
    '''
    try:
        if not os.path.exists(workspace_path):
            return f"Error: Workspace does not exist: {workspace_path}"
        
        if not os.path.isdir(workspace_path):
            return f"Error: Path is not a directory: {workspace_path}"
        
        # Check if it's a workspace by looking for workspace info file
        workspace_info = os.path.join(workspace_path, ".workspace.json")
        if not os.path.exists(workspace_info):
            if not force:
                return f"Error: Not a valid workspace (missing .workspace.json). Use force=True to delete anyway."
        
        # Get workspace info for confirmation
        info = {}
        if os.path.exists(workspace_info):
            with open(workspace_info, "r") as f:
                info = json.load(f)
        
        # Calculate directory size (approximate)
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(workspace_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                try:
                    total_size += os.path.getsize(fp)
                except OSError:
                    pass
        
        size_mb = total_size / (1024 * 1024)
        
        # Delete workspace
        shutil.rmtree(workspace_path)
        
        return f"Successfully deleted workspace: {workspace_path}\n" \
               f"Name: {info.get('name', 'N/A')}\n" \
               f"Size: {size_mb:.2f} MB\n" \
               f"Description: {info.get('description', 'N/A')}"
    
    except PermissionError as e:
        return f"Error: Permission denied when deleting workspace: {str(e)}"
    except OSError as e:
        return f"Error: OS error when deleting workspace: {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error when deleting workspace: {str(e)}"

def list_workspaces(parent_dir: str = None) -> str:
    '''
    List all workspaces in a directory.
    
    :param parent_dir: Parent directory to search for workspaces
    :type parent_dir: str
    :return: List of workspaces with information
    :rtype: str
    '''
    try:
        if parent_dir is None:
            parent_dir = os.path.expanduser("~/workspaces")
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)
        
        if not os.path.exists(parent_dir):
            return f"Error: Parent directory does not exist: {parent_dir}"
        
        workspaces = []
        
        # Search for workspaces (directories with .workspace.json)
        for item in os.listdir(parent_dir):
            item_path = os.path.join(parent_dir, item)
            if os.path.isdir(item_path):
                workspace_info = os.path.join(item_path, ".workspace.json")
                if os.path.exists(workspace_info):
                    try:
                        with open(workspace_info, "r") as f:
                            info = json.load(f)
                            workspaces.append(info)
                    except:
                        # Invalid JSON, skip
                        pass
        
        if not workspaces:
            return f"No workspaces found in {parent_dir}"
        
        # Format output
        result = [f"Workspaces in {parent_dir}:"]
        result.append("-" * 80)
        result.append(f"{'Name':<20} {'Path':<30} {'Template':<15} {'Created':<20}")
        result.append("-" * 80)
        
        for ws in workspaces:
            name = ws.get('name', 'Unknown')[:18]
            path = ws.get('path', '')[:28]
            template = ws.get('template', 'basic')[:13]
            created = ws.get('created', 'Unknown')
            
            # Convert timestamp to readable date if possible
            try:
                import time
                created_time = time.ctime(float(created))
                created = created_time[:19]
            except:
                pass
            
            result.append(f"{name:<20} {path:<30} {template:<15} {created:<20}")
        
        result.append(f"\nTotal: {len(workspaces)} workspace(s)")
        
        return "\n".join(result)
    
    except Exception as e:
        return f"Error: Unexpected error when listing workspaces: {str(e)}"

def get_workspace_info(workspace_path: str) -> str:
    '''
    Get detailed information about a workspace.
    
    :param workspace_path: Path to workspace directory
    :type workspace_path: str
    :return: Workspace information
    :rtype: str
    '''
    try:
        if not os.path.exists(workspace_path):
            return f"Error: Workspace does not exist: {workspace_path}"
        
        workspace_info_file = os.path.join(workspace_path, ".workspace.json")
        
        info = {}
        if os.path.exists(workspace_info_file):
            with open(workspace_info_file, "r") as f:
                info = json.load(f)
        
        # Get directory statistics
        total_files = 0
        total_dirs = 0
        total_size = 0
        
        for dirpath, dirnames, filenames in os.walk(workspace_path):
            total_dirs += len(dirnames)
            total_files += len(filenames)
            for f in filenames:
                fp = os.path.join(dirpath, f)
                try:
                    total_size += os.path.getsize(fp)
                except OSError:
                    pass
        
        size_mb = total_size / (1024 * 1024)
        
        # Format output
        result = [f"Workspace Information:"]
        result.append("=" * 60)
        result.append(f"Name: {info.get('name', os.path.basename(workspace_path))}")
        result.append(f"Path: {workspace_path}")
        result.append(f"Template: {info.get('template', 'N/A')}")
        result.append(f"Description: {info.get('description', 'N/A')}")
        result.append(f"Created: {info.get('created', 'N/A')}")
        result.append("")
        result.append("Statistics:")
        result.append(f"  Directories: {total_dirs}")
        result.append(f"  Files: {total_files}")
        result.append(f"  Total size: {size_mb:.2f} MB")
        result.append("")
        
        # List subdirectories
        result.append("Directory Structure:")
        for item in os.listdir(workspace_path):
            if item.startswith(".") and item != ".workspace.json":
                continue
            
            item_path = os.path.join(workspace_path, item)
            if os.path.isdir(item_path):
                # Count files in directory
                file_count = sum(1 for _ in Path(item_path).rglob('*') if _.is_file())
                result.append(f"  📁 {item}/ ({file_count} files)")
            else:
                size_kb = os.path.getsize(item_path) / 1024
                result.append(f"  📄 {item} ({size_kb:.1f} KB)")
        
        # Check for virtual environment
        venv_paths = [
            os.path.join(workspace_path, "venv"),
            os.path.join(workspace_path, ".venv"),
            os.path.join(workspace_path, "env"),
            os.path.join(workspace_path, ".env")
        ]
        
        for venv_path in venv_paths:
            if os.path.exists(venv_path) and os.path.isdir(venv_path):
                result.append("")
                result.append("Virtual Environment:")
                result.append(f"  Path: {venv_path}")
                result.append(f"  Type: {'venv' if os.path.exists(os.path.join(venv_path, 'pyvenv.cfg')) else 'Unknown'}")
                break
        
        return "\n".join(result)
    
    except Exception as e:
        return f"Error: Unexpected error when getting workspace info: {str(e)}"

def create_virtualenv(venv_path: str, python_version: str = None, 
                      system_site_packages: bool = False, venv_type: str = "venv", 
                      force: bool = False) -> str:
    '''
    Create a new Python virtual environment.
    
    :param venv_path: Path for the virtual environment
    :type venv_path: str
    :param python_version: Python version (e.g., python3.8, python3.9)
    :type python_version: str
    :param system_site_packages: Allow access to system site packages
    :type system_site_packages: bool
    :param venv_type: Type of virtual environment (venv, virtualenv, conda)
    :type venv_type: str
    :param force: Overwrite existing virtual environment
    :type force: bool
    :return: Creation status message
    :rtype: str
    '''
    try:
        if os.path.exists(venv_path):
            if not force:
                return f"Error: Virtual environment already exists: {venv_path}. Use force=True to overwrite."
            else:
                shutil.rmtree(venv_path)
                print(f"Removed existing virtual environment: {venv_path}")
        
        if venv_type.lower() == "venv":
            # Use built-in venv module
            builder = venv.EnvBuilder(
                system_site_packages=system_site_packages,
                clear=True,
                with_pip=True
            )
            builder.create(venv_path)
            
            result = f"Successfully created venv at: {venv_path}"
            
        elif venv_type.lower() == "virtualenv":
            # Use virtualenv command
            cmd = ["virtualenv", venv_path]
            if python_version:
                cmd.extend(["-p", python_version])
            if system_site_packages:
                cmd.append("--system-site-packages")
            
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            result = f"Successfully created virtualenv at: {venv_path}"
            
        elif venv_type.lower() == "conda":
            # Use conda to create environment
            if not shutil.which("conda"):
                return "Error: Conda is not installed or not in PATH"
            
            env_name = os.path.basename(venv_path)
            cmd = ["conda", "create", "-n", env_name, "-y"]
            if python_version:
                cmd.append(f"python={python_version}")
            
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            result = f"Successfully created conda environment: {env_name}"
            
        else:
            return f"Error: Unsupported virtual environment type: {venv_type}"
        
        # Get Python version from the new environment
        if venv_type.lower() in ["venv", "virtualenv"]:
            python_exec = os.path.join(venv_path, "bin", "python") if sys.platform != "win32" else os.path.join(venv_path, "Scripts", "python.exe")
            if os.path.exists(python_exec):
                version_output = subprocess.run(
                    [python_exec, "--version"],
                    capture_output=True,
                    text=True
                )
                result += f"\nPython version: {version_output.stdout.strip()}"
        
        return result
    
    except subprocess.CalledProcessError as e:
        return f"Error: Failed to create virtual environment: {str(e)}\nStderr: {e.stderr}"
    except Exception as e:
        return f"Error: Unexpected error when creating virtual environment: {str(e)}"

def delete_virtualenv(venv_path: str, force: bool = False) -> str:
    '''
    Delete a virtual environment.
    
    :param venv_path: Path to virtual environment
    :type venv_path: str
    :param force: Force deletion without confirmation
    :type force: bool
    :return: Deletion status message
    :rtype: str
    '''
    try:
        if not os.path.exists(venv_path):
            return f"Error: Virtual environment does not exist: {venv_path}"
        
        # Check if it's a valid virtual environment
        is_valid_venv = False
        
        # Check for venv/virtualenv structure
        if sys.platform != "win32":
            if os.path.exists(os.path.join(venv_path, "bin", "python")):
                is_valid_venv = True
        else:
            if os.path.exists(os.path.join(venv_path, "Scripts", "python.exe")):
                is_valid_venv = True
        
        # Check for conda environment (in conda envs directory)
        conda_envs_dir = os.path.join(os.path.expanduser("~"), ".conda", "envs")
        if venv_path.startswith(conda_envs_dir):
            is_valid_venv = True
        
        if not is_valid_venv and not force:
            return f"Error: Not a valid virtual environment: {venv_path}. Use force=True to delete anyway."
        
        # Delete the virtual environment
        shutil.rmtree(venv_path)
        
        return f"Successfully deleted virtual environment: {venv_path}"
    
    except PermissionError as e:
        return f"Error: Permission denied when deleting virtual environment: {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error when deleting virtual environment: {str(e)}"

def list_virtualenvs(parent_dir: str = None) -> str:
    '''
    List all virtual environments in a directory.
    
    :param parent_dir: Parent directory to search for virtual environments
    :type parent_dir: str
    :return: List of virtual environments with information
    :rtype: str
    '''
    try:
        if parent_dir is None:
            # Default search locations
            search_paths = [
                os.getcwd(),
                os.path.expanduser("~/venvs"),
                os.path.expanduser("~/.virtualenvs"),
                os.path.join(os.path.expanduser("~"), ".conda", "envs")
            ]
        else:
            search_paths = [parent_dir]
        
        venv_list = []
        
        for search_path in search_paths:
            if not os.path.exists(search_path):
                continue
            
            # Check for conda environments
            if search_path.endswith("envs") and os.path.basename(search_path) == "envs":
                if os.path.exists(search_path):
                    for item in os.listdir(search_path):
                        venv_path = os.path.join(search_path, item)
                        if os.path.isdir(venv_path):
                            venv_list.append({
                                "name": item,
                                "path": venv_path,
                                "type": "conda",
                                "location": search_path
                            })
            
            # Check for venv/virtualenv directories
            for item in os.listdir(search_path):
                venv_path = os.path.join(search_path, item)
                if os.path.isdir(venv_path):
                    # Check if it's a venv/virtualenv
                    is_venv = False
                    venv_type = "unknown"
                    
                    # Check for venv structure
                    if sys.platform != "win32":
                        if os.path.exists(os.path.join(venv_path, "bin", "python")):
                            is_venv = True
                            venv_type = "venv"
                    else:
                        if os.path.exists(os.path.join(venv_path, "Scripts", "python.exe")):
                            is_venv = True
                            venv_type = "venv"
                    
                    # Check for virtualenv structure
                    if not is_venv and os.path.exists(os.path.join(venv_path, "pyvenv.cfg")):
                        is_venv = True
                        venv_type = "virtualenv"
                    
                    if is_venv:
                        venv_list.append({
                            "name": item,
                            "path": venv_path,
                            "type": venv_type,
                            "location": search_path
                        })
        
        if not venv_list:
            return "No virtual environments found."
        
        # Format output
        result = ["Virtual Environments:"]
        result.append("-" * 100)
        result.append(f"{'Name':<20} {'Type':<10} {'Path':<50} {'Location':<20}")
        result.append("-" * 100)
        
        for venv_info in venv_list:
            name = venv_info["name"][:18]
            venv_type = venv_info["type"][:8]
            path = venv_info["path"][:48]
            location = venv_info["location"][:18]
            result.append(f"{name:<20} {venv_type:<10} {path:<50} {location:<20}")
        
        result.append(f"\nTotal: {len(venv_list)} virtual environment(s)")
        
        return "\n".join(result)
    
    except Exception as e:
        return f"Error: Unexpected error when listing virtual environments: {str(e)}"

def activate_virtualenv(venv_path: str) -> str:
    '''
    Get activation commands for a virtual environment.
    
    :param venv_path: Path to virtual environment
    :type venv_path: str
    :return: Activation commands for different platforms
    :rtype: str
    '''
    try:
        if not os.path.exists(venv_path):
            return f"Error: Virtual environment does not exist: {venv_path}"
        
        # Determine virtual environment type
        is_conda = False
        if "conda" in venv_path.lower() or "envs" in venv_path.lower():
            # Check if it's a conda environment
            env_name = os.path.basename(venv_path)
            conda_envs_dir = os.path.join(os.path.expanduser("~"), ".conda", "envs")
            if venv_path.startswith(conda_envs_dir):
                is_conda = True
        
        result = [f"Activation commands for: {venv_path}"]
        result.append("=" * 60)
        
        if is_conda:
            env_name = os.path.basename(venv_path)
            result.append("Conda Environment:")
            result.append(f"  conda activate {env_name}")
            result.append("")
            result.append("To deactivate:")
            result.append("  conda deactivate")
        else:
            # Standard venv/virtualenv
            result.append("Standard Virtual Environment:")
            
            if sys.platform == "win32":
                activate_script = os.path.join(venv_path, "Scripts", "activate.bat")
                if os.path.exists(activate_script):
                    result.append(f"  {activate_script}")
                result.append("")
                result.append("For PowerShell:")
                result.append(f"  {os.path.join(venv_path, 'Scripts', 'Activate.ps1')}")
            else:
                # Unix/Linux/Mac
                activate_script = os.path.join(venv_path, "bin", "activate")
                if os.path.exists(activate_script):
                    result.append(f"  source {activate_script}")
            
            result.append("")
            result.append("To deactivate:")
            result.append("  deactivate")
        
        result.append("")
        result.append("Alternative: Use the Python interpreter directly:")
        if sys.platform != "win32":
            python_path = os.path.join(venv_path, "bin", "python")
        else:
            python_path = os.path.join(venv_path, "Scripts", "python.exe")
        
        if os.path.exists(python_path):
            result.append(f"  {python_path} your_script.py")
        else:
            result.append("  (Python interpreter not found)")
        
        return "\n".join(result)
    
    except Exception as e:
        return f"Error: Unexpected error when getting activation commands: {str(e)}"

def install_packages(venv_path: str, requirements: str = None, 
                     packages: list = None, force: bool = False) -> str:
    '''
    Install packages in a virtual environment.
    
    :param venv_path: Path to virtual environment
    :type venv_path: str
    :param requirements: Path to requirements.txt file
    :type requirements: str
    :param packages: List of packages to install
    :type packages: list
    :param force: Force reinstallation of packages
    :type force: bool
    :return: Installation status message
    :rtype: str
    '''
    try:
        if not os.path.exists(venv_path):
            return f"Error: Virtual environment does not exist: {venv_path}"
        
        # Determine pip executable path
        if sys.platform != "win32":
            pip_exec = os.path.join(venv_path, "bin", "pip")
        else:
            pip_exec = os.path.join(venv_path, "Scripts", "pip.exe")
        
        if not os.path.exists(pip_exec):
            return f"Error: pip not found in virtual environment: {venv_path}"
        
        result_lines = []
        
        # Install from requirements.txt
        if requirements:
            if os.path.exists(requirements):
                cmd = [pip_exec, "install", "-r", requirements]
                if force:
                    cmd.append("--force-reinstall")
                
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if process.returncode == 0:
                    result_lines.append(f"Successfully installed packages from {requirements}")
                    # Count installed packages
                    lines = process.stdout.split('\n')
                    installed_count = sum(1 for line in lines if "Successfully installed" in line or "Requirement already satisfied" in line)
                    result_lines.append(f"Installed/Updated {installed_count} packages")
                else:
                    result_lines.append(f"Error installing packages from {requirements}:")
                    result_lines.append(process.stderr)
            else:
                result_lines.append(f"Error: Requirements file not found: {requirements}")
        
        # Install individual packages
        if packages:
            for package in packages:
                cmd = [pip_exec, "install", package]
                if force:
                    cmd.append("--force-reinstall")
                
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if process.returncode == 0:
                    result_lines.append(f"Successfully installed: {package}")
                else:
                    result_lines.append(f"Error installing {package}: {process.stderr}")
        
        if not requirements and not packages:
            return "Error: No packages or requirements file specified"
        
        return "\n".join(result_lines)
    
    except subprocess.TimeoutExpired:
        return "Error: Installation timed out. Try increasing timeout or install fewer packages at once."
    except Exception as e:
        return f"Error: Unexpected error when installing packages: {str(e)}"

def deactivate_virtualenv(venv_path: str) -> str:
    '''
    Deactivate a virtual environment.
    Note: This function only provides instructions since deactivation 
    needs to happen in the shell that activated the environment.
    
    :param venv_path: Path to virtual environment
    :type venv_path: str
    :return: Deactivation instructions
    :rtype: str
    '''
    try:
        if not os.path.exists(venv_path):
            return f"Error: Virtual environment does not exist: {venv_path}"
        
        # Determine virtual environment type
        is_conda = False
        if "conda" in venv_path.lower() or "envs" in venv_path.lower():
            is_conda = True
        
        if is_conda:
            return "To deactivate conda environment, run:\n  conda deactivate"
        else:
            return "To deactivate virtual environment, run:\n  deactivate"
    
    except Exception as e:
        return f"Error: Unexpected error when getting deactivation instructions: {str(e)}"

def check_virtualenv(venv_path: str) -> str:
    '''
    Check if a virtual environment exists and is valid.
    
    :param venv_path: Path to virtual environment
    :type venv_path: str
    :return: Check results
    :rtype: str
    '''
    try:
        if not os.path.exists(venv_path):
            return f"Error: Virtual environment does not exist: {venv_path}"
        
        result = [f"Virtual Environment Check: {venv_path}"]
        result.append("=" * 60)
        
        # Check structure
        result.append("Structure Check:")
        
        is_valid = True
        missing_items = []
        
        if sys.platform != "win32":
            required_items = [
                ("bin/python", "Python executable"),
                ("bin/pip", "pip executable"),
                ("bin/activate", "Activation script")
            ]
        else:
            required_items = [
                ("Scripts/python.exe", "Python executable"),
                ("Scripts/pip.exe", "pip executable"),
                ("Scripts/activate.bat", "Activation script")
            ]
        
        for rel_path, desc in required_items:
            full_path = os.path.join(venv_path, rel_path)
            if os.path.exists(full_path):
                result.append(f"  ✓ {desc}: {full_path}")
            else:
                result.append(f"  ✗ {desc}: NOT FOUND")
                missing_items.append(desc)
                is_valid = False
        
        # Check pyvenv.cfg
        pyvenv_cfg = os.path.join(venv_path, "pyvenv.cfg")
        if os.path.exists(pyvenv_cfg):
            result.append(f"  ✓ Configuration file: {pyvenv_cfg}")
            # Read and display some config
            with open(pyvenv_cfg, "r") as f:
                for line in f.readlines()[:3]:  # First 3 lines
                    result.append(f"    {line.strip()}")
        else:
            result.append("  ✗ Configuration file: NOT FOUND")
            is_valid = False
        
        # Check Python version
        if sys.platform != "win32":
            python_exec = os.path.join(venv_path, "bin", "python")
        else:
            python_exec = os.path.join(venv_path, "Scripts", "python.exe")
        
        if os.path.exists(python_exec):
            try:
                version_output = subprocess.run(
                    [python_exec, "--version"],
                    capture_output=True,
                    text=True
                )
                if version_output.returncode == 0:
                    result.append(f"  ✓ Python version: {version_output.stdout.strip()}")
                else:
                    result.append(f"  ✗ Python version: Cannot determine")
                    is_valid = False
            except:
                result.append(f"  ✗ Python version: Cannot execute")
                is_valid = False
        
        # Overall status
        result.append("")
        result.append("Overall Status:")
        if is_valid:
            result.append("  ✓ VALID virtual environment")
        else:
            result.append("  ✗ INVALID virtual environment")
            if missing_items:
                result.append(f"  Missing: {', '.join(missing_items)}")
        
        return "\n".join(result)
    
    except Exception as e:
        return f"Error: Unexpected error when checking virtual environment: {str(e)}"

def upgrade_pip(venv_path: str) -> str:
    '''
    Upgrade pip in a virtual environment.
    
    :param venv_path: Path to virtual environment
    :type venv_path: str
    :return: Upgrade status message
    :rtype: str
    '''
    try:
        if not os.path.exists(venv_path):
            return f"Error: Virtual environment does not exist: {venv_path}"
        
        # Determine pip executable path
        if sys.platform != "win32":
            pip_exec = os.path.join(venv_path, "bin", "pip")
        else:
            pip_exec = os.path.join(venv_path, "Scripts", "pip.exe")
        
        if not os.path.exists(pip_exec):
            return f"Error: pip not found in virtual environment: {venv_path}"
        
        # Upgrade pip
        cmd = [pip_exec, "install", "--upgrade", "pip"]
        
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if process.returncode == 0:
            # Get new pip version
            version_cmd = [pip_exec, "--version"]
            version_process = subprocess.run(
                version_cmd,
                capture_output=True,
                text=True
            )
            
            if version_process.returncode == 0:
                version_info = version_process.stdout.strip()
                return f"Successfully upgraded pip\nCurrent version: {version_info}"
            else:
                return "Successfully upgraded pip (version unknown)"
        else:
            return f"Error upgrading pip: {process.stderr}"
    
    except subprocess.TimeoutExpired:
        return "Error: pip upgrade timed out."
    except Exception as e:
        return f"Error: Unexpected error when upgrading pip: {str(e)}"

def export_requirements(venv_path: str) -> str:
    '''
    Export installed packages to requirements.txt.
    
    :param venv_path: Path to virtual environment
    :type venv_path: str
    :return: Export status message
    :rtype: str
    '''
    try:
        if not os.path.exists(venv_path):
            return f"Error: Virtual environment does not exist: {venv_path}"
        
        # Determine pip executable path
        if sys.platform != "win32":
            pip_exec = os.path.join(venv_path, "bin", "pip")
        else:
            pip_exec = os.path.join(venv_path, "Scripts", "pip.exe")
        
        if not os.path.exists(pip_exec):
            return f"Error: pip not found in virtual environment: {venv_path}"
        
        # Freeze requirements
        cmd = [pip_exec, "freeze"]
        
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        if process.returncode == 0:
            requirements = process.stdout.strip()
            
            if not requirements:
                return "No packages installed in this virtual environment."
            
            # Count packages
            package_count = len([line for line in requirements.split('\n') if line.strip()])
            
            # Save to requirements.txt
            requirements_file = os.path.join(venv_path, "requirements.txt")
            with open(requirements_file, "w") as f:
                f.write(requirements)
            
            return f"Successfully exported {package_count} packages to {requirements_file}\n\nPackages:\n{requirements}"
        else:
            return f"Error exporting requirements: {process.stderr}"
    
    except Exception as e:
        return f"Error: Unexpected error when exporting requirements: {str(e)}"

TOOL_CALL_MAP = {
    "create_workspace": create_workspace,
    "delete_workspace": delete_workspace,
    "list_workspaces": list_workspaces,
    "get_workspace_info": get_workspace_info,
    "create_virtualenv": create_virtualenv,
    "delete_virtualenv": delete_virtualenv,
    "list_virtualenvs": list_virtualenvs,
    "activate_virtualenv": activate_virtualenv,
    "install_packages": install_packages,
    "deactivate_virtualenv": deactivate_virtualenv,
    "check_virtualenv": check_virtualenv,
    "upgrade_pip": upgrade_pip,
    "export_requirements": export_requirements,
}