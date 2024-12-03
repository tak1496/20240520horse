import requests
from bs4 import BeautifulSoup
import time
import csv

import numpy as np
import pandas as pd
import pyparsing as pp
import math

#取得開始年
year_start = 2024

#取得終了年
year_end = 2025

# DataFrame列名定義
position_col = ['diff', 'horse_no', 'side']
# 差の定数(unit:馬身)
DIFF_GROUP = 0.3
DIFF_MIN = 1.5
DIFF_MID = 3.0
DIFF_MUCH = 6.0

class ParsePass():
    
    def __init__(self):
        
        # 馬番
        horse_no = pp.Word(pp.nums).setParseAction(self._horse_no_action)
        
        # 馬群
        group = pp.Suppress(pp.Literal('(')) + \
                    pp.Optional(pp.delimitedList(pp.Word(pp.nums), delim=',')) + \
                    pp.Suppress(pp.Literal(')'))
        group.ignore('*')
        group.setParseAction(self._group_action)

        # 情報要素
        element = (group | horse_no)
        
        # 前走馬との差
        diff_min = pp.Suppress(pp.Optional(pp.Literal(','))).setParseAction(self._diff_min_action) + element
        diff_mid = pp.Suppress(pp.Literal('-')).setParseAction(self._diff_mid_action) + element
        diff_much = pp.Suppress(pp.Literal('=')).setParseAction(self._diff_much_action) + element

        # 全体定義
        self._passing_order = element + pp.ZeroOrMore( diff_mid | diff_much | diff_min )
        
    def _horse_no_action(self, token):

        df_append = pd.DataFrame(data=[[self._diff, token[0], 1]], columns=position_col)
        self._data = pd.concat([self._data, df_append], ignore_index=True, axis=0).drop_duplicates().reset_index(drop=True)
        return

    def _group_action(self, token):
        
        for i, no in enumerate(token):
            
            df_append = pd.DataFrame(data=[[self._diff, no, 1+i]], columns=position_col)
            self._data = pd.concat([self._data, df_append], ignore_index=True, axis=0).drop_duplicates().reset_index(drop=True)
            self._diff += DIFF_GROUP
        self._diff -= DIFF_GROUP
        return
        
    def _diff_min_action(self, token):

        self._diff += DIFF_MIN
        return
        
    def _diff_mid_action(self, token):
        
        self._diff += DIFF_MID
        return
    
    def _diff_much_action(self, token):
        
        self._diff += DIFF_MUCH
        return
        
    def parse(self, pass_str):

        # 初期化
        self._data = pd.DataFrame(columns=position_col)
        self._diff = 0
        # parse
        self._passing_order.parseString(pass_str)
        # index調整
        self._data.index = np.arange(1, len(self._data)+1)
        self._data.index.name = 'rank'

        return(self._data)

pass_parsing = ParsePass()

corner_mappings = [
    {"01芝":   {"3C":540, "4C":266}},
    {"02芝":   {"3C":470, "4C":262}},
    {"03芝":   {"3C":480, "4C":292}},
    {"04芝":   {"3C":830, "4C":640}},
    {"04芝外": {"3C":1050, "4C":850}},
    {"05芝":   {"3C":780, "4C":526}},
    {"06芝":   {"3C":540, "4C":310}},
    {"06芝外": {"3C":540, "4C":310}},
    {"07芝":   {"3C":650, "4C":413}},
    {"08芝":   {"3C":600, "4C":328}},
    {"08芝外": {"3C":630, "4C":404}},
    {"09芝":   {"3C":630, "4C":357}},
    {"09芝外": {"3C":790, "4C":474}},
    {"10芝":   {"3C":500, "4C":293}},
    {"01ダ":   {"3C":480, "4C":264}},
    {"02ダ":   {"3C":420, "4C":260}},
    {"03ダ":   {"3C":420, "4C":296}},
    {"04ダ":   {"3C":510, "4C":354}},
    {"05ダ":   {"3C":730, "4C":502}},
    {"06ダ":   {"3C":520, "4C":308}},
    {"07ダ":   {"3C":600, "4C":411}},
    {"08ダ":   {"3C":570, "4C":329}},
    {"09ダ":   {"3C":600, "4C":353}},
    {"10ダ":   {"3C":430, "4C":291}}
]

def corner_mapping(val):
    for dict in corner_mappings:
        try:
            return dict[val]
            break
        except:
            continue

header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"}

