from Blockchain import Blockchain
from Diploma import DiplomaGenerator as Diploma_gen

test = Blockchain()
ivan_dip = Diploma_gen(dict())
diploma_text = ivan_dip.generate()
print(diploma_text)

# Verify signature
is_valid = Diploma_gen.verify_diploma(diploma_text, ivan_dip.get_public_key())
print(f"\n----------------------------------------\nПодпись {'валидна' if is_valid else 'недействительна'}")

# Get serialized keys
public_pem = ivan_dip.get_public_key_pem()
private_pem = ivan_dip.get_private_key_pem()

print(f"\nОткрытый ключ:\n{public_pem}")
print(f"\nЗакрытый ключ:\n{private_pem}")