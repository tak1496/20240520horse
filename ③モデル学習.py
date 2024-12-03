import lightgbm as lgb
import pandas as pd
from sklearn.metrics import roc_curve,roc_auc_score
import matplotlib.pyplot  as plt
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import optuna.integration.lightgbm as lgb2
import pickle

def split_date(df, test_size):
    sorted_id_list = df.sort_values('日付').index.unique()
    train_id_list = sorted_id_list[:round(len(sorted_id_list) * (1-test_size))]
    test_id_list = sorted_id_list[round(len(sorted_id_list) * (1-test_size)):]
    train = df.loc[train_id_list]
    test = df.loc[test_id_list]
    return train, test

dis_mappings = {
    '0_1000', '0_1200', '0_1400', '0_1500', '0_1600', '0_1800', '0_2000', '0_2200', '0_2300', '0_2400', '0_2500', '0_2600', '0_3000', '0_3200', '0_3400', '0_3600',
    '1_1000', '1_1150', '1_1200', '1_1300', '1_1400', '1_1600', '1_1700', '1_1800', '1_1900', '1_2000', '1_2100', '1_2400', '1_2500'
}

class_mappings = {'4歳以上':3, '3歳以上':3, '3歳':2, '2歳':1,'障害':0}

race_list =[]
for i in range(1,4,1):
    if i==2:
        continue
    for j in range(10):
        if j==5 or j==6:
            pass
        else:
            continue
        for k in range(2):
            for m in dis_mappings:
                race_list.append( str(j+1) +'_'+ str(i) +'_'+str(k) +'_'+ str(m) )

# データの読み込み
all_data = pd.read_csv('encoded/race_list.csv')

#着順を変換
all_data['着順'] = all_data['着順'].map(lambda x: 1 if x==1 else 0)
#all_data['着順'] = all_data['着順'].mask( ( (all_data['着順']<4) & (all_data['タイム差']<=0.3) ), 1)
#all_data['着順'] = all_data['着順'].mask(all_data["着順"]!=1,0)

drop_col = ["枠番","馬番",                                                        "33Lap","タイム差",         "PCI","体重差"]
           #"枠番","馬番","走破時間","斤量","上がり","通過順3","通過順4","ペース","33Lap","タイム差","斤量比","PCI","体重差"
f = open("encoded/dis_column_data.txt","rb")
drop_list = pickle.load(f)

drop_item=[]
for i in range(len(drop_list)):
    for j in range(len(drop_col)):
        drop_item.append(drop_list[i]+"_"+drop_col[j])

