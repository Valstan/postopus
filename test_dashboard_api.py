#!/usr/bin/env python3
"""
Quick test script to demonstrate the Postopus Dashboard API functionality.
"""
import asyncio
import json
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent))

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    print("⚠️  httpx not available. Install with: pip install httpx")

async def test_dashboard_api():
    """Test the dashboard API endpoints."""
    if not HTTPX_AVAILABLE:
        return
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Postopus Dashboard API...")
    print(f"🌐 Base URL: {base_url}")
    
    async with httpx.AsyncClient() as client:
        # Test endpoints
        endpoints = [
            ("/health", "Health Check"),
            ("/api/info", "Application Info"),
            ("/api/auth/status", "Auth Status"),
            ("/api/dashboard/stats", "Dashboard Statistics"),
            ("/api/dashboard/recent-posts", "Recent Posts"),
            ("/api/dashboard/regional-stats", "Regional Statistics"),
            ("/api/dashboard/chart-data", "Chart Data"),
            ("/api/dashboard/system-status", "System Status"),
            ("/api/dashboard/overview", "Dashboard Overview")
        ]
        
        results = []
        
        for endpoint, description in endpoints:
            try:
                print(f"📡 Testing {description}: {endpoint}")
                response = await client.get(f"{base_url}{endpoint}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Success: {len(str(data))} chars response")
                    results.append({
                        "endpoint": endpoint,
                        "status": "success",
                        "description": description,
                        "response_size": len(str(data))
                    })
                else:
                    print(f"   ❌ Error: {response.status_code}")
                    results.append({
                        "endpoint": endpoint,
                        "status": "error",
                        "description": description,
                        "error_code": response.status_code
                    })
                    
            except Exception as e:
                print(f"   💥 Exception: {str(e)[:50]}...")
                results.append({
                    "endpoint": endpoint,
                    "status": "exception",
                    "description": description,
                    "error": str(e)
                })
        
        # Summary
        successful = len([r for r in results if r["status"] == "success"])
        total = len(results)
        
        print(f"\n📊 Test Summary:")
        print(f"   ✅ Successful: {successful}/{total}")
        print(f"   ❌ Failed: {total - successful}/{total}")
        
        if successful == total:
            print("🎉 All API endpoints are working correctly!")
        else:
            print("⚠️  Some endpoints need attention.")
        
        return results

def sync_test():
    """Synchronous wrapper for the async test."""
    try:
        return asyncio.run(test_dashboard_api())
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Starting API test...")
    print("💡 Make sure the Postopus server is running on localhost:8000")
    print("💡 Start server with: python -m uvicorn src.web.simple_main:app --reload")
    print()
    
    results = sync_test()
    
    if results:
        print("\n📋 Detailed Results:")
        for result in results:
            status_icon = "✅" if result["status"] == "success" else "❌"
            print(f"   {status_icon} {result['description']}: {result['endpoint']}")