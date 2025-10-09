#!/usr/bin/env python3
"""
Demo: Static Bearer Token vs Dynamic Token Generation
Shows the difference between the two authentication methods
"""

import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from guidewire_client import GuidewireClient, GuidewireConfig

def demo_static_token():
    """Demo using a static bearer token"""
    
    print("🔐 DEMO: STATIC BEARER TOKEN")
    print("=" * 40)
    
    # Simulate having a static token
    config = GuidewireConfig()
    config.bearer_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example_static_token"
    
    client = GuidewireClient(config)
    
    print(f"✅ Setup: Static bearer token provided")
    print(f"❌ No username/password needed")
    print(f"❌ No token expiry management")
    print(f"❌ No automatic refresh")
    
    # Test token validation
    if client._ensure_valid_token():
        print(f"✅ Token ready: {client._current_token[:30]}...")
    
    print(f"\n💡 Use Case: Long-lived tokens from Guidewire admin")
    print(f"💡 Best for: Production environments with static tokens")

def demo_dynamic_token():
    """Demo using dynamic token generation"""
    
    print("\n🔄 DEMO: DYNAMIC TOKEN GENERATION")
    print("=" * 40)
    
    # Simulate having username/password
    config = GuidewireConfig()
    config.username = "service_account"
    config.password = "secure_password"
    
    client = GuidewireClient(config)
    
    print(f"✅ Setup: Username and password provided")
    print(f"✅ Automatic token generation when needed")
    print(f"✅ Token expiry monitoring")
    print(f"✅ Automatic refresh before expiry")
    
    print(f"\n💡 Use Case: When you only have username/password")
    print(f"💡 Best for: Development or when tokens expire frequently")

def show_configuration_options():
    """Show the different ways to configure authentication"""
    
    print("\n⚙️ CONFIGURATION OPTIONS")
    print("=" * 40)
    
    print(f"\n📋 Option 1: Static Bearer Token (Simplest)")
    print(f"   .env file:")
    print(f"   GUIDEWIRE_BEARER_TOKEN=your_actual_token_here")
    print(f"   ✅ No expiry management")
    print(f"   ✅ No username/password needed")
    print(f"   ✅ Direct API access")
    
    print(f"\n📋 Option 2: Dynamic Token Generation")
    print(f"   .env file:")
    print(f"   GUIDEWIRE_USERNAME=your_service_account")
    print(f"   GUIDEWIRE_PASSWORD=your_password")
    print(f"   ✅ Automatic token generation")
    print(f"   ✅ Automatic refresh")
    print(f"   ✅ Handles token expiry")
    
    print(f"\n🎯 RECOMMENDATION:")
    print(f"   If you have a bearer token → Use Option 1")
    print(f"   If you only have username/password → Use Option 2")

if __name__ == "__main__":
    demo_static_token()
    demo_dynamic_token()
    show_configuration_options()