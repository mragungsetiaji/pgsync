import psycopg
from typing import List, Dict, Tuple, Any


class PostgresSource:
    """
    A class to handle PostgreSQL database connections and operations using psycopg3.
    """
    def __init__(
        self,
        host: str,
        port: int = 5432,
        database: str = "",
        user: str = "",
        password: str = ""
    ):
        """
        Initialize connection parameters for PostgreSQL database.
        
        Args:
            host: Database server host
            port: Database server port (default: 5432)
            database: Database name
            user: Username for authentication
            password: Password for authentication
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.conn_params = {
            "host": host,
            "port": port,
            "dbname": database,
            "user": user,
            "password": password
        }

    def check_connection(self) -> bool:
        """
        Check if the database connection is working.
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            with psycopg.connect(**self.conn_params) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    result = cur.fetchone()
                    return result[0] == 1
        except Exception as e:
            print(f"Connection check failed: {str(e)}")
            return False

    def fetch_tables(self) -> List[str]:
        """
        Fetch all tables in the current database.
        
        Returns:
            List[str]: List of table names
        """
        try:
            with psycopg.connect(**self.conn_params) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                        ORDER BY table_name
                    """)
                    tables = [table[0] for table in cur.fetchall()]
                    return tables
        except Exception as e:
            print(f"Failed to fetch tables: {str(e)}")
            return []

    def fetch_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Fetch all columns for a given table with their data types and constraints.
        
        Args:
            table_name: Name of the table
            
        Returns:
            List[Dict[str, Any]]: List of column details including name, data type, nullable status, etc.
        """
        try:
            with psycopg.connect(**self.conn_params) as conn:
                with conn.cursor() as cur:
                    query = """
                        SELECT 
                            column_name, 
                            data_type, 
                            character_maximum_length,
                            is_nullable, 
                            column_default
                        FROM 
                            information_schema.columns 
                        WHERE 
                            table_schema = 'public' AND 
                            table_name = %s
                        ORDER BY 
                            ordinal_position
                    """
                    cur.execute(query, (table_name,))
                    
                    columns = []
                    for col in cur.fetchall():
                        columns.append({
                            'name': col[0],
                            'data_type': col[1],
                            'max_length': col[2],
                            'nullable': col[3] == 'YES',
                            'default': col[4]
                        })
                    return columns
        except Exception as e:
            print(f"Failed to fetch columns for table {table_name}: {str(e)}")
            return []

    def fetch_all_tables_with_columns(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch all tables with their column details.
        
        Returns:
            Dict[str, List[Dict[str, Any]]]: Dictionary with table names as keys and lists of column details as values
        """
        result = {}
        tables = self.fetch_tables()
        for table in tables:
            columns = self.fetch_columns(table)
            result[table] = columns
        return result
    
    def fetch_schema(self) -> Dict[str, Any]:
        """
        Fetch the complete database schema including tables, columns, and constraints.
        
        Returns:
            Dict[str, Any]: Dictionary containing the database schema
        """
        try:
            schema = {
                "tables": {},
                "views": {},
                "functions": [],
                "database_info": {}
            }
            
            # Get database information
            with psycopg.connect(**self.conn_params) as conn:
                with conn.cursor() as cur:
                    # Get database version
                    cur.execute("SELECT version()")
                    version = cur.fetchone()[0]
                    schema["database_info"]["version"] = version
                    
                    # Get database name
                    schema["database_info"]["name"] = self.database
                    
                    # Get all tables with their columns
                    tables = self.fetch_tables()
                    for table_name in tables:
                        columns = self.fetch_columns(table_name)
                        
                        # Get primary key information
                        cur.execute("""
                            SELECT 
                                a.attname as column_name
                            FROM 
                                pg_index i
                                JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
                            WHERE
                                i.indrelid = %s::regclass AND
                                i.indisprimary;
                        """, (table_name,))
                        pk_columns = [row[0] for row in cur.fetchall()]
                        
                        # Get foreign key information
                        cur.execute("""
                            SELECT
                                kcu.column_name,
                                ccu.table_name AS foreign_table_name,
                                ccu.column_name AS foreign_column_name
                            FROM
                                information_schema.table_constraints AS tc
                                JOIN information_schema.key_column_usage AS kcu
                                    ON tc.constraint_name = kcu.constraint_name
                                    AND tc.table_schema = kcu.table_schema
                                JOIN information_schema.constraint_column_usage AS ccu
                                    ON ccu.constraint_name = tc.constraint_name
                                    AND ccu.table_schema = tc.table_schema
                            WHERE
                                tc.constraint_type = 'FOREIGN KEY' AND
                                tc.table_name = %s;
                        """, (table_name,))
                        foreign_keys = []
                        for fk in cur.fetchall():
                            foreign_keys.append({
                                'column': fk[0],
                                'references_table': fk[1],
                                'references_column': fk[2]
                            })
                        
                        # Get indexes
                        cur.execute("""
                            SELECT
                                i.relname as index_name,
                                a.attname as column_name,
                                ix.indisunique as is_unique
                            FROM
                                pg_class t,
                                pg_class i,
                                pg_index ix,
                                pg_attribute a
                            WHERE
                                t.oid = ix.indrelid
                                AND i.oid = ix.indexrelid
                                AND a.attrelid = t.oid
                                AND a.attnum = ANY(ix.indkey)
                                AND t.relkind = 'r'
                                AND t.relname = %s
                            ORDER BY
                                i.relname, a.attnum;
                        """, (table_name,))
                        
                        indexes = {}
                        for idx_row in cur.fetchall():
                            idx_name, col_name, is_unique = idx_row
                            if idx_name not in indexes:
                                indexes[idx_name] = {"columns": [], "unique": is_unique}
                            indexes[idx_name]["columns"].append(col_name)
                        
                        # Get row count estimate
                        cur.execute("SELECT reltuples::bigint FROM pg_class WHERE relname = %s", (table_name,))
                        row_count = cur.fetchone()
                        estimated_row_count = int(row_count[0]) if row_count and row_count[0] else 0
                        
                        # Combine all information
                        schema["tables"][table_name] = {
                            "name": table_name,
                            "columns": columns,
                            "primary_key": pk_columns,
                            "foreign_keys": foreign_keys,
                            "indexes": list(indexes.values()),
                            "estimated_row_count": estimated_row_count
                        }
                    
                    # Get views
                    cur.execute("""
                        SELECT 
                            table_name as view_name, 
                            view_definition
                        FROM 
                            information_schema.views
                        WHERE 
                            table_schema = 'public'
                    """)
                    
                    for view_row in cur.fetchall():
                        view_name, view_def = view_row
                        view_columns = self.fetch_columns(view_name)
                        schema["views"][view_name] = {
                            "name": view_name,
                            "columns": view_columns,
                            "definition": view_def
                        }
                    
                    # Get functions
                    cur.execute("""
                        SELECT 
                            p.proname as function_name,
                            pg_get_functiondef(p.oid) as function_def
                        FROM 
                            pg_proc p
                            JOIN pg_namespace n ON p.pronamespace = n.oid
                        WHERE 
                            n.nspname = 'public'
                    """)
                    
                    for func_row in cur.fetchall():
                        func_name, func_def = func_row
                        schema["functions"].append({
                            "name": func_name,
                            "definition": func_def
                        })
                    
            return schema
                    
        except Exception as e:
            print(f"Failed to fetch schema: {str(e)}")
            return {}

    def execute_query(self, query: str, params: Tuple = None) -> List[Tuple]:
        """
        Execute a SQL query and return results.
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
            
        Returns:
            List[Tuple]: Query results
        """
        try:
            with psycopg.connect(**self.conn_params) as conn:
                with conn.cursor() as cur:
                    cur.execute(query, params or ())
                    if cur.description:  # Check if query returns data
                        return cur.fetchall()
                    else:
                        conn.commit()
                        return []
        except Exception as e:
            raise e