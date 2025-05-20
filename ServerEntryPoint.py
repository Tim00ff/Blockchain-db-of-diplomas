import CreateUser
from Server import start_server

def main():
    while True:
        print("Choose an option:")
        print("1. Create a new user")
        print("2. Start the server")
        print("3. Close application")

        choice = input("Enter: ")

        if choice == '1':
            print("Creating a new user...")
            CreateUser.create_user()

        elif choice == '2':
            print("Starting the server...")
            start_server()

        elif choice == '3':
            print("Closing application...")
            break

        else:
            print("Invalid choice! Please enter 1 or 2.")

if __name__ == "__main__":
    main()