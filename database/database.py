from base import function_ai, parameters_func, property_param
import os
import json
import sqlite3
from typing import Dict, List, Any, Optional, Union
import traceback
import re

# ============================================================================
# PROPERTY DEFINITIONS
# ============================================================================

# Database connection properties
__DB_CONN_TYPE_PROP__ = property_param(
    name="db_type",
    description="Type of database: 'sqlite', 'mysql', 'postgresql', etc.",
    t="string",
    required=True
)

__DB_PATH_PROP__ = property_param(
    name="db_path",
    description="Path to SQLite database file or connection string for other databases.",
    t="string",
    required=True
)

__DB_HOST_PROP__ = property_param(
    name="host",
    description="Database host (for MySQL/PostgreSQL).",
    t="string"
)

__DB_PORT_PROP__ = property_param(
    name="port",
    description="Database port (for MySQL/PostgreSQL).",
    t="integer"
)

__DB_USER_PROP__ = property_param(
    name="user",
    description="Database username (for MySQL/PostgreSQL).",
    t="string"
)

__DB_PASSWORD_PROP__ = property_param(
    name="password",
    description="Database password (for MySQL/PostgreSQL).",
    t="string"
)

__DB_NAME_PROP__ = property_param(
    name="database",
    description="Database name (for MySQL/PostgreSQL).",
    t="string"
)

__QUERY_PROP__ = property_param(
    name="query",
    description="SQL query to execute.",
    t="string",
    required=True
)

__PARAMS_PROP__ = property_param(
    name="params",
    description="Parameters for SQL query as JSON string.",
    t="string"
)

__TABLE_NAME_PROP__ = property_param(
    name="table",
    description="Name of the database table.",
    t="string",
    required=True
)

__DATA_PROP__ = property_param(
    name="data",
    description="Data to insert/update as JSON string.",
    t="string",
    required=True
)

__WHERE_CONDITION_PROP__ = property_param(
    name="where",
    description="WHERE condition for update/delete operations.",
    t="string"
)

__COLUMNS_PROP__ = property_param(
    name="columns",
    description="Columns to select (comma-separated or '*' for all).",
    t="string"
)

__LIMIT_PROP__ = property_param(
    name="limit",
    description="Limit number of rows to return.",
    t="integer"
)

__OFFSET_PROP__ = property_param(
    name="offset",
    description="Offset for pagination.",
    t="integer"
)

__ORDER_BY_PROP__ = property_param(
    name="order_by",
    description="ORDER BY clause for sorting.",
    t="string"
)

__CONNECTION_ID_PROP__ = property_param(
    name="connection_id",
    description="Identifier for the database connection (optional, for connection pooling).",
    t="string"
)

__ISOLATION_LEVEL_PROP__ = property_param(
    name="isolation_level",
    description="Transaction isolation level: 'DEFERRED', 'IMMEDIATE', or 'EXCLUSIVE' (SQLite).",
    t="string"
)

__BATCH_SIZE_PROP__ = property_param(
    name="batch_size",
    description="Batch size for bulk operations.",
    t="integer"
)

__BACKUP_PATH_PROP__ = property_param(
    name="backup_path",
    description="Path for the backup file (optional, will generate timestamped name if not provided).",
    t="string"
)

# ============================================================================
# FUNCTION DEFINITIONS
# ============================================================================

# Database connection functions
__CONNECT_DB_FUNCTION__ = function_ai(
    name="connect_database",
    description="Connect to a database (SQLite, MySQL, PostgreSQL). Returns connection info or error.",
    parameters=parameters_func([
        __DB_CONN_TYPE_PROP__,
        __DB_PATH_PROP__,
        __DB_HOST_PROP__,
        __DB_PORT_PROP__,
        __DB_USER_PROP__,
        __DB_PASSWORD_PROP__,
        __DB_NAME_PROP__,
        __CONNECTION_ID_PROP__
    ])
)

__DISCONNECT_DB_FUNCTION__ = function_ai(
    name="disconnect_database",
    description="Disconnect from a database and clean up resources.",
    parameters=parameters_func([
        __DB_CONN_TYPE_PROP__,
        __DB_PATH_PROP__,
        __CONNECTION_ID_PROP__
    ])
)

# Query execution functions
__EXECUTE_QUERY_FUNCTION__ = function_ai(
    name="execute_query",
    description="Execute a SQL query and return results as JSON. For SELECT queries.",
    parameters=parameters_func([
        __DB_CONN_TYPE_PROP__,
        __DB_PATH_PROP__,
        __QUERY_PROP__,
        __PARAMS_PROP__,
        __CONNECTION_ID_PROP__
    ])
)

__EXECUTE_NON_QUERY_FUNCTION__ = function_ai(
    name="execute_non_query",
    description="Execute a SQL non-query (INSERT, UPDATE, DELETE) and return affected rows count.",
    parameters=parameters_func([
        __DB_CONN_TYPE_PROP__,
        __DB_PATH_PROP__,
        __QUERY_PROP__,
        __PARAMS_PROP__,
        __CONNECTION_ID_PROP__
    ])
)

