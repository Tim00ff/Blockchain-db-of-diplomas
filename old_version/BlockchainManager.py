import json
from typing import Optional
from Blockchain import Blockchain
from DiplomaGenerator import DiplomaGenerator
from KeyManager import KeyManager
from Block import Block

class BlockchainManager:
    def __init__(self, blockchain: Blockchain = None):
        self.blockchain = blockchain or Blockchain()
        self.current_diploma: Optional[DiplomaGenerator] = None

    def print_menu(self):
        print("\n" + "=" * 40)
        print("Blockchain Manager".center(40))
        print("=" * 40)
        print("1. Add New Block")
        print("2. Read Block Data")
        print("3. Validate Blocks Range")
        print("4. Load Diploma from Block")
        print("5. Exit")
        print("=" * 40)

    def start(self):
        while True:
            self.print_menu()
            choice = input("Select option (1-5): ")

            if choice == '1':
                self.add_block_ui()
            elif choice == '2':
                self.read_block_ui()
            elif choice == '3':
                self.validate_range_ui()
            elif choice == '4':
                self.load_diploma_ui()
            elif choice == '5':
                print("Exiting...")
                break
            else:
                print("Invalid option, try again")

    def add_block_ui(self):
        print("\n" + "=" * 40)
        print("Add New Block".center(40))
        print("=" * 40)

        dip_file = input("Enter diploma file path: ")
        key_file = input("Enter key file path: ")

        try:
            # Load diploma and keys
            diploma = DiplomaGenerator.from_file(dip_file)
            key_manager = KeyManager.from_file(key_file)

            # Create and add block
            self.blockchain.create_and_add_block(
                diploma_data=diploma.to_dict(),
                public_key=key_manager.public_key
            )

            print(f"\nBlock #{len(self.blockchain) - 1} added successfully!")

        except Exception as e:
            print(f"\nError adding block: {str(e)}")

    def read_block_ui(self):
        print("\nAvailable Block IDs: 0 -", len(self.blockchain) - 1)
        try:
            block_id = int(input("Enter block ID: "))
            block = self.blockchain.get_block(block_id)

            print("\n" + "=" * 40)
            print(f"Block #{block_id} Data".center(40))
            print("=" * 40)
            print(json.dumps(block.diploma_data, indent=2, ensure_ascii=False))

        except (ValueError, IndexError) as e:
            print(f"Invalid block ID: {str(e)}")

    def validate_range_ui(self):
        print("\nAvailable Block IDs: 0 -", len(self.blockchain) - 1)
        try:
            start = int(input("Enter start ID: "))
            end = int(input("Enter end ID: "))

            is_valid = self.blockchain.validate_chain(start, end)
            status = "VALID" if is_valid else "INVALID"

            print("\n" + "=" * 40)
            print(f"Chain validation ({start}-{end}): {status}")

        except Exception as e:
            print(f"Validation error: {str(e)}")

    def load_diploma_ui(self):
        print("\nAvailable Block IDs: 0 -", len(self.blockchain) - 1)
        try:
            block_id = int(input("Enter block ID: "))
            block = self.blockchain.get_block(block_id)

            self.current_diploma = DiplomaGenerator(block.diploma_data)
            self._diploma_submenu()

        except Exception as e:
            print(f"Error loading diploma: {str(e)}")

    def _diploma_submenu(self):
        while True:
            print("\n" + "=" * 40)
            print("Diploma Operations".center(40))
            print("=" * 40)
            print("1. Print Diploma")
            print("2. Save to File")
            print("3. Return to Main Menu")

            choice = input("Select option (1-3): ")

            if choice == '1':
                print("\n" + "=" * 40)
                print(self.current_diploma.to_string())
            elif choice == '2':
                filename = input("Enter output filename: ")
                self.current_diploma.save_to_file(filename)
                print(f"Diploma saved to {filename}")
            elif choice == '3':
                break
            else:
                print("Invalid option, try again")

    def print_chain_info(self):
        self.blockchain.print_chain_info()

    def add_block_from_miner(self, block_data, miner_id):
        # Проверка Proof-of-Work
        new_block = Block(
            block_id=len(self.blockchain),
            diploma_data=block_data,
            public_key=block_data["public_key"],
            prev_hash=self.blockchain.chain[-1].hash if self.blockchain.chain else "0" * 64
        )
        if new_block.verify_diploma():
            self.blockchain.add_block(new_block)
            return True
        return False