for cls in race_list:
    #data = all_data[ all_data["course_id"]==cls ]
    data = all_data[ all_data["class_id"]==cls ]
    
    if data.empty == False:
        # 特徴量とターゲットの分割
        train, test = split_date(data, 0.2)
        drop_item = ["race_id","馬","騎手","枠番","馬番","走破時間","着順","体重","体重変化","性","齢","斤量","上がり","日付","クラス","芝・ダート","距離","回り","馬場","コース内外","場id","6F","33Lap","side3","side4","脚質","通過順3","通過順4","ペース","3Fペース","トレセン","調教師","馬主","Sラップ","タイム差","走破時間換算","斤量比","class_id","course_id","PCI","平均体重","体重差","平均PCI","PCI差","父","父父","母父","C1_0_0","C1_1_0","C2_0_0","C2_1_0","C3_0_0","C3_1_0","C4_0_0","C4_0_1","C4_1_0","C5_0_0","C5_1_0","C6_0_0","C6_0_1","C6_1_0","C7_0_0","C7_1_0","C8_0_0","C8_0_1","C8_1_0","C9_0_0","C9_0_1","C9_1_0","C10_0_0","C10_1_0","左回","右回","直線長","直線短","急カーブ","複合カーブ","スパイラル","小回","ゴール前平坦","ゴール前緩坂","ゴール前急坂","芝","ダート","馬番成績","騎手成績","調教師成績","父成績"]+drop_item
                    #"race_id","馬","騎手","枠番","馬番","走破時間","着順","体重","体重変化","性","齢","斤量","上がり","日付","クラス","芝・ダート","距離","回り","馬場","コース内外","場id","6F","33Lap","side3","side4","脚質","通過順3","通過順4","ペース","3Fペース","トレセン","調教師","馬主","Sラップ","タイム差","走破時間換算","斤量比","class_id","course_id","PCI","平均体重","体重差","平均PCI","PCI差","父","父父","母父","C1_0_0","C1_1_0","C2_0_0","C2_1_0","C3_0_0","C3_1_0","C4_0_0","C4_0_1","C4_1_0","C5_0_0","C5_1_0","C6_0_0","C6_0_1","C6_1_0","C7_0_0","C7_1_0","C8_0_0","C8_0_1","C8_1_0","C9_0_0","C9_0_1","C9_1_0","C10_0_0","C10_1_0","左回","右回","直線長","直線短","急カーブ","複合カーブ","スパイラル","小回","ゴール前平坦","ゴール前緩坂","ゴール前急坂","芝","ダート","馬番成績","騎手成績","調教師成績","父成績"
        X_train = train.drop(drop_item, axis=1)
        y_train = train['着順']
        X_test = test.drop(drop_item, axis=1)
        y_test = test['着順']

        # LightGBMデータセットの作成
        train_data = lgb2.Dataset(X_train, label=y_train)
        valid_data = lgb2.Dataset(X_test, label=y_test)
        
        params = {
            'objective': 'binary',  # 二値分類問題
            'metric': 'binary_logloss',  # 損失関数
            'verbosity': -1,
            'boosting_type': 'gbdt',
            'class_weight':'balanced',
            'random_state':100
        }

        # LightGBMによる学習とパラメーターチューニング
        model = lgb2.train(params, train_data, valid_sets=valid_data)
        params = model.params
        
        lgb_clf = lgb.LGBMClassifier(**params)
        lgb_clf.fit(X_train, y_train)
        y_pred_train = lgb_clf.predict_proba(X_train)[:,1]
        y_pred = lgb_clf.predict_proba(X_test)[:,1]
        
        #モデルの評価
        try:
            print(roc_auc_score(y_test,y_pred))
        except:
            print()
            
        total_cases = len(y_test)  # テストデータの総数
        TP = (y_test == 1) & (y_pred >= 0.5)  # True positives
        FP = (y_test == 0) & (y_pred >= 0.5)  # False positives
        TN = (y_test == 0) & (y_pred < 0.5)  # True negatives
        FN = (y_test == 1) & (y_pred < 0.5)  # False negatives

        TP_count = sum(TP)
        FP_count = sum(FP)
        TN_count = sum(TN)
        FN_count = sum(FN)

        accuracy_TP = TP_count / total_cases * 100
        misclassification_rate_FP = FP_count / total_cases * 100
        accuracy_TN = TN_count / total_cases * 100
        misclassification_rate_FN = FN_count / total_cases * 100

        print("Total cases:", total_cases)
        print("True positives:", TP_count, "(", "{:.2f}".format(accuracy_TP), "%)")
        print("False positives:", FP_count, "(", "{:.2f}".format(misclassification_rate_FP), "%)")
        print("True negatives:", TN_count, "(", "{:.2f}".format(accuracy_TN), "%)")
        print("False negatives:", FN_count, "(", "{:.2f}".format(misclassification_rate_FN), "%)")
        
        # モデルの保存
        lgb_clf.booster_.save_model('model/' + cls +'model.txt')

        # 特徴量の重要度を取得
        importance = lgb_clf.feature_importances_

        # 特徴量の名前を取得
        feature_names = X_train.columns

        # 特徴量の重要度を降順にソート
        indices = np.argsort(importance)[::-1]

        # 特徴量の重要度を降順に表示
        for f in range(X_train.shape[1]):
            print("%2d) %-*s %f" % (f + 1, 30, feature_names[indices[f]], importance[indices[f]]))

        '''
        # LightGBMデータセットの作成
        train_data = lgb.Dataset(X_train, label=y_train)
        valid_data = lgb.Dataset(X_test, label=y_test)
        params={
            'num_leaves':32,
            'min_data_in_leaf':190,
            'class_weight':'balanced',
            'random_state':100
            }
        #params={'objective': 'binary', 'metric': 'binary_logloss', 'verbosity': -1, 'boosting_type': 'gbdt', 'class_weight': 'balanced', 'random_state': 100, 'feature_pre_filter': False, 'lambda_l1': 7.149680511850056e-07, 'lambda_l2': 6.732250615431922, 'num_leaves': 6, 'feature_fraction': 0.42, 'bagging_fraction': 0.6550358614019851, 'bagging_freq': 4, 'min_child_samples': 20, 'num_iterations': 1000, 'early_stopping_round': None}

        lgb_clf = lgb.LGBMClassifier(**params)
        lgb_clf.fit(X_train, y_train)
        y_pred_train = lgb_clf.predict_proba(X_train)[:,1]
        y_pred = lgb_clf.predict_proba(X_test)[:,1]
        
        print(cls)
        #モデルの評価
        try:
            print(roc_auc_score(y_test,y_pred))
        except:
            print()
            
        total_cases = len(y_test)  # テストデータの総数
        TP = (y_test == 1) & (y_pred >= 0.5)  # True positives
        FP = (y_test == 0) & (y_pred >= 0.5)  # False positives
        TN = (y_test == 0) & (y_pred < 0.5)  # True negatives
        FN = (y_test == 1) & (y_pred < 0.5)  # False negatives

        TP_count = sum(TP)
        FP_count = sum(FP)
        TN_count = sum(TN)
        FN_count = sum(FN)

        accuracy_TP = TP_count / total_cases * 100
        misclassification_rate_FP = FP_count / total_cases * 100
        accuracy_TN = TN_count / total_cases * 100
        misclassification_rate_FN = FN_count / total_cases * 100

        print("Total cases:", total_cases)
        print("True positives:", TP_count, "(", "{:.2f}".format(accuracy_TP), "%)")
        print("False positives:", FP_count, "(", "{:.2f}".format(misclassification_rate_FP), "%)")
        print("True negatives:", TN_count, "(", "{:.2f}".format(accuracy_TN), "%)")
        print("False negatives:", FN_count, "(", "{:.2f}".format(misclassification_rate_FN), "%)")

        # モデルの保存
        lgb_clf.booster_.save_model('model/' + cls +'model.txt')

        # 特徴量の重要度を取得
        importance = lgb_clf.feature_importances_

        # 特徴量の名前を取得
        feature_names = X_train.columns

        # 特徴量の重要度を降順にソート
        indices = np.argsort(importance)[::-1]

        # 特徴量の重要度を降順に表示
        for f in range(X_train.shape[1]):
            print("%2d) %-*s %f" % (f + 1, 30, feature_names[indices[f]], importance[indices[f]]))
        '''
        
