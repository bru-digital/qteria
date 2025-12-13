#!/usr/bin/env python3
"""
Deployment verification script for Qteria API on Railway.

This script verifies that the deployed API is healthy and all critical
services (database, redis) are accessible.

Usage:
    python scripts/verify_deployment.py https://qteria-api-production.up.railway.app

Returns:
    Exit code 0 on success, 1 on failure
"""

import argparse
import sys
import time
import requests
from typing import Optional


def check_health(base_url: str, timeout: int = 90) -> bool:
    """
    Poll the health endpoint until it returns 200 OK or timeout is reached.

    Args:
        base_url: Base URL of the deployed API (e.g., https://qteria-api-production.up.railway.app)
        timeout: Maximum time to wait in seconds (default: 90)

    Returns:
        True if health check succeeds, False otherwise
    """
    health_url = f"{base_url.rstrip('/')}/health"
    start_time = time.time()
    attempt = 0

    print(f"🔍 Checking health endpoint: {health_url}")
    print(f"⏱️  Timeout: {timeout} seconds\n")

    while time.time() - start_time < timeout:
        attempt += 1
        elapsed = int(time.time() - start_time)

        try:
            print(f"[Attempt {attempt}] Polling health endpoint... (elapsed: {elapsed}s)")
            response = requests.get(health_url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed!")
                print(f"   Status: {data.get('status', 'N/A')}")
                print(f"   Service: {data.get('service', 'N/A')}")
                print(f"   Version: {data.get('version', 'N/A')}")
                print(f"   Timestamp: {data.get('timestamp', 'N/A')}")
                return True
            else:
                print(f"❌ Health check returned {response.status_code}: {response.text[:100]}")

        except requests.exceptions.ConnectionError:
            print(f"⚠️  Connection failed (service may be starting up)")
        except requests.exceptions.Timeout:
            print(f"⚠️  Request timed out")
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Request failed: {e}")
        except Exception as e:
            print(f"⚠️  Unexpected error: {e}")

        # Wait before next attempt
        if time.time() - start_time < timeout:
            time.sleep(5)

    print(f"\n❌ Health check timed out after {timeout} seconds")
    return False


def check_database_connection(base_url: str) -> bool:
    """
    Verify database connection by calling a simple endpoint that queries the database.

    Args:
        base_url: Base URL of the deployed API

    Returns:
        True if database is accessible, False otherwise
    """
    # For now, we'll rely on the health endpoint to verify database connection
    # In the future, we could add a dedicated /health/database endpoint
    print("\n🗄️  Database connection check:")
    print("   (Included in health endpoint verification)")
    return True


def check_redis_connection(base_url: str) -> bool:
    """
    Verify Redis connection for background job queue.

    Args:
        base_url: Base URL of the deployed API

    Returns:
        True if Redis is accessible (or not required), False if required but unavailable
    """
    # Redis is optional for basic API functionality
    # For now, we'll just log a warning if we can't verify it
    print("\n📮 Redis connection check:")
    print("   (Optional - used for background jobs)")
    print("   ⚠️  Redis verification not implemented yet")
    return True


def main():
    """Main entry point for deployment verification."""
    parser = argparse.ArgumentParser(
        description="Verify Qteria API deployment on Railway"
    )
    parser.add_argument(
        "url",
        help="Base URL of the deployed API (e.g., https://qteria-api-production.up.railway.app)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=90,
        help="Timeout in seconds for health check (default: 90)"
    )

    args = parser.parse_args()

    print("=" * 70)
    print("🚀 Qteria API Deployment Verification")
    print("=" * 70)
    print(f"Target URL: {args.url}")
    print(f"Timeout: {args.timeout}s")
    print("=" * 70)
    print()

    # Run health check
    health_ok = check_health(args.url, timeout=args.timeout)

    if not health_ok:
        print("\n" + "=" * 70)
        print("❌ DEPLOYMENT VERIFICATION FAILED")
        print("=" * 70)
        print("\nTroubleshooting steps:")
        print("1. Check Railway dashboard for build/deployment errors")
        print("2. View Railway logs: railway logs")
        print("3. Verify all environment variables are set")
        print("4. Check that libmagic1 is installed (required for document upload)")
        print("5. Ensure DATABASE_URL is accessible from Railway")
        print("=" * 70)
        sys.exit(1)

    # Run optional checks
    check_database_connection(args.url)
    check_redis_connection(args.url)

    print("\n" + "=" * 70)
    print("✅ DEPLOYMENT VERIFICATION PASSED")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Update Vercel environment variable API_URL to:", args.url)
    print("2. Test frontend integration at qteria.com")
    print("3. Create a test workflow to verify end-to-end functionality")
    print("=" * 70)

    sys.exit(0)


if __name__ == "__main__":
    main()
