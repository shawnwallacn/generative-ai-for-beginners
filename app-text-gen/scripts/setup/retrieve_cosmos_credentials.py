#!/usr/bin/env python3
"""
Retrieve Azure Cosmos DB credentials and save to .env configuration
Run this after Cosmos DB account is provisioned
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run Azure CLI command"""
    print(f"\n[*] {description}...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True, check=True)
        output = result.stdout.strip()
        if output:
            print(f"    [OK] Retrieved")
        return output
    except subprocess.CalledProcessError as e:
        print(f"    [ERROR] {e.stderr}")
        return None

def main():
    """Main credential retrieval"""
    
    print("\n" + "="*70)
    print("AZURE COSMOS DB CREDENTIAL RETRIEVAL")
    print("="*70)
    
    resource_group = "genai-search"
    cosmos_name = "genai-cosmosdb"
    
    print(f"\nConfiguration:")
    print(f"  Resource Group: {resource_group}")
    print(f"  Cosmos DB Name: {cosmos_name}")
    
    # Get endpoint
    print(f"\n{'='*70}")
    print("Retrieving Credentials")
    print(f"{'='*70}")
    
    endpoint = run_command(
        f'az cosmosdb show --resource-group {resource_group} --name {cosmos_name} --query documentEndpoint -o tsv',
        "Getting endpoint"
    )
    
    # Get primary key
    key = run_command(
        f'az cosmosdb keys list --resource-group {resource_group} --name {cosmos_name} --query primaryMasterKey -o tsv',
        "Getting primary key"
    )
    
    # Get connection string
    conn_str = run_command(
        f'az cosmosdb keys list --resource-group {resource_group} --name {cosmos_name} --type connection-strings --query "connectionStrings[0].connectionString" -o tsv',
        "Getting connection string"
    )
    
    if not (endpoint and key and conn_str):
        print("\n[ERROR] Failed to retrieve all credentials")
        print("  Possible causes:")
        print("    - Cosmos DB not yet provisioned")
        print("    - Check resource group and name")
        print("    - Verify Azure CLI authentication")
        return 1
    
    # Create .env content
    print(f"\n{'='*70}")
    print("Generated Configuration")
    print(f"{'='*70}")
    
    env_content = f"""
# === Azure Cosmos DB Configuration ===
COSMOS_DB_ENDPOINT={endpoint}
COSMOS_DB_KEY={key}
COSMOS_DB_CONNECTION_STRING={conn_str}
COSMOS_DB_DATABASE_NAME=genai-kb
COSMOS_DB_CONTAINER_NAME=documents
"""
    
    print("\nAdd these lines to your .env file:")
    print(env_content)
    
    # Save to temporary file
    env_file = Path(__file__).parent / ".env.cosmosdb.tmp"
    with open(env_file, "w") as f:
        f.write(env_content)
    
    print(f"[OK] Configuration saved to: {env_file.name}")
    print(f"\nNext steps:")
    print(f"  1. Copy the above values to your .env file")
    print(f"  2. Or run: cat {env_file.name} >> .env")
    print(f"  3. Then: pip install azure-cosmos")
    print(f"  4. Ready to integrate with KB manager!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

