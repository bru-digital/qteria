"""
Seed script to create a test user for authentication testing.
"""

import bcrypt
import uuid
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment variables")

# Create engine and session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()


def create_test_user():
    """Create a test user with hashed password."""

    # Generate UUIDs
    org_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    # Test credentials
    test_email = "test@qteria.com"
    test_password = "password123"
    test_name = "Test User"

    # Hash password with bcrypt
    password_hash = bcrypt.hashpw(test_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    try:
        # Check if organization already exists
        org_result = session.execute(
            text("SELECT id FROM organizations WHERE name = :name"), {"name": "Test Organization"}
        )
        existing_org = org_result.fetchone()

        if existing_org:
            org_id = str(existing_org[0])
            print(f"Using existing organization: {org_id}")
        else:
            # Create test organization
            session.execute(
                text(
                    """
                    INSERT INTO organizations (id, name, subscription_tier, subscription_status)
                    VALUES (:id, :name, :tier, :status)
                """
                ),
                {"id": org_id, "name": "Test Organization", "tier": "trial", "status": "trial"},
            )
            print(f"Created organization: {org_id}")

        # Check if user already exists
        user_result = session.execute(
            text("SELECT id FROM users WHERE email = :email"), {"email": test_email}
        )
        existing_user = user_result.fetchone()

        if existing_user:
            # Update existing user's password
            session.execute(
                text(
                    """
                    UPDATE users
                    SET password_hash = :password_hash
                    WHERE email = :email
                """
                ),
                {"password_hash": password_hash, "email": test_email},
            )
            print(f"Updated existing user: {test_email}")
        else:
            # Create test user
            session.execute(
                text(
                    """
                    INSERT INTO users (id, organization_id, email, name, password_hash, role)
                    VALUES (:id, :org_id, :email, :name, :password_hash, :role)
                """
                ),
                {
                    "id": user_id,
                    "org_id": org_id,
                    "email": test_email,
                    "name": test_name,
                    "password_hash": password_hash,
                    "role": "admin",
                },
            )
            print(f"Created user: {test_email}")

        session.commit()

        print("\n" + "=" * 60)
        print("Test user created successfully!")
        print("=" * 60)
        print(f"Email:        {test_email}")
        print(f"Password:     {test_password}")
        print(f"Organization: {org_id}")
        print(f"Role:         admin")
        print("=" * 60)

    except Exception as e:
        session.rollback()
        print(f"Error creating test user: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    create_test_user()