# Table operations
__CREATE_TABLE_FUNCTION__ = function_ai(
    name="create_table",
    description="Create a new table in the database.",
    parameters=parameters_func([
        __DB_CONN_TYPE_PROP__,
        __DB_PATH_PROP__,
        __TABLE_NAME_PROP__,
        __QUERY_PROP__,  # Table schema SQL
        __CONNECTION_ID_PROP__
    ])
)

__DROP_TABLE_FUNCTION__ = function_ai(
    name="drop_table",
    description="Drop a table from the database.",
    parameters=parameters_func([
        __DB_CONN_TYPE_PROP__,
        __DB_PATH_PROP__,
        __TABLE_NAME_PROP__,
        __CONNECTION_ID_PROP__
    ])
)

__LIST_TABLES_FUNCTION__ = function_ai(
    name="list_tables",
    description="List all tables in the database.",
    parameters=parameters_func([
        __DB_CONN_TYPE_PROP__,
        __DB_PATH_PROP__,
        __CONNECTION_ID_PROP__
    ])
)

__DESCRIBE_TABLE_FUNCTION__ = function_ai(
    name="describe_table",
    description="Describe table structure (columns, types, etc.).",
    parameters=parameters_func([
        __DB_CONN_TYPE_PROP__,
        __DB_PATH_PROP__,
        __TABLE_NAME_PROP__,
        __CONNECTION_ID_PROP__
    ])
)

# CRUD operations
__INSERT_DATA_FUNCTION__ = function_ai(
    name="insert_data",
    description="Insert data into a table.",
    parameters=parameters_func([
        __DB_CONN_TYPE_PROP__,
        __DB_PATH_PROP__,
        __TABLE_NAME_PROP__,
        __DATA_PROP__,
        __CONNECTION_ID_PROP__
    ])
)

__UPDATE_DATA_FUNCTION__ = function_ai(
    name="update_data",
    description="Update data in a table.",
    parameters=parameters_func([
        __DB_CONN_TYPE_PROP__,
        __DB_PATH_PROP__,
        __TABLE_NAME_PROP__,
        __DATA_PROP__,
        __WHERE_CONDITION_PROP__,
        __CONNECTION_ID_PROP__
    ])
)

__DELETE_DATA_FUNCTION__ = function_ai(
    name="delete_data",
    description="Delete data from a table.",
    parameters=parameters_func([
        __DB_CONN_TYPE_PROP__,
        __DB_PATH_PROP__,
        __TABLE_NAME_PROP__,
        __WHERE_CONDITION_PROP__,
        __CONNECTION_ID_PROP__
    ])
)

__SELECT_DATA_FUNCTION__ = function_ai(
    name="select_data",
    description="Select data from a table with optional filtering, sorting, and pagination.",
    parameters=parameters_func([
        __DB_CONN_TYPE_PROP__,
        __DB_PATH_PROP__,
        __TABLE_NAME_PROP__,
        __COLUMNS_PROP__,
        __WHERE_CONDITION_PROP__,
        __ORDER_BY_PROP__,
        __LIMIT_PROP__,
        __OFFSET_PROP__,
        __CONNECTION_ID_PROP__
    ])
)

# Transaction management
__BEGIN_TRANSACTION_FUNCTION__ = function_ai(
    name="begin_transaction",
    description="Begin a database transaction.",
    parameters=parameters_func([
        __DB_CONN_TYPE_PROP__,
        __DB_PATH_PROP__,
        __ISOLATION_LEVEL_PROP__,
        __CONNECTION_ID_PROP__
    ])
)

__COMMIT_TRANSACTION_FUNCTION__ = function_ai(
    name="commit_transaction",
    description="Commit the current transaction.",
    parameters=parameters_func([
        __DB_CONN_TYPE_PROP__,
        __DB_PATH_PROP__,
        __CONNECTION_ID_PROP__
    ])
)

__ROLLBACK_TRANSACTION_FUNCTION__ = function_ai(
    name="rollback_transaction",
    description="Rollback the current transaction.",
    parameters=parameters_func([
        __DB_CONN_TYPE_PROP__,
        __DB_PATH_PROP__,
        __CONNECTION_ID_PROP__
    ])
)

# Utility functions
__EXPORT_TO_JSON_FUNCTION__ = function_ai(
    name="export_to_json",
    description="Export table data to JSON format.",
    parameters=parameters_func([
        __DB_CONN_TYPE_PROP__,
        __DB_PATH_PROP__,
        __TABLE_NAME_PROP__,
        __QUERY_PROP__,  # Optional custom query
        __LIMIT_PROP__,
        __CONNECTION_ID_PROP__
    ])
)

__IMPORT_FROM_JSON_FUNCTION__ = function_ai(
    name="import_from_json",
    description="Import data from JSON into a table.",
    parameters=parameters_func([
        __DB_CONN_TYPE_PROP__,
        __DB_PATH_PROP__,
        __TABLE_NAME_PROP__,
        __DATA_PROP__,  # JSON data
        __BATCH_SIZE_PROP__,
        __CONNECTION_ID_PROP__
    ])
)

__EXECUTE_SCRIPT_FUNCTION__ = function_ai(
    name="execute_sql_script",
    description="Execute multiple SQL statements from a script file or string.",
    parameters=parameters_func([
        __DB_CONN_TYPE_PROP__,
        __DB_PATH_PROP__,
        __QUERY_PROP__,  # SQL script content
        __CONNECTION_ID_PROP__
    ])
)

