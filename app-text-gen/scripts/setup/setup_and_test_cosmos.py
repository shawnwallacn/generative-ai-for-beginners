#!/usr/bin/env python3
"""
Quick setup script to test Cosmos DB connection
"""

import os
from pathlib import Path

# Set credentials directly for testing
# Load from environment variables - DO NOT hardcode credentials here
credentials = {
    "COSMOS_DB_ENDPOINT": os.environ.get("COSMOS_DB_ENDPOINT", ""),
    "COSMOS_DB_KEY": os.environ.get("COSMOS_DB_KEY", ""),
    "COSMOS_DB_CONNECTION_STRING": os.environ.get("COSMOS_DB_CONNECTION_STRING", ""),
    "COSMOS_DB_DATABASE_NAME": os.environ.get("COSMOS_DB_DATABASE_NAME", "genai-kb"),
    "COSMOS_DB_CONTAINER_NAME": os.environ.get("COSMOS_DB_CONTAINER_NAME", "documents"),
}

def test_cosmos():
    """Test Cosmos DB connection"""
    
    print("\n" + "="*70)
    print("COSMOS DB CONNECTION TEST")
    print("="*70)
    
    # Set env vars for this test
    for key, value in credentials.items():
        os.environ[key] = value
    
    try:
        from azure.cosmos import CosmosClient
        
        print(f"\n[*] Testing connection to Cosmos DB...")
        
        client = CosmosClient(
            credentials["COSMOS_DB_ENDPOINT"],
            credentials["COSMOS_DB_KEY"]
        )
        
        # Get database
        db_client = client.get_database_client(credentials["COSMOS_DB_DATABASE_NAME"])
        
        # Get container
        container_client = db_client.get_container_client(credentials["COSMOS_DB_CONTAINER_NAME"])
        
        # Test with a simple query
        results = list(container_client.query_items(
            query="SELECT TOP 1 * FROM c",
            enable_cross_partition_query=True,
            max_item_count=1
        ))
        
        print(f"    [OK] Successfully connected to Cosmos DB!")
        print(f"    Endpoint: {credentials['COSMOS_DB_ENDPOINT']}")
        print(f"    Database: {credentials['COSMOS_DB_DATABASE_NAME']}")
        print(f"    Container: {credentials['COSMOS_DB_CONTAINER_NAME']}")
        print(f"\n[OK] COSMOS DB READY FOR USE!\n")
        
        # Now add to .env file
        print(f"{'='*70}")
        print("Adding credentials to .env file")
        print(f"{'='*70}")
        
        env_file = Path(__file__).parent / ".env"
        
        # Read existing .env
        existing = ""
        if env_file.exists():
            with open(env_file, "r") as f:
                existing = f.read()
        
        # Check if already has Cosmos config
        if "COSMOS_DB_ENDPOINT" in existing:
            print("\n[*] Cosmos DB configuration already in .env")
            return 0
        
        # Add credentials
        cosmos_config = "\n# === Azure Cosmos DB Configuration ===\n"
        cosmos_config += f"COSMOS_DB_ENDPOINT={credentials['COSMOS_DB_ENDPOINT']}\n"
        cosmos_config += f"COSMOS_DB_KEY={credentials['COSMOS_DB_KEY']}\n"
        cosmos_config += f"COSMOS_DB_CONNECTION_STRING={credentials['COSMOS_DB_CONNECTION_STRING']}\n"
        cosmos_config += f"COSMOS_DB_DATABASE_NAME={credentials['COSMOS_DB_DATABASE_NAME']}\n"
        cosmos_config += f"COSMOS_DB_CONTAINER_NAME={credentials['COSMOS_DB_CONTAINER_NAME']}\n"
        cosmos_config += "COSMOS_DB_REGION=westus\n"
        
        with open(env_file, "a") as f:
            f.write(cosmos_config)
        
        print(f"\n[OK] Credentials added to .env file")
        print(f"    File: {env_file}")
        
        return 0
        
    except Exception as e:
        print(f"\n[ERROR] Connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(test_cosmos())