for year in range(year_start, year_end):
    race_data_all = []
    #取得するデータのヘッダー情報を先に追加しておく
    race_data_all.append(['race_id','馬','騎手','枠番','馬番','走破時間','勝ち時計','オッズ','通過順','着順','体重','体重変化','性','齢','斤量','上がり','人気','レース名','日付','開催','クラス','芝・ダート','距離','回り','馬場','天気','コース内外','場id','場名', '6F','33Lap','side3','side4','脚質','通過順3','通過順4','ペース','3Fペース','トレセン','調教師','馬主','Sラップ'])
    List=[]
    #競馬場
    l=["01","02","03","04","05","06","07","08","09","10"]
    for w in range(len(l)):
        place = ""
        if l[w] == "01":
            place = "札幌"
        elif l[w] == "02":
            place = "函館"
        elif l[w] == "03":
            place = "福島"
        elif l[w] == "04":
            place = "新潟"
        elif l[w] == "05":
            place = "東京"
        elif l[w] == "06":
            place = "中山"
        elif l[w] == "07":
            place = "中京"
        elif l[w] == "08":
            place = "京都"
        elif l[w] == "09":
            place = "阪神"
        elif l[w] == "10":
            place = "小倉"

        #開催回数分ループ（6回）
        for z in range(7):
            continueCounter = 0  # 'continue'が実行された回数をカウントするためのカウンターを追加
            #開催日数分ループ（12日）
            for y in range(13):
                race_id = ''
                if y<9:
                    race_id = str(year)+l[w]+"0"+str(z+1)+"0"+str(y+1)
                    url1="https://db.netkeiba.com/race/"+race_id
                    url2="https://race.netkeiba.com/race/result.html?race_id="+race_id
                else:
                    race_id = str(year)+l[w]+"0"+str(z+1)+str(y+1)
                    url1="https://db.netkeiba.com/race/"+race_id
                    url2="https://race.netkeiba.com/race/result.html?race_id="+race_id
                #yの更新をbreakするためのカウンター
                yBreakCounter = 0
                #レース数分ループ（12R）
                for x in range(12):
                    if x<9:
                        url=url1+str("0")+str(x+1)
                        url_r=url2+str("0")+str(x+1)
                        current_race_id = race_id+str("0")+str(x+1)
                    else:
                        url=url1+str(x+1)
                        url_r=url2+str(x+1)
                        current_race_id = race_id+str(x+1)
                    try:
                        time.sleep(1)
                        r=requests.get(url, headers=header)

                    #リクエストを投げすぎるとエラーになることがあるため
                    #失敗したら10秒待機してリトライする
                    except requests.exceptions.RequestException as e:
                        print(f"Error: {e}")
                        print("Retrying in 10 seconds...")
                        time.sleep(10)  # 10秒待機
                        r=requests.get(url, headers=header)
                    #バグ対策でdecode
                    soup = BeautifulSoup(r.content.decode("euc-jp", "ignore"), "html.parser")
                    soup_span = soup.find_all("span")

                    # テーブルを指定
                    main_table = soup.find("table", {"class": "race_table_01 nk_tb_common"})
                    
                    # テーブル内の全ての行を取得
                    try:
                        main_rows = main_table.find_all("tr")
                    except:
                        print('continue: ' + url)
                        continueCounter += 1  # 'continue'が実行された回数をカウントアップ
                        if continueCounter == 2:  # 'continue'が2回連続で実行されたらループを抜ける
                            continueCounter = 0
                            break
                        continue
                    
                    ##ラップタイムと勝利勝ち馬の走破時間
                    table_data = soup.find_all("table", summary="ラップタイム")
                    lap6=0
                    v_runtime=0
                    v_3F=0
                    s_lap=0

                    result_pace_url = requests.get(url_r, headers=header)
                    result_soup = BeautifulSoup(result_pace_url.content.decode("euc-jp", "ignore"), "html.parser")
                    pace_span = result_soup.find("div", {"class": "RapPace_Title"})
                    try:
                        pace = pace_span.span.text
                    except:
                        pace = "M"

                    for i, result in enumerate(table_data[0].find_all("tr")):
                        if i==0:
                            lap_data = result.td.text
                            laps = lap_data.split("-")
                            lap_count = len(laps)
                            for i in range(0,lap_count):
                                if i<3:
                                    s_lap = s_lap + float(laps[i])
                                    
                                v_runtime = v_runtime + float(laps[i])
                                if i>=lap_count-3:
                                    v_3F = v_3F + float(laps[i])
                            cnt=0
                            for i in range(lap_count, 0, -1):
                                if cnt>2:
                                    lap6 = lap6 + float(laps[i-1])
                                if cnt==5:
                                    break
                                cnt=cnt+1

                        if i==1:
                            pace_data = result.td.text
                    
                    ##レースの情報(距離、芝ダート、内外、回り、馬場状態、天気)
                    try:
                        var = soup_span[8]
                        sur=str(var).split("/")[0].split(">")[1][0]
                        rou=str(var).split("/")[0].split(">")[1][1]
                        dis=str(var).split("/")[0].split(">")[1].split("m")[0][-4:]
                        con=str(var).split("/")[2].split(":")[1][1]
                        wed=str(var).split("/")[1].split(":")[1][1]
                        corse_side = str(var).split("/")[0].split(">")[1].split("m")[0].find("外")
                    except IndexError:
                        try:
                            var = soup_span[7]
                            sur=str(var).split("/")[0].split(">")[1][0]
                            rou=str(var).split("/")[0].split(">")[1][1]
                            dis=str(var).split("/")[0].split(">")[1].split("m")[0][-4:]
                            con=str(var).split("/")[2].split(":")[1][1]
                            wed=str(var).split("/")[1].split(":")[1][1]
                            corse_side = str(var).split("/")[0].split(">")[1].split("m")[0].find("外")
                        except IndexError:
                            var = soup_span[6]
                            sur=str(var).split("/")[0].split(">")[1][0]
                            rou=str(var).split("/")[0].split(">")[1][1]
                            dis=str(var).split("/")[0].split(">")[1].split("m")[0][-4:]
                            con=str(var).split("/")[2].split(":")[1][1]
                            wed=str(var).split("/")[1].split(":")[1][1]
                            corse_side = str(var).split("/")[0].split(">")[1].split("m")[0].find("外")

                    cor = l[w]+sur
                    cs=0
                    if corse_side!=-1:
                        cor = cor+'外'
                        cs=1
                    corner_dis = corner_mapping(cor)

                    lap33_6=0
                    lap33=0
                    if corner_dis!=None:
                        
                        ##馬身差のタイム
                        hb_second = float(lap6) / ( 600 / 2.5 )
                    
                        ##コーナー、ラップデータの取得
                        table_data = soup.find_all("table", summary="コーナー通過順位")
                        ##新処理
                        df_lap3=''
                        df_lap4=''
                        for i, result in enumerate(table_data[0].find_all("tr")):
                            if str(result.th.text)=='3コーナー':
                                df_lap3 = pass_parsing.parse(result.td.text)
                                df_lap3["脚質"]=1
                                df_lap3["馬身"]=0
                                diff3 = round(max(df_lap3["diff"]) / 4, 2)
                                leg=1
                                diff3_chk=0
                                for i in range(len(df_lap3["diff"])):
                                    if df_lap3.iloc[i,2]==1:
                                        if diff3_chk<int(df_lap3.iloc[i,0]):
                                            leg = leg + 1
                                            diff3_chk = diff3_chk+diff3
                                            if leg==3:
                                                diff3_chk = diff3_chk+diff3
                                            
                                    df_lap3.iloc[i,4]=diff3_chk
                                    df_lap3.iloc[i,3]=leg
                                    
                            if str(result.th.text)=='4コーナー':
                                df_lap4 = pass_parsing.parse(result.td.text)

                        ##3C位置と4C位置までの距離
                        dis34 = float(corner_dis["3C"]) - float(corner_dis["4C"])

                        ##6F-3Cの距離
                        f6_span = 600 - float(corner_dis["3C"])

                    ##レースデータの取得
                    race_data = []
                    for i, row in enumerate(main_rows[1:], start=1):# ヘッダ行をスキップ
                        cols = row.find_all("td")
                        #走破時間
                        runtime=''
                        try:
                            runtime= cols[7].text.strip()
                        except IndexError:
                            runtime = ''
                        soup_nowrap = soup.find_all("td",nowrap="nowrap",class_=None)
                        #通過順
                        pas = ''
                        try:
                            pas = str(cols[10].text.strip())
                        except:
                            pas = ''
                        weight = 0
                        weight_dif = 0
                        #体重
                        var = cols[14].text.strip()
                        try:
                            weight = int(var.split("(")[0])
                            weight_dif = int(var.split("(")[1][0:-1])
                        except ValueError:
                            weight = 0
                            weight_dif = 0
                        weight = weight
                        weight_dif = weight_dif
                        #上がり
                        last = ''
                        side3=0
                        side4=0
                        leg3=0
                        try:
                            last = cols[11].text.strip()
                            if last!='':
                                if lap6!=0:
                                    ##3Cの距離-各馬の3Cの距離
                                    try:
                                        rank = df_lap3[df_lap3['horse_no']==cols[2].text.strip()].index[0]
                                        diff3 = float(df_lap3["diff"][rank])
                                        corner_dis3 = float(corner_dis["3C"])+(diff3 * 2.5)
                                        side3 = df_lap3["side"][rank]
                                        leg3 = df_lap3["脚質"][rank]
                                    except:
                                        continue
                                    
                                    ##4Cの距離-各馬の4Cの距離
                                    try:
                                        rank = df_lap4[df_lap4['horse_no']==cols[2].text.strip()].index[0]
                                        diff4 = float(df_lap4["diff"][rank])
                                        corner_dis4 = float(corner_dis["4C"])+(diff4 * 2.5)
                                        side4 = df_lap4["side"][rank]
                                    except:
                                        continue

                                    ##3Cの馬身差-4Cの馬身差
                                    diff34=0
                                    diff34 = diff3 - diff4

                                    ##各馬の3Cから4Cまでの推進率
                                    diff_par = 0
                                    if diff34!=0:
                                        diff_par = diff34 / dis34

                                    ##各馬の推定6F時の馬身差
                                    diff6 = float(f6_span) * float(diff_par)
                                    ##各馬の推定6F位置
                                    diff6 = diff6 + diff3

                                    ##6Lapタイムから各馬の推定6F位置の馬身差時間
                                    ##各馬の推定6Fタイム
                                    lap33_6 = lap6 + (diff6 * hb_second)

                                    ##6Lap-3Lapで33Lapを求める
                                    lap33 = float(lap33_6) - float(last)
                                    
                        except IndexError:
                            last = ''
                        #人気
                        pop = ''
                        try:
                            pop = cols[13].text.strip()
                        except IndexError:
                            pop = ''
 
                        soup_smalltxt = soup.find_all("p",class_="smalltxt")
                        detail=str(soup_smalltxt).split(">")[1].split(" ")[1]
                        date=str(soup_smalltxt).split(">")[1].split(" ")[0]
                        clas=str(soup_smalltxt).split(">")[1].split(" ")[2].replace(u'\xa0', u' ').split(" ")[0]
                        title=str(soup.find_all("h1")[1]).split(">")[1].split("<")[0]
                        '''
                        chk = grade_mapping(title)
                        if chk!=0:
                            clas = str(clas) + str(chk)
                        '''

                        pas_rank = pas.split("-")
                        pas3 = pas_rank[ len(pas_rank)-2 ]
                        pas4 = pas_rank[ len(pas_rank)-1 ]

                        race_data = [
                            current_race_id,
                            cols[3].text.strip(),#馬の名前
                            cols[6].text.strip(),#騎手の名前
                            cols[1].text.strip(),##枠番
                            cols[2].text.strip(),#馬番
                            runtime,#走破時間
                            v_runtime, #勝ち時計
                            cols[12].text.strip(),#オッズ,
                            pas,#通過順
                            cols[0].text.strip(),#着順
                            weight,#体重
                            weight_dif,#体重変化
                            cols[4].text.strip()[0],#性
                            cols[4].text.strip()[1],#齢
                            cols[5].text.strip(),#斤量
                            last,#上がり
                            pop,#人気,
                            title,#レース名
                            date,#日付
                            detail,
                            clas,#クラス
                            sur,#芝かダートか
                            dis,#距離
                            rou,#回り
                            con,#馬場状態
                            wed,#天気
                            cs, #コース内外
                            l[w],#場
                            place,
                            lap33_6, #6Fラップ
                            lap33, #33ラップ
                            side3, #3コーナー内外
                            side4, #4コーナー内外
                            leg3, #脚質
                            pas3, #通過順3
                            pas4, #通過順4
                            pace, #ペース
                            v_3F, #3Fペース
                            cols[18].text.strip()[1], #トレセン
                            cols[18].find("a").text.strip(), #調教師
                            cols[19].find("a").text.strip(), #馬主
                            s_lap #スタート3Fラップ
                            ]
                        lap3=0
                        race_data_all.append(race_data)
                    
                    print(detail+str(x+1)+"R　"+ str(url))#進捗を表示
                    
                if yBreakCounter == 12:#12レース全部ない日が検出されたら、その開催中の最後の開催日と考える
                    break
    #1年毎に出力
    #出力先とファイル名は修正してください
    with open('data/'+str(year)+'.csv', 'w', newline='',encoding="SHIFT-JIS") as f:
        csv.writer(f).writerows(race_data_all)
    print("終了")
