# encrypt_password.py
from cryptography.fernet import Fernet

# 1. 產生一組新的隨機金鑰 (Key)
key = Fernet.generate_key()
print(f"==== 你的解密金鑰 (KEY) ====")
# 請把這行印出來的內容複製下來，要貼到主程式裡
print(key.decode()) 
print("============================\n")

# 2. 建立加密器
cipher_suite = Fernet(key)

# 3. 把你的原始密碼放進去 (請向 IT 索取 amtaxi 的實際密碼)
# 假設原始密碼是 'your_actual_password_from_IT'
original_password = "query_user20191110"

# 將密碼編碼並加密
encrypted_bytes = cipher_suite.encrypt(original_password.encode())
encrypted_text = encrypted_bytes.decode()

print(f"==== 加密後的密碼 (TOKEN) ====")
# 請把這行印出來的內容複製下來，也要貼到主程式裡
print(encrypted_text)
print("==============================\n")