__BACKUP_DATABASE_FUNCTION__ = function_ai(
    name="backup_database",
    description="Create a backup of the database.",
    parameters=parameters_func([
        __DB_CONN_TYPE_PROP__,
        __DB_PATH_PROP__,
        __BACKUP_PATH_PROP__,  # separate property for backup path
        __CONNECTION_ID_PROP__
    ])
)

# List of all tools
tools = [
    __CONNECT_DB_FUNCTION__,
    __DISCONNECT_DB_FUNCTION__,
    __EXECUTE_QUERY_FUNCTION__,
    __EXECUTE_NON_QUERY_FUNCTION__,
    __CREATE_TABLE_FUNCTION__,
    __DROP_TABLE_FUNCTION__,
    __LIST_TABLES_FUNCTION__,
    __DESCRIBE_TABLE_FUNCTION__,
    __INSERT_DATA_FUNCTION__,
    __UPDATE_DATA_FUNCTION__,
    __DELETE_DATA_FUNCTION__,
    __SELECT_DATA_FUNCTION__,
    __BEGIN_TRANSACTION_FUNCTION__,
    __COMMIT_TRANSACTION_FUNCTION__,
    __ROLLBACK_TRANSACTION_FUNCTION__,
    __EXPORT_TO_JSON_FUNCTION__,
    __IMPORT_FROM_JSON_FUNCTION__,
    __EXECUTE_SCRIPT_FUNCTION__,
    __BACKUP_DATABASE_FUNCTION__
]

# ============================================================================
# DATABASE CONNECTION MANAGEMENT
# ============================================================================

# Simple connection cache for SQLite
_connection_cache = {}

def _get_sqlite_connection(db_path: str, connection_id: Optional[str] = None):
    """Get or create SQLite connection."""
    cache_key = connection_id if connection_id else db_path
    
    if cache_key in _connection_cache:
        return _connection_cache[cache_key]
    
    try:
        # Ensure directory exists
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dict-like objects
        _connection_cache[cache_key] = conn
        return conn
    except sqlite3.Error as e:
        # SQLite-specific errors (e.g., corrupted database, syntax error)
        error_type = type(e).__name__
        raise Exception(f"SQLite error [{error_type}]: {str(e)}. Database: {db_path}")
    except OSError as e:
        # OS errors (permission denied, disk full, etc.)
        error_type = type(e).__name__
        raise Exception(f"OS error [{error_type}]: {str(e)}. Database: {db_path}")
    except Exception as e:
        # Any other unexpected error
        error_type = type(e).__name__
        raise Exception(f"Failed to connect to SQLite database [{error_type}]: {str(e)}. Database: {db_path}")

def _close_sqlite_connection(db_path: str, connection_id: Optional[str] = None):
    """Close SQLite connection."""
    cache_key = connection_id if connection_id else db_path
    
    if cache_key in _connection_cache:
        conn = _connection_cache[cache_key]
        try:
            conn.close()
        except Exception:
            pass
        del _connection_cache[cache_key]
        return True
    return False

def _get_connection(db_type: str, db_path: str, **kwargs):
    """Get database connection based on type."""
    connection_id = kwargs.get('connection_id')
    
    if db_type.lower() == 'sqlite':
        return _get_sqlite_connection(db_path, connection_id)
    else:
        # For now, only support SQLite
        # Future: Add MySQL, PostgreSQL support
        raise Exception(f"Database type '{db_type}' not yet supported. Currently only 'sqlite' is supported.")

def _close_connection(db_type: str, db_path: str, connection_id: Optional[str] = None):
    """Close database connection."""
    if db_type.lower() == 'sqlite':
        return _close_sqlite_connection(db_path, connection_id)
    else:
        # For other databases, just remove from cache
        cache_key = connection_id if connection_id else f"{db_type}:{db_path}"
        if cache_key in _connection_cache:
            del _connection_cache[cache_key]
        return True

# ============================================================================
# FUNCTION IMPLEMENTATIONS
# ============================================================================

def connect_database(db_type: str, db_path: str, host: str = None, port: int = None,
                     user: str = None, password: str = None, database: str = None,
                     connection_id: str = None) -> str:
    """
    Connect to a database.
    
    Currently supports SQLite. MySQL and PostgreSQL support will be added in the future.
    
    Args:
        db_type: Type of database ('sqlite', 'mysql', 'postgresql')
        db_path: Path to SQLite file or connection string
        host: Database host (for MySQL/PostgreSQL)
        port: Database port (for MySQL/PostgreSQL)
        user: Database username (for MySQL/PostgreSQL)
        password: Database password (for MySQL/PostgreSQL)
        database: Database name (for MySQL/PostgreSQL)
        connection_id: Optional connection identifier
        
    Returns:
        Connection information or error message
    """
    try:
        if db_type.lower() not in ['sqlite']:
            return f"Error: Database type '{db_type}' not yet supported. Currently only 'sqlite' is supported."
        
        if db_type.lower() == 'sqlite':
            # For SQLite, db_path should be a file path
            if not db_path:
                return "Error: SQLite database path is required."
            
            conn = _get_sqlite_connection(db_path, connection_id)
            
            # Test the connection
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            
            db_info = {
                "type": "sqlite",
                "path": db_path,
                "connection_id": connection_id or "default",
                "status": "connected",
                "tables": []
            }
            
            # Get list of tables
            try:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                db_info["tables"] = [table[0] for table in tables]
            except:
                pass
            
            cursor.close()
            
            return json.dumps(db_info, indent=2)
        
    except Exception as e:
        return f"Error connecting to database: {str(e)}"

