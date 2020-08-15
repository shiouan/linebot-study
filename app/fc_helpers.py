# coding=utf-8

import requests

from linebot.models import MessageAction, QuickReply, QuickReplyButton
import pandas as pd


class FcParser(object):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
            }
        self.all_fc_interest_rate = self.__get_all_fc_interest_rate()

    def __get_TCB_rate(self):
        url = 'https://www.tcb-bank.com.tw/finance_info/Pages/foreign_deposit_loans_rate.aspx'
        response = requests.get(url=url, headers=self.headers)
        df = pd.read_html(response.text)[6]
        df.columns = ['幣別', '活期', '一週', '一個月', '三個月', '六個月', '九個月', '一年']
        df.dropna(inplace=True)
        df['銀行'] = '合作金庫'
        df = df.apply(lambda s: s.str.replace('%', ''))
        return df

    def __get_ESUN_rate(self):
        url = 'https://www.esunbank.com.tw/bank/personal/deposit/rate/foreign/deposit-rate'
        response = requests.get(url=url, headers=self.headers)
        df = pd.read_html(response.text)[0].drop([0, 1])
        
        df.columns = ['幣別', '活期', '一週', '二週', '三週', '一個月', '三個月', '六個月', '九個月', '一年']
        df['銀行'] = '玉山銀行'
        return df

    def __get_TAIWAN_rate(self):
        url = 'https://rate.bot.com.tw/ir?Lang=zh-TW'
        response = requests.get(url=url, headers=self.headers)
        df = pd.read_html(response.text)[0]
        df = df.drop(df.columns[[-1, -2]], axis=1)
        df.columns = ['幣別', '活期', '一週', '二週', '三週', '一個月', '三個月', '六個月', '九個月', '一年']
        df = df[df['幣別'] != '美金 (USD) 大額']
        df['銀行'] = '臺灣銀行'
        return df
        
    def __get_all_fc_interest_rate(self):
        # get interest rates from each banks
        tcb_fc_rate = self.__get_TCB_rate()
        esun_fc_rate = self.__get_ESUN_rate()
        taiwan_fc_rate = self.__get_TAIWAN_rate()
        # integration interest rates
        df = pd.concat([tcb_fc_rate, esun_fc_rate, taiwan_fc_rate], sort=False)
        df['幣別'] = df['幣別'].str.extract('([A-Z]+)')
        df.set_index(['銀行', '幣別'], inplace=True)
        columns = ['活期', '一週', '二週', '三週', '一個月', '三個月', '六個月', '九個月', '一年']
        all_fc_interest_rate = df.apply(pd.to_numeric, errors='coerce')[columns]
        return all_fc_interest_rate
    
    def get_best_fc_interest_rate(self, currency):
        index = self.all_fc_interest_rate.index.get_level_values('幣別') == currency
        fc_interest_rate = self.all_fc_interest_rate.iloc[index]
        best_fc_interest_rate = pd.DataFrame({
            '銀行': fc_interest_rate.idxmax(),
            '利率': fc_interest_rate.max()
            })
        return best_fc_interest_rate

    def update_fc_interest_rate(self):
        self.all_fc_interest_rate = self.__get_all_fc_interest_rate()


class FcConsultant(object):
    def __init__(self):
        self.fc_parser = FcParser()
    
    def __set_menu(self):
        message = '請選擇幣別'
        quick_reply=QuickReply(items=[
                QuickReplyButton(action=MessageAction(label="美元(USD)", text="@利率-USD")),
                QuickReplyButton(action=MessageAction(label="人民幣(CNY)", text="@利率-CNY")),
                QuickReplyButton(action=MessageAction(label="澳幣(AUD)", text="@利率-AUD")),
                QuickReplyButton(action=MessageAction(label="港幣(HKD)", text="@利率-HKD")),
                QuickReplyButton(action=MessageAction(label="新加坡幣(SGD)", text="@利率-SGD"))
                ])
        return message, quick_reply

    def __show_best_fc_interest_rate(self, currency):
        message = f'【最佳{currency}利率】\n'
        quick_reply = None
        df = self.fc_parser.get_best_fc_interest_rate(currency)
        for index, row in df.iterrows():
            message += '\n{}｜{}｜{}'.format(index, row['銀行'][0], row['利率'])
        return message, quick_reply

    def anwser(self, message):
        msg_segment = message.split('-')
        if msg_segment[0] == '@利率':
            if len(msg_segment) == 1 :
                message, quick_reply = self.__set_menu()
            else:
                currency = msg_segment[1]
                message, quick_reply = self.__show_best_fc_interest_rate(currency)
        return message, quick_reply
