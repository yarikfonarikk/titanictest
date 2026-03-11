import pandas as pd
import sqlite3
import numpy as np

# ==========================================
# 1. ЗАГРУЗКА CSV
# ==========================================

try:
    df_raw = pd.read_csv('titanic.csv', encoding='utf-8')
    print(f"CSV загружен. Строк: {len(df_raw)}")
except FileNotFoundError:
    print(" Файл не найден. Положи train.csv в папку со скриптом.")

data_base_conn=sqlite3.connect('kaggle_db')

df_raw.to_sql('data_base1', data_base_conn , if_exists='replace', index=False)
print(" Данные загружены в SQL таблицу")



query="""
SELECT (select avg(Fare) from data_base1) as average_price,Passengerid,Age,Fare,Survived from data_base1
WHERE fare>70 
LIMIT 200
"""
df=pd.read_sql_query(query,data_base_conn)
print(df.columns.tolist())
data_base_conn.close()
df['median_age'] = df['Age'].median()
df['Is_Rich'] = (df['Fare'] > 100).astype(int)
mode_fare=df['Fare'].mode()[0]
df['Fare']=df['Fare'].fillna(mode_fare) #change 0 fare to most common fare
# Корреляция между ценой билета и выживаемостью (NumPy)
corr = np.corrcoef(df['Is_Rich'].values, df['Survived'].values)[0, 1]
print(f"\nКорреляция Rich и Survived: {corr:.4f}")
df.to_csv('cleaned_titanic.csv', index=False)
print("\n Очищенные данные сохранены в cleaned_titanic.csv")