def disconnect_database(db_type: str, db_path: str, connection_id: str = None) -> str:
    """
    Disconnect from a database.
    
    Args:
        db_type: Type of database ('sqlite', 'mysql', 'postgresql')
        db_path: Path to SQLite file or connection string
        connection_id: Optional connection identifier
        
    Returns:
        Success or error message
    """
    try:
        success = _close_connection(db_type, db_path, connection_id)
        if success:
            return "Successfully disconnected from database."
        else:
            return "No active connection found to disconnect."
    except Exception as e:
        return f"Error disconnecting from database: {str(e)}"

def execute_query(db_type: str, db_path: str, query: str, params: str = None,
                  connection_id: str = None) -> str:
    """
    Execute a SQL query and return results.
    
    Args:
        db_type: Type of database ('sqlite')
        db_path: Path to SQLite file
        query: SQL query to execute
        params: JSON string of query parameters
        connection_id: Optional connection identifier
        
    Returns:
        Query results as JSON or error message
    """
    try:
        # Parse parameters if provided
        query_params = None
        if params:
            try:
                query_params = json.loads(params)
                if isinstance(query_params, dict):
                    query_params = tuple(query_params.values())
                elif isinstance(query_params, list):
                    query_params = tuple(query_params)
            except json.JSONDecodeError as e:
                return f"Error parsing parameters JSON: {str(e)}"
        
        # Get connection
        conn = _get_connection(db_type, db_path, connection_id=connection_id)
        
        # Execute query
        cursor = conn.cursor()
        
        if query_params:
            cursor.execute(query, query_params)
        else:
            cursor.execute(query)
        
        # Fetch results
        if query.strip().upper().startswith("SELECT"):
            rows = cursor.fetchall()
            
            # Convert rows to list of dictionaries
            result = []
            for row in rows:
                if isinstance(row, sqlite3.Row):
                    result.append(dict(row))
                else:
                    # Convert tuple to dict with column names
                    columns = [desc[0] for desc in cursor.description] if cursor.description else []
                    row_dict = {}
                    for i, value in enumerate(row):
                        col_name = columns[i] if i < len(columns) else f"column_{i}"
                        row_dict[col_name] = value
                    result.append(row_dict)
            
            cursor.close()
            
            return json.dumps({
                "success": True,
                "row_count": len(result),
                "data": result
            }, indent=2)
        else:
            # For non-SELECT queries, commit and return affected rows
            conn.commit()
            affected_rows = cursor.rowcount
            cursor.close()
            
            return json.dumps({
                "success": True,
                "affected_rows": affected_rows,
                "message": "Query executed successfully."
            }, indent=2)
        
    except Exception as e:
        return f"Error executing query: {str(e)}\nQuery: {query}"

def execute_non_query(db_type: str, db_path: str, query: str, params: str = None,
                      connection_id: str = None) -> str:
    """
    Execute a non-query SQL statement (INSERT, UPDATE, DELETE).
    
    Args:
        db_type: Type of database ('sqlite')
        db_path: Path to SQLite file
        query: SQL query to execute
        params: JSON string of query parameters
        connection_id: Optional connection identifier
        
    Returns:
        Execution result with affected rows count
    """
    try:
        # Parse parameters if provided
        query_params = None
        if params:
            try:
                query_params = json.loads(params)
                if isinstance(query_params, dict):
                    query_params = tuple(query_params.values())
                elif isinstance(query_params, list):
                    query_params = tuple(query_params)
            except json.JSONDecodeError as e:
                return f"Error parsing parameters JSON: {str(e)}"
        
        # Get connection
        conn = _get_connection(db_type, db_path, connection_id=connection_id)
        
        # Execute query
        cursor = conn.cursor()
        
        if query_params:
            cursor.execute(query, query_params)
        else:
            cursor.execute(query)
        
        # Commit transaction
        conn.commit()
        affected_rows = cursor.rowcount
        cursor.close()
        
        return json.dumps({
            "success": True,
            "affected_rows": affected_rows,
            "message": f"Successfully executed. {affected_rows} row(s) affected."
        }, indent=2)
        
    except Exception as e:
        return f"Error executing non-query: {str(e)}\nQuery: {query}"

