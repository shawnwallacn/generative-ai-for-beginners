"""
Image Generation module for DALL-E 3
Enables generating, saving, and managing AI-generated images
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from openai import AzureOpenAI


IMAGES_DIR = "generated_images"
IMAGE_METADATA_FILE = "image_metadata.json"
IMAGE_PROMPTS_FILE = "image_prompts.json"


class ImageGenerator:
    """Manages image generation with DALL-E 3"""
    
    def __init__(self):
        """Initialize image generator with Azure OpenAI client"""
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment = os.getenv("AZURE_OPENAI_DALLE_DEPLOYMENT", "dall-e-3")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        
        if not self.api_key or not self.endpoint:
            raise ValueError(
                "Azure OpenAI credentials not found. "
                "Please set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT in .env"
            )
        
        self.client = AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.endpoint
        )
        
        self._ensure_directories()
        self.metadata = self._load_metadata()
        self.prompts = self._load_prompts()
    
    def _ensure_directories(self):
        """Create necessary directories"""
        if not os.path.exists(IMAGES_DIR):
            os.makedirs(IMAGES_DIR)
    
    def _get_metadata_path(self) -> str:
        """Get path to metadata file"""
        return os.path.join(IMAGES_DIR, IMAGE_METADATA_FILE)
    
    def _get_prompts_path(self) -> str:
        """Get path to prompts file"""
        return os.path.join(IMAGES_DIR, IMAGE_PROMPTS_FILE)
    
    def _load_metadata(self) -> Dict:
        """Load image metadata"""
        path = self._get_metadata_path()
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading metadata: {e}")
                return {"images": []}
        return {"images": []}
    
    def _save_metadata(self):
        """Save image metadata"""
        try:
            with open(self._get_metadata_path(), 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            print(f"Error saving metadata: {e}")
    
    def _load_prompts(self) -> Dict:
        """Load saved prompts"""
        path = self._get_prompts_path()
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading prompts: {e}")
                return {"prompts": []}
        return {"prompts": []}
    
    def _save_prompts(self):
        """Save prompts"""
        try:
            with open(self._get_prompts_path(), 'w') as f:
                json.dump(self.prompts, f, indent=2)
        except Exception as e:
            print(f"Error saving prompts: {e}")
    
    def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
        style: str = "vivid",
        save_metadata: bool = True
    ) -> Tuple[Optional[str], Optional[Dict]]:
        """
        Generate an image with DALL-E 3
        
        Args:
            prompt: Text description of the image
            size: Image size (1024x1024, 1024x1792, 1792x1024)
            quality: 'standard' or 'hd' (hd costs more)
            style: 'vivid' or 'natural'
            save_metadata: Whether to save metadata
        
        Returns:
            Tuple of (image_path, metadata_dict)
        """
        try:
            print(f"\nGenerating image with prompt: {prompt}")
            print(f"Size: {size} | Quality: {quality} | Style: {style}")
            print("[*] Calling DALL-E 3 API...")
            
            # Call DALL-E 3 API
            response = self.client.images.generate(
                model=self.deployment,
                prompt=prompt,
                size=size,
                n=1,
                quality=quality,
                style=style
            )
            
            if not response.data:
                print("[-] No image generated")
                return None, None
            
            image_url = response.data[0].url
            print(f"[+] Image generated successfully")
            print(f"[+] Image URL: {image_url[:60]}...")
            
            # Download image
            print("[*] Downloading image...")
            image_data = requests.get(image_url).content
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"image_{timestamp}.png"
            image_path = os.path.join(IMAGES_DIR, filename)
            
            # Save image
            with open(image_path, "wb") as f:
                f.write(image_data)
            
            file_size_kb = len(image_data) / 1024
            print(f"[+] Image saved: {image_path}")
            print(f"[+] File size: {file_size_kb:.1f} KB")
            
            # Create metadata
            metadata = {
                "id": filename.replace(".png", ""),
                "filename": filename,
                "prompt": prompt,
                "size": size,
                "quality": quality,
                "style": style,
                "url": image_url,
                "generated_at": datetime.now().isoformat(),
                "file_size_kb": file_size_kb
            }
            
            if save_metadata:
                self.metadata["images"].append(metadata)
                self._save_metadata()
            
            return image_path, metadata
            
        except Exception as e:
            print(f"[-] Error generating image: {e}")
            return None, None
    
    def generate_with_metaprompt(
        self,
        user_prompt: str,
        metaprompt: str,
        size: str = "1024x1024",
        quality: str = "standard"
    ) -> Tuple[Optional[str], Optional[Dict]]:
        """
        Generate image with a metaprompt for safety/style control
        
        Args:
            user_prompt: User's image description
            metaprompt: System prompt for style/safety control
            size: Image size
            quality: standard or hd
        
        Returns:
            Tuple of (image_path, metadata_dict)
        """
        # Combine prompts
        combined_prompt = f"{metaprompt}\n\n{user_prompt}"
        
        return self.generate_image(combined_prompt, size=size, quality=quality)
    
    def save_prompt(self, name: str, prompt: str, description: str = "") -> bool:
        """Save a prompt template for reuse"""
        try:
            prompt_entry = {
                "name": name,
                "prompt": prompt,
                "description": description,
                "saved_at": datetime.now().isoformat()
            }
            
            self.prompts["prompts"].append(prompt_entry)
            self._save_prompts()
            print(f"[+] Prompt '{name}' saved")
            return True
        except Exception as e:
            print(f"[-] Error saving prompt: {e}")
            return False
    
    def list_prompts(self) -> List[Dict]:
        """List all saved prompts"""
        return self.prompts.get("prompts", [])
    
    def get_prompt(self, name: str) -> Optional[str]:
        """Get a saved prompt by name"""
        for p in self.prompts.get("prompts", []):
            if p["name"].lower() == name.lower():
                return p["prompt"]
        return None
    
    def list_generated_images(self) -> List[Dict]:
        """List all generated images"""
        return self.metadata.get("images", [])
    
    def get_image_stats(self) -> Dict:
        """Get image generation statistics"""
        images = self.metadata.get("images", [])
        
        if not images:
            return {
                "total_images": 0,
                "total_size_mb": 0,
                "average_size_kb": 0
            }
        
        total_size_kb = sum(img.get("file_size_kb", 0) for img in images)
        
        return {
            "total_images": len(images),
            "total_size_mb": total_size_kb / 1024,
            "average_size_kb": total_size_kb / len(images),
            "latest_image": images[-1] if images else None
        }


def get_safety_metaprompt() -> str:
    """Get a metaprompt for safe, family-friendly images"""
    return """You are an assistant designer that creates images for all ages.

