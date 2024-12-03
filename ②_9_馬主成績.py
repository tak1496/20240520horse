import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
import numpy as np
import scipy.stats
import sys

df_race_list = pd.read_csv('encoded/race_list.csv')
df_race_list["owner_id"] = df_race_list["日付"].astype(str) +'_'+ df_race_list["馬主"].astype(str)

df_race_id = df_race_list.copy()
df_race_id = df_race_id.groupby(['race_id','日付']).agg({'馬番':'max'}).reset_index()
df_race_id = df_race_id.sort_values(['日付','race_id'])

try:
    df_rate = pd.read_csv('encoded/owner_win_rate.csv')
    df_rate = pd.merge(df_race_list, df_rate, on='owner_id', how='left')
    df_rate = df_rate.sort_values(['日付'])
    df_rate = df_rate.loc[:, ["race_id","着順","日付","馬主","owner_id","馬主成績"]]
    df_concat = df_rate[ df_rate["馬主成績"].notnull() ]
    df_processing = df_rate[ df_rate["馬主成績"].isnull() ]
    df_processing = df_processing.groupby(["日付","馬主","owner_id"]).agg({'着順':'mean'}).reset_index()
    df_processing = df_processing.sort_values(['日付'])    
except:
    # データの読み込み
    yearStart = 2017
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
    
    df_race_id = df_combined.copy()
    df_race_id = df_race_id.groupby(['race_id','日付']).agg({'馬番':'max'}).reset_index()
    df_race_id = df_race_id.sort_values(['日付','race_id'])

    df_combined["owner_id"] = df_combined["日付"].astype(str) +'_'+ df_combined["馬主"].astype(str)
    df_processing = df_combined.loc[:, ["race_id","着順","日付","芝・ダート","コース内外","場id","距離","馬主","owner_id"]]
    df_processing = df_processing.groupby(["日付","馬主","owner_id"]).agg({'着順':'mean'}).reset_index()
    df_processing = df_processing.sort_values(['日付'])

for i, row in enumerate(df_processing.itertuples()):
    idx = row[0]
    df_processing.loc[idx, "馬主成績"] = 0.5
    d = df_processing.loc[idx,"日付"] #日付
    on = df_processing.loc[idx,"馬主"]

    owner_id = str(d) +'_'+ str(on)
    df_ol = df_processing[ (df_processing["馬主"]==on) & (df_processing["日付"]<d) & (df_processing["馬主成績"].notnull()) ]
    df_ol = df_ol.sort_values(['日付'])
    if df_ol.empty==False:
        df_ol = df_ol.tail(1)
        df_processing.loc[idx,"馬主成績"] = df_ol.loc[df_ol.index.values.tolist(),"馬主成績"].values.tolist()[0]
    else:
        df_processing.loc[idx,"馬主成績"] = 0.5

    p = df_processing.loc[idx,"馬主成績"]
    point = round(0.2 * (1-(df_processing.loc[idx,"着順"]/18)) + 0.8 * p ,2)
    df_processing.loc[idx,"馬主成績"] = point
    print(d,owner_id,point)

try:
    df_processing = pd.concat([df_processing, df_concat])
except:
    pass

#↓後で直す
df_processing = df_processing.groupby(['owner_id']).agg({'馬主成績':'mean'}).reset_index()
df_processing = df_processing.drop(["race_id"],axis=1)
#df_processing = df_processing.drop(["着順","日付","馬主"],axis=1)

print("データ変換：完了")

# エンコーディングとスケーリング後のデータを確認
print("ファイル出力：開始")
df_processing.to_csv('encoded/owner_win_rate.csv', index=False)
df_processing.to_csv('encoded/owner_win_rate_shift.csv', index=False,encoding="SHIFT_JIS")
print("ファイル出力：終了")
