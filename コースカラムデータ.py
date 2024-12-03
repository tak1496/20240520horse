import pandas as pd
import pickle

df_race_list = pd.read_csv('encoded/race_list2.csv')
df_race_list = df_race_list.drop(["騎手","体重","体重変化","性","齢","クラス","馬場","回り","コース内外","6F","side3","side4","脚質","3Fペース","トレセン","調教師","馬主","Sラップ","走破時間換算","class_id","course_id","平均体重","平均PCI","PCI差"], axis=1)

df_race_list = df_race_list.sort_values(['日付','race_id','着順']).reset_index()

course = df_race_list.groupby(['場id','距離','芝・ダート'])['走破時間'].min().reset_index()
col_mappings = ["枠番","馬番","走破時間","斤量","上がり","33Lap","通過順3","通過順4","ペース","タイム差","斤量比","PCI","体重差"]

course_col = []
dis_col = []
for i, row in enumerate(course.itertuples()):
    dis_col.append("C"+str(row[1])+"_"+str(row[2])+"_"+str(row[3]))
    for j in range(len(col_mappings)):
        course_col.append("C"+str(row[1])+"_"+str(row[2])+"_"+str(row[3])+"_"+col_mappings[j])

with open("encoded/course_column_data.txt", "wb") as f:
    pickle.dump(course_col, f)

with open("encoded/dis_column_data.txt", "wb") as f:
    pickle.dump(dis_col, f)
