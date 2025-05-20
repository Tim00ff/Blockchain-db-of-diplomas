import bcrypt
import json
import os
from typing import List, Dict

ROLES = ['admin', 'miner']  # Removed viewer


def get_valid_username(existing_users: List[Dict]) -> str:
    """Get unique username with validation"""
    while True:
        username = input("Enter username: ").strip()
        if not username:
            print("Username cannot be empty!")
            continue

        if any(user['username'] == username for user in existing_users):
            print(f"Username '{username}' already exists!")
            continue

        return username


def select_role() -> str:
    """Role selection menu"""
    print("\nSelect user role:")
    for i, role in enumerate(ROLES, 1):
        print(f"{i}. {role.capitalize()}")

    while True:
        choice = input("Enter choice (1-2): ").strip()  # Changed to 1-2
        if choice in ['1', '2']:  # Updated validation
            return ROLES[int(choice) - 1]
        print("Invalid choice! Please enter 1-2")


def create_user():
    """Create new user with role assignment"""
    # Load existing users
    users = []
    if os.path.exists('users.json'):
        with open('users.json', 'r') as f:
            users = json.load(f)

    # Get user input
    username = get_valid_username(users)
    password = input("Enter password: ").strip()

    # Hash password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Select role
    role = select_role()

    # Create user record
    user_data = {
        "username": username,
        "hashed_password": hashed_password.decode('utf-8'),
        "role": role,
        "status": "active"
    }

    # Save to file
    users.append(user_data)
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=4, sort_keys=True)

    print(f"\nUser '{username}' created successfully!")
    print(f"Role: {role.capitalize()}")
    print(f"Debug password: {password}")


if __name__ == "__main__":
    print("=== User Creation Tool ===")
    create_user()