from dotenv import load_dotenv
from source.postgres import Postgres
import os

load_dotenv()

# Database dependency
def get_db():
    # Get database connection info from environment variables
    db = Postgres(
        host=os.getenv("PG_HOST", ""),
        port=int(os.getenv("PG_PORT", "")),
        database=os.getenv("PG_DATABASE", ""),
        user=os.getenv("PG_USER", ""),
        password=os.getenv("PG_PASSWORD", "")
    )
    return db