def create_table(db_type: str, db_path: str, table: str, query: str = None,
                 connection_id: str = None) -> str:
    """
    Create a new table in the database.
    
    Args:
        db_type: Type of database ('sqlite')
        db_path: Path to SQLite file
        table: Name of the table to create
        query: SQL CREATE TABLE statement (if not provided, will generate simple one)
        connection_id: Optional connection identifier
        
    Returns:
        Success or error message
    """
    try:
        # Get connection
        conn = _get_connection(db_type, db_path, connection_id=connection_id)
        
        cursor = conn.cursor()
        
        # Check if table already exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        if cursor.fetchone():
            cursor.close()
            return f"Error: Table '{table}' already exists."
        
        # Create table
        if query:
            create_sql = query
        else:
            # Generate a simple table with id and created_at columns
            create_sql = f"""
            CREATE TABLE {table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        
        cursor.execute(create_sql)
        conn.commit()
        cursor.close()
        
        return f"Successfully created table '{table}'."
        
    except Exception as e:
        return f"Error creating table: {str(e)}"

def drop_table(db_type: str, db_path: str, table: str, connection_id: str = None) -> str:
    """
    Drop a table from the database.
    
    Args:
        db_type: Type of database ('sqlite')
        db_path: Path to SQLite file
        table: Name of the table to drop
        connection_id: Optional connection identifier
        
    Returns:
        Success or error message
    """
    try:
        # Get connection
        conn = _get_connection(db_type, db_path, connection_id=connection_id)
        
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        if not cursor.fetchone():
            cursor.close()
            return f"Error: Table '{table}' does not exist."
        
        # Drop table
        cursor.execute(f"DROP TABLE {table}")
        conn.commit()
        cursor.close()
        
        return f"Successfully dropped table '{table}'."
        
    except Exception as e:
        return f"Error dropping table: {str(e)}"

def list_tables(db_type: str, db_path: str, connection_id: str = None) -> str:
    """
    List all tables in the database.
    
    Args:
        db_type: Type of database ('sqlite')
        db_path: Path to SQLite file
        connection_id: Optional connection identifier
        
    Returns:
        List of tables as JSON
    """
    try:
        # Get connection
        conn = _get_connection(db_type, db_path, connection_id=connection_id)
        
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Get view count for each table
        table_info = []
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                table_info.append({"name": table, "row_count": count})
            except:
                table_info.append({"name": table, "row_count": "unknown"})
        
        cursor.close()
        
        return json.dumps({
            "success": True,
            "tables": table_info,
            "count": len(tables)
        }, indent=2)
        
    except Exception as e:
        return f"Error listing tables: {str(e)}"

def describe_table(db_type: str, db_path: str, table: str, connection_id: str = None) -> str:
    """
    Describe table structure.
    
    Args:
        db_type: Type of database ('sqlite')
        db_path: Path to SQLite file
        table: Name of the table to describe
        connection_id: Optional connection identifier
        
    Returns:
        Table schema information as JSON
    """
    try:
        # Get connection
        conn = _get_connection(db_type, db_path, connection_id=connection_id)
        
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        if not cursor.fetchone():
            cursor.close()
            return f"Error: Table '{table}' does not exist."
        
        # Get table schema
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        
        # Format column information
        column_info = []
        for col in columns:
            column_info.append({
                "cid": col[0],
                "name": col[1],
                "type": col[2],
                "notnull": bool(col[3]),
                "default_value": col[4],
                "pk": bool(col[5])
            })
        
        # Get foreign key information
        cursor.execute(f"PRAGMA foreign_key_list({table})")
        foreign_keys = cursor.fetchall()
        
        fk_info = []
        for fk in foreign_keys:
            fk_info.append({
                "id": fk[0],
                "seq": fk[1],
                "table": fk[2],
                "from": fk[3],
                "to": fk[4],
                "on_update": fk[5],
                "on_delete": fk[6],
                "match": fk[7]
            })
        
        cursor.close()
        
        return json.dumps({
            "success": True,
            "table": table,
            "columns": column_info,
            "foreign_keys": fk_info,
            "column_count": len(column_info)
        }, indent=2)
        
    except Exception as e:
        return f"Error describing table: {str(e)}"

def insert_data(db_type: str, db_path: str, table: str, data: str,
                connection_id: str = None) -> str:
    """
    Insert data into a table.
    
    Args:
        db_type: Type of database ('sqlite')
        db_path: Path to SQLite file
        table: Name of the table
        data: JSON string of data to insert (can be single object or array)
        connection_id: Optional connection identifier
        
    Returns:
        Insert result with last inserted ID
    """
    try:
        # Parse data
        try:
            data_obj = json.loads(data)
        except json.JSONDecodeError as e:
            return f"Error parsing data JSON: {str(e)}"
        
        # Get connection
        conn = _get_connection(db_type, db_path, connection_id=connection_id)
        
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        if not cursor.fetchone():
            cursor.close()
            return f"Error: Table '{table}' does not exist."
        
        # Insert data
        if isinstance(data_obj, dict):
            # Single record
            columns = list(data_obj.keys())
            placeholders = ", ".join(["?"] * len(columns))
            sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
            
            cursor.execute(sql, tuple(data_obj.values()))
            last_id = cursor.lastrowid
            row_count = 1
            
        elif isinstance(data_obj, list):
            # Multiple records
            if not data_obj:
                cursor.close()
                return "Error: Empty data array provided."
            
            # All records should have same structure
            first_record = data_obj[0]
            if not isinstance(first_record, dict):
                cursor.close()
                return "Error: Data array should contain objects/dictionaries."
            
            columns = list(first_record.keys())
            placeholders = ", ".join(["?"] * len(columns))
            sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
            
            row_count = 0
            for record in data_obj:
                if not isinstance(record, dict):
                    continue
                
                # Ensure record has all columns (fill missing with None)
                values = [record.get(col) for col in columns]
                cursor.execute(sql, tuple(values))
                row_count += 1
            
            last_id = cursor.lastrowid
        else:
            cursor.close()
            return f"Error: Invalid data format. Expected object or array, got {type(data_obj).__name__}"
        
        conn.commit()
        cursor.close()
        
        return json.dumps({
            "success": True,
            "row_count": row_count,
            "last_insert_id": last_id,
            "message": f"Successfully inserted {row_count} row(s)."
        }, indent=2)
        
    except Exception as e:
        return f"Error inserting data: {str(e)}"

def update_data(db_type: str, db_path: str, table: str, data: str,
                where: str = None, connection_id: str = None) -> str:
    """
    Update data in a table.
    
    Args:
        db_type: Type of database ('sqlite')
        db_path: Path to SQLite file
        table: Name of the table
        data: JSON string of data to update
        where: WHERE condition (optional, updates all rows if not provided)
        connection_id: Optional connection identifier
        
    Returns:
        Update result with affected rows count
    """
    try:
        # Parse data
        try:
            data_obj = json.loads(data)
            if not isinstance(data_obj, dict):
                return f"Error: Data should be a JSON object, got {type(data_obj).__name__}"
        except json.JSONDecodeError as e:
            return f"Error parsing data JSON: {str(e)}"
        
        # Get connection
        conn = _get_connection(db_type, db_path, connection_id=connection_id)
        
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        if not cursor.fetchone():
            cursor.close()
            return f"Error: Table '{table}' does not exist."
        
        # Build SET clause
        set_clause = ", ".join([f"{key} = ?" for key in data_obj.keys()])
        values = list(data_obj.values())
        
        # Build SQL
        sql = f"UPDATE {table} SET {set_clause}"
        if where:
            sql += f" WHERE {where}"
        
        # Execute update
        cursor.execute(sql, tuple(values))
        affected_rows = cursor.rowcount
        
        conn.commit()
        cursor.close()
        
        return json.dumps({
            "success": True,
            "affected_rows": affected_rows,
            "message": f"Successfully updated {affected_rows} row(s)."
        }, indent=2)
        
    except Exception as e:
        return f"Error updating data: {str(e)}"

def delete_data(db_type: str, db_path: str, table: str, where: str = None,
                connection_id: str = None) -> str:
    """
    Delete data from a table.
    
    Args:
        db_type: Type of database ('sqlite')
        db_path: Path to SQLite file
        table: Name of the table
        where: WHERE condition (optional, deletes all rows if not provided)
        connection_id: Optional connection identifier
        
    Returns:
        Delete result with affected rows count
    """
    try:
        # Get connection
        conn = _get_connection(db_type, db_path, connection_id=connection_id)
        
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        if not cursor.fetchone():
            cursor.close()
            return f"Error: Table '{table}' does not exist."
        
        # Build SQL
        sql = f"DELETE FROM {table}"
        if where:
            sql += f" WHERE {where}"
        
        # Execute delete
        cursor.execute(sql)
        affected_rows = cursor.rowcount
        
        conn.commit()
        cursor.close()
        
        return json.dumps({
            "success": True,
            "affected_rows": affected_rows,
            "message": f"Successfully deleted {affected_rows} row(s)."
        }, indent=2)
        
    except Exception as e:
        return f"Error deleting data: {str(e)}"

def select_data(db_type: str, db_path: str, table: str, columns: str = "*",
                where: str = None, order_by: str = None, limit: int = None,
                offset: int = None, connection_id: str = None) -> str:
    """
    Select data from a table.
    
    Args:
        db_type: Type of database ('sqlite')
        db_path: Path to SQLite file
        table: Name of the table
        columns: Columns to select (comma-separated or '*')
        where: WHERE condition
        order_by: ORDER BY clause
        limit: Limit number of rows
        offset: Offset for pagination
        connection_id: Optional connection identifier
        
    Returns:
        Selected data as JSON
    """
    try:
        # Get connection
        conn = _get_connection(db_type, db_path, connection_id=connection_id)
        
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        if not cursor.fetchone():
            cursor.close()
            return f"Error: Table '{table}' does not exist."
        
        # Build SQL
        sql = f"SELECT {columns} FROM {table}"
        
        if where:
            sql += f" WHERE {where}"
        
        if order_by:
            sql += f" ORDER BY {order_by}"
        
        if limit is not None:
            sql += f" LIMIT {limit}"
            if offset is not None:
                sql += f" OFFSET {offset}"
        
        # Execute query
        cursor.execute(sql)
        rows = cursor.fetchall()
        
        # Convert rows to list of dictionaries
        result = []
        for row in rows:
            if isinstance(row, sqlite3.Row):
                result.append(dict(row))
            else:
                # Convert tuple to dict with column names
                columns_list = [desc[0] for desc in cursor.description] if cursor.description else []
                row_dict = {}
                for i, value in enumerate(row):
                    col_name = columns_list[i] if i < len(columns_list) else f"column_{i}"
                    row_dict[col_name] = value
                result.append(row_dict)
        
        cursor.close()
        
        return json.dumps({
            "success": True,
            "table": table,
            "row_count": len(result),
            "data": result
        }, indent=2)
        
    except Exception as e:
        return f"Error selecting data: {str(e)}"

def begin_transaction(db_type: str, db_path: str, isolation_level: str = None,
                      connection_id: str = None) -> str:
    """
    Begin a database transaction.
    
    Args:
        db_type: Type of database ('sqlite')
        db_path: Path to SQLite file
        isolation_level: Transaction isolation level
        connection_id: Optional connection identifier
        
    Returns:
        Success or error message
    """
    try:
        # Get connection
        conn = _get_connection(db_type, db_path, connection_id=connection_id)
        
        # SQLite doesn't support explicit BEGIN with isolation levels in the same way
        # We'll just note that we're starting a transaction context
        return "Transaction context started. Use commit_transaction or rollback_transaction to complete."
        
    except Exception as e:
        return f"Error beginning transaction: {str(e)}"

def commit_transaction(db_type: str, db_path: str, connection_id: str = None) -> str:
    """
    Commit the current transaction.
    
    Args:
        db_type: Type of database ('sqlite')
        db_path: Path to SQLite file
        connection_id: Optional connection identifier
        
    Returns:
        Success or error message
    """
    try:
        # Get connection
        conn = _get_connection(db_type, db_path, connection_id=connection_id)
        
        conn.commit()
        return "Transaction committed successfully."
        
    except Exception as e:
        return f"Error committing transaction: {str(e)}"

def rollback_transaction(db_type: str, db_path: str, connection_id: str = None) -> str:
    """
    Rollback the current transaction.
    
    Args:
        db_type: Type of database ('sqlite')
        db_path: Path to SQLite file
        connection_id: Optional connection identifier
        
    Returns:
        Success or error message
    """
    try:
        # Get connection
        conn = _get_connection(db_type, db_path, connection_id=connection_id)
        
        conn.rollback()
        return "Transaction rolled back successfully."
        
    except Exception as e:
        return f"Error rolling back transaction: {str(e)}"

def export_to_json(db_type: str, db_path: str, table: str, query: str = None,
                   limit: int = None, connection_id: str = None) -> str:
    """
    Export table data to JSON format.
    
    Args:
        db_type: Type of database ('sqlite')
        db_path: Path to SQLite file
        table: Name of the table
        query: Custom SQL query (optional, uses SELECT * FROM table if not provided)
        limit: Limit number of rows to export
        connection_id: Optional connection identifier
        
    Returns:
        Exported data as JSON
    """
    try:
        # Get connection
        conn = _get_connection(db_type, db_path, connection_id=connection_id)
        
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        if not cursor.fetchone():
            cursor.close()
            return f"Error: Table '{table}' does not exist."
        
        # Build query
        if query:
            sql = query
        else:
            sql = f"SELECT * FROM {table}"
            if limit is not None:
                sql += f" LIMIT {limit}"
        
        # Execute query
        cursor.execute(sql)
        rows = cursor.fetchall()
        
        # Convert rows to list of dictionaries
        result = []
        for row in rows:
            if isinstance(row, sqlite3.Row):
                result.append(dict(row))
            else:
                # Convert tuple to dict with column names
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                row_dict = {}
                for i, value in enumerate(row):
                    col_name = columns[i] if i < len(columns) else f"column_{i}"
                    row_dict[col_name] = value
                result.append(row_dict)
        
        cursor.close()
        
        # Return as pretty JSON
        return json.dumps({
            "success": True,
            "table": table,
            "row_count": len(result),
            "exported_data": result
        }, indent=2)
        
    except Exception as e:
        return f"Error exporting data: {str(e)}"

def import_from_json(db_type: str, db_path: str, table: str, data: str,
                     batch_size: int = 100, connection_id: str = None) -> str:
    """
    Import data from JSON into a table.
    
    Args:
        db_type: Type of database ('sqlite')
        db_path: Path to SQLite file
        table: Name of the table
        data: JSON string of data to import
        batch_size: Batch size for bulk insert
        connection_id: Optional connection identifier
        
    Returns:
        Import result with count of imported rows
    """
    try:
        # Parse data
        try:
            data_obj = json.loads(data)
        except json.JSONDecodeError as e:
            return f"Error parsing data JSON: {str(e)}"
        
        if not isinstance(data_obj, list):
            return "Error: Data should be a JSON array of objects."
        
        # Get connection
        conn = _get_connection(db_type, db_path, connection_id=connection_id)
        
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        if not cursor.fetchone():
            cursor.close()
            return f"Error: Table '{table}' does not exist."
        
        # Get column names from first record
        if not data_obj:
            cursor.close()
            return "Error: Empty data array."
        
        first_record = data_obj[0]
        if not isinstance(first_record, dict):
            cursor.close()
            return "Error: Data array should contain objects/dictionaries."
        
        columns = list(first_record.keys())
        if not columns:
            cursor.close()
            return "Error: Empty record found in data."
        
        # Prepare insert statement
        placeholders = ", ".join(["?"] * len(columns))
        sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
        
        # Insert data in batches
        imported_count = 0
        batch = []
        
        for i, record in enumerate(data_obj):
            if not isinstance(record, dict):
                continue
            
            # Ensure record has all columns (fill missing with None)
            values = [record.get(col) for col in columns]
            batch.append(values)
            
            # Execute batch when batch_size is reached
            if len(batch) >= batch_size:
                cursor.executemany(sql, batch)
                imported_count += len(batch)
                batch = []
        
        # Insert remaining records
        if batch:
            cursor.executemany(sql, batch)
            imported_count += len(batch)
        
        conn.commit()
        cursor.close()
        
        return json.dumps({
            "success": True,
            "imported_rows": imported_count,
            "message": f"Successfully imported {imported_count} row(s) into '{table}'."
        }, indent=2)
        
    except Exception as e:
        return f"Error importing data: {str(e)}"

def execute_sql_script(db_type: str, db_path: str, query: str,
                       connection_id: str = None) -> str:
    """
    Execute multiple SQL statements from a script.
    
    Args:
        db_type: Type of database ('sqlite')
        db_path: Path to SQLite file
        query: SQL script content
        connection_id: Optional connection identifier
        
    Returns:
        Execution results
    """
    try:
        # Get connection
        conn = _get_connection(db_type, db_path, connection_id=connection_id)
        
        cursor = conn.cursor()
        
        # Split script into individual statements
        statements = []
        current_statement = ""
        
        for line in query.split('\n'):
            line = line.strip()
            if not line or line.startswith('--'):
                continue
            
            current_statement += line + " "
            
            # Check if statement is complete (ends with semicolon)
            if current_statement.strip().endswith(';'):
                statements.append(current_statement.strip())
                current_statement = ""
        
        # Add last statement if not empty
        if current_statement.strip():
            statements.append(current_statement.strip())
        
        # Execute statements
        results = []
        for i, stmt in enumerate(statements):
            try:
                cursor.execute(stmt)
                
                # Determine statement type
                stmt_upper = stmt.upper().strip()
                if stmt_upper.startswith("SELECT"):
                    rows = cursor.fetchall()
                    results.append({
                        "statement": i + 1,
                        "type": "SELECT",
                        "row_count": len(rows),
                        "success": True
                    })
                else:
                    results.append({
                        "statement": i + 1,
                        "type": "NON-SELECT",
                        "affected_rows": cursor.rowcount,
                        "success": True
                    })
            except Exception as e:
                results.append({
                    "statement": i + 1,
                    "type": "ERROR",
                    "error": str(e),
                    "success": False
                })
        
        conn.commit()
        cursor.close()
        
        return json.dumps({
            "success": True,
            "statements_executed": len(statements),
            "results": results
        }, indent=2)
        
    except Exception as e:
        return f"Error executing SQL script: {str(e)}"

def backup_database(db_type: str, db_path: str, backup_path: str = None,
                    connection_id: str = None) -> str:
    """
    Create a backup of the database.
    
    Args:
        db_type: Type of database ('sqlite')
        db_path: Path to SQLite file
        backup_path: Path for backup file (default: original path with .backup timestamp)
        connection_id: Optional connection identifier
        
    Returns:
        Backup result with file path
    """
    try:
        if db_type.lower() != 'sqlite':
            return f"Error: Backup only supported for SQLite databases, not '{db_type}'."
        
        if not os.path.exists(db_path):
            return f"Error: Database file not found: {db_path}"
        
        # Generate backup path if not provided
        if not backup_path:
            import time
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            base, ext = os.path.splitext(db_path)
            backup_path = f"{base}_{timestamp}{ext}"
        
        # Ensure backup directory exists
        backup_dir = os.path.dirname(backup_path)
        if backup_dir and not os.path.exists(backup_dir):
            os.makedirs(backup_dir, exist_ok=True)
        
        # Get connection and create backup
        conn = _get_connection(db_type, db_path, connection_id=connection_id)
        
        # SQLite backup using built-in backup method
        backup_conn = sqlite3.connect(backup_path)
        conn.backup(backup_conn)
        backup_conn.close()
        
        # Get file size
        file_size = os.path.getsize(backup_path)
        
        return json.dumps({
            "success": True,
            "original_db": db_path,
            "backup_path": backup_path,
            "file_size": file_size,
            "message": f"Database backup created successfully: {backup_path}"
        }, indent=2)
        
    except Exception as e:
        return f"Error creating database backup: {str(e)}"

# ============================================================================
# TOOL CALL MAP
# ============================================================================

TOOL_CALL_MAP = {
    "connect_database": connect_database,
    "disconnect_database": disconnect_database,
    "execute_query": execute_query,
    "execute_non_query": execute_non_query,
    "create_table": create_table,
    "drop_table": drop_table,
    "list_tables": list_tables,
    "describe_table": describe_table,
    "insert_data": insert_data,
    "update_data": update_data,
    "delete_data": delete_data,
    "select_data": select_data,
    "begin_transaction": begin_transaction,
    "commit_transaction": commit_transaction,
    "rollback_transaction": rollback_transaction,
    "export_to_json": export_to_json,
    "import_from_json": import_from_json,
    "execute_sql_script": execute_sql_script,
    "backup_database": backup_database
}