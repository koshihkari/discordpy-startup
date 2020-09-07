import asyncio
import re


import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup


timeout = True


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
    async def tenki(self,ctx):
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


def setup(bot):
    bot.add_cog(Sonota(bot))