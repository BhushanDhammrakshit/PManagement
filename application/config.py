import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

AZURE_TABLE_CONN_STR = os.getenv("AZURE_TABLE_CONN_STR")
USER_INFO_TABLE = os.getenv("USER_INFO_TABLE")
USER_STOCKS_TABLE = os.getenv("USER_STOCKS_TABLE")
