from azure.data.tables import TableServiceClient
from application.config import AZURE_TABLE_CONN_STR, USER_INFO_TABLE, USER_STOCKS_TABLE

service = TableServiceClient.from_connection_string(conn_str=AZURE_TABLE_CONN_STR)

user_table_client = service.get_table_client(table_name=USER_INFO_TABLE)
stocks_table_client = service.get_table_client(table_name=USER_STOCKS_TABLE)


def get_user_by_row_key(row_key: str):
    return user_table_client.get_entity(partition_key="PartitionKey", row_key=row_key)


def get_user_stocks_by_row_key(row_key: str):
    return stocks_table_client.query_entities(
        query_filter=f"RowKey eq '{row_key}'"
    )
