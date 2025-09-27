#!/usr/bin/env python3
"""
Test script to verify the setup and dependencies
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import fastapi
        print("✓ FastAPI imported successfully")
    except ImportError as e:
        print(f"✗ FastAPI import failed: {e}")
        return False
    
    try:
        import sqlalchemy
        print("✓ SQLAlchemy imported successfully")
    except ImportError as e:
        print(f"✗ SQLAlchemy import failed: {e}")
        return False
    
    try:
        import pdfplumber
        print("✓ pdfplumber imported successfully")
    except ImportError as e:
        print(f"✗ pdfplumber import failed: {e}")
        return False
    
    try:
        import docx
        print("✓ python-docx imported successfully")
    except ImportError as e:
        print(f"✗ python-docx import failed: {e}")
        return False
    
    try:
        import pandas
        print("✓ pandas imported successfully")
    except ImportError as e:
        print(f"✗ pandas import failed: {e}")
        return False
    
    try:
        import pytesseract
        print("✓ pytesseract imported successfully")
    except ImportError as e:
        print(f"✗ pytesseract import failed: {e}")
        return False
    
    try:
        import google.generativeai
        print("✓ Google Generative AI imported successfully")
    except ImportError as e:
        print(f"✗ Google Generative AI import failed: {e}")
        return False
    
    return True


def test_tesseract():
    """Test if Tesseract OCR is available"""
    print("\nTesting Tesseract OCR...")
    
    try:
        import pytesseract
        # Try to get tesseract version
        version = pytesseract.get_tesseract_version()
        print(f"✓ Tesseract version: {version}")
        return True
    except Exception as e:
        print(f"✗ Tesseract not available: {e}")
        print("Please install Tesseract OCR:")
        print("  Ubuntu/Debian: sudo apt-get install tesseract-ocr")
        print("  macOS: brew install tesseract")
        print("  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
        return False


def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        from config import settings
        print(f"✓ Configuration loaded successfully")
        print(f"  Database URL: {settings.database_url[:50]}...")
        print(f"  Gemini API Key: {'✓ Set' if settings.gemini_api_key else '✗ Not set'}")
        print(f"  Gemini Model: {settings.gemini_model}")
        print(f"  Upload directory: {settings.upload_dir}")
        print(f"  Log level: {settings.log_level}")
        return True
    except Exception as e:
        print(f"✗ Configuration loading failed: {e}")
        return False


def test_database_models():
    """Test database model imports"""
    print("\nTesting database models...")
    
    try:
        from database import EmailIntake, SubmissionDraft, Submission, WorkItem
        print("✓ Database models imported successfully")
        return True
    except Exception as e:
        print(f"✗ Database models import failed: {e}")
        return False


def main():
    """Run all tests"""
    print("Underwriting Workbench - Setup Test")
    print("=" * 40)
    
    all_passed = True
    
    all_passed &= test_imports()
    all_passed &= test_tesseract()
    all_passed &= test_config()
    all_passed &= test_database_models()
    
    print("\n" + "=" * 40)
    if all_passed:
        print("✓ All tests passed! Setup looks good.")
        print("\nNext steps:")
        print("1. Set up your .env file with database and API keys")
        print("2. Create the PostgreSQL database")
        print("3. Run: python run.py")
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
