import urllib.parse

import discord
from discord.ext import commands
import wikipedia
import requests


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
            except Exception as e:
                print(e)
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


def setup(bot):
    bot.add_cog(SearchCog(bot))