The image needs to be safe for work and appropriate for children.

The image needs to be in color.

Do not generate any images containing:
- violence, blood, gore
- nudity or sexual content
- adult themes or language
- weapons or dangerous objects
- dark or disturbing content

Focus on: creativity, positivity, educational value"""


def get_artistic_metaprompt() -> str:
    """Get a metaprompt for artistic style"""
    return """You are an artistic designer creating visually stunning images.

Use artistic techniques and styles such as:
- Oil painting style
- Digital art
- Watercolor
- Contemporary art
- Professional photography lighting

Make the image visually rich, detailed, and professionally composed."""


def interactive_image_generator(image_gen: ImageGenerator):
    """Interactive menu for image generation"""
    while True:
        print("\n" + "="*60)
        print("Image Generation with DALL-E 3")
        print("="*60)
        
        print("\nOptions:")
        print("1. Generate image from prompt")
        print("2. Generate with safety metaprompt")
        print("3. Generate with artistic metaprompt")
        print("4. Use saved prompt")
        print("5. Save prompt template")
        print("6. List saved prompts")
        print("7. View generated images")
        print("8. View statistics")
        print("0. Back to main menu")
        
        choice = input("\nSelect option (0-8): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            prompt = input("Enter image prompt: ").strip()
            if prompt:
                size = input("Size (1024x1024/1024x1792/1792x1024) [default: 1024x1024]: ").strip() or "1024x1024"
                quality = input("Quality (standard/hd) [default: standard]: ").strip() or "standard"
                image_gen.generate_image(prompt, size=size, quality=quality)
        
        elif choice == "2":
            prompt = input("Enter image prompt: ").strip()
            if prompt:
                metaprompt = get_safety_metaprompt()
                image_gen.generate_with_metaprompt(prompt, metaprompt)
        
        elif choice == "3":
            prompt = input("Enter image prompt: ").strip()
            if prompt:
                metaprompt = get_artistic_metaprompt()
                image_gen.generate_with_metaprompt(prompt, metaprompt)
        
        elif choice == "4":
            prompts = image_gen.list_prompts()
            if not prompts:
                print("No saved prompts found")
                continue
            
            print("\nSaved prompts:")
            for i, p in enumerate(prompts, 1):
                print(f"  {i}. {p['name']}: {p['description']}")
            
            try:
                p_choice = int(input("Select prompt (number): ")) - 1
                if 0 <= p_choice < len(prompts):
                    prompt_text = prompts[p_choice]["prompt"]
                    image_gen.generate_image(prompt_text)
            except ValueError:
                print("Invalid selection")
        
        elif choice == "5":
            name = input("Prompt name: ").strip()
            prompt = input("Prompt text: ").strip()
            description = input("Description (optional): ").strip()
            if name and prompt:
                image_gen.save_prompt(name, prompt, description)
        
        elif choice == "6":
            prompts = image_gen.list_prompts()
            if not prompts:
                print("No saved prompts")
            else:
                print("\nSaved prompts:")
                for p in prompts:
                    print(f"\n  Name: {p['name']}")
                    print(f"  Description: {p.get('description', 'N/A')}")
                    print(f"  Prompt: {p['prompt'][:100]}...")
        
        elif choice == "7":
            images = image_gen.list_generated_images()
            if not images:
                print("No generated images")
            else:
                print(f"\nGenerated images ({len(images)} total):")
                for img in images[-5:]:  # Show last 5
                    print(f"\n  File: {img['filename']}")
                    print(f"  Prompt: {img['prompt'][:80]}...")
                    print(f"  Size: {img['file_size_kb']:.1f} KB")
                    print(f"  Generated: {img['generated_at']}")
        
        elif choice == "8":
            stats = image_gen.get_image_stats()
            print("\nImage Generation Statistics:")
            print(f"  Total images generated: {stats['total_images']}")
            print(f"  Total size: {stats['total_size_mb']:.1f} MB")
            if stats['total_images'] > 0:
                print(f"  Average size: {stats['average_size_kb']:.1f} KB")

