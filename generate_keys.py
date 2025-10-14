#!/usr/bin/env python3
"""
Generate secure keys for production environment
"""
import secrets

print("🔐 Generating Secure Keys for Production")
print("=" * 60)
print()

secret_key = secrets.token_hex(32)
jwt_secret_key = secrets.token_hex(32)

print("Generated keys (add to .env.production):")
print()
print(f"SECRET_KEY={secret_key}")
print(f"JWT_SECRET_KEY={jwt_secret_key}")
print()
print("✅ Keys generated successfully!")
print()
print("⚠️  IMPORTANT: Keep these keys secure and never commit to git!")

