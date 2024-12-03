import pandas as pd
import numpy as np
import scipy.stats
import sys

print("ファイル取得：開始")
df_race_list = pd.read_csv('encoded/race_list.csv')

df_race_list["race_horse_id"] = df_race_list["race_id"].astype(str) +'_'+ df_race_list["馬"]
df_race_list["umaban_id"] = df_race_list["race_id"].astype(str) +'_'+ df_race_list["場id"].astype(str) +'_'+ df_race_list["芝・ダート"].astype(str) +'_'+ df_race_list["コース内外"].astype(str) +'_'+ df_race_list["距離"].astype(str) +'_'+ df_race_list["馬番"].astype(str)
df_race_list["jockey_id"] = df_race_list["race_id"].astype(str) +'_'+ df_race_list["場id"].astype(str) +'_'+ df_race_list["芝・ダート"].astype(str) +'_'+ df_race_list["コース内外"].astype(str) +'_'+ df_race_list["距離"].astype(str) +'_'+ df_race_list["騎手"].astype(str)
df_race_list["tracen_id"] = df_race_list["race_id"].astype(str) +'_'+ df_race_list["場id"].astype(str) +'_'+ df_race_list["芝・ダート"].astype(str) +'_'+ df_race_list["コース内外"].astype(str) +'_'+ df_race_list["距離"].astype(str) +'_'+ df_race_list["トレセン"].astype(str)
df_race_list["trainer_id"] = df_race_list["race_id"].astype(str) +'_'+ df_race_list["場id"].astype(str) +'_'+ df_race_list["芝・ダート"].astype(str) +'_'+ df_race_list["コース内外"].astype(str) +'_'+ df_race_list["距離"].astype(str) +'_'+ df_race_list["調教師"].astype(str)
df_race_list["owner_id"] = df_race_list["日付"].astype(str) +'_'+ df_race_list["馬主"].astype(str)
df_race_list["father_id"] = df_race_list["race_id"].astype(str) +'_'+ df_race_list["場id"].astype(str) +'_'+ df_race_list["芝・ダート"].astype(str) +'_'+ df_race_list["コース内外"].astype(str) +'_'+ df_race_list["距離"].astype(str) +'_'+ df_race_list["父"].astype(str)

try:
    df_rate = pd.read_csv('encoded/course_win_rate.csv')
    df_race_list = pd.merge(df_race_list, df_rate, on='race_horse_id', how='left')
    df_rate = []
except:
    pass

try:
    df_rate = pd.read_csv('encoded/course_features.csv')
    df_race_list = pd.merge(df_race_list, df_rate, on='race_horse_id', how='left')
    df_rate = []
except:
    pass

try:
    df_rate = pd.read_csv('encoded/umaban_win_rate.csv')
    df_race_list = pd.merge(df_race_list, df_rate, on='umaban_id', how='left')
    df_rate = []
except:
    pass

try:
    df_rate = pd.read_csv('encoded/jockey_win_rate.csv')
    df_race_list = pd.merge(df_race_list, df_rate, on='jockey_id', how='left')
    df_rate = []
except:
    pass

try:
    df_rate = pd.read_csv('encoded/trainer_win_rate.csv')
    df_race_list = pd.merge(df_race_list, df_rate, on='trainer_id', how='left')
    df_rate = []
except:
    pass

try:
    df_rate = pd.read_csv('encoded/owner_win_rate.csv')
    df_race_list = pd.merge(df_race_list, df_rate, on='owner_id', how='left')
    df_rate = []
except:
    pass

try:
    df_rate = pd.read_csv('encoded/father_win_rate.csv')
    df_race_list = pd.merge(df_race_list, df_rate, on='father_id', how='left')
    df_rate = []
except:
    pass

try:
    df_rate = pd.read_csv('encoded/course_ability.csv')
    #df_rate["race_horse_id"] = df_rate["race_id"].astype(str) +'_'+ df_rate["馬"]
    #df_rate = df_rate.drop(["index","race_id","馬","枠番","馬番","走破時間","着順","斤量","上がり","日付","芝・ダート","距離","場id","33Lap","通過順3","通過順4","ペース","タイム差","斤量比","PCI","体重差"],axis=1)
    df_race_list = pd.merge(df_race_list, df_rate, on='race_horse_id', how='left')
    df_rate = []
except:
    pass

'''
df_rate = pd.read_csv('encoded/tracen_win_rate.csv')
df_race_list = pd.merge(df_race_list, df_rate, on='tracen_id', how='left')
df_rate = []
'''

df_race_list = df_race_list.drop(["race_horse_id","umaban_id","jockey_id","tracen_id","trainer_id","owner_id","father_id"],axis=1)

print("ファイル出力：開始")
df_race_list.to_csv('encoded/race_list.csv', index=False)
df_race_list.head(10000).to_csv('encoded/race_list_shift.csv', index=False, encoding="shift_jis")
print("ファイル出力：終了")

