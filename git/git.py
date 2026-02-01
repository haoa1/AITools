from base import function_ai, parameters_func, property_param

import os
import subprocess
import sys
import re

# Module metadata
__module_metadata__ = {
    "name": "git",
    "version": "1.0.0",
    "description": "Git version control operations",
    "author": "AITools Team",
    "dependencies": [],
    "tags": ["git", "version-control", "vcs"]
}

__GIT_PROPERTY_ONE__ = property_param(
    name="repo_path",
    description="The path to the git repository (default: current directory).",
    t="string"
)

__GIT_PROPERTY_TWO__ = property_param(
    name="branch",
    description="The branch name for git operations.",
    t="string"
)

__GIT_PROPERTY_THREE__ = property_param(
    name="message",
    description="The commit message.",
    t="string"
)

__GIT_PROPERTY_4__ = property_param(
    name="remote",
    description="The remote repository name (default: origin).",
    t="string"
)

__GIT_PROPERTY_5__ = property_param(
    name="files",
    description="List of files to operate on.",
    t="array"
)

__GIT_PROPERTY_6__ = property_param(
    name="file",
    description="A single file to operate on.",
    t="string"
)

__GIT_PROPERTY_7__ = property_param(
    name="tag",
    description="The tag name for git operations.",
    t="string"
)

__GIT_PROPERTY_8__ = property_param(
    name="commit_hash",
    description="The commit hash for git operations.",
    t="string"
)

__GIT_PROPERTY_9__ = property_param(
    name="force",
    description="Force the operation (use with caution).",
    t="boolean"
)

__GIT_PROPERTY_10__ = property_param(
    name="all",
    description="Apply operation to all changes.",
    t="boolean"
)

__GIT_PROPERTY_11__ = property_param(
    name="url",
    description="The URL of the git repository.",
    t="string"
)

__GIT_PROPERTY_12__ = property_param(
    name="depth",
    description="Clone depth (shallow clone).",
    t="integer"
)

__GIT_PROPERTY_13__ = property_param(
    name="key",
    description="The configuration key for git config.",
    t="string"
)

__GIT_PROPERTY_14__ = property_param(
    name="value",
    description="The configuration value for git config.",
    t="string"
)

__GIT_STATUS_FUNCTION__ = function_ai(name="git_status",
                                      description="Show the working tree status.",
                                      parameters=parameters_func([__GIT_PROPERTY_ONE__]))

__GIT_LOG_FUNCTION__ = function_ai(name="git_log",
                                   description="Show commit logs.",
                                   parameters=parameters_func([__GIT_PROPERTY_ONE__, __GIT_PROPERTY_8__]))

__GIT_DIFF_FUNCTION__ = function_ai(name="git_diff",
                                    description="Show changes between commits, commit and working tree, etc.",
                                    parameters=parameters_func([__GIT_PROPERTY_ONE__, __GIT_PROPERTY_6__, __GIT_PROPERTY_8__]))

__GIT_BRANCH_FUNCTION__ = function_ai(name="git_branch",
                                      description="List, create, or delete branches.",
                                      parameters=parameters_func([__GIT_PROPERTY_ONE__, __GIT_PROPERTY_TWO__, __GIT_PROPERTY_9__]))

__GIT_CLONE_FUNCTION__ = function_ai(name="git_clone",
                                     description="Clone a repository into a new directory.",
                                     parameters=parameters_func([__GIT_PROPERTY_11__, __GIT_PROPERTY_ONE__, __GIT_PROPERTY_12__]))

__GIT_PULL_FUNCTION__ = function_ai(name="git_pull",
                                    description="Fetch from and integrate with another repository or a local branch.",
                                    parameters=parameters_func([__GIT_PROPERTY_ONE__, __GIT_PROPERTY_4__, __GIT_PROPERTY_TWO__]))

__GIT_PUSH_FUNCTION__ = function_ai(name="git_push",
                                    description="Update remote refs along with associated objects.",
                                    parameters=parameters_func([__GIT_PROPERTY_ONE__, __GIT_PROPERTY_4__, __GIT_PROPERTY_TWO__, __GIT_PROPERTY_9__]))

