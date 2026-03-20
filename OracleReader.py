# ==========================================
# 1. 匯入模組區 (Importing Modules)
# 告訴 Python 我們這支程式需要用到哪些外部工具包
# ==========================================

import os 
# import: 匯入。 os: 作業系統 (Operating System) 的內建模組，這裡用來讀取系統的環境變數。

import oracledb 
# oracledb: 這是用來與 Oracle 資料庫溝通的專用套件。

import pandas as pd 
# pandas: 強大的數據處理套件。 
# as pd: 給它取個簡短的別名 "pd"，這樣後面寫程式就不用一直打 pandas，打 pd 就好。

from dotenv import load_dotenv 
# from ... import ...: 從某個大套件中，單獨拿出一個小工具。
# 這裡的意思是：從 dotenv 套件中，拿出 load_dotenv 這個函式（用來讀取隱藏的密碼檔 .env）。

import logging 
# logging: 內建的日誌模組。用來記錄程式跑到哪裡、發生什麼事（比單純用 print 更專業、更好追蹤）。

# ==========================================
# 2. 初始設定 (Configuration)
# ==========================================

# logging.basicConfig: 設定日誌的基礎格式。
# level=logging.INFO: 設定紀錄等級。INFO 代表一般資訊，只有 INFO 等級（含）以上的嚴重訊息才會被記錄下來。
# format='...': 設定印出來的文字長怎樣，這裡設定為「時間 - 等級 - 具體訊息」。
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# ==========================================
# 3. 定義主功能函式 (Defining the Main Function)
# 將抽取資料的邏輯打包成一個可重複使用的區塊
# ==========================================

# def: 定義 (define) 一個函式。
# extract_oracle_data: 我們幫這個函式取的名稱。
# (query, output_filename): 括號內是「參數」。代表呼叫這個函式時，必須給它「SQL 語法 (query)」和「存檔檔名 (output_filename)」。
def extract_oracle_data(query, output_filename):
    
    # 呼叫 load_dotenv()，它會去尋找同一個資料夾下的 .env 檔案，把裡面的密碼載入到系統環境中。
    load_dotenv()
    
    # os.getenv("變數名稱"): 去系統環境中取得對應的機密資料，並把它們存進左邊的變數 (user, password, dsn) 裡。
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    dsn = os.getenv("DB_DSN")

    # try: 開始一個「例外處理」區塊。
    # 意思是：「嘗試」執行下面的程式碼。如果過程中發生任何錯誤，程式不會立刻崩潰當機，而是會跳到後面的 except 區塊。
    try:
        # logging.info("..."): 在畫面上印出一條正常的提示訊息。
        logging.info("正在建立與 Oracle 資料庫的連線...")
        
        # oracledb.connect(...): 執行連線動作。
        # 把我們剛剛取得的 user, password, dsn 交給這個套件去敲資料庫的門。
        # 連線成功後，將這條連線通道存入變數 connection 中。
        connection = oracledb.connect(user=user, password=password, dsn=dsn)
        
        logging.info("連線成功，正在執行查詢...")
        
        # pd.read_sql(...): pandas 的內建函式。
        # query: 你要執行的 SQL 指令。 con=connection: 告訴它透過哪一條連線去執行。
        # 執行完畢後，它會自動把資料庫拿回來的資料變成一個類似 Excel 表格的格式（稱為 DataFrame），並存進變數 df。
        df = pd.read_sql(query, con=connection)
        
        # df.to_csv(...): 把剛剛那個 DataFrame 表格，匯出並存成 CSV 檔案。
        # index=False: 告訴 pandas 存檔時，不要把最左邊用來算行數的數字流水號 (0, 1, 2...) 一併存進去。
        df.to_csv(output_filename, index=False)
        
        # 這裡的 f"..." 稱為 f-string (格式化字串)。它允許你在字串裡面用 {} 直接塞入變數的值。
        logging.info(f"數據已成功抽取並儲存至 {output_filename}")

    # except: 如果上面的 try 區塊發生了錯誤，就會跳到這裡。
    # oracledb.Error: 這是特別針對「Oracle 資料庫出錯」的分類。
    # as e: 把詳細的錯誤訊息抓下來，取名為變數 e。
    except oracledb.Error as e:
        # logging.error: 記錄一筆「錯誤」等級的日誌，並把錯誤訊息 e 印出來。
        logging.error(f"資料庫發生錯誤: {e}")
        
    # 這是第二個 except。Exception 包含了「所有其他未預期的錯誤」（例如記憶體爆掉、網路斷線等）。
    except Exception as e:
        logging.error(f"發生未預期的錯誤: {e}")
        
    # finally: 例外處理的最後一塊拼圖。
    # 無論上面的 try 是成功執行，還是中途出錯跑到 except，最後「一定」會執行 finally 裡面的程式碼。通常用來做打掃收尾。
    finally:
        # if: 條件判斷式。
        # 'connection' in locals(): 檢查當前的區域變數 (locals) 裡面，有沒有 'connection' 這個東西。（避免連線根本沒建立就斷掉而產生錯誤）。
        # and connection: 並且確認這條連線不是空的 (None)。
        if 'connection' in locals() and connection:
            # connection.close(): 把資料庫連線關閉。這非常重要！忘記關的話會佔用伺服器資源。
            connection.close()
            logging.info("資料庫連線已關閉。")


# ==========================================
# 4. 程式執行起點 (Entry Point)
# ==========================================

# if __name__ == "__main__": 這是 Python 非常經典的起手式。
# 它的意思是：「如果這支程式是被使用者『直接執行』的，才跑下面的程式碼」。
# 如果這支程式是被其他 Python 檔案當成工具包 import 過去，下面的程式碼就不會自動觸發。
if __name__ == "__main__":
    
    # 建立一個字串變數 sql_query，裡面裝著你要查詢的 SQL 語法。
    sql_query = "SELECT * FROM your_target_table WHERE ROWNUM <= 1000"
    
    # 建立一個字串變數 output_file，指定存檔的檔名。
    output_file = "extracted_data.csv"
    
    # 真正去「呼叫（執行）」我們在上面定義好的函式，並把 SQL 語法和檔名當作參數丟進去。
    extract_oracle_data(sql_query, output_file)