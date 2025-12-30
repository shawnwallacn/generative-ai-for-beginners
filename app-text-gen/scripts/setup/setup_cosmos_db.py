#!/usr/bin/env python3
"""
Azure Cosmos DB Setup Script for Phase 2

This script automates the creation of Azure Cosmos DB infrastructure
for the Knowledge Base vector database.
"""

import subprocess
import json
import sys
from pathlib import Path

# Configuration
RESOURCE_GROUP = "genai-search"
COSMOS_DB_NAME = "genai-cosmosdb"
DATABASE_NAME = "genai-kb"
CONTAINER_NAME = "documents"
REGION = "eastus"
THROUGHPUT = 400  # RU/s (minimum)

def run_command(cmd, description):
    """Run Azure CLI command and handle errors"""
    print(f"\n[*] {description}...")
    print(f"    Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"    [OK] Success")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"    [ERROR] {e.stderr}")
        return None
    except Exception as e:
        print(f"    [ERROR] {e}")
        return None

def main():
    """Main setup orchestration"""
    
    print("\n" + "="*70)
    print("AZURE COSMOS DB SETUP FOR PHASE 2")
    print("="*70)
    
    print(f"\nConfiguration:")
    print(f"  Resource Group: {RESOURCE_GROUP}")
    print(f"  Cosmos DB Name: {COSMOS_DB_NAME}")
    print(f"  Region: {REGION}")
    print(f"  Database: {DATABASE_NAME}")
    print(f"  Container: {CONTAINER_NAME}")
    print(f"  Throughput: {THROUGHPUT} RU/s")
    
    # Step 1: Verify current subscription
    print(f"\n{'='*70}")
    print("STEP 1: Verify Azure Subscription")
    print(f"{'='*70}")
    
    sub_output = run_command(
        ["az", "account", "show", "--query", "{Subscription: name, Account: user.name}", "-o", "json"],
        "Checking current subscription"
    )
    
    if sub_output:
        try:
            sub_info = json.loads(sub_output)
            print(f"    Subscription: {sub_info.get('Subscription')}")
            print(f"    Account: {sub_info.get('Account')}")
        except:
            pass
    else:
        print("    [WARNING] Could not verify subscription")
        return 1
    
    # Step 2: Create Cosmos DB Account
    print(f"\n{'='*70}")
    print("STEP 2: Create Cosmos DB Account")
    print(f"{'='*70}")
    
    cosmos_output = run_command(
        [
            "az", "cosmosdb", "create",
            "--resource-group", RESOURCE_GROUP,
            "--name", COSMOS_DB_NAME,
            "--kind", "GlobalDocumentDB",
            "--default-consistency-level", "Strong",
            "--locations", f"regionName={REGION} failoverPriority=0",
            "--query", "{Name: name, Endpoint: documentEndpoint, Status: provisioningState}",
            "-o", "json"
        ],
        "Creating Cosmos DB account"
    )
    
    if not cosmos_output:
        print("    [ERROR] Failed to create Cosmos DB account")
        print("    Possible issue: Account may already exist")
        
        # Try to get existing account
        print("\n    Attempting to retrieve existing account...")
        cosmos_output = run_command(
            [
                "az", "cosmosdb", "show",
                "--resource-group", RESOURCE_GROUP,
                "--name", COSMOS_DB_NAME,
                "--query", "{Name: name, Endpoint: documentEndpoint, Status: provisioningState}",
                "-o", "json"
            ],
            "Retrieving existing Cosmos DB account"
        )
    
    if cosmos_output:
        try:
            cosmos_info = json.loads(cosmos_output)
            print(f"    Name: {cosmos_info.get('Name')}")
            print(f"    Status: {cosmos_info.get('Status')}")
        except:
            pass
    
    # Step 3: Create Database
    print(f"\n{'='*70}")
    print("STEP 3: Create Database")
    print(f"{'='*70}")
    
    db_output = run_command(
        [
            "az", "cosmosdb", "sql", "database", "create",
            "--resource-group", RESOURCE_GROUP,
            "--account-name", COSMOS_DB_NAME,
            "--name", DATABASE_NAME,
            "--max-throughput", str(THROUGHPUT)
        ],
        f"Creating database '{DATABASE_NAME}'"
    )
    
    if not db_output:
        print("    [WARNING] Database creation may have failed or already exists")
    
    # Step 4: Create Container
    print(f"\n{'='*70}")
    print("STEP 4: Create Container")
    print(f"{'='*70}")
    
    container_output = run_command(
        [
            "az", "cosmosdb", "sql", "container", "create",
            "--resource-group", RESOURCE_GROUP,
            "--account-name", COSMOS_DB_NAME,
            "--database-name", DATABASE_NAME,
            "--name", CONTAINER_NAME,
            "--partition-key-path", "/collection_id",
            "--max-throughput", str(THROUGHPUT)
        ],
        f"Creating container '{CONTAINER_NAME}'"
    )
    
    if not container_output:
        print("    [WARNING] Container creation may have failed or already exists")
    
    # Step 5: Get Connection Credentials
    print(f"\n{'='*70}")
    print("STEP 5: Retrieve Connection Credentials")
    print(f"{'='*70}")
    
    # Get endpoint
    endpoint_output = run_command(
        [
            "az", "cosmosdb", "show",
            "--resource-group", RESOURCE_GROUP,
            "--name", COSMOS_DB_NAME,
            "--query", "documentEndpoint",
            "-o", "tsv"
        ],
        "Getting Cosmos DB endpoint"
    )
    
    # Get primary key
    key_output = run_command(
        [
            "az", "cosmosdb", "keys", "list",
            "--resource-group", RESOURCE_GROUP,
            "--name", COSMOS_DB_NAME,
            "--query", "primaryMasterKey",
            "-o", "tsv"
        ],
        "Getting Cosmos DB primary key"
    )
    
    # Get connection string
    conn_output = run_command(
        [
            "az", "cosmosdb", "keys", "list",
            "--resource-group", RESOURCE_GROUP,
            "--name", COSMOS_DB_NAME,
            "--type", "connection-strings",
            "--query", "connectionStrings[0].connectionString",
            "-o", "tsv"
        ],
        "Getting Cosmos DB connection string"
    )
    
    # Step 6: Display Results and .env Template
    print(f"\n{'='*70}")
    print("STEP 6: Configuration Summary")
    print(f"{'='*70}")
    
    print(f"\n[OK] Setup Complete!")
    
    if endpoint_output and key_output and conn_output:
        print(f"\nAdd these to your .env file:")
        print(f"\n# Azure Cosmos DB Configuration")
        print(f"COSMOS_DB_ENDPOINT={endpoint_output}")
        print(f"COSMOS_DB_KEY={key_output}")
        print(f"COSMOS_DB_CONNECTION_STRING={conn_output}")
        print(f"COSMOS_DB_DATABASE_NAME={DATABASE_NAME}")
        print(f"COSMOS_DB_CONTAINER_NAME={CONTAINER_NAME}")
        
        # Save to file
        env_template = f"""
# === Azure Cosmos DB Configuration ===
COSMOS_DB_ENDPOINT={endpoint_output}
COSMOS_DB_KEY={key_output}
COSMOS_DB_CONNECTION_STRING={conn_output}
COSMOS_DB_DATABASE_NAME={DATABASE_NAME}
COSMOS_DB_CONTAINER_NAME={CONTAINER_NAME}
"""
        
        env_file = Path(__file__).parent / ".env.cosmosdb"
        with open(env_file, "w") as f:
            f.write(env_template)
        print(f"\n[OK] Credentials saved to: .env.cosmosdb")
        print(f"    Copy the above values to your .env file")
    
    print(f"\n{'='*70}")
    print("Next Steps:")
    print(f"{'='*70}")
    print(f"1. Copy credentials to .env file")
    print(f"2. Run: pip install azure-cosmos")
    print(f"3. Implement CosmosDBStorage class")
    print(f"4. Integrate with KB manager")
    print(f"5. Run end-to-end tests")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

