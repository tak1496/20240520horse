import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
import numpy as np
import scipy.stats
import sys
import datetime

course_mappings = {
    "C1_0_0":9, "C1_1_0":10, "C2_0_0":11, "C2_1_0":12, "C3_0_0":13, "C3_1_0":14, "C4_0_0":15, "C4_0_1":16, "C4_1_0":17, "C5_0_0":18, "C5_1_0":19, "C6_0_0":20, "C6_0_1":21, "C6_1_0":22, "C7_0_0":23, "C7_1_0":24, "C8_0_0":25, "C8_0_1":26, "C8_1_0":27, "C9_0_0":28, "C9_0_1":29, "C9_1_0":30, "C10_0_0":31, "C10_1_0":32
}

df_race_list = pd.read_csv('encoded/race_list.csv')
df_race_list["race_horse_id"] = df_race_list["race_id"].astype(str) +'_'+ df_race_list["馬"]

df_race_id = df_race_list.copy()
df_race_id = df_race_id.groupby(['race_id','日付']).agg({'タイム差':'max'}).reset_index()
df_race_id = df_race_id.sort_values(['日付','race_id'])

try:
    df_rate = pd.read_csv('encoded/course_win_rate.csv')
    df_rate = pd.merge(df_race_list, df_rate, on='race_horse_id', how='left')
    df_rate = df_rate.sort_values(['日付','race_id'])
    df_rate = df_rate.loc[:, ["race_id","馬","着順","日付","芝・ダート","コース内外","場id","タイム差","race_horse_id","C1_0_0","C1_1_0","C2_0_0","C2_1_0","C3_0_0","C3_1_0","C4_0_0","C4_0_1","C4_1_0","C5_0_0","C5_1_0","C6_0_0","C6_0_1","C6_1_0","C7_0_0","C7_1_0","C8_0_0","C8_0_1","C8_1_0","C9_0_0","C9_0_1","C9_1_0","C10_0_0","C10_1_0"]]
    #df_rate = df_rate.drop(["騎手","枠番","馬番","走破時間","体重","体重変化","性","齢","斤量","上がり","クラス","距離","回り","馬場","6F","33Lap","side3","side4","脚質","通過順3","通過順4","ペース","3Fペース","タイム差","斤量比","class_id","course_id","PCI","平均体重","体重差","平均PCI","PCI差","日付1","走破時間1","33Lap1","通過順31","通過順41","ペース1","斤量比1","PCI1","体重差1","日付2","走破時間2","33Lap2","通過順32","通過順42","ペース2","斤量比2","PCI2","体重差2","日付3","走破時間3","33Lap3","通過順33","通過順43","ペース3","斤量比3","PCI3","体重差3","日付4","走破時間4","33Lap4","通過順34","通過順44","ペース4","斤量比4","PCI4","体重差4","日付5","走破時間5","33Lap5","通過順35","通過順45","ペース5","斤量比5","PCI5","体重差5"], axis=1)
    df_concat = df_rate[ df_rate["C1_0_0"].notnull() ]
    df_processing = df_rate[ df_rate["C1_0_0"].isnull() ]
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

    for i in range(1,11,1):
        for j in range(0,2,1):
            for k in range(0,2,1):
                if (i==4 and j==0 and k==1) or (i==6 and j==0 and k==1) or (i==8 and j==0 and k==1) or (i==9 and j==0 and k==1):
                    df_processing["C"+str(i)+'_'+str(j)+'_'+str(k)]=0.5
                elif (k==0):
                    df_processing["C"+str(i)+'_'+str(j)+'_'+str(k)]=0.5
                    
    df_processing = df_processing.sort_values(['日付','race_id'])
    df_rate = df_processing
    #df_processing = df_processing[ df_processing["馬"]=="イクイノックス" ]

for i, row in enumerate(df_processing.itertuples()):
    idx = row[0]
    df_processing.loc[idx,"C1_0_0":"C10_1_0"] = 0.5
    race_id = df_processing.loc[idx,"race_id"]
    hn = df_processing.loc[idx,"馬"]
    d = df_processing.loc[idx,"日付"]
    n = df_race_id[ df_race_id["race_id"]==race_id ]
    n = n.loc[n.index.values.tolist(),"タイム差"].values.tolist()[0]

    df_hl = df_rate[ (df_rate["馬"]==hn) & (df_rate["日付"]<d) ]
    df_hl = df_hl.sort_values(['日付'])
    if df_hl.empty==False:
        df_hl = df_hl.tail(1)        
        df_processing.loc[idx,"C1_0_0":"C10_1_0"] = df_hl.loc[df_hl.index.values.tolist(),"C1_0_0":"C10_1_0"].values.tolist()[0]
    else:
        df_processing.loc[idx,"C1_0_0":"C10_1_0"] = 0.5
        
    course_id = "C"+df_processing.loc[idx,"場id"].astype(str)+'_'+df_processing.loc[idx,"芝・ダート"].astype(str)+'_'+df_processing.loc[idx,"コース内外"].astype(str)
    col = course_mappings[course_id]
    p = df_processing.iloc[i,col]
    if df_processing.loc[idx,"タイム差"]!=0:
        point = round( (0.2 * (1-(df_processing.loc[idx,"タイム差"]/n))) + (0.8 * p) ,2)
    else:
        point = round( 0.2 + (0.8 * p) ,2)
    df_processing.iloc[i,col] = point
    print(d,hn,point,p,n)

try:
    df_processing = pd.concat([df_processing, df_concat])
except:
    pass

df_processing = df_processing.drop(["race_id","馬","着順","日付","芝・ダート","コース内外","場id","タイム差"],axis=1)

print("データ変換：完了")

# エンコーディングとスケーリング後のデータを確認
print("ファイル出力：開始")
df_processing.to_csv('encoded/course_win_rate.csv', index=False)
df_processing.to_csv('encoded/course_win_rate_shift.csv', index=False, encoding="SHIFT_JIS")
print("ファイル出力：終了")
