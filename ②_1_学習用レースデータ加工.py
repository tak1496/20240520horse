import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
import numpy as np
import scipy.stats
import sys

dis_mappings = {
    '0_1000', '0_1200', '0_1400', '0_1500', '0_1600', '0_1800', '0_2000', '0_2200', '0_2300', '0_2400', '0_2500', '0_2600', '0_3000', '0_3200', '0_3400', '0_3600',
    '1_1000', '1_1150', '1_1200', '1_1300', '1_1400', '1_1600', '1_1700', '1_1800', '1_1900', '1_2000', '1_2100', '1_2400', '1_2500'
}

class_mappings = {'4歳以上':3, '４歳以上':3, '3歳以上':3, '３歳以上':3, '3歳':2, '３歳':2, '2歳':1, '２歳':1,'障害':0}
l=["01","02","03","04","05","06","07","08","09","10"]
                
class_list =[]
for dis in dis_mappings:
    for i in range(4):
        class_list.append( str(i) +'_'+ dis )

course_list =[]        
for i in range(10):
    for l in range(4):
        for k in dis_mappings:
            course_list.append( str(i+1) +'_'+ str(l) +'_'+ str(k) )

def class_mapping(row):
    for key, value in class_mappings.items():
        if key in row:
            return value
    return 0  # If no mapping is found, return 0

def age_mapping(age):
    age = int(age)
    if age>3:
        return 3
    else:
        return age-1

def weight_time_mapping(w):
    if w>=12:
        return 1
    elif w>=10:
        return 0.6
    elif w>=8:
        return 0.3
    elif w<=-12:
        return 1
    elif w<=-10:
        return 0.6
    elif w<=-8:
        return 0.3
    else:
        return 0

def class_pace(x):
    if x<48:
        pace = 3
    elif x<50:
        pace = 2.5
    elif x<53:
        pace = 2
    elif x<56:
        pace = 1.5
    else:
        pace = 1
    return pace

# データの読み込み
yearStart = 2013
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

# 既存のコード：走破時間を秒に変換
time_parts = df_combined['走破時間'].str.split(':', expand=True)
seconds = time_parts[0].astype(float) * 60 + time_parts[1].str.split('.', expand=True)[0].astype(float) + time_parts[1].str.split('.', expand=True)[1].astype(float) / 10
df_combined['走破時間'] = seconds
df_combined['タイム差'] = round( seconds - df_combined['勝ち時計'].astype(float),1)

# 前方補完
seconds = seconds.fillna(method='ffill')

# 平均と標準偏差を計算
mean_seconds = seconds.mean()
std_seconds = seconds.std()

# 標準化を行う
df_combined['走破時間換算'] = -((seconds - mean_seconds) / std_seconds)

# 外れ値の処理：-3より小さい値は-3に、2.5より大きい値は2に変換
df_combined['走破時間換算'] = df_combined['走破時間換算'].apply(lambda x: -3 if x < -3 else (2 if x > 2.5 else x))

# 2回目の標準化の前に再度平均と標準偏差を計算
mean_seconds_2 = df_combined['走破時間換算'].mean()
std_seconds_2 = df_combined['走破時間換算'].std()

# 2回目の標準化
df_combined['走破時間換算'] = (df_combined['走破時間換算'] - mean_seconds_2) / std_seconds_2
df_combined['走破時間換算'] = df_combined['走破時間換算'].round(3)
print('1回目平均' + str(mean_seconds))
print('2回目平均' + str(mean_seconds_2))
print('1回目標準偏差' + str(std_seconds))
print('2回目標準偏差' + str(std_seconds_2))

# データを格納するDataFrameを作成
time_df = pd.DataFrame({
    'Mean': [mean_seconds, mean_seconds_2],
    'Standard Deviation': [std_seconds, std_seconds_2]
})
# indexに名前を付ける
time_df.index = ['First Time', 'Second Time']
# DataFrameをCSVファイルとして出力
time_df.to_csv('config/standard_deviation.csv')

#通過順の平均を出す
pas = df_combined['通過順'].str.split('-', expand=True)
df_combined['通過順'] = pas.astype(float).mean(axis=1)

df_combined['齢'] = df_combined['齢'].mask(df_combined['齢']==1, 10)
df_combined['斤量比'] = round( (df_combined['斤量'] / df_combined['体重']) * (df_combined['距離']/1800) ,3)

