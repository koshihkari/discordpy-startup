import asyncio
import re


import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup


timeout = True


class Toaru(object):
    def __init__(self):
        self.base_value = [2,4,6,8,10]

    def kakera(self,want,assigment_value,detail):
        try:
            if int(detail) > 20:
                return self.miss()
            total = 0
            want = int(want)
            detail = 20 - int(detail)
            for value in self.base_value:
                if int(assigment_value) > value:
                    continue
                while True:
                    total += value
                    want -= 1
                    detail += 1
                    if detail == 20 and value != 10:
                        detail = 0
                        break
                    if want == 0:
                        break
                if want == 0:
                    break
            if value == 10:
                detail = '制限なし'
            else:
                detail = 20 - detail
            msg = f'欠片の価値：{value}\nその価値で購入できる残り個数：{detail}'
            embed = discord.Embed(title='計算結果',color=discord.Color.purple())
            embed.add_field(name='欠片必要個数',value=total)
            embed.add_field(name='欠片購入条件の変化',value=msg)
        except ValueError:
            return self.miss()
        return embed


        
    def koin(self,want):
        try:
            base = int(want) // 5
        except ValueError:
            embed = self.miss()
            return embed
        if int(want) % 5 != 0:
            embed = self.miss()
            return embed
        koukan_num = base
        koukan = base * 800
        kousin = 0
        while True:
            for _ in range(4):
                if not base > 0:
                    break
                kousin += 10
                base -= 1
            for _ in range(5):
                if not base > 0:
                    break                
                kousin += 20
                base -= 1
                
            while base > 0:
                kousin += 30
                base -= 1
            break
        description = '交換必要数：' + str(koukan) +'\n' + '更新必要数：' + str(kousin) + '\n' + '交換回数：' + str(koukan_num) + '\n' + '合計必要数：' + str(kousin+koukan)
        embed = discord.Embed(title='計算結果',description=description,color=discord.Color.green())
        return embed

    def miss(self):
        description = """
        これらを適しているか確認をしてください
        ・値が数字でない
        ・適切な数字でない(コインの場合、一度の交換で5個覚醒結晶が交換されるため)
        ・(欠片の場合)覚醒結晶の交換に必要な欠片の数が2,4,6,8,10のいずれでもない
        ・kakeraコマンドのdetailに20より大きい値を与えている
        """
        embed = discord.Embed(title='与えられた値が不適です',description=description,color=discord.Color.red())
        return embed


class WeatherSearch():
    def search_weather(self,timeout):
        if not timeout:
            return None
        url = 'https://rss-weather.yahoo.co.jp/rss/days/4410.xml'
        responce = requests.get(url)
        if responce.status_code != 200:
            return None
        soup = BeautifulSoup(responce.text,'html.parser')
        week_date = soup.find_all('title')
        return week_date

    def properly(self,week_date):
        n = 1
        embed = discord.Embed(title='東京の天気',color=discord.Color.red())
        for day_date in week_date:
            if n == 1:
                n += 1
                continue
            base_devide = re.search('Y',day_date.text)
            base_info = day_date.text[:base_devide.start()-3]
            # 【 7日（月） 東京（東京） 】 晴一時雨 - 31℃/25℃
            devide_date = re.search('）',base_info)
            date_date = base_info[1:devide_date.end()]
            devide_weather = re.search('-',base_info)
            start_weather_message = re.search('】',day_date.text)
            weather_date = base_info[start_weather_message.end():devide_weather.start()]
            temperature_date = base_info[devide_weather.end()+1:]
            message = '・' + weather_date + '\n' + '・' + temperature_date
            embed.add_field(name=date_date,value=message)
            if n == 8:
                break
            n += 1
        return embed

    def wrong(self):
        message = """
        時間を空けてもう一度実行しなおしてください
以下が失敗の原因と考えられます
・情報の取得に失敗
・連続の実行を確認
このメッセージが何度も確認される場合はこしひかりまで連絡をお願いします
        """
        embed = discord.Embed(title='コマンドの実行に失敗しました',description=message,color=discord.Color.red())
        return embed


class Sonota(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    @commands.command()
    async def weather(self,ctx):
        global timeout
        weather_search = WeatherSearch()
        week_date = weather_search.search_weather(timeout)
        timeout = False
        if week_date is None:
            embed = weather_search.wrong()
            await ctx.send(embed=embed)
        embed = weather_search.properly(week_date)
        await ctx.send(embed=embed)
        await asyncio.sleep(5)
        timeout = True
        
    @commands.command()
    async def koin(self,ctx,want):
        """
        仮想試練・異能決戦・異能対戦・共闘コインによる覚醒結晶の交換に必要なコインの数を計算します
        """
        toaru = Toaru()
        embed = toaru.koin(want)
        await ctx.send(embed=embed)
    
    @commands.command()
    async def kakera(self,ctx,want=0,value=2,detail=20):
        """
        覚醒結晶のかけらの必要数を計算します。(当ってるかわからない)
        コマンド 希望する数 覚醒結晶購入に必要なかけらの数(初期設定2) かけらの価値が変わらずにいくつまで交換できるか(初期設定20)
        """
        toaru = Toaru()
        embed = toaru.kakera(want,value,detail)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Sonota(bot))
