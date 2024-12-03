import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
import numpy as np
import scipy.stats
import sys

df_race_list = pd.read_csv('encoded/race_list.csv')
df_race_list["father_id"] = df_race_list["race_id"].astype(str) +'_'+ df_race_list["場id"].astype(str) +'_'+ df_race_list["芝・ダート"].astype(str) +'_'+ df_race_list["コース内外"].astype(str) +'_'+ df_race_list["距離"].astype(str) +'_'+ df_race_list["父"].astype(str)

df_race_id = df_race_list.copy()
df_race_id = df_race_id.groupby(['race_id','日付']).agg({'タイム差':'max'}).reset_index()
df_race_id = df_race_id.sort_values(['日付','race_id'])

try:
    df_rate = pd.read_csv('encoded/father_win_rate.csv')
    df_rate = pd.merge(df_race_list, df_rate, on='father_id', how='left')
    df_rate = df_rate.sort_values(['日付','race_id'])
    df_rate = df_rate.loc[:, ["race_id","日付","芝・ダート","コース内外","場id","タイム差","距離","父","father_id","父成績"]]
    df_concat = df_rate[ df_rate["父成績"].notnull() ]
    df_processing = df_rate[ df_rate["父成績"].isnull() ]
    df_processing = df_processing.groupby(["race_id","日付","芝・ダート","コース内外","場id","距離","父","father_id"]).agg({'タイム差':'mean'}).reset_index()
    df_processing = df_processing.sort_values(['日付','race_id'])
except:
    # データの読み込み
    yearStart = 2011
    yearEnd = 2024
    yearList = np.arange(yearStart, yearEnd + 1, 1, int)
    df = []
    print("ファイル取得：開始")
    for for_year in yearList:
        var_path = "data/" + str(for_year) + ".csv"
        var_data = pd.read_csv(
            var_path,
            encoding="SHIFT-JIS",
            header=0,
            parse_dates=['日付'], 
            date_parser=lambda x: pd.to_datetime(x, format='%Y年%m月%d日')
        )
    
        # '着順'カラムの値を数値に変換しようとして、エラーが発生する場合はNaNにする
        var_data['着順'] = pd.to_numeric(var_data['着順'], errors='coerce')
        # NaNの行を削除する
        var_data = var_data.dropna(subset=['着順'])
        
        # 必要であれば、'着順'カラムのデータ型を整数に変換する
        var_data['着順'] = var_data['着順'].astype(int)
    
        df.append(var_data)

    print("ファイル取得：完了")
    print("データ変換：開始")

    # DataFrameの結合
    df_combined = pd.concat(df, ignore_index=True)

    # mapを使ったラベルの変換
    shiba_mapping = {'芝': 0, 'ダ': 1, '障': 2}
    df_combined['芝・ダート'] = df_combined['芝・ダート'].map(shiba_mapping)
    df_combined = df_combined[ df_combined["芝・ダート"]!=2]

    # 既存のコード：走破時間を秒に変換
    time_parts = df_combined['走破時間'].str.split(':', expand=True)
    seconds = time_parts[0].astype(float) * 60 + time_parts[1].str.split('.', expand=True)[0].astype(float) + time_parts[1].str.split('.', expand=True)[1].astype(float) / 10
    df_combined['走破時間'] = seconds
    df_combined['タイム差'] = round( seconds - df_combined['勝ち時計'].astype(float),1)

    df_race_id = df_combined.copy()
    df_race_id = df_race_id.groupby(['race_id','日付']).agg({'タイム差':'max'}).reset_index()
    df_race_id = df_race_id.sort_values(['日付','race_id'])

    df_horse = pd.read_csv('encoded/horse_pedigree.csv')
    df_combined = pd.merge(df_combined, df_horse, on='馬', how='left')
    df_combined["father_id"] = df_combined["race_id"].astype(str) +'_'+ df_combined["場id"].astype(str) +'_'+ df_combined["芝・ダート"].astype(str) +'_'+ df_combined["コース内外"].astype(str) +'_'+ df_combined["距離"].astype(str) +'_'+ df_combined["父"].astype(str)
    df_processing = df_combined.loc[:, ["race_id","日付","芝・ダート","コース内外","場id","タイム差","距離","父","father_id"]]
    df_processing = df_processing.groupby(["race_id","日付","芝・ダート","コース内外","場id","距離","父","father_id"]).agg({"タイム差":'mean'}).reset_index()
    df_processing["父成績"] = 0.5
    df_processing = df_processing.sort_values(['日付','race_id'])
    df_rate = df_processing

for i, row in enumerate(df_processing.itertuples()):
    idx = row[0]
    df_processing.loc[idx, "父成績"] = 0.5
    race_id = df_processing.loc[idx,"race_id"]
    d = df_processing.loc[idx,"日付"] #日付
    c = df_processing.loc[idx,"場id"] #場id
    sd = df_processing.loc[idx,"芝・ダート"] #芝・ダート
    us = df_processing.loc[idx,"コース内外"] #コース内外
    dis = df_processing.loc[idx,"距離"] #距離
    ft = df_processing.loc[idx,"父"]
    n = df_race_id[ df_race_id["race_id"]==race_id ]
    n = n.loc[n.index.values.tolist(),"タイム差"].values.tolist()[0]

    father_id = str(race_id) +'_'+ str(c) +'_'+ str(sd) +'_'+ str(us) +'_'+ str(dis) +'_'+ str(ft)
    df_fl = df_rate[ (df_rate["父"]==ft) & (df_rate["場id"]==c) & (df_rate["芝・ダート"]==sd) & (df_rate["コース内外"]==us) & (df_rate["距離"]==dis) & (df_rate["race_id"]<race_id) & (df_rate["父成績"].notnull()) ]
    df_fl = df_fl.sort_values(['日付'])
    if df_fl.empty==False:
        df_fl = df_fl.tail(1)
        df_processing.loc[idx,"父成績"] = df_fl.loc[df_fl.index.values.tolist(),"父成績"].values.tolist()[0]
    else:
        df_processing.loc[idx,"父成績"] = 0.5

    p = df_processing.loc[idx,"父成績"]
    if df_processing.loc[idx,"タイム差"]!=0:
        point = round( (0.2 * (1-(df_processing.loc[idx,"タイム差"]/n))) + (0.8 * p) ,2)
    else:
        point = round( 0.2 + (0.8 * p) ,2)

    df_processing.loc[idx,"父成績"] = point
    print(d,father_id,point,p,n)

try:
    df_processing = pd.concat([df_processing, df_concat])
except:
    pass

df_processing = df_processing.drop(["race_id","日付","芝・ダート","コース内外","場id","タイム差","距離","父"],axis=1)
#↓後で直す
df_processing = df_processing.groupby(['father_id']).agg({'父成績':'mean'}).reset_index()

print("データ変換：完了")

# エンコーディングとスケーリング後のデータを確認
print("ファイル出力：開始")
df_processing.to_csv('encoded/father_win_rate.csv', index=False)
df_processing.head(10000).to_csv('encoded/father_win_rate_shift.csv', index=False,encoding="SHIFT_JIS")
print("ファイル出力：終了")
