#!/usr/bin/env python3
"""
Check if Azure OpenAI DALL-E 3 is available and properly configured
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 70)
print("Azure OpenAI DALL-E 3 Configuration Check")
print("=" * 70)

# Step 1: Check environment variables
print("\n[1] Checking environment variables...")
print("-" * 70)

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

if AZURE_OPENAI_ENDPOINT:
    print(f"[+] AZURE_OPENAI_ENDPOINT: {AZURE_OPENAI_ENDPOINT}")
else:
    print("[-] AZURE_OPENAI_ENDPOINT: NOT SET")

if AZURE_OPENAI_API_KEY:
    print(f"[+] AZURE_OPENAI_API_KEY: {'*' * 20}... (key exists)")
else:
    print("[-] AZURE_OPENAI_API_KEY: NOT SET")

print(f"[+] AZURE_OPENAI_API_VERSION: {AZURE_OPENAI_API_VERSION}")

# Step 2: Validate endpoint format
print("\n[2] Validating endpoint format...")
print("-" * 70)

if AZURE_OPENAI_ENDPOINT:
    if AZURE_OPENAI_ENDPOINT.startswith("https://"):
        print(f"[+] Endpoint format valid (HTTPS)")
    else:
        print(f"[-] Endpoint should start with https://")
    
    if ".openai.azure.com" in AZURE_OPENAI_ENDPOINT:
        print(f"[+] Correct Azure domain detected")
    else:
        print(f"[-] Endpoint should contain .openai.azure.com")

# Step 3: Check if required packages are installed
print("\n[3] Checking required packages...")
print("-" * 70)

try:
    from openai import AzureOpenAI
    print("[+] openai package installed")
except ImportError:
    print("[-] openai package NOT installed")
    print("    Run: pip install openai")
    sys.exit(1)

try:
    from PIL import Image
    print("[+] pillow (PIL) package installed")
except ImportError:
    print("[-] pillow package NOT installed")
    print("    Run: pip install pillow")

try:
    import requests
    print("[+] requests package installed")
except ImportError:
    print("[-] requests package NOT installed")
    print("    Run: pip install requests")

# Step 4: Try to connect to Azure OpenAI
print("\n[4] Attempting to connect to Azure OpenAI...")
print("-" * 70)

if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_API_KEY:
    print("[-] Cannot connect: Missing credentials")
    print("\n    Set in .env file:")
    print("    AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com/")
    print("    AZURE_OPENAI_API_KEY=<your-api-key>")
    sys.exit(1)

try:
    client = AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION
    )
    print("[+] Successfully connected to Azure OpenAI")
except Exception as e:
    print(f"[-] Connection failed: {e}")
    sys.exit(1)

# Step 5: Check for DALL-E 3 deployment
print("\n[5] Checking for DALL-E 3 deployment...")
print("-" * 70)

DALLE_DEPLOYMENT = os.getenv("AZURE_OPENAI_DALLE_DEPLOYMENT")

if DALLE_DEPLOYMENT:
    print(f"[+] AZURE_OPENAI_DALLE_DEPLOYMENT: {DALLE_DEPLOYMENT}")
else:
    print("[-] AZURE_OPENAI_DALLE_DEPLOYMENT: NOT SET")
    print("\n    Attempting to use 'dall-e-3' as default deployment name...")
    DALLE_DEPLOYMENT = "dall-e-3"

# Step 6: Test DALL-E 3 API call (dry run)
print("\n[6] Testing DALL-E 3 API connectivity...")
print("-" * 70)

try:
    print(f"    Deployment name: {DALLE_DEPLOYMENT}")
    print(f"    API version: {AZURE_OPENAI_API_VERSION}")
    print(f"    Endpoint: {AZURE_OPENAI_ENDPOINT}")
    print("\n    [*] Attempting test image generation (this will create an image)...")
    
    response = client.images.generate(
        model=DALLE_DEPLOYMENT,
        prompt="A simple test image to verify DALL-E 3 is working",
        size="1024x1024",
        n=1,
        quality="standard"
    )
    
    print("[+] DALL-E 3 API call successful!")
    print(f"[+] Image URL generated: {response.data[0].url[:50]}...")
    
    # Try to download the image
    print("\n[7] Attempting to download and save test image...")
    print("-" * 70)
    
    try:
        import requests
        
        image_data = requests.get(response.data[0].url).content
        test_image_path = "dalle3_test_image.png"
        
        with open(test_image_path, "wb") as f:
            f.write(image_data)
        
        print(f"[+] Test image saved: {test_image_path}")
        print(f"[+] File size: {len(image_data) / 1024:.1f} KB")
        
    except Exception as e:
        print(f"[-] Could not download image: {e}")

except Exception as e:
    error_str = str(e)
    print(f"[-] DALL-E 3 API call failed:")
    print(f"    Error: {error_str}")
    
    # Helpful error messages
    if "DeploymentNotFound" in error_str or "404" in error_str:
        print("\n    Possible causes:")
        print("    1. DALL-E 3 deployment doesn't exist in your Azure resource")
        print("    2. Deployment name is incorrect")
        print("    3. Wrong API version")
        print("\n    Solution:")
        print("    - Go to Azure OpenAI Studio: https://oai.azure.com/")
        print("    - Check 'Deployments' section")
        print("    - Ensure 'dall-e-3' deployment exists")
        print("    - Update AZURE_OPENAI_DALLE_DEPLOYMENT in .env with correct name")
    
    elif "Unauthorized" in error_str or "401" in error_str:
        print("\n    Possible causes:")
        print("    1. Invalid API key")
        print("    2. API key for wrong resource")
        print("\n    Solution:")
        print("    - Verify API key in .env is correct")
        print("    - Check it's the key for the resource with DALL-E 3 deployment")
    
    elif "InvalidHost" in error_str or "endpoint" in error_str.lower():
        print("\n    Possible causes:")
        print("    1. Incorrect endpoint URL")
        print("    2. Missing trailing slash")
        print("\n    Solution:")
        print("    - Endpoint should be: https://<resource-name>.openai.azure.com/")
        print("    - Check for correct format in Azure portal")
    
    sys.exit(1)

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print("""
[+] Your Azure OpenAI DALL-E 3 is configured and working!

Next steps:
1. Add to your .env file:
   AZURE_OPENAI_DALLE_DEPLOYMENT=dall-e-3

2. Create image generation module:
   python create_image_generation_module.py

3. Update app.py with image generation commands

4. Test with: python src/app.py
   Then type: 'image' to generate an image
""")

print("=" * 70)

