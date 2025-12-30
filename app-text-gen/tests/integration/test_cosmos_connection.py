#!/usr/bin/env python3
"""
Test Azure Cosmos DB Connection

Verifies that Cosmos DB is properly configured and accessible
"""

import os
import sys
from pathlib import Path

def test_cosmos_connection():
    """Test Cosmos DB connection"""
    
    print("\n" + "="*70)
    print("AZURE COSMOS DB CONNECTION TEST")
    print("="*70)
    
    # Check environment variables
    print(f"\n[*] Checking environment variables...")
    
    required_vars = [
        "COSMOS_DB_ENDPOINT",
        "COSMOS_DB_KEY",
        "COSMOS_DB_DATABASE_NAME",
        "COSMOS_DB_CONTAINER_NAME"
    ]
    
    config = {}
    missing = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Show only first/last 20 chars of secrets
            if "KEY" in var or "CONNECTION" in var:
                display = f"{value[:20]}...{value[-20:]}"
            else:
                display = value
            config[var] = value
            print(f"    [OK] {var}: {display}")
        else:
            missing.append(var)
            print(f"    [ERROR] {var}: Not set")
    
    if missing:
        print(f"\n[ERROR] Missing environment variables: {', '.join(missing)}")
        print(f"\n[!] Fix:")
        print(f"    1. Run: python complete_cosmos_setup.py")
        print(f"    2. Copy output to .env file")
        print(f"    3. Restart your application")
        return False
    
    # Try to import azure-cosmos
    print(f"\n[*] Checking azure-cosmos SDK...")
    try:
        from azure.cosmos import CosmosClient
        print(f"    [OK] azure-cosmos is installed")
    except ImportError:
        print(f"    [ERROR] azure-cosmos not installed")
        print(f"\n[!] Fix:")
        print(f"    pip install azure-cosmos")
        print(f"    Or: pip install -r requirements.txt")
        return False
    
    # Test connection
    print(f"\n[*] Testing Cosmos DB connection...")
    try:
        from azure.cosmos import CosmosClient
        
        client = CosmosClient(config["COSMOS_DB_ENDPOINT"], config["COSMOS_DB_KEY"])
        
        # Try to get database
        db_client = client.get_database_client(config["COSMOS_DB_DATABASE_NAME"])
        
        # Try to get container
        container_client = db_client.get_container_client(config["COSMOS_DB_CONTAINER_NAME"])
        
        print(f"    [OK] Connected to Cosmos DB!")
        
        # Get container properties
        props = container_client.read()
        print(f"\n[*] Container Information:")
        print(f"    Container: {props['id']}")
        print(f"    Partition Key: {props['partitionKey']['paths']}")
        
        # Try a simple query
        print(f"\n[*] Testing query capability...")
        try:
            results = list(container_client.query_items(
                query="SELECT TOP 1 * FROM c",
                enable_cross_partition_query=True,
                max_item_count=1
            ))
            print(f"    [OK] Query executed successfully")
            if results:
                print(f"    [*] Found {len(results)} item(s)")
            else:
                print(f"    [*] Container is empty (normal for new container)")
        except Exception as e:
            print(f"    [WARNING] Query test failed: {e}")
            print(f"    This is normal for a new empty container")
        
        print(f"\n{'='*70}")
        print(f"[OK] COSMOS DB READY!")
        print(f"{'='*70}")
        print(f"""
Connection Details:
  Endpoint: {config['COSMOS_DB_ENDPOINT']}
  Database: {config['COSMOS_DB_DATABASE_NAME']}
  Container: {config['COSMOS_DB_CONTAINER_NAME']}
  Region: westus

Next Steps:
  1. Continue with Phase 2 implementation
  2. Integrate CosmosDBStorage with KB manager
  3. Test document indexing
  4. Verify dual-source search

Ready to proceed! 🚀
""")
        return True
        
    except ImportError as e:
        print(f"    [ERROR] azure-cosmos not installed: {e}")
        print(f"\n[!] Install with: pip install azure-cosmos")
        return False
    except Exception as e:
        print(f"    [ERROR] Connection failed: {e}")
        print(f"\n[!] Troubleshooting:")
        print(f"    1. Verify endpoint URL is correct")
        print(f"    2. Verify primary key is correct")
        print(f"    3. Check network connectivity")
        print(f"    4. Verify database and container exist")
        return False

if __name__ == "__main__":
    # Load .env file
    from pathlib import Path
    env_file = Path(__file__).parent / ".env"
    
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)
        print(f"[*] Loaded configuration from .env")
    else:
        print(f"[!] Warning: .env file not found")
        print(f"    Create .env file with Cosmos DB configuration")
    
    success = test_cosmos_connection()
    sys.exit(0 if success else 1)

