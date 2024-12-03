import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
import numpy as np
import scipy.stats
import sys

col_mappings = ["枠番","馬番","走破時間","斤量","上がり","33Lap","通過順3","通過順4","ペース","タイム差","斤量比","PCI","体重差"]

df_race_list = pd.read_csv('encoded/race_list.csv')
df_race_list["race_horse_id"] = df_race_list["race_id"].astype(str) +'_'+ df_race_list["馬"].astype(str)

df_rate = pd.read_csv('encoded/course_ability.csv')
df_race_list = pd.merge(df_race_list, df_rate, on='race_horse_id', how='left')
df_race_list = df_race_list.sort_values(['日付','race_id'])
df_race_list = df_race_list.drop(["騎手","着順","体重","体重変化","性","齢","クラス","回り","馬場","コース内外","6F","side3","side4","脚質","3Fペース","トレセン","調教師","馬主","Sラップ","走破時間換算","class_id","course_id","平均体重","平均PCI","PCI差","父","父父","母父"],axis=1)
df_concat = df_race_list[ df_race_list.isnull().sum(axis=1)<=1400 ]
df_processing = df_race_list[ df_race_list.isnull().sum(axis=1)>1400 ]
df_processing = df_processing.sort_values(['日付','race_id'])

for i, row in enumerate(df_processing.itertuples()):
    idx = row[0]
    hn = df_processing.loc[idx,"馬"]
    d = df_processing.loc[idx,"日付"]
    c = df_processing.loc[idx,"場id"]
    dis = df_processing.loc[idx,"距離"]
    gd = df_processing.loc[idx,"芝・ダート"]

    colm="C"+str(c)+"_"+str(dis)+"_"+str(gd)
    
    df_hl = df_race_list[ (df_race_list["馬"]==hn) & (df_race_list["日付"]<d) ]
    df_hl = df_hl.sort_values(['日付'])
    if df_hl.empty==False:
        df_hl = df_hl.tail(1)
        df_processing.loc[idx,"C1_1000_0_枠番":"C10_2600_0_体重差"] = df_hl.loc[df_hl.index.values.tolist(),"C1_1000_0_枠番":"C10_2600_0_体重差"].values.tolist()[0]

    chk = 0
    if df_processing.loc[idx, colm+"_走破時間"]=="":
        chk=1
    elif (df_race_list.loc[idx, "タイム差"].astype(float) <= df_race_list.loc[idx, colm+"_タイム差"].astype(float)) and (df_race_list.loc[idx, "走破時間"].astype(float) <= df_race_list.loc[idx, colm+"_走破時間"].astype(float)):
        chk=1

    if chk==1:
        for j in range(len(col_mappings)):
            df_processing.loc[idx, colm+"_"+col_mappings[j]] = df_processing.loc[idx,col_mappings[j]]

    print(i,d, hn)

try:
    df_processing = pd.concat([df_processing, df_concat])
except:
    pass

df_processing.to_csv('encoded/course_ability.csv', index=False)
print("ファイル出力：終了")
