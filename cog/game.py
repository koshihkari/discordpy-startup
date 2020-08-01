import asyncio
import random

import discord
from discord.ext import commands


class Numeron(object):
    def __init__(self,player_1,player_2):
        self.player_1 = player_1
        self.player_2 = player_2
        self.player_1_number = []
        self.player_2_number = []
        self.now_player = player_1

    def judge(self,number):
        """
        引数に与えられた値が、数字であるか・重複なしで3種の数字かの判定。
        正しい値の時のみbase_listが返され、それ以外はFalseが返される
        """
        base_list = []
        for s in number:
            try:
                base_list.append(int(s))
            except ValueError:
                return False
        if not len(base_list) == len(set(base_list)) == 3:
            return False
        return base_list

    def eat_bite(self,atack_num:list,opponent_num:list):
        """
        EAT,BITEの判定をします。
        """
        n = 0
        eat = 0
        bite = 0
        for _ in range(3):
            use_judge = [0,1,2]
            use_judge.remove(n)
            if opponent_num[n] != atack_num[n]:
                if opponent_num[n] == atack_num[use_judge[0]] or opponent_num[n] == atack_num[use_judge[1]]:
                    bite += 1
                else:
                    pass
            else:
                eat += 1
            n += 1
        return eat, bite
    
    def mk_situation(self,situation1:list,situation2:list):
        reply = self.player_1.mention + '\n'
        for i in situation1:
            reply += str(i['ans']) + '：' + str(i['eat']) + 'EAT-' + str(i['bite']) + 'BITE\n'
        reply += '----------------------\n' + self.player_2.mention + '\n'
        for v in situation2:
            reply += str(v['ans']) + '：' + str(v['eat']) + 'EAT-' + str(v['bite']) + 'BITE\n'
        return reply

    def rt_dict(self,answer,eat,bite):
        d = {'ans': answer, 'eat': eat, 'bite': bite}
        return d


class GmaeCog(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.command(aliases=["num"])
    async def numeron(self,ctx,opponent:discord.Member):
        """
        メンションした相手とnumeronで対戦します。先攻はランダムでbotが選びます。
        """
        if ctx.channel == ctx.author.dm_channel:
            await ctx.send('DMではなくサーバーのチャンネルでコマンドを実行してください')
            return
        if opponent.bot:
            await ctx.send('botをメンションしないでください')
            return
        random_number = random.randint(1,2)
        if random_number == 1:
            reply_atack = ctx.author.name + "が先攻です"
            await ctx.send(reply_atack)
            numeron = Numeron(ctx.author,opponent)
        else:
            reply_atack = opponent.name + "が先攻です"
            await ctx.send(reply_atack)
            numeron = Numeron(opponent,ctx.author)
        #このループで数字を決める
        while True:
            #個人チャットでの受け取りをできるようにする
            def check_player(m):
                return m.author == numeron.player_1 and m.channel == numeron.player_1.dm_channel
            def check_opponent(m):
                return m.author == numeron.player_2 and m.channel == numeron.player_2.dm_channel

            await ctx.send('DMでBotの指示を待機してください')
            if numeron.player_1.dm_channel == None:
                await numeron.player_1.create_dm()
            await numeron.player_1.dm_channel.send('決めた数字を送ってください(相手が当てる数字)。')
            #numeron.judgeを用いて番号を決定する
            while True:    
                try:
                    str_num1 = await self.bot.wait_for('message',check=check_player,timeout=120.0)
                except asyncio.TimeoutError:
                    await ctx.send('2分間の無操作によりゲームを終了します')
                    return
                if not numeron.judge(str_num1.content):
                    continue
                else:
                    break
            
            if numeron.player_2.dm_channel == None:
                await numeron.player_2.create_dm()
            await numeron.player_2.dm_channel.send('決めたを数字を送ってください(相手が当てる数字)。')            
            while True:
                try:
                    str_num2 = await self.bot.wait_for('message',check=check_opponent,timeout=120.0)
                except asyncio.TimeoutError:
                    await ctx.send('2分間の無操作によりゲームを終了します')
                    return
                if not numeron.judge(str_num2.content):
                    continue
                else:
                    break

            numeron.player_1_number = numeron.judge(str_num1.content)
            numeron.player_2_number = numeron.judge(str_num2.content)
            break

        turn_rep = numeron.now_player.mention + 'の番です'
        await ctx.send(turn_rep)

        while True:          
            #攻めの値の決定
            def check(m):
                return m.author == numeron.now_player and m.channel == ctx.channel
            atack_num = await self.bot.wait_for('message',check=check)
            if atack_num.content == 'end':
                await ctx.send('ゲームを終了します。')
                return
            #numeron.judgeを活用してatack_numをリスト化する
            atack_list = numeron.judge(atack_num.content)
            if not atack_list:
                continue
            if numeron.now_player == numeron.player_1:
                eat, bite = numeron.eat_bite(atack_list,numeron.player_2_number)
            else:
                eat, bite = numeron.eat_bite(atack_list,numeron.player_1_number) 
            result_dict = numeron.rt_dict(atack_num.content, eat, bite)
            if numeron.now_player == numeron.player_1:
                numeron.situation_p1.append(result_dict)
            elif numeron.now_player == numeron.player_2:
                numeron.situation_p2.append(result_dict)
            send_reply = numeron.mk_situation(numeron.situation_p1,numeron.situation_p2)
            embed = discord.Embed(title='対戦状況',description=send_reply,color=0x00FFFF)
            await ctx.send(embed=embed)
            if eat == 3:
                finish_rep = numeron.now_player.name + 'の勝利です!'
                tell_answer = numeron.player_1.name + ": " + str_num1.content + ', ' + numeron.player_2.name + ": " + str_num2.content
                await ctx.send(finish_rep)
                await ctx.send(tell_answer)
                break
            if numeron.now_player == numeron.player_1:
                numeron.now_player = numeron.player_2
            else:
                numeron.now_player = numeron.player_1
            
            turn_rep = numeron.now_player.mention + 'の番です'
            await ctx.send(turn_rep)

    @commands.command(aliases=["nr"])
    async def nrule(self,ctx):
        """
        numeronの簡易的なルール説明をします。
        詳しく知りたい方はwikiコマンドを使用してください。
        """
        reply = """
        ```numeronのルールを説明します。
・それぞれのプレイヤーが、0-9までの数字が書かれた10枚のカードのうち3枚を使って、3桁の番号を作成する。カードに重複は無いので「550」「377」といった同じ数字を2つ以上使用した番号は作れない。
・先攻のプレイヤーは相手の番号を推理してコールする。相手はコールされた番号と自分の番号を見比べ、コールされた番号がどの程度合っているかを発表する。数字と桁が合っていた場合は「EAT」（イート）、数字は合っているが桁は合っていない場合は「BITE」（バイト）となる。 
・例として相手の番号が「765」・コールされた番号が「746」であった場合は、3桁のうち「7」は桁の位置が合致しているためEAT、「6」は数字自体は合っているが桁の位置が違うためBITE。EATが1つ・BITEが1つなので、「1EAT-1BITE」となる。
・これを先攻・後攻が繰り返して行い、先に相手の番号を完全に当てきった（3桁なら3EATを相手に発表させた）プレイヤーの勝利となる(wikipediaより引用)。```
"""
        await ctx.send(reply)


def setup(bot):
    bot.add_cog(GmaeCog(bot))
