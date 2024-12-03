import pandas as pd
import numpy as np

# 行の表示数を設定（例：None は制限なし）
pd.set_option('display.max_rows', None)

df = pd.read_csv('encoded/race_list.csv')
df = df.drop(["race_id","馬","騎手","日付","class_id","course_id","トレセン","調教師","馬主","父","父父","母父"], axis=1)

df['着順'] = df['着順'].mask( ( (df['着順']<4) & (df['タイム差']<=0.3) ), 1)
df['着順'] = df['着順'].mask(df["着順"]!=1,0)


# 「着順」と他のカラムとの相関係数を計算
correlations = df.corr()['着順'].sort_values()
print(correlations)

# 相関係数の絶対値が0.01以下のものを抽出する
sample_correlations = correlations[correlations.abs() <= 0.01]
print(sample_correlations)
