import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
import numpy as np
import scipy.stats
import sys
import datetime

features_mappings = {"左回":0,"右回":1,"直線長":2,"直線短":3,"急カーブ":4,"複合カーブ":5,"スパイラル":6,"小回":7,"ゴール前平坦":8,"ゴール前緩坂":9,"ゴール前急坂":10,'芝':11,'ダート':12}
course_features = {
    '1_0_0': ["右回", "直線短",  "複合カーブ",    "ゴール前平坦",    "芝"     ],
    '1_1_0': ["右回", "直線短",  "複合カーブ",    "ゴール前平坦",    "ダート" ],
    '2_0_0': ["右回", "直線短",  "小回",          "ゴール前平坦",    "芝"     ],
    '2_1_0': ["右回", "直線短",  "小回",          "ゴール前平坦",    "ダート" ],
    '3_0_0': ["右回", "直線短",  "スパイラル",    "ゴール前平坦",    "芝"     ],
    '3_1_0': ["右回", "直線短",  "スパイラル",    "ゴール前平坦",    "ダート" ],
    '4_0_0': ["左回", "直線短",  "急カーブ",      "ゴール前平坦",    "芝"     ],
    '4_1_0': ["左回", "直線短",  "急カーブ",      "ゴール前平坦",    "ダート" ],
    '4_0_1': ["左回", "直線長",  "急カーブ",      "ゴール前平坦",    "芝"     ],
    '5_0_0': ["左回", "直線長",  "複合カーブ",    "ゴール前緩坂",    "芝"     ],
    '5_1_0': ["左回", "直線長",  "複合カーブ",    "ゴール前緩坂",    "ダート" ],
    '6_0_0': ["右回", "直線短",  "小回",          "ゴール前急坂",    "芝"     ],
    '6_1_0': ["右回", "直線短",  "小回",          "ゴール前急坂",    "ダート" ],
    '6_0_1': ["右回", "直線短",  "複合カーブ",    "ゴール前急坂",    "芝"     ],
    '7_0_0': ["左回", "直線長",  "スパイラル",    "ゴール前急坂",    "芝"     ],
    '7_1_0': ["左回", "直線長",  "スパイラル",    "ゴール前急坂",    "ダート" ],
    '8_0_0': ["右回", "直線短",  "複合カーブ",    "ゴール前平坦",    "芝"     ],
    '8_1_0': ["右回", "直線短",  "複合カーブ",    "ゴール前平坦",    "ダート" ],
    '8_0_1': ["右回", "直線長",  "複合カーブ",    "ゴール前平坦",    "芝"     ],
    '9_0_0': ["右回", "直線短",  "複合カーブ",    "ゴール前急坂",    "芝"     ],
    '9_1_0': ["右回", "直線短",  "複合カーブ",    "ゴール前急坂",    "ダート" ],
    '9_0_1': ["右回", "直線長",  "複合カーブ",    "ゴール前急坂",    "芝"     ],
    '10_0_0':["右回", "直線短",  "スパイラル",    "ゴール前平坦",    "芝"     ],
    '10_1_0':["右回", "直線短",  "スパイラル",    "ゴール前平坦",    "ダート" ]
}

df_race_list = pd.read_csv('encoded/race_list.csv')
df_race_list["race_horse_id"] = df_race_list["race_id"].astype(str) +'_'+ df_race_list["馬"]

df_race_id = df_race_list.copy()
df_race_id = df_race_id.groupby(['race_id','日付']).agg({'タイム差':'max'}).reset_index()
df_race_id = df_race_id.sort_values(['日付','race_id'])

try:
    df_rate = pd.read_csv('encoded/course_features.csv')
    df_rate = pd.merge(df_race_list, df_rate, on='race_horse_id', how='left')
    df_rate = df_rate.sort_values(['日付','race_id'])
    df_rate = df_rate.loc[:, ["race_id","馬","着順","日付","芝・ダート","コース内外","場id","タイム差","race_horse_id","左回","右回","直線長","直線短","急カーブ","複合カーブ","スパイラル","小回","ゴール前平坦","ゴール前緩坂","ゴール前急坂","芝","ダート"]]
    df_concat = df_rate[ df_rate["左回"].notnull() ]
    df_processing = df_rate[ df_rate["左回"].isnull() ]
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

    df_combined["race_horse_id"] = df_combined["race_id"].astype(str) +'_'+ df_combined["馬"]
    df_processing = df_combined.drop(["騎手","枠番","馬番","走破時間","勝ち時計","オッズ","通過順","体重","体重変化","性","齢","斤量","上がり","人気","レース名","開催","回り","天気","クラス","距離","馬場","場名","6F","33Lap","side3","side4","脚質","通過順3","通過順4","ペース","3Fペース","トレセン","調教師","馬主","Sラップ"],axis=1)

    keys_output = features_mappings.keys()
    for key in keys_output:
        df_processing[key] = 0.5

    df_processing = df_processing.sort_values(['日付','race_id'])
    df_rate = df_processing
    #df_processing = df_processing[ df_processing["馬"]=="イクイノックス" ]

for i, row in enumerate(df_processing.itertuples()):
    idx = row[0]
    df_processing.loc[idx, "左回":"ダート"] = 0.5
    race_id = df_processing.loc[idx,"race_id"]
    hn = df_processing.loc[idx,"馬"]
    d = df_processing.loc[idx,"日付"]
    n = df_race_id[ df_race_id["race_id"]==race_id ]
    n = n.loc[n.index.values.tolist(),"タイム差"].values.tolist()[0]

    df_hl = df_rate[ (df_rate["馬"]==hn) & (df_rate["日付"]<d) ]
    df_hl = df_hl.sort_values(['日付'])
    if df_hl.empty==False:
        df_hl = df_hl.tail(1)
        df_processing.loc[idx, "左回":"ダート"] = df_hl.loc[df_hl.index.values.tolist(),"左回":"ダート"].values.tolist()[0]
    else:
        df_processing.loc[idx, "左回":"ダート"] = 0.5

    course_id = df_processing.loc[idx,"場id"].astype(str)+'_'+df_processing.loc[idx,"芝・ダート"].astype(str)+'_'+df_processing.loc[idx,"コース内外"].astype(str)
    course_data = course_features[course_id]
    for col in course_data:
        p = df_processing.loc[idx, col]
        if df_processing.loc[idx,"タイム差"]!=0:
            point = round( (0.2 * (1-(df_processing.loc[idx,"タイム差"]/n))) + (0.8 * p) ,2)
        else:
            point = round( 0.2 + (0.8 * p) ,2)

        df_processing.loc[idx, col] = point

    print(d,hn,point,p,n)

try:
    df_processing = pd.concat([df_processing, df_concat])
except:
    pass

df_processing = df_processing.drop(["race_id","馬","着順","日付","芝・ダート","コース内外","場id","タイム差"],axis=1)

print("データ変換：完了")

# エンコーディングとスケーリング後のデータを確認
print("ファイル出力：開始")
df_processing.to_csv('encoded/course_features.csv', index=False)
df_processing.to_csv('encoded/course_features_shift.csv', index=False,encoding="SHIFT_JIS")
print("ファイル出力：終了")
