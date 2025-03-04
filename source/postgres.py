import psycopg
from typing import List, Dict, Optional, Tuple, Any


class Postgres:
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