__GIT_COMMIT_FUNCTION__ = function_ai(name="git_commit",
                                      description="Record changes to the repository.",
                                      parameters=parameters_func([__GIT_PROPERTY_ONE__, __GIT_PROPERTY_THREE__, __GIT_PROPERTY_10__]))

__GIT_ADD_FUNCTION__ = function_ai(name="git_add",
                                   description="Add file contents to the index.",
                                   parameters=parameters_func([__GIT_PROPERTY_ONE__, __GIT_PROPERTY_5__, __GIT_PROPERTY_10__, __GIT_PROPERTY_6__]))

__GIT_CHECKOUT_FUNCTION__ = function_ai(name="git_checkout",
                                        description="Switch branches or restore working tree files.",
                                        parameters=parameters_func([__GIT_PROPERTY_ONE__, __GIT_PROPERTY_TWO__, __GIT_PROPERTY_6__, __GIT_PROPERTY_9__]))

__GIT_FETCH_FUNCTION__ = function_ai(name="git_fetch",
                                     description="Download objects and refs from another repository.",
                                     parameters=parameters_func([__GIT_PROPERTY_ONE__, __GIT_PROPERTY_4__]))

__GIT_MERGE_FUNCTION__ = function_ai(name="git_merge",
                                     description="Join two or more development histories together.",
                                     parameters=parameters_func([__GIT_PROPERTY_ONE__, __GIT_PROPERTY_TWO__, __GIT_PROPERTY_9__]))

__GIT_TAG_FUNCTION__ = function_ai(name="git_tag",
                                   description="Create, list, delete or verify a tag object signed with GPG.",
                                   parameters=parameters_func([__GIT_PROPERTY_ONE__, __GIT_PROPERTY_7__, __GIT_PROPERTY_THREE__, __GIT_PROPERTY_9__]))

__GIT_REMOTE_FUNCTION__ = function_ai(name="git_remote",
                                      description="Manage set of tracked repositories.",
                                      parameters=parameters_func([__GIT_PROPERTY_ONE__, __GIT_PROPERTY_4__, __GIT_PROPERTY_11__]))

__GIT_RESET_FUNCTION__ = function_ai(name="git_reset",
                                     description="Reset current HEAD to the specified state.",
                                     parameters=parameters_func([__GIT_PROPERTY_ONE__, __GIT_PROPERTY_8__, __GIT_PROPERTY_6__, __GIT_PROPERTY_9__]))

__GIT_STASH_FUNCTION__ = function_ai(name="git_stash",
                                     description="Stash the changes in a dirty working directory away.",
                                     parameters=parameters_func([__GIT_PROPERTY_ONE__]))

__GIT_SHOW_FUNCTION__ = function_ai(name="git_show",
                                    description="Show various types of objects.",
                                    parameters=parameters_func([__GIT_PROPERTY_ONE__, __GIT_PROPERTY_8__, __GIT_PROPERTY_6__]))

__GIT_REBASE_FUNCTION__ = function_ai(name="git_rebase",
                                      description="Reapply commits on top of another base tip.",
                                      parameters=parameters_func([__GIT_PROPERTY_ONE__, __GIT_PROPERTY_TWO__, __GIT_PROPERTY_9__]))

__GIT_CONFIG_FUNCTION__ = function_ai(name="git_config",
                                      description="Get or set git configuration.",
                                      parameters=parameters_func([__GIT_PROPERTY_ONE__, __GIT_PROPERTY_13__, __GIT_PROPERTY_14__]))

__GIT_INIT_FUNCTION__ = function_ai(name="git_init",
                                   description="Initialize a new git repository.",
                                   parameters=parameters_func([__GIT_PROPERTY_ONE__]))

tools = [
    __GIT_STATUS_FUNCTION__,
    __GIT_LOG_FUNCTION__,
    __GIT_DIFF_FUNCTION__,
    __GIT_BRANCH_FUNCTION__,
    __GIT_CLONE_FUNCTION__,
    __GIT_PULL_FUNCTION__,
    __GIT_PUSH_FUNCTION__,
    __GIT_COMMIT_FUNCTION__,
    __GIT_ADD_FUNCTION__,
    __GIT_CHECKOUT_FUNCTION__,
    __GIT_FETCH_FUNCTION__,
    __GIT_MERGE_FUNCTION__,
    __GIT_TAG_FUNCTION__,
    __GIT_REMOTE_FUNCTION__,
    __GIT_RESET_FUNCTION__,
    __GIT_STASH_FUNCTION__,
    __GIT_SHOW_FUNCTION__,
    __GIT_REBASE_FUNCTION__,
    __GIT_INIT_FUNCTION__,
    __GIT_CONFIG_FUNCTION__
]