# mapを使ったラベルの変換
df_combined['クラス'] = df_combined['クラス'].apply(class_mapping)          
sex_mapping = {'牡':0, '牝': 1, 'セ': 2}
df_combined['性'] = df_combined['性'].map(sex_mapping)
shiba_mapping = {'芝': 0, 'ダ': 1, '障': 2}
df_combined['芝・ダート'] = df_combined['芝・ダート'].map(shiba_mapping)
mawari_mapping = {'右': 0, '左': 1, '芝': 2, '直': 2}
df_combined['回り'] = df_combined['回り'].map(mawari_mapping)
baba_mapping = {'良': 0, '稍': 1, '重': 2, '不': 3}
df_combined['馬場'] = df_combined['馬場'].map(baba_mapping)
tenki_mapping = {'晴': 0, '曇': 1, '小': 2, '雨': 3, '雪': 4}
df_combined['天気'] = df_combined['天気'].map(tenki_mapping)
pace_mapping = {'S': 1, 'M': 2, 'H': 3}
df_combined['ペース'] = df_combined['ペース'].map(pace_mapping)

df_combined = df_combined[ df_combined["芝・ダート"]!=2]

df_combined["6F"] = df_combined["6F"].mask( df_combined["距離"]==1200, df_combined["走破時間"].astype(float)-df_combined["上がり"].astype(float) )
df_combined["6F"] = df_combined["6F"].mask( df_combined["距離"]!=1200, ((df_combined["走破時間"]-df_combined["上がり"]) / (df_combined["距離"]-600)) * 600 )

print("データ変換：完了")

df_combined["class_id"] = df_combined["場id"].astype(str) +'_'+ df_combined["クラス"].astype(str) +'_'+ df_combined["コース内外"].astype(str) +'_'+ df_combined["芝・ダート"].astype(str)  +'_'+ df_combined["距離"].astype(str)
df_combined["course_id"] = df_combined["場id"].astype(str) +'_'+ df_combined["クラス"].astype(str) +'_'+ df_combined["コース内外"].astype(str) +'_'+ df_combined["芝・ダート"].astype(str)

df_course = df_combined.copy()

for i in range(8):
    df_course["aaa"+str(i)]=0

df_course["aaa0"] = df_course["aaa0"].mask( (df_combined['着順']==1) & (df_combined['タイム差']<=0.3) & (df_combined["馬場"]==0), df_combined["走破時間"])
df_course["aaa1"] = df_course["aaa1"].mask( (df_combined['着順']==1) & (df_combined['タイム差']<=0.3) & (df_combined["馬場"]==1), df_combined["走破時間"])
df_course["aaa2"] = df_course["aaa2"].mask( (df_combined['着順']==1) & (df_combined['タイム差']<=0.3) & (df_combined["馬場"]==2), df_combined["走破時間"])
df_course["aaa3"] = df_course["aaa3"].mask( (df_combined['着順']==1) & (df_combined['タイム差']<=0.3) & (df_combined["馬場"]==3), df_combined["走破時間"])
df_course["aaa4"] = df_course["aaa4"].mask( (df_combined['タイム差']<=1) & (df_combined["馬場"]==0), df_combined["走破時間"])
df_course["aaa5"] = df_course["aaa5"].mask( (df_combined['タイム差']<=1) & (df_combined["馬場"]==1), df_combined["走破時間"])
df_course["aaa6"] = df_course["aaa6"].mask( (df_combined['タイム差']<=1) & (df_combined["馬場"]==2), df_combined["走破時間"])
df_course["aaa7"] = df_course["aaa7"].mask( (df_combined['タイム差']<=1) & (df_combined["馬場"]==3), df_combined["走破時間"])

for i in range(8):
    df_course['aaa'+str(i)] = df_course['aaa'+str(i)].replace(0,np.NaN)

df_combined["6F"] = df_combined["6F"].astype(float).round(1)
df_combined["33Lap"] = round( df_combined["6F"].astype(float) - df_combined["上がり"].astype(float) ,2)
df_combined["33Lap"] = round(df_combined["33Lap"].mask(df_combined["距離"]==1200,(df_combined["走破時間"].astype(float)-df_combined["上がり"].astype(float)) - df_combined["上がり"].astype(float)),2)
df_combined["33Lap"] = df_combined["33Lap"].mask(df_combined["距離"]<1200, ((df_combined["6F"].astype(float)/(df_combined["距離"].astype(float)-600))*600)-df_combined["上がり"].astype(float)).round(1)

df_combined["PCI"] = round( ((((((df_combined["走破時間"].astype(float) - df_combined["上がり"].astype(float)) / ((df_combined["距離"].astype(int)/200)-3) )*3) / df_combined["上がり"].astype(float))*100)-50) ,2)

df_combined["PCIペース"] = round( ((((((df_combined["勝ち時計"].astype(float) - df_combined["3Fペース"].astype(float)) / ((df_combined["距離"].astype(int)/200)-3) )*3) / df_combined["3Fペース"].astype(float))*100)-50) ,2)
df_combined['ペース'] = df_combined['PCIペース'].apply(class_pace)
df_combined = df_combined.drop(["PCIペース"], axis=1)

