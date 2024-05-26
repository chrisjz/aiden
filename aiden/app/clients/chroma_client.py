import os

import chromadb
from chromadb import Settings


def get_chroma_client(agent_id: str = "0"):
    """
    Initialize and return a Chroma client configured for a specific agent ID.

    Args:
        agent_id (str): The agent identifier to create a tenant-specific client.

    Returns:
        chromadb.HttpClient: A Chroma client instance for the specified agent.
    """
    host = os.environ.get("CHROMA_HOST", "localhost")
    port = int(os.environ.get("CHROMA_PORT", "8432"))
    tenant = f"agent_{agent_id}"
    database = "brain"

    # Create database and tenant if they don't exist
    admin_client = chromadb.AdminClient(
        Settings(
            chroma_api_impl="chromadb.api.fastapi.FastAPI",
            chroma_server_host=host,
            chroma_server_http_port=port,
        )
    )

    try:
        admin_client.create_tenant(tenant)
    except Exception:
        pass

    try:
        admin_client.create_database(database, tenant)
    except Exception:
        pass

    # Initialize chroma client with dynamic tenant based on agent ID
    chroma_client = chromadb.HttpClient(
        host=host, port=port, tenant=tenant, database=database, ssl=False
    )

    return chroma_client