def _run_git_command(repo_path, args, timeout=30):
    """Internal helper function to run git commands."""
    try:
        if repo_path and os.path.exists(repo_path):
            cwd = repo_path
        else:
            cwd = os.getcwd()
        
        # Check if git is available
        try:
            subprocess.run(['git', '--version'], capture_output=True, check=True, timeout=5)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return "Error: Git is not installed or not in PATH"
        
        # Run git command
        result = subprocess.run(
            ['git'] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        output = result.stdout.strip()
        error = result.stderr.strip()
        
        if result.returncode != 0:
            if "not a git repository" in error.lower():
                return f"Error: Not a git repository: {cwd}"
            elif "permission denied" in error.lower():
                return f"Error: Permission denied: {error}"
            else:
                return f"Git command failed: {error}"
        
        return output if output else "Command executed successfully (no output)"
    
    except subprocess.TimeoutExpired:
        return f"Error: Git command timed out after {timeout} seconds"
    except PermissionError as e:
        return f"Error: Permission error: {str(e)}"
    except Exception as e:
        return f"Error: Unexpected error executing git command: {str(e)}"

def git_status(repo_path: str = None) -> str:
    '''
    Show the working tree status.
    
    :param repo_path: Path to git repository
    :type repo_path: str
    :return: Git status output
    :rtype: str
    '''
    return _run_git_command(repo_path, ['status'])

def git_log(repo_path: str = None, commit_hash: str = None) -> str:
    '''
    Show commit logs.
    
    :param repo_path: Path to git repository
    :type repo_path: str
    :param commit_hash: Specific commit hash to show
    :type commit_hash: str
    :return: Git log output
    :rtype: str
    '''
    args = ['log', '--oneline', '--graph', '--decorate', '-10']
    if commit_hash:
        args = ['log', '--oneline', '-1', commit_hash]
    return _run_git_command(repo_path, args)

def git_diff(repo_path: str = None, file: str = None, commit_hash: str = None) -> str:
    '''
    Show changes between commits, commit and working tree, etc.
    
    :param repo_path: Path to git repository
    :type repo_path: str
    :param file: Specific file to diff
    :type file: str
    :param commit_hash: Commit hash to compare with
    :type commit_hash: str
    :return: Git diff output
    :rtype: str
    '''
    args = ['diff']
    if commit_hash:
        args.append(commit_hash)
    if file:
        args.append('--')
        args.append(file)
    return _run_git_command(repo_path, args)

def git_branch(repo_path: str = None, branch: str = None, force: bool = False) -> str:
    '''
    List, create, or delete branches.
    
    :param repo_path: Path to git repository
    :type repo_path: str
    :param branch: Branch name (for create/delete operations)
    :type branch: str
    :param force: Force delete branch
    :type force: bool
    :return: Branch operation output
    :rtype: str
    '''
    if branch:
        # Create new branch
        return _run_git_command(repo_path, ['checkout', '-b', branch])
    else:
        # List branches
        return _run_git_command(repo_path, ['branch', '-a'])

def git_clone(url: str, repo_path: str = None, depth: int = None) -> str:
    '''
    Clone a repository into a new directory.
    
    :param url: Repository URL
    :type url: str
    :param repo_path: Target directory path
    :type repo_path: str
    :param depth: Clone depth (shallow clone)
    :type depth: int
    :return: Clone operation output
    :rtype: str
    '''
    try:
        args = ['clone']
        if depth:
            args.extend(['--depth', str(depth)])
        args.append(url)
        if repo_path:
            args.append(repo_path)
        
        return _run_git_command(None, args, timeout=300)  # Longer timeout for clone
    except Exception as e:
        return f"Error cloning repository: {str(e)}"

def git_pull(repo_path: str = None, remote: str = "origin", branch: str = None) -> str:
    '''
    Fetch from and integrate with another repository or a local branch.
    
    :param repo_path: Path to git repository
    :type repo_path: str
    :param remote: Remote name
    :type remote: str
    :param branch: Branch name
    :type branch: str
    :return: Pull operation output
    :rtype: str
    '''
    args = ['pull', remote]
    if branch:
        args.append(branch)
    return _run_git_command(repo_path, args)

def git_push(repo_path: str = None, remote: str = "origin", branch: str = None, force: bool = False) -> str:
    '''
    Update remote refs along with associated objects.
    
    :param repo_path: Path to git repository
    :type repo_path: str
    :param remote: Remote name
    :type remote: str
    :param branch: Branch name
    :type branch: str
    :param force: Force push
    :type force: bool
    :return: Push operation output
    :rtype: str
    '''
    args = ['push']
    if force:
        args.append('--force')
    args.append(remote)
    if branch:
        args.append(branch)
    return _run_git_command(repo_path, args)

def git_commit(repo_path: str = None, message: str = "", all: bool = False) -> str:
    '''
    Record changes to the repository.
    
    :param repo_path: Path to git repository
    :type repo_path: str
    :param message: Commit message
    :type message: str
    :param all: Commit all changed files
    :type all: bool
    :return: Commit operation output
    :rtype: str
    '''
    if not message:
        return "Error: Commit message is required"
    
    args = ['commit']
    if all:
        args.append('-a')
    args.extend(['-m', message])
    return _run_git_command(repo_path, args)

def git_add(repo_path: str = None, files: list = None, all: bool = False, file: str = None) -> str:
    '''
    Add file contents to the index.
    
    :param repo_path: Path to git repository
    :type repo_path: str
    :param files: List of files to add
    :type files: list
    :param all: Add all changes
    :type all: bool
    :param file: Single file to add
    :type file: str
    :return: Add operation output
    :rtype: str
    '''
    args = ['add']
    if all:
        args.append('.')
    elif file:
        args.append(file)
    elif files:
        for f in files:
            args.append(f)
    else:
        return "Error: No files specified for git add"
    
    return _run_git_command(repo_path, args)

def git_checkout(repo_path: str = None, branch: str = None, file: str = None, force: bool = False) -> str:
    '''
    Switch branches or restore working tree files.
    
    :param repo_path: Path to git repository
    :type repo_path: str
    :param branch: Branch name to checkout
    :type branch: str
    :param file: File to checkout (restore)
    :type file: str
    :param force: Force checkout
    :type force: bool
    :return: Checkout operation output
    :rtype: str
    '''
    args = ['checkout']
    if force:
        args.append('--force')
    
    if branch:
        args.append(branch)
    elif file:
        args.append('--')
        args.append(file)
    else:
        return "Error: Either branch or file must be specified"
    
    return _run_git_command(repo_path, args)

def git_fetch(repo_path: str = None, remote: str = "origin") -> str:
    '''
    Download objects and refs from another repository.
    
    :param repo_path: Path to git repository
    :type repo_path: str
    :param remote: Remote name
    :type remote: str
    :return: Fetch operation output
    :rtype: str
    '''
    args = ['fetch', remote]
    return _run_git_command(repo_path, args)

def git_merge(repo_path: str = None, branch: str = None, force: bool = False) -> str:
    '''
    Join two or more development histories together.
    
    :param repo_path: Path to git repository
    :type repo_path: str
    :param branch: Branch to merge
    :type branch: str
    :param force: Force merge
    :type force: bool
    :return: Merge operation output
    :rtype: str
    '''
    if not branch:
        return "Error: Branch name is required for merge"
    
    args = ['merge']
    if force:
        args.append('--force')
    args.append(branch)
    return _run_git_command(repo_path, args)

def git_tag(repo_path: str = None, tag: str = None, message: str = "", force: bool = False) -> str:
    '''
    Create, list, delete or verify a tag object.
    
    :param repo_path: Path to git repository
    :type repo_path: str
    :param tag: Tag name
    :type tag: str
    :param message: Tag message
    :type message: str
    :param force: Force tag creation
    :type force: bool
    :return: Tag operation output
    :rtype: str
    '''
    if tag:
        args = ['tag']
        if force:
            args.append('--force')
        if message:
            args.extend(['-a', tag, '-m', message])
        else:
            args.append(tag)
    else:
        args = ['tag', '-l']
    
    return _run_git_command(repo_path, args)

def git_remote(repo_path: str = None, remote: str = None, url: str = None) -> str:
    '''
    Manage set of tracked repositories.
    
    :param repo_path: Path to git repository
    :type repo_path: str
    :param remote: Remote name
    :type remote: str
    :param url: Remote URL
    :type url: str
    :return: Remote operation output
    :rtype: str
    '''
    if remote and url:
        args = ['remote', 'add', remote, url]
    elif remote:
        args = ['remote', 'get-url', remote]
    else:
        args = ['remote', '-v']
    
    return _run_git_command(repo_path, args)

def git_reset(repo_path: str = None, commit_hash: str = None, file: str = None, force: bool = False) -> str:
    '''
    Reset current HEAD to the specified state.
    
    :param repo_path: Path to git repository
    :type repo_path: str
    :param commit_hash: Commit hash to reset to
    :type commit_hash: str
    :param file: Specific file to reset
    :type file: str
    :param force: Force reset
    :type force: bool
    :return: Reset operation output
    :rtype: str
    '''
    args = ['reset']
    if force:
        args.append('--hard')
    
    if commit_hash:
        args.append(commit_hash)
    elif file:
        args.append('--')
        args.append(file)
    
    return _run_git_command(repo_path, args)

def git_stash(repo_path: str = None) -> str:
    '''
    Stash the changes in a dirty working directory away.
    
    :param repo_path: Path to git repository
    :type repo_path: str
    :return: Stash operation output
    :rtype: str
    '''
    return _run_git_command(repo_path, ['stash'])

def git_show(repo_path: str = None, commit_hash: str = None, file: str = None) -> str:
    '''
    Show various types of objects.
    
    :param repo_path: Path to git repository
    :type repo_path: str
    :param commit_hash: Commit hash to show
    :type commit_hash: str
    :param file: Specific file to show
    :type file: str
    :return: Show operation output
    :rtype: str
    '''
    args = ['show']
    if commit_hash:
        args.append(commit_hash)
    if file:
        args.append('--')
        args.append(file)
    
    return _run_git_command(repo_path, args)

def git_rebase(repo_path: str = None, branch: str = None, force: bool = False) -> str:
    '''
    Reapply commits on top of another base tip.
    
    :param repo_path: Path to git repository
    :type repo_path: str
    :param branch: Branch to rebase onto
    :type branch: str
    :param force: Force rebase
    :type force: bool
    :return: Rebase operation output
    :rtype: str
    '''
    if not branch:
        return "Error: Branch name is required for rebase"
    
    args = ['rebase']
    if force:
        args.append('--force')
    args.append(branch)
    
    return _run_git_command(repo_path, args)

def git_init(repo_path: str = None) -> str:
    '''
    Initialize a new git repository.
    
    :param repo_path: Path to initialize repository
    :type repo_path: str
    :return: Init operation output
    :rtype: str
    '''
    return _run_git_command(repo_path, ['init'])

def git_config(repo_path: str = None, key: str = None, value: str = None) -> str:
    '''
    Get or set git configuration.
    
    :param repo_path: Path to git repository
    :type repo_path: str
    :param key: Configuration key
    :type key: str
    :param value: Configuration value
    :type value: str
    :return: Config operation output
    :rtype: str
    '''
    try:
        if key and value:
            # Set configuration
            args = ['config', key, value]
        elif key:
            # Get configuration
            args = ['config', '--get', key]
        else:
            # List all configuration
            args = ['config', '--list']
        
        return _run_git_command(repo_path, args)
    except Exception as e:
        return f"Error in git_config: {str(e)}"

TOOL_CALL_MAP = {
    "git_status": git_status,
    "git_log": git_log,
    "git_diff": git_diff,
    "git_branch": git_branch,
    "git_clone": git_clone,
    "git_pull": git_pull,
    "git_push": git_push,
    "git_commit": git_commit,
    "git_add": git_add,
    "git_checkout": git_checkout,
    "git_fetch": git_fetch,
    "git_merge": git_merge,
    "git_tag": git_tag,
    "git_remote": git_remote,
    "git_reset": git_reset,
    "git_stash": git_stash,
    "git_show": git_show,
    "git_rebase": git_rebase,
    "git_init": git_init,
    "git_config": git_config,
}