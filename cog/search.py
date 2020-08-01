import urllib.parse

import discord
from discord.ext import commands
import wikipedia
import requests


class Weather(object):
    def weather_search(self,user_id):
    #{user_id(int):weather_id(str)}
        id_dict = {625161458145034270:'130010',677040897514536960:'120010',475916023690821642:'140020'}
        url = 'http://weather.livedoor.com/forecast/webservice/json/v1?'
        try:
            query_params = {'city': id_dict[user_id]}
        except KeyError:
            return ['あなたの居住区は登録されていません','登録を希望する場合はこしひかりに連絡連絡～♪']
        result_list = []
        data = requests.get(url, params=query_params).json()
        for weather in data['forecasts']:
            result_list.append(weather['dateLabel'] + 'の天気：' + weather['telop'])
        return result_list


class SearchCog(commands.Cog):

    def __init__(self,bot):
        self.bot = bot
    
    @commands.command()
    async def wiki(self,ctx,*,search_word):
        """
        指定単語をWikipediaで検索します。
        10個以内の検索候補に絞り、指定されたワードの説明、URLを送ります。
        """
        wikipedia.set_lang('ja')
        if search_word == 'random':
            random_word = wikipedia.random()
            title = f'検索結果：{random_word}'
            random_page = wikipedia.page(random_word)
            random_content = random_page.content
            responce_word = random_word
            responce_word = random_content[0:random_content.find("。")] + "。\n"                
            wiki_word = urllib.parse.unquote(random_page.url[30:])
            responce_word += 'https://ja.wikipedia.org/wiki/' + wiki_word
            embed = discord.Embed(title=title, description=responce_word, color=0xc1661c)
            await ctx.send(embed=embed)
            return

        number = 0
        express = ''
        search = wikipedia.search(search_word)
        for i in search:
            number += 1
            express += str(number) + ':' + i + '\n'
        embed = discord.Embed(title='検索候補',description=express,color=0x00FFFF)
        await ctx.send(embed=embed)

        if len(search) > 0:

            def check(m):
                if not m.content.isdecimal():
                    return False
                else:
                    return m.author == ctx.author and m.channel == ctx.channel and 1<= int(m.content) <= 10

            base_index = await self.bot.wait_for('message',check=check)
            index = int(base_index.content) - 1
            try:
                wiki_page = wikipedia.page(search[index])
            except Exception:
                responce_word = 'エラーだよ！'
            else:
                wiki_content = wiki_page.content
                responce_word = wiki_content[0:wiki_content.find("。")] + "。\n"                
                wiki_word = urllib.parse.unquote(wiki_page.url[30:])
                responce_word += 'https://ja.wikipedia.org/wiki/' + wiki_word
                #31
        else:
            responce_word = 'その単語は登録されてないよ！'
    
        #return responce_word
        embed = discord.Embed(title='検索結果', description=responce_word, color=0x00FFFF)
        await ctx.send(embed=embed)

    @commands.command()
    async def weather(self,ctx):
        """
        コマンド実行者居住区の天気を知ることができます
        """
        weather = Weather()
        result = weather.weather_search(ctx.author.id)
        title_name = f'★{ctx.author.name}居住区の天気★'
        word_num = len(result)
        if word_num == 2:
            reply = f'{result[0]}\n{result[1]}'
        elif word_num == 3:
            reply = f'{result[0]}\n{result[1]}\n{result[2]}'
        else:
            reply = 'エラーだよ！'
        embed = discord.Embed(title=title_name,description=reply,color=0X00BFFF)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(SearchCog(bot))
