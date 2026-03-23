import os
import sys
import oracledb
import pandas as pd
import tkinter as tk
from tkinter import messagebox, filedialog
from cryptography.fernet import Fernet

# ==========================================
# 1. 安全設定區 (請填入你的金鑰)
# ==========================================
# 請將你之前用 encrypt_password.py 產生的 KEY 和 TOKEN 貼在這裡
DECRYPT_KEY = "wzXffIU5YqrSHJyIOy9BGY6CHL7skdfDj8mIzVvsvEw=" 
ENCRYPTED_PASSWORD_TOKEN = "gAAAAABpvQr5PqglJ9C5o36jqDCZFJYQRz4woKThaZ9qtJQpRXbiVEMIhqWU4xhVgfZnWQPdSvBjuwaxmSPV-8n8Zb9_fYzeeqM2pWw0EHH02wDtTCtC_1I="

DB_USER = "queryuser"
DB_DSN = "172.18.1.153:1521/orcl"

# ==========================================
# 2. 核心抽取邏輯 (已加入防禦機制與警告消除)
# ==========================================
def extract_oracle_data(query, output_filename):
    try:
        # 1. 安全解密
        cipher_suite = Fernet(DECRYPT_KEY.encode())
        decrypted_password_bytes = cipher_suite.decrypt(ENCRYPTED_PASSWORD_TOKEN.encode())
        real_password = decrypted_password_bytes.decode()

        # 2. 取得路徑 (支援 .py 與打包後的 .exe)
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            
        oracle_client_path = os.path.join(base_dir, "instantclient_19_30")

        # 3. 清理環境變數 (防止舊版衝突)
        env_vars_to_clear = ["ORACLE_HOME", "TNS_ADMIN", "ORA_TZFILE", "NLS_LANG"]
        for var in env_vars_to_clear:
            if var in os.environ:
                del os.environ[var]

        # ==========================================
        # ★ 修正重點：防禦機制必須在啟動翻譯官「之前」執行 ★
        # ==========================================
        # 1. 傳統 PATH 覆蓋
        os.environ["PATH"] = oracle_client_path + os.pathsep + os.environ.get("PATH", "")
        
        # 2. Python 3.8+ Windows 專用的 DLL 強制載入大絕招
        if hasattr(os, 'add_dll_directory'):
            os.add_dll_directory(oracle_client_path)
        # ==========================================

        # 4. 初始化與連線 (此時系統已經被強迫只能讀取我們的 19.30 資料夾了)
        oracledb.init_oracle_client(lib_dir=oracle_client_path) 
        connection = oracledb.connect(user=DB_USER, password=real_password, dsn=DB_DSN)

        # 5. 執行查詢 (使用原生 cursor 避開 pandas 警告)
        cursor = connection.cursor()
        cursor.execute(query)
        
        # 抓取欄位名稱與資料
        columns = [col[0] for col in cursor.description]
        data = cursor.fetchall()
        
        # 轉換為 DataFrame 並存成 CSV
        df = pd.DataFrame(data, columns=columns)
        df.to_csv(output_filename, index=False, encoding='utf-8-sig') 
        
        return True, f"成功！資料已儲存至:\n{output_filename}"

    except oracledb.DatabaseError as e:
        error, = e.args
        return False, f"資料庫錯誤:\n代碼: {error.code}\n訊息: {error.message}"
    except Exception as e:
        return False, f"發生錯誤:\n{e}"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection:
            connection.close()

# ==========================================
# 3. 繪製視窗外觀 (GUI)
# ==========================================
def run_tool():
    sql_query = text_sql.get("1.0", tk.END).strip()
    if not sql_query:
        messagebox.showwarning("警告", "請輸入 SQL 查詢語法！")
        return
    
    # 讓用戶選擇存檔位置
    output_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV 檔案", "*.csv")],
        title="選擇儲存位置",
        initialfile="Oracle_Extract.csv"
    )
    
    if not output_path:
        return 
        
    # 變更按鈕狀態，提示正在執行中
    btn_run.config(text="正在抽取資料，請稍候...", state=tk.DISABLED)
    root.update()

    # 執行抽取
    success, message = extract_oracle_data(sql_query, output_path)
    
    # 恢復按鈕狀態並顯示結果
    btn_run.config(text="執行並匯出 CSV", state=tk.NORMAL)
    if success:
        messagebox.showinfo("執行完畢", message)
    else:
        messagebox.showerror("執行失敗", message)

# 建立主視窗
root = tk.Tk()
root.title("Oracle 數據抽取工具 v1.0") 
root.geometry("550x400")

label_instruction = tk.Label(root, text="請在下方輸入 Oracle SQL 查詢語法：", font=("Arial", 12))
label_instruction.pack(pady=10)

text_sql = tk.Text(root, height=12, width=65)
text_sql.pack(pady=5)
text_sql.insert(tk.END, "SELECT * FROM V$VERSION") # 預設放一個簡單的查詢讓用戶測試

btn_run = tk.Button(root, text="執行並匯出 CSV", font=("Arial", 12, "bold"), bg="lightblue", command=run_tool)
btn_run.pack(pady=20)

root.mainloop()