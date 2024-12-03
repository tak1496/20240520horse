import os
import pandas as pd
import re

# フォルダのパス
dir_path = "predict_result"
#date = input("日付：")
date = "202401017"
# フォルダ内のすべてのファイルとディレクトリを取得
all_items = os.listdir(dir_path)
# フォルダを除外して、ファイルのみのリストを作成
file_list = [item for item in all_items if os.path.isfile(os.path.join(dir_path, item))]

output_list = []
for path in file_list:
    match = re.search(r'race_data_(.*?)_\d+.csv', path)
    if match:
        extracted = match.group(1)
        output_list.append([extracted])
        output_list.append(["自信度","馬番","馬","予測結果"])

        # 予測を行う新しいデータの読み込み
        data = pd.read_csv('predict_result/' + path)
        #data["予測結果"] = data["予測結果"].round(3)
        #data["予測平均"] = data["予測平均"].round(3)
        # '予測結果'列に基づいて降順でソート
        sorted_data = data.sort_values(by=['予測結果','予測平均'], ascending=False)

        # sorted_dataから予測結果、馬番、馬の情報を取り出し、output_dfに追加
        for index, row in sorted_data.iterrows():
            confidence = ""

            # 条件を整理して可読性を向上させる
            # row のキーへのアクセスを変数に保存
            predicted_result = row["予測結果"]

            # 記号のランク順 (◎、〇、△) に条件を配置
            if predicted_result >= 0.95:
                confidence = "◎"
            elif predicted_result >= 0.9:
                confidence = "〇"
            elif predicted_result >= 0.85:
                confidence = "▲"

            #output_list.append([confidence,row["馬番"], row["馬"], round(row["脚質"],1), round(row["予測結果"], 5), round(row["予測平均"], 5)])
            output_list.append([confidence,row["馬番"], row["馬"],row["予測結果"],row["予測平均"],row["レース数"]])

        output_list.append([])

# 最後にリストからDataFrameを作成し、csvファイルとして出力
output_df = pd.DataFrame(output_list)
output_df.to_csv('predict_result/output_' + date + '.csv', index=False, encoding = "shift-jis")
