import os
import oracledb
import pandas as pd

# ==========================================
# 1. 設定區
# ==========================================
DB_USER = "queryuser"
DB_PASSWORD = "query_user20191110" 
DB_DSN = "172.18.1.153:1521/orcl"

base_dir = os.path.dirname(os.path.abspath(__file__))
oracle_client_path = os.path.join(base_dir, "instantclient_19_30")

print(f"🔍 正在載入 Oracle Client，路徑為: {oracle_client_path}")

# ==========================================
# 2. 乾淨的環境清理 (絕對不要自己設定 ORA_TZFILE)
# ==========================================
# 只要確保這些干擾變數「不存在」就好，剩下的交給 Instant Client 自己決定
env_vars_to_clear = ["ORACLE_HOME", "TNS_ADMIN", "ORA_TZFILE", "NLS_LANG"]
for var in env_vars_to_clear:
    if var in os.environ:
        del os.environ[var]
        print(f"🧹 已清除系統中衝突的 {var} 變數")

# ==========================================
# 3. 核心測試邏輯
# ==========================================
try:
    print("⏳ 正在初始化 Oracle 厚模式...")
    # 只要這行有給對路徑，oracledb 底層會自動處理 PATH 等問題
    oracledb.init_oracle_client(lib_dir=oracle_client_path)
    print("✅ 厚模式初始化成功！")
    
    print(f"⏳ 正在連線至 {DB_DSN} ...")
    connection = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
    print("✅ 恭喜！資料庫連線成功！")
    
    test_query = "SELECT * FROM amtaxi.tab_carinfo WHERE ROWNUM <= 10"
    
    print("⏳ 正在執行 SQL 查詢...")
    df = pd.read_sql(test_query, con=connection)
    
    print("✅ 查詢成功！撈取到的資料如下：")
    print("-" * 30)
    print(df)
    print("-" * 30)

except oracledb.DatabaseError as e:
    error, = e.args
    print(f"❌ 資料庫錯誤代碼: {error.code}")
    print(f"❌ 資料庫錯誤訊息: {error.message}")
except Exception as e:
    print(f"❌ 發生未預期的錯誤: {e}")
finally:
    if 'connection' in locals() and connection:
        connection.close()
        print("🔒 資料庫連線已安全關閉。")




