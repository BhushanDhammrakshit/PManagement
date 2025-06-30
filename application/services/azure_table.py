from azure.data.tables import TableServiceClient
from application.config import AZURE_TABLE_CONN_STR, USER_INFO_TABLE, USER_STOCKS_TABLE

service = TableServiceClient.from_connection_string(conn_str=AZURE_TABLE_CONN_STR)

user_table_client = service.get_table_client(table_name=USER_INFO_TABLE)
stocks_table_client = service.get_table_client(table_name=USER_STOCKS_TABLE)




def get_user_by_credentials(email: str, password: str):
    filter_query = f"Email eq '{email}' and Password eq '{password}'"
    users = user_table_client.query_entities(query_filter=filter_query)

    # Return the first match (if any)
    for user in users:
        return user  # user includes PartitionKey, RowKey, Email, etc.
    
    return None  # No user found



def get_user_stocks_by_row_key(row_key: str):
    return stocks_table_client.query_entities(
        query_filter=f"UserId eq '{row_key}'"
    )
