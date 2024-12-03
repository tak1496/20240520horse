from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import time

# データの読み込み
df_combined = pd.read_csv('encoded/race_list.csv')
try:
    df_combined = df_combined.drop(["父","父父","母父"],axis=1)
except:
    pass

all_data = df_combined.groupby(["馬"]).agg({'race_id':'max'}).reset_index()

try:
    df_horse = pd.read_csv('encoded/horse_pedigree.csv')
except:
    df_horse = pd.DataFrame(columns = ["馬","race_id","父","父父","母父"])

all_data = pd.merge(all_data, df_horse, on='馬', how='left')
all_data = all_data[ all_data["父"].isnull() ]

print("血統データ作成")

header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"}

for i, row in enumerate(all_data.itertuples()):
    idx = row[0]
    hn = all_data.loc[idx,"馬"]
    race_id = all_data.loc[idx,"race_id"]

    url = "https://race.netkeiba.com/race/shutuba.html?race_id="+str(race_id)
    for zzz in range(10):
        time.sleep(1)
        response = requests.get(url, headers=header)
        if response.status_code == 200:
            break

    soup = BeautifulSoup(response.content, "html.parser")
    # テーブルを指定
    try:
        a_tag = soup.find("a", {"title": hn[:9],"target":"_blank"})
        url2 = a_tag.get('href')        
    except:
        a_tag = soup.find("a", {"title": hn,"target":"_blank"})
        url2 = a_tag.get('href')
        
    for zzz in range(10):
        time.sleep(1)
        response2 = requests.get(url2, headers=header)
        if response.status_code == 200:
            break

    soup2 = BeautifulSoup(response2.content, "html.parser")
    table2 = soup2.find("table", {"class": "blood_table"})
    main_rows2 = table2.find_all("tr")
    cols2 = main_rows2[0].find_all("td")
    ft = cols2[0].text.strip()
    gf = cols2[1].text.strip()
    cols2 = main_rows2[2].find_all("td")
    mf = cols2[1].text.strip()
    data = {'馬': [hn], '父': [ft], '父父': [gf], '母父': [mf] }
    pedigree = pd.DataFrame(data)
    df_horse = pd.concat([df_horse, pedigree])
    print(hn,ft)
    hn=None
    race_id=None
    url=None
    response=None
    soup=None
    a_tag=None
    url2=None
    response2=None
    soup2=None
    table2=None
    main_rows2=None
    cols2=None
    data=None
    pedigree=None
    time.sleep(1)

print("血統データ保存中")
df_horse.to_csv('encoded/horse_pedigree.csv', index=False)

##血統データを結合
print("血統データ結合")
df_combined = pd.merge(df_combined, df_horse, on='馬', how='left')
df_combined.to_csv('encoded/race_list.csv', index=False)
df_combined.head(10000).to_csv('encoded/race_list_shift.csv', index=False, encoding="shift_jis")
