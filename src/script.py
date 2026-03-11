import pandas as pd
import sqlite3
import numpy as np
import time

# ==========================================
# 1. ЗАГРУЗКА CSV
# ==========================================

try:
    df_raw = pd.read_csv('data/titanic.csv', encoding='utf-8')
    print(f"CSV загружен. Строк: {len(df_raw)}")
except FileNotFoundError:
    print(" Файл не найден. Положи train.csv в папку со скриптом.")

conn=sqlite3.connect('kaggle_db')
cursor = conn.cursor()

# Удаляем индекс если есть
cursor.execute("DROP INDEX IF EXISTS idx_fare")
conn.commit()

# Замер БЕЗ индекса
start = time.time()
for _ in range(100):
    cursor.execute("SELECT * FROM data_base1 WHERE Fare > 100")
    _ = cursor.fetchall()
time_without = time.time() - start
print(f"⏱ Без индекса (100 запросов): {time_without:.4f} сек")

# Создаем индекс
cursor.execute("CREATE INDEX idx_fare ON data_base1(Fare)")
conn.commit()

# Замер С индексом
start = time.time()
for _ in range(100):
    cursor.execute("SELECT * FROM data_base1 WHERE Fare > 100")
    _ = cursor.fetchall()
time_with = time.time() - start
print(f"⏱ С индексом (100 запросов): {time_with:.4f} сек")

print(f"\n🚀 Ускорение: {time_without / time_with:.2f}x")


df_raw.to_sql('data_base1', conn , if_exists='replace', index=False)
print(" Данные загружены в SQL таблицу")



query="""
SELECT (select avg(Fare) from data_base1) as average_price,Passengerid,Age,Fare,Survived from data_base1
WHERE fare>70 
LIMIT 200
"""
df=pd.read_sql_query(query,conn)
print(df.columns.tolist())

df['median_age'] = df['Age'].median()
df['Is_Rich'] = (df['Fare'] > 100).astype(int)
mode_fare=df['Fare'].mode()[0]
df['Fare']=df['Fare'].fillna(mode_fare) #change 0 fare to most common fare
# Корреляция между ценой билета и выживаемостью (NumPy)
corr = np.corrcoef(df['Is_Rich'].values, df['Survived'].values)[0, 1]
print(f"\nКорреляция Rich и Survived: {corr:.4f}")
df.to_csv('cleaned_titanic.csv', index=False)
print("\n Очищенные данные сохранены в cleaned_titanic.csv")
