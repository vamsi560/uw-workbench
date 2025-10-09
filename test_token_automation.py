#!/usr/bin/env python3
"""
Test Guidewire Token Automation
Tests automatic token generation and refresh functionality
"""

import os
import sys
import json
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from guidewire_client import GuidewireClient, GuidewireConfig

def test_token_automation():
    """Test automatic token generation and refresh"""
    
    print("🔐 GUIDEWIRE TOKEN AUTOMATION TEST")
    print("=" * 50)
    
    # Create client instance
    client = GuidewireClient()
    
    print(f"📋 Configuration:")
    print(f"   API URL: {client.config.full_url}")
    print(f"   Auth URL: {client.config.auth_url}")
    print(f"   Static Bearer Token: {'✅ Available' if client.config.bearer_token else '❌ Not Set'}")
    print(f"   Username/Password: {'✅ Available' if (client.config.username and client.config.password) else '❌ Not Set'}")
    
    # Determine auth method
    if client.config.bearer_token:
        print(f"   🎯 Auth Method: Static Bearer Token (Recommended)")
    elif client.config.username and client.config.password:
        print(f"   🎯 Auth Method: Dynamic Token Generation")
    else:
        print(f"   ⚠️  Auth Method: None configured")
    
    # Test 1: Token setup
    print(f"\n🔄 TEST 1: Token Setup")
    if client.config.bearer_token:
        print("   ✅ Using static bearer token - no generation needed")
        print(f"   🔑 Token preview: {client.config.bearer_token[:20]}...")
    elif client.config.username and client.config.password:
        print("   🔄 Attempting dynamic token generation...")
        token = client._generate_token()
        if token:
            print(f"   ✅ Token generated successfully")
            print(f"   📅 Expires at: {datetime.fromtimestamp(client._token_expires_at) if client._token_expires_at else 'Unknown'}")
            print(f"   🔑 Token preview: {token[:20]}...")
        else:
            print("   ❌ Token generation failed")
    else:
        print("   ⚠️  No authentication configured - need either bearer token or username/password")
    
    # Test 2: Valid token check
    print(f"\n✅ TEST 2: Token Validation")
    if client._ensure_valid_token():
        print("   ✅ Valid token obtained")
        print(f"   🔑 Current token: {'Set' if client._current_token else 'Not set'}")
        print(f"   📅 Valid until: {datetime.fromtimestamp(client._token_expires_at) if client._token_expires_at else 'Static token'}")
    else:
        print("   ❌ Failed to obtain valid token")
    
    # Test 3: Connection test with token
    print(f"\n🌐 TEST 3: Connection Test with Token")
    try:
        connection_result = client.test_connection()
        if connection_result.get("success"):
            print("   ✅ Connection successful")
            print(f"   📊 Status: {connection_result.get('status_code')}")
            print(f"   ⏱️  Response time: {connection_result.get('response_time_ms', 0):.0f}ms")
        else:
            print("   ❌ Connection failed")
            print(f"   📝 Message: {connection_result.get('message', 'Unknown error')}")
    except Exception as e:
        print(f"   ❌ Connection test failed: {str(e)}")
    
    # Test 4: Simulate token expiry and refresh
    print(f"\n🔄 TEST 4: Token Refresh Simulation")
    if client._token_expires_at:
        # Simulate expired token by setting expiry to past
        original_expiry = client._token_expires_at
        client._token_expires_at = datetime.now().timestamp() - 100  # 100 seconds ago
        
        print("   ⏰ Simulated token expiry...")
        print(f"   🔄 Checking if refresh needed: {'Yes' if not client._is_token_valid() else 'No'}")
        
        if client._ensure_valid_token():
            print("   ✅ Token refreshed successfully")
            print(f"   📅 New expiry: {datetime.fromtimestamp(client._token_expires_at)}")
        else:
            print("   ❌ Token refresh failed")
        
        # Restore original expiry
        client._token_expires_at = original_expiry
    else:
        print("   ⚠️  Using static token - no expiry simulation")
    
    print(f"\n🎯 SUMMARY:")
    auth_ready = client.config.bearer_token or (client.config.username and client.config.password)
    print(f"   Configuration: {'✅ Ready' if auth_ready else '❌ Incomplete'}")
    print(f"   Token Management: {'✅ Working' if client._current_token else '❌ Failed'}")
    print(f"   API Connectivity: {'✅ Ready' if client._current_token else '❌ Not Ready'}")
    
    if client.config.bearer_token:
        print(f"\n💡 NOTE: Using static bearer token - no username/password needed!")
    elif not (client.config.username and client.config.password):
        print(f"\n💡 SETUP NEEDED:")
        print(f"   Option 1: Add GUIDEWIRE_BEARER_TOKEN=your_token to .env")
        print(f"   Option 2: Add GUIDEWIRE_USERNAME + GUIDEWIRE_PASSWORD to .env")
    
    return client._current_token is not None

if __name__ == "__main__":
    success = test_token_automation()
    sys.exit(0 if success else 1)