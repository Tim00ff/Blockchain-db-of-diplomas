import os
from typing import Optional, List, Dict
from cryptography.hazmat.primitives.asymmetric import rsa
from Block import Block


class Blockchain:
    def __init__(
            self,
            path: str = "Blockchain",
            diploma_data: Optional[Dict] = None,
            public_key: Optional[rsa.RSAPublicKey] = None
    ):
        self.chain: List[Block] = []
        self.path = path
        self.current_id = 0

        os.makedirs(self.path, exist_ok=True)

        try:
            has_blocks = self._load_chain()
        except RuntimeError as e:
            raise ValueError(f"Error loading blockchain: {str(e)}")

            # Если блоков нет и переданы параметры - создаем genesis
        if not has_blocks:
            if diploma_data and public_key:
                self._create_genesis_block(diploma_data, public_key)
            else:
                raise ValueError(
                    "Cannot initialize blockchain: "
                    "No existing blocks and missing initialization parameters"
                )

    def _load_chain(self) -> bool:
        """Загружает цепочку из файлов. Возвращает True если блоки найдены, False если папка пустая"""
        try:
            block_files = sorted(
                [f for f in os.listdir(self.path) if f.startswith("Block_")],
                key=lambda x: int(x.split('_')[1].split('.')[0]))

            if not block_files:  # Нет файлов блоков
                return False

            for filename in block_files:
                block = Block.from_file(os.path.join(self.path, filename))
                self.chain.append(block)
                self.current_id = max(self.current_id, block.id + 1)

            return True

        except Exception as e:
            raise RuntimeError(f"Chain loading failed: {str(e)}")

    def _create_genesis_block(self, data: Dict, public_key: rsa.RSAPublicKey):
        if 'signature' not in data:
            raise ValueError("Genesis data must be signed")

        genesis = Block(
            block_id=0,
            diploma_data=data,
            public_key=public_key,
            prev_hash="0" * 64
        )
        genesis.mine()
        self.chain.append(genesis)
        self.current_id = 1
        genesis.save_to_file(self.path)

    def add_block(self, block: Block):
        if self.chain:
            if block.prev_hash != self.chain[-1].hash:
                raise ValueError("Previous hash mismatch")
            if block.id != self.current_id:
                raise ValueError("Invalid block ID")

        block.save_to_file(self.path)
        self.chain.append(block)
        self.current_id += 1

    def create_and_add_block(self, diploma_data: dict, public_key: rsa.RSAPublicKey):
        prev_hash = self.chain[-1].hash if self.chain else "0" * 64
        new_block = Block(
            block_id=self.current_id,
            diploma_data=diploma_data,
            public_key=public_key,
            prev_hash=prev_hash
        )
        new_block.mine()
        self.add_block(new_block)

    def validate_chain(self, start: int = 0, end: Optional[int] = None) -> bool:
        if not self.chain:
            return True

        end = end or len(self.chain) - 1
        if start < 0 or end >= len(self.chain) or start > end:
            raise ValueError("Invalid range")

        try:
            for i in range(start, end + 1):
                current = self.chain[i]

                if not current.verify_diploma():
                    return False

                if current.hash != current.calculate_hash():
                    return False

                if i > 0 and current.prev_hash != self.chain[i - 1].hash:
                    return False

                if not current.hash.startswith('0' * current.difficulty):
                    return False

            return True
        except Exception:
            return False

    def print_chain_info(self):
        """Выводит подробную информацию о блокчейне"""
        print("\n" + "=" * 60)
        print("Blockchain Information".center(60))
        print("=" * 60)

        # Основная информация
        print(f"\nTotal Blocks: {len(self.chain)}")
        print(f"Current Block ID: {self.current_id}")
        print(f"Chain Validity: {'VALID' if self.validate_chain() else 'INVALID'}")

        # Информация о последнем блоке
        if self.chain:
            last_block = self.chain[-1]
            print("\nLast Block Details:")
            print(f"ID: {last_block.id}")
            print(f"Hash: {last_block.hash[:20]}...{last_block.hash[-20:]}")
            print(f"Timestamp: {last_block.timestamp}")
            print(f"Diploma Reg Number: {last_block.diploma_data.get('reg_number', 'N/A')}")
        else:
            print("\nNo blocks in the chain")

        # Список всех блоков
        print("\nBlock List:")
        print("-" * 60)
        for block in self.chain:
            print(f"Block #{block.id:04d}")
            print(f"Hash: {block.hash[:15]}...")
            print(f"Prev Hash: {block.prev_hash[:15]}..." if block.prev_hash else "Genesis Block")
            print(f"Diploma: {block.diploma_data.get('reg_number', 'Unknown')}")
            print("-" * 60)

        print("=" * 60 + "\n")

    def get_block(self, block_id):
        return self.chain[block_id]
    def __len__(self):
        return len(self.chain)

    def __getitem__(self, index):
        return self.chain[index]

    def __repr__(self):
        return f"Blockchain({len(self)} blocks, current_id={self.current_id})"