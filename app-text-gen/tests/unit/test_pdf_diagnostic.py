#!/usr/bin/env python3
"""
PDF Parsing Diagnostic Script

Tests PDF parsing with detailed debugging information
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from kb_manager import DocumentParser

def test_pdf_parsing(pdf_path):
    """Test PDF parsing with detailed diagnostics"""
    
    pdf_file = Path(pdf_path)
    
    if not pdf_file.exists():
        print(f"[ERROR] File not found: {pdf_path}")
        return False
    
    print("\n" + "="*70)
    print("PDF PARSING DIAGNOSTIC")
    print("="*70)
    
    print(f"\nFile: {pdf_file.name}")
    print(f"Size: {pdf_file.stat().st_size / (1024*1024):.2f} MB")
    print(f"Path: {pdf_file.absolute()}")
    
    # Try parsing with pdfplumber directly
    print("\n" + "-"*70)
    print("Attempting to parse with pdfplumber...")
    print("-"*70)
    
    try:
        import pdfplumber
        print(f"[OK] pdfplumber version: {pdfplumber.__version__}")
        
        with pdfplumber.open(str(pdf_file)) as pdf:
            page_count = len(pdf.pages)
            print(f"[OK] PDF loaded successfully")
            print(f"[OK] Total pages: {page_count}")
            
            text_content = ""
            table_content = ""
            scanned_pages = 0
            
            print(f"\nAnalyzing pages...")
            for i, page in enumerate(pdf.pages, 1):
                print(f"  Page {i}/{page_count}...", end=" ", flush=True)
                
                # Try text extraction
                page_text = page.extract_text()
                if page_text:
                    text_content += page_text + "\n"
                    print(f"Text: {len(page_text)} chars", end=" | ", flush=True)
                else:
                    print(f"Text: None", end=" | ", flush=True)
                
                # Try table extraction
                try:
                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            for row in table:
                                table_content += " ".join([str(cell) if cell else "" for cell in row]) + "\n"
                        print(f"Tables: {len(tables)}", end=" | ", flush=True)
                    else:
                        print(f"Tables: None", end=" | ", flush=True)
                except:
                    print(f"Tables: Error", end=" | ", flush=True)
                
                # Check if page looks like an image (scanned)
                chars = page.chars
                if chars:
                    print(f"Chars: {len(chars)}")
                else:
                    print(f"Chars: 0 (likely scanned)")
                    scanned_pages += 1
            
            print(f"\n{'='*70}")
            print("SUMMARY")
            print(f"{'='*70}")
            print(f"Total text content: {len(text_content)} characters")
            print(f"Total table content: {len(table_content)} characters")
            print(f"Scanned pages (no char data): {scanned_pages}/{page_count}")
            
            if len(text_content) == 0:
                print("\n[WARNING] No text content extracted!")
                if scanned_pages == page_count:
                    print("  -> PDF appears to be scanned images only")
                    print("  -> OCR required to extract text")
                else:
                    print("  -> Unknown parsing issue")
                    print("  -> Try opening PDF manually to verify content")
            else:
                print(f"\n[OK] Successfully extracted text!")
                print(f"  First 200 characters preview:")
                print(f"  {text_content[:200]}...")
                return True
                    
    except ImportError:
        print("[ERROR] pdfplumber not installed")
        print("  Install with: pip install pdfplumber")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return len(text_content) > 0

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python test_pdf_diagnostic.py <pdf_file>")
        print("\nExample: python test_pdf_diagnostic.py document.pdf")
        return 1
    
    pdf_path = sys.argv[1]
    success = test_pdf_parsing(pdf_path)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())

