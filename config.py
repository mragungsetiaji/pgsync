from dotenv import load_dotenv
import os

load_dotenv()

PG_HOST=os.getenv("PG_HOST", "")
PG_PORT=int(os.getenv("PG_PORT", ""))
PG_DATABASE=os.getenv("PG_DATABASE", "")
PG_USER=os.getenv("PG_USER", "")
PG_PASSWORD=os.getenv("PG_PASSWORD", "")

REDIS_HOST=os.getenv("REDIS_HOST", "")
REDIS_PORT=int(os.getenv("REDIS_PORT", ""))
REDIS_DB=int(os.getenv("REDIS_DB", ""))
REDIS_PASSWORD=os.getenv("REDIS_PASSWORD", "")