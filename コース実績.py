import pandas as pd
#from math import isnan
import pickle

df_race_list = pd.read_csv('encoded/race_list2.csv')
df_race_list = df_race_list.drop(["騎手","体重","体重変化","性","齢","クラス","馬場","回り","コース内外","6F","side3","side4","脚質","3Fペース","トレセン","調教師","馬主","Sラップ","走破時間換算","class_id","course_id","平均体重","平均PCI","PCI差"], axis=1)
df_race_list["race_horse_id"] = df_race_list["race_id"].astype(str) +'_'+ df_race_list["馬"].astype(str)
df_race_list = df_race_list.sort_values(['日付','race_id','着順']).reset_index()

col_mappings = ["枠番","馬番","走破時間","斤量","上がり","33Lap","通過順3","通過順4","ペース","タイム差","斤量比","PCI","体重差"]

f = open("encoded/course_column_data.txt","rb")
course_colm_list = pickle.load(f)
for i in range(len(course_colm_list)):
    df_race_list[course_colm_list[i]]=""

'''
for i, row in enumerate(course.itertuples()):
    for j in range(len(col_mappings)):
        df_race_list["C"+str(row[1])+"_"+str(row[2])+"_"+str(row[3])+"_"+col_mappings[j]]=""
'''

for i, row in enumerate(df_race_list.itertuples()):
    idx1=row[0]
    race_id = df_race_list.loc[i,"race_id"]
    hn = df_race_list.loc[i,"馬"]
    d = df_race_list.loc[i,"日付"]
    c = df_race_list.loc[i,"場id"]
    dis = df_race_list.loc[i,"距離"]
    gd = df_race_list.loc[i,"芝・ダート"]

    colm="C"+str(c)+"_"+str(dis)+"_"+str(gd)

    df_hl = df_race_list[ (df_race_list["馬"]==hn) & (df_race_list["日付"]<d) ]
    df_hl = df_hl.sort_values(['日付'])
    if df_hl.empty==False:
        df_hl = df_hl.tail(1)
        df_race_list.loc[idx1,"C1_1000_0_枠番":"C10_2600_0_体重差"] = df_hl.loc[df_hl.index.values.tolist(),"C1_1000_0_枠番":"C10_2600_0_体重差"].values.tolist()[0]

    chk = 0
    if df_race_list.loc[idx1, colm+"_走破時間"]=="":
    #if isnan(df_race_list.loc[idx1, colm+"_走破時間"]):
        chk=1
    elif (df_race_list.loc[idx1, "タイム差"].astype(float) <= df_race_list.loc[idx1, colm+"_タイム差"].astype(float)) and (df_race_list.loc[idx1, "走破時間"].astype(float) <= df_race_list.loc[idx1, colm+"_走破時間"].astype(float)):
        chk=1

    if chk==1:
        for j in range(len(col_mappings)):
            df_race_list.loc[idx1, colm+"_"+col_mappings[j]] = df_race_list.loc[idx1,col_mappings[j]]

    print(i,d, hn)

    if i%10000==0:
        df_race_list2 = df_race_list.drop(["index","race_id","馬","枠番","馬番","着順","走破時間","斤量","上がり","日付","芝・ダート","距離","場id","33Lap","通過順3","通過順4","ペース","タイム差","斤量比","PCI","体重差"],axis=1)
        df_race_list2.head(i).to_csv('encoded/course_ability.csv', index=False)
        if i<100000:
            df_race_list2.head(i).to_csv('encoded/course_ability_shift.csv', index=False, encoding="SHIFT_JIS")
            print("---------- Save ----------")

df_race_list = df_race_list.drop(["index","race_id","馬","枠番","馬番","着順","走破時間","斤量","上がり","日付","芝・ダート","距離","場id","33Lap","通過順3","通過順4","ペース","タイム差","斤量比","PCI","体重差"],axis=1)
df_race_list.to_csv('encoded/course_ability.csv', index=False)
#df_race_list.to_csv('encoded/course_ability_shift.csv', index=False, encoding="SHIFT_JIS")







