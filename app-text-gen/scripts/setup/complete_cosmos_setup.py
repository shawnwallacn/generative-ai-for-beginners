#!/usr/bin/env python3
"""
Complete Azure Cosmos DB Setup Script

This script handles:
1. Creating database and containers
2. Retrieving connection credentials
3. Generating .env configuration
"""

import subprocess
import json
import sys
from pathlib import Path

def run_command(cmd, description, check=True):
    """Run Azure CLI command and return output"""
    print(f"\n[*] {description}...")
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            shell=True,
            check=check
        )
        if result.returncode == 0:
            print(f"    [OK] Success")
            return result.stdout.strip()
        else:
            if result.stderr:
                print(f"    [ERROR] {result.stderr}")
            return None
    except Exception as e:
        print(f"    [ERROR] {e}")
        return None

def main():
    """Main setup orchestration"""
    
    print("\n" + "="*70)
    print("AZURE COSMOS DB COMPLETE SETUP")
    print("="*70)
    
    resource_group = "genai-search"
    cosmos_name = "genai-cosmosdb"
    database_name = "genai-kb"
    container_name = "documents"
    
    config = {
        "resource_group": resource_group,
        "cosmos_name": cosmos_name,
        "database_name": database_name,
        "container_name": container_name,
    }
    
    print(f"\nConfiguration:")
    print(f"  Resource Group: {resource_group}")
    print(f"  Cosmos DB: {cosmos_name}")
    print(f"  Region: westus")
    print(f"  Database: {database_name}")
    print(f"  Container: {container_name}")
    
    # Step 1: Verify Cosmos DB account exists and is provisioned
    print(f"\n{'='*70}")
    print("STEP 1: Verify Cosmos DB Account")
    print(f"{'='*70}")
    
    status = run_command(
        f'az cosmosdb show --resource-group {resource_group} --name {cosmos_name} --query provisioningState -o tsv',
        "Checking account provisioning status"
    )
    
    if not status:
        print("\n[ERROR] Cosmos DB account not found or not provisioned")
        print("  Make sure the account creation is complete before running this script")
        return 1
    
    if status != "Succeeded":
        print(f"\n[ERROR] Account provisioning status: {status}")
        print("  Status should be 'Succeeded'")
        return 1
    
    print(f"    Status: {status}")
    
    # Step 2: Create Database
    print(f"\n{'='*70}")
    print("STEP 2: Create Database")
    print(f"{'='*70}")
    
    db_result = run_command(
        f'az cosmosdb sql database create --resource-group {resource_group} --account-name {cosmos_name} --name {database_name} --max-throughput 400',
        f"Creating database '{database_name}'",
        check=False
    )
    
    if db_result:
        print(f"    Database: {database_name}")
    
    # Step 3: Create Container
    print(f"\n{'='*70}")
    print("STEP 3: Create Container")
    print(f"{'='*70}")
    
    container_result = run_command(
        f'az cosmosdb sql container create --resource-group {resource_group} --account-name {cosmos_name} --database-name {database_name} --name {container_name} --partition-key-path /collection_id --max-throughput 400',
        f"Creating container '{container_name}'",
        check=False
    )
    
    if container_result:
        print(f"    Container: {container_name}")
        print(f"    Partition Key: /collection_id")
    
    # Step 4: Retrieve Credentials
    print(f"\n{'='*70}")
    print("STEP 4: Retrieve Credentials")
    print(f"{'='*70}")
    
    endpoint = run_command(
        f'az cosmosdb show --resource-group {resource_group} --name {cosmos_name} --query documentEndpoint -o tsv',
        "Getting endpoint"
    )
    
    key = run_command(
        f'az cosmosdb keys list --resource-group {resource_group} --name {cosmos_name} --query primaryMasterKey -o tsv',
        "Getting primary key"
    )
    
    conn_str = run_command(
        f'az cosmosdb keys list --resource-group {resource_group} --name {cosmos_name} --type connection-strings --query "connectionStrings[0].connectionString" -o tsv',
        "Getting connection string"
    )
    
    if not (endpoint and key and conn_str):
        print("\n[ERROR] Failed to retrieve credentials")
        return 1
    
    # Step 5: Display Configuration
    print(f"\n{'='*70}")
    print("STEP 5: Configuration Generated")
    print(f"{'='*70}")
    
    env_content = f"""# === Azure Cosmos DB Configuration ===
COSMOS_DB_ENDPOINT={endpoint}
COSMOS_DB_KEY={key}
COSMOS_DB_CONNECTION_STRING={conn_str}
COSMOS_DB_DATABASE_NAME={database_name}
COSMOS_DB_CONTAINER_NAME={container_name}
COSMOS_DB_REGION=westus
"""
    
    print("\n[OK] Setup Complete!")
    print("\nAdd these lines to your .env file:\n")
    print(env_content)
    
    # Save to temporary file
    temp_env = Path(__file__).parent / ".env.cosmos"
    try:
        with open(temp_env, "w") as f:
            f.write(env_content)
        print(f"\n[OK] Configuration saved to: {temp_env.name}")
        print(f"\nTo merge into your .env file:")
        print(f"  cat {temp_env.name} >> .env")
        print(f"\nOr copy the values manually to your .env file")
    except Exception as e:
        print(f"\n[WARNING] Could not save to file: {e}")
        print("  Copy the configuration above to your .env file manually")
    
    # Final summary
    print(f"\n{'='*70}")
    print("NEXT STEPS")
    print(f"{'='*70}")
    print(f"""
1. Copy the configuration to your .env file:
   - Copy the lines above
   - Paste into .env file
   - Save the file

2. Install azure-cosmos SDK:
   pip install azure-cosmos

3. Test the connection:
   python test_cosmos_connection.py

4. Continue with Phase 2 implementation:
   - Integrate with KB manager
   - Test document indexing
   - Verify dual-source search

5. Update requirements.txt if not done:
   pip install -r requirements.txt
""")
    
    print(f"{'='*70}")
    print("Status: [OK] COSMOS DB READY FOR USE")
    print(f"{'='*70}\n")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