df_horse = df_combined.copy()
df_horse = df_horse.drop(["race_id","騎手","枠番","馬番","走破時間","勝ち時計","オッズ","通過順","体重変化","性","斤量","上がり","人気","レース名","日付","開催","クラス","芝・ダート","距離","回り","馬場","天気","コース内外","場id","場名","6F","33Lap","side3","side4","脚質","通過順3","通過順4","ペース","3Fペース","斤量比","class_id","course_id","PCI","走破時間換算"],axis=1)
for i in range(1, 4, 1):
    df_horse['体重'+str(i)] = 0
for i in range(1, 4, 1):
    df_horse['勝利体重'+str(i)] = 0

for i, data in enumerate(df_horse.itertuples()):
    try:
        age = age_mapping(df_horse.loc[i, '齢'])
        df_horse.loc[i, '体重'+str(age)] = df_horse.loc[i, '体重']
        if (df_horse.loc[i,'着順']<4) & (df_horse.loc[i,'タイム差']<=0.3):
            df_horse.loc[i,'勝利体重'+str(age)] = df_horse.loc[i,'体重']
    except:
        pass

df_horse.loc[:, "体重1":"勝利体重3"] = df_horse.loc[:, "体重1":"勝利体重3"].replace(0,np.NaN)
df_horse = df_horse.groupby(["馬"]).agg({'体重1':'mean','体重2':'mean','体重3':'mean','勝利体重1':'mean','勝利体重2':'mean','勝利体重3':'mean'}).reset_index().round(1)

df_combined = pd.merge(df_combined, df_horse, on='馬', how='left')
df_combined["平均体重"]=df_combined["体重"]
df_combined["体重差"]=df_combined["体重変化"]

for i in range(1, 4, 1):
    df_combined["平均体重"] = df_combined["平均体重"].mask(df_combined["齢"].apply(age_mapping)==i, df_combined["勝利体重"+str(i)].astype(float))

df_combined["平均体重"] = df_combined["平均体重"].fillna(0)
for i, data in enumerate(df_combined.itertuples()):
    if df_combined.loc[i,'平均体重']==0:
        age = age_mapping(df_combined.loc[i, '齢'])
        df_combined.loc[i,'平均体重'] = df_combined.loc[i,'体重'+str(age)]

df_combined["体重差"] = df_combined["体重"].astype(float) - df_combined["平均体重"].astype(float)
df_combined["平均体重"]=df_combined["平均体重"].fillna(df_combined["体重"])
df_combined["体重差"]=df_combined["体重差"].fillna(df_combined["体重変化"])

df_course_time = df_combined[ (df_combined['着順']==1) & (df_combined['タイム差']<=0.3) ].copy()
df_course_time = df_course_time.groupby(["class_id","場id","コース内外","クラス","芝・ダート","距離"]).agg({'走破時間':'mean','上がり':'mean','6F':'mean','33Lap':'mean','ペース':'mean','PCI':'mean'}).reset_index().round(1)
df_course_time = df_course_time.rename({'走破時間': '平均走破時間','上がり': '平均上がり','6F': '平均6F','33Lap': '平均33Lap','ペース': '平均ペース','PCI':'平均PCI'}, axis='columns')
df_course_time.to_csv('encoded/course_time.csv', index=False)
df_course_time = df_course_time.drop(["場id","コース内外","クラス","芝・ダート","距離","平均走破時間","平均上がり","平均6F","平均33Lap","平均ペース"], axis=1, inplace=False)
df_combined = pd.merge(df_combined, df_course_time, on='class_id', how='left')
df_combined["PCI差"] = df_combined["平均PCI"].astype(float) - df_combined["PCI"].astype(float)

'''
df_combined['斤量負担']=0
df_combined['斤量負担'] = df_combined['斤量負担'].mask(df_combined['斤量比']>0.125, ( ((df_combined['斤量比'].astype(float)-0.125)) / ((df_combined['距離']/1800)*0.2) )).round(3)
df_combined["48TIME"] = round(((df_combined["走破時間"].astype(float) - ( (df_combined['斤量'].astype(float)-48)*((df_combined['距離'].astype(int)/1600)*0.2)) - df_combined['斤量負担'].astype(float) + (((df_combined['距離'].astype(int)/1600)*0.2)))/df_combined['距離'].astype(int))*100,2)
'''
df_combined = df_combined.drop(["勝ち時計","オッズ","通過順","人気","レース名","開催","天気","場名","体重1","体重2","体重3","勝利体重1","勝利体重2","勝利体重3"],axis=1)

# エンコーディングとスケーリング後のデータを確認
print("ファイル出力：開始")
df_combined.to_csv('encoded/race_list.csv', index=False)
df_combined.to_csv('encoded/race_list_shift.csv', index=False, encoding="shift_jis")
df_horse.to_csv('encoded/horse_data.csv', index=False)
print("ファイル出力：終了")
