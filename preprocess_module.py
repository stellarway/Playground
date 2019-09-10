#!/usr/bin/env python
# coding: utf-8

# In[1]:


def preprocess(trade, pledge, payment, combat, activity):
    
    import pandas as pd
    import numpy as np
    # 2. 기본 틀 생성
    unique = activity.acc_id.unique()
    acc_id_lst = sorted(list(unique)*28)
    day_lst = (list(range(1,29))*len(unique))
    full_acc_id_day = pd.DataFrame({'acc_id' : acc_id_lst, 'day' : day_lst})

    # 3. 각 테이블 전처리

    ##  (1) activity테이블 전처리

    new_activity = activity.sort_values(by=['acc_id','day'])
    new_activity.index = range(len(new_activity))
    new_activity = new_activity[['acc_id','day'] + list(new_activity.columns)[2:]]

    activity_result = new_activity.groupby(['acc_id','day']).sum()
    activity_result['char_id'] = new_activity.drop_duplicates(['acc_id','day','char_id']).groupby(['acc_id','day']).char_id.count()
    activity_result['server'] = new_activity.drop_duplicates(['acc_id','day','server']).groupby(['acc_id','day']).server.count()
    activity_result = activity_result.reset_index()
    activity_result = activity_result[['acc_id','day','char_id','server'] + list(activity_result.columns[3:-1])]
    activity_result = activity_result.rename(columns={'char_id' : 'activity_char_cnt',
                                                      'server' : 'activity_server_cnt'})
    charId= new_activity.sort_values(['acc_id','day','playtime']).groupby(['acc_id','day']).last().char_id.reset_index()
    activity_result['max_char_id'] = charId['char_id']

    ## (2) Trade 테이블 전처리

    class TradePre:
        def __init__(self, tradeData, actData):
            self.trade = tradeData
            self.act = actData
            self.key = self.act[['acc_id', 'day', 'max_char_id']]
    #     colName = source_acc_id or target_acc_id
        def count(self, day):
            count = self.trade[self.trade['day']==day].acc_id.value_counts()
            key_cnt = self.key[self.key['day']==day]
            df = pd.merge(key_cnt, pd.DataFrame({'acc_id':list(count.keys()), 'count':count}))
            return df

    #     colName = source_acc_id or target_acc_id
        def amount(self, day):
            df = self.trade[self.trade['day']==day].groupby('acc_id')            .apply(lambda x:pd.Series({'day':day, 
                                       'amount': sum(x.item_amount), 
                                       'price': sum(x.item_price)})).reset_index()
            return df

    #     colName = source_acc_id or target_acc_id    
        def maxType(self, day):
            df = self.trade[self.trade['day']==day].groupby('acc_id')            .apply(lambda x:pd.Series({'day':day, 
                                       'type_max': x.item_type.value_counts().idxmax()})).reset_index()
            return df

        def concat(self, func):
            df = pd.concat(list(map(lambda x: func(x), range(1,29))))
            return df


    ### 대가성 거래 데이터

    trade_origin = trade.copy()

    tradeData = trade_origin.dropna()

    sell_tradeData = tradeData.rename(columns = {'source_acc_id':'acc_id','source_char_id':'char_id'})
    buy_tradeData = tradeData.rename(columns = {'target_acc_id':'acc_id', 'target_char_id':'char_id'})

    sell = TradePre(sell_tradeData,activity_result)
    buy = TradePre(buy_tradeData,activity_result)

    sell_cnt = sell.concat(sell.count)
    sell_amount = sell.concat(sell.amount)
    # %time sell_maxType = sell.concat(sell.maxType)
    buy_cnt = buy.concat(buy.count)
    buy_amount = buy.concat(buy.amount)
    # %time buy_maxType = buy.concat(buy.maxType)

    sellDf = sell_cnt.merge(sell_amount) #.merge(sell_maxType)
    buyDf = buy_cnt.merge(buy_amount) #.merge(buy_maxType)

    sellDf = sellDf.rename(columns ={'count':'sell_cnt', 'amount':'sell_amount',
                                         'price':'sell_price'})
    buyDf = buyDf.rename(columns ={'count':'buy_cnt', 'amount':'buy_amount',
                                       'price':'buy_price'})
    trDf = pd.merge(sellDf, buyDf, how = 'outer')

    ### 대가 없는 거래데이터

    exchangeData = trade_origin[pd.isna(trade_origin['item_price'])]

    give_tradeData = exchangeData.rename(columns = {'source_acc_id':'acc_id','source_char_id':'char_id'})
    get_tradeData = exchangeData.rename(columns = {'target_acc_id':'acc_id', 'target_acc_id':'acc_id'})
    give = TradePre(give_tradeData,activity_result)
    get = TradePre(get_tradeData,activity_result)

    give_cnt = give.concat(give.count)
    give_amount = give.concat(give.amount)
    # %time give_maxType = give.concat(give.maxType)
    get_cnt = get.concat(get.count)
    get_amount = get.concat(get.amount)
    # %time get_maxType = get.concat(get.maxType)

    giveDf = give_cnt.merge(give_amount) #.merge(give_maxType)
    getDf = get_cnt.merge(get_amount) #.merge(get_maxType)

    giveDf = giveDf.rename(columns ={'count':'give_cnt', 'amount':'give_amount',
                                         'price':'give_price'})

    getDf = getDf.rename(columns ={'count':'get_cnt', 'amount':'get_amount',
                                       'price':'get_price'})
    exDf = pd.merge(giveDf, getDf, how = 'outer')

    trade_result = trDf.sort_values(['acc_id','day']).reset_index(drop=True)
    exchange_result = exDf.sort_values(['acc_id','day']).reset_index(drop=True)

    # trade_result.to_csv('trade_result.csv')
    # exchange_result.to_csv('exchange_result.csv')

    ## (3) 전투 데이터

    key = activity[['acc_id', 'day', 'char_id','playtime']]
    # max_class = key.merge(combat, how='left').sort_values(['acc_id','char_id','playtime'])\
    # .groupby(['acc_id','char_id']).last()['class'].fillna(-1).reset_index()\
    # .rename(columns = {'class':'max_class'})

    combatDf = combat.groupby(['acc_id','day']).sum().reset_index()
    combat_char_cnt = combat.drop_duplicates(['acc_id','day','char_id'])    .groupby(['acc_id','day']).char_id.count().reset_index().rename(columns = {'char_id':'combat_char_cnt'})
    combat_server_cnt = combat.drop_duplicates(['acc_id','day','server'])    .groupby(['acc_id','day']).server.count().reset_index().rename(columns = {'server':'combat_server_cnt'})
    level = combat.sort_values(['acc_id','day','level']).groupby(['acc_id','day']).last().level.reset_index().rename(columns = {'level':'max_level'})
    # combatDf = combatDf.reset_index()

    combatDf = combatDf.merge(combat_char_cnt, how = 'left', on = ['acc_id', 'day'])
    combatDf = combatDf.merge(combat_server_cnt, how = 'left', on = ['acc_id', 'day'])
    combatDf = combatDf.merge(level, how = 'left', on = ['acc_id', 'day'])
    del combatDf['char_id']
    # combatDf = combatDf.merge(activity['char_id'], how = 'left', on = ['acc_id', 'day'])
    # combatDf = combatDf.merge(max_class, how = 'left', on = ['acc_id', 'char_id'])
    # del combatDf['char_id']

    combat_result = combatDf[['acc_id','day']+list(combatDf.columns)[-3:]+list(combatDf.columns)[4:-3]]    .rename(columns={'random_attacker_cnt':'combat_random_attacker_cnt',
                     'random_defender_cnt':'combat_random_defender_cnt',
                     'temp_cnt':'combat_temp_cnt',
                     'same_pledge_cnt':'combat_same_pledge_cnt',
                     'etc_cnt':'combat_etc_cnt'})

    # combat_result.to_csv('combat_result.csv')

    ## (4) pledge테이블 처리

    new_pledge = pledge.sort_values(by=['acc_id','day'])
    new_pledge.index = range(len(new_pledge))
    new_pledge = new_pledge[['acc_id','day'] + list(new_pledge.columns)[2:]]


    def func(x1,x2):
        if x2==0:
            return 0
        else:
            return x1/x2
    new_pledge['pledge_combat_cnt_mean'] = new_pledge.apply(lambda x : func(x['pledge_combat_cnt'],x['combat_char_cnt']),axis=1)
    new_pledge['random_attacker_cnt_mean'] = new_pledge.apply(lambda x : func(x['random_attacker_cnt'],x['combat_char_cnt']),axis=1)
    new_pledge['random_defender_cnt_mean'] = new_pledge.apply(lambda x : func(x['random_defender_cnt'],x['combat_char_cnt']),axis=1)
    new_pledge['same_pledge_cnt_mean'] = new_pledge.apply(lambda x : func(x['same_pledge_cnt'],x['combat_char_cnt']),axis=1)
    new_pledge['temp_cnt_mean'] = new_pledge.apply(lambda x : func(x['temp_cnt'],x['combat_char_cnt']),axis=1)
    new_pledge['etc_cnt_mean'] = new_pledge.apply(lambda x : func(x['etc_cnt'],x['combat_char_cnt']),axis=1)
    new_pledge['combat_play_time_mean'] = new_pledge.apply(lambda x : func(x['combat_play_time'],x['combat_char_cnt']),axis=1)

    new_pledge['non_combat_play_time_mean'] = new_pledge.apply(lambda x : func(x['non_combat_play_time'],x['play_char_cnt']),axis=1)

    pledge_result = new_pledge.groupby(['acc_id','day']).mean()
    pledge_result['char_id'] = new_pledge.drop_duplicates(['acc_id','day','char_id']).groupby(['acc_id','day']).char_id.count()
    pledge_result['server'] = new_pledge.drop_duplicates(['acc_id','day','server']).groupby(['acc_id','day']).server.count()
    pledge_result = pledge_result.reset_index()
    pledge_result = pledge_result[['acc_id','day','char_id','server'] + list(pledge_result.columns[14:-1])]
    pledge_result = pledge_result.rename(columns={'char_id' : 'pledge_char_cnt',
                                                 'server' : 'pledge_server_cnt'})

    ### pledge_size 데이터 프레임 생성

    #### 28일간 play_char_cnt 합계 기준으로 사이즈 잰 것

    pledge_size = new_pledge[['day','pledge_id','play_char_cnt']].drop_duplicates(['day','pledge_id']).groupby(['pledge_id']).sum().reset_index()[['pledge_id','play_char_cnt']]
    pledge_size = pledge_size.rename(columns = {'play_char_cnt' : 'acc_id_cnt'})
    pledge_size = pledge_size.sort_values('acc_id_cnt', ascending=False).reset_index(drop=True)
    pledge_size['pledge_id'] = pledge_size['pledge_id'].astype(str)
    pledge_size.head()

    ### max_playtime_char_id로 혈맹 사이즈 가져오기(activity엔 데이터가 없으나 혈맹에 있는 경우 그날 가장 먼저 등장한 캐릭터의 혈맹으로 사이즈 가져오기)

    activity_max_playtime_char_id = new_activity[['acc_id','day']].drop_duplicates(['acc_id','day'])
    activity_max_playtime_char_id['char_id'] = list(new_activity.sort_values(['acc_id','day','playtime']).groupby(['acc_id','day']).last().char_id)

    pledge_char_id_pledge_id = new_pledge[['acc_id','day','char_id','pledge_id']]
    pledge_char_id_pledge_id['pledge_id'] = pledge_char_id_pledge_id['pledge_id'].astype(str)
    pledge_char_id_pledge_id = pledge_char_id_pledge_id.drop_duplicates(['acc_id','day','char_id'])

    df = activity_max_playtime_char_id.merge(pledge_char_id_pledge_id,on=['acc_id','day','char_id'],how='left').dropna(subset=['pledge_id']).merge(pledge_size,on=['pledge_id'],how='left')
    df2 = pledge_result.merge(df, on=['acc_id','day'], how='left')
    df3 = df2[pd.isna(df2.acc_id_cnt)][['acc_id','day']].reset_index(drop=True)
    df4 = new_pledge.groupby(['acc_id','day']).pledge_id.first().reset_index()
    df5 = df3.merge(df4, on = ['acc_id','day'], how = 'left')
    df5['pledge_id'] = df5['pledge_id'].astype(str)
    df6 = df5.merge(pledge_size, on=['pledge_id'], how = 'left')
    df7 = df[['acc_id','day','pledge_id','acc_id_cnt']]
    df8 = df7.append(df6, ignore_index=True)
    df9 = pledge_result.merge(df8, on = ['acc_id','day'], how = 'left')
    del df9['pledge_id']
    pledge_result = df9.rename(columns={'acc_id_cnt' : 'pledge_size'})


    # 4. save

    total_result = full_acc_id_day.merge(activity_result,
                                         on = ['acc_id','day'], how = 'left')
    total_result = total_result.merge(pledge_result,
                                      on = ['acc_id','day'], how = 'left')
    total_result = total_result.merge(combat_result,
                                      on = ['acc_id','day'], how = 'left')
    total_result = total_result.merge(exchange_result,
                                      on = ['acc_id','day'], how = 'left')
    total_result = total_result.merge(trade_result,
                                      on = ['acc_id','day'], how = 'left')
    total_result = total_result.merge(payment,
                                      on = ['acc_id','day'], how = 'left')

    total_result = total_result.fillna(0)
    total_result = total_result[['acc_id','day','activity_char_cnt','activity_server_cnt','playtime','npc_kill','solo_exp','party_exp','quest_exp','rich_monster','death','revive','exp_recovery','pledge_char_cnt','pledge_server_cnt','pledge_size','max_level','combat_random_attacker_cnt','combat_random_defender_cnt','combat_temp_cnt','combat_same_pledge_cnt','combat_etc_cnt','num_opponent','give_cnt','give_amount','give_price','get_cnt','get_amount','get_price','sell_cnt','sell_amount','sell_price','buy_cnt','buy_amount','buy_price']]
    
    return total_result

