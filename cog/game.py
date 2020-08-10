import asyncio
import random

import discord
from discord.ext import commands


OWN_ID = 720137311186059275

class Numeron(object):
    def __init__(self,player_1,player_2):
        self.player_1 = player_1
        self.player_2 = player_2
        self.player_1_number = []
        self.player_2_number = []
        self.situation_p1 = []
        self.situation_p2 = []
        self.now_player = player_1
        #以下はbot対戦時のみ
        self.candidates = [(x,y,z) for x in range(10) for y in range(10) for z in range(10) if x != y and y != z and x != z]
        self.new_candidates = []
        self.bot_eat = 0
        self.bot_bite = 0
        self.bot_number = 0

    def start(self):
        """
        botの初手数字決定
        """
        l = [(x,y,z) for x in range(10) for y in range(10) for z in range(10) if x != y and y != z and x != z]
        number = random.choice(l)
        return number

    def ai_decide(self):
        for cand in self.candidates:
            num_of_eat = 0
            num_of_bite = 0
            for number_digit, cand_digit in zip(self.bot_number,cand):
                if cand_digit == number_digit:
                    num_of_eat += 1  # 同じ位置に同じ数字がある、EAT
                elif cand_digit in self.bot_number:
                    num_of_bite += 1  # 同じ位置ではないが同じ数字がある、BITE
            if num_of_eat == self.bot_eat and num_of_bite == self.bot_bite:
                self.new_candidates.append(cand)  # EAT、BITEの条件が適合したので新しい候補リストに入れる
        self.candidates = self.new_candidates.copy()
        self.new_candidates.clear()
        atack = random.choice(self.candidates)
        return atack

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

    def eat_bite(self,atack_num,opponent_num):
        """
        EAT,BITEの判定をします。
        """
        n = 0
        eat = 0
        bite = 0
        for _ in range(3):
            use_judge = [0,1,2]
            use_judge.remove(n)
            print(opponent_num,atack_num,n)
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
        reply1 = ''
        reply2 = ''
        for i in situation1:
            reply1 += str(i['ans']) + '：' + str(i['eat']) + 'EAT-' + str(i['bite']) + 'BITE\n'
        for v in situation2:
            reply2 += str(v['ans']) + '：' + str(v['eat']) + 'EAT-' + str(v['bite']) + 'BITE\n'
        embed = discord.Embed(title='対戦状況っすー！',color=0x00FFFF)
        embed.add_field(name=self.player_1.name,value=reply1,inline=False)
        if len(reply2) == 0:
            embed.add_field(name=self.player_2.name,value='コールなし',inline=False)
        else:
            embed.add_field(name=self.player_2.name,value=reply2,inline=False)
        return embed

    def rt_dict(self,atack_list,eat,bite):
        atack_list_str = ''.join(map(str, atack_list))
        d = {'ans': atack_list_str, 'eat': eat, 'bite': bite}
        return d


class GmaeCog(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.command(aliases=["num"])
    async def numeron(self,ctx,opponent:discord.Member):
        """
        メンションした相手とnumeronで対戦しまっすー！先攻はランダムでbotが選びまっすー！
        """
        if ctx.channel == ctx.author.dm_channel:
            await ctx.send('DMではなくサーバーのチャンネルでコマンドを実行してっすー！')
            return
        if opponent.bot:
            if opponent.id != OWN_ID:
                await ctx.send(f'{self.bot.user.name}以外のbotをメンションしないでっすー！')
                return
        random_number = random.randint(1,2)
        if opponent.id == OWN_ID:
            await ctx.send(f'{ctx.author.name}が先攻でっすー！')
            numeron = Numeron(ctx.author,opponent)
        elif random_number == 1:
            reply_atack = ctx.author.name + "が先攻でっすー！"
            await ctx.send(reply_atack)
            numeron = Numeron(ctx.author,opponent)
        else:
            reply_atack = opponent.name + "が先攻でっすー！"
            await ctx.send(reply_atack)
            numeron = Numeron(opponent,ctx.author)
        #このループで数字を決める
        while True:
            if numeron.player_2.bot:
                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel
                await ctx.send('決めた数字を送ってください(相手が当てる数字)。')
                try:
                    str_num1 = await self.bot.wait_for('message',check=check,timeout=30.0)
                except asyncio.TimeoutError:
                    await ctx.send('30秒間の無操作によりゲームを終了します')
                    return
                if not numeron.judge(str_num1.content):
                    continue
                else:
                    numeron.player_1_number = numeron.judge(str_num1.content)
                    numeron.player_2_number = numeron.start()
                    break
            else:
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
                        await ctx.send('2分間の無操作によりゲームを終了しまっすー！')
                        return
                    if not numeron.judge(str_num1.content):
                        continue
                    else:
                        break
                numeron.player_1_number = numeron.judge(str_num1.content)
                if numeron.player_2.dm_channel == None:
                    await numeron.player_2.create_dm()
                await numeron.player_2.dm_channel.send('決めたを数字を送ってください(相手が当てる数字)。')            
                while True:
                    try:
                        str_num2 = await self.bot.wait_for('message',check=check_opponent,timeout=120.0)
                    except asyncio.TimeoutError:
                        await ctx.send('2分間の無操作によりゲームを終了するっすー！')
                        return
                    if not numeron.judge(str_num2.content):
                        continue
                    else:
                        break
                numeron.player_2_number = numeron.judge(str_num2.content)
                break


        turn_rep = numeron.now_player.mention + 'の番っすー！'
        await ctx.send(turn_rep)
        n = 1

        while True:          
            #攻めの値の決定
            if numeron.now_player.id == OWN_ID:
                if n == 2:
                    atack_list = numeron.start()
                else:
                    atack_list = numeron.ai_decide()
            else:
                def check_p1_bot(m):
                    return m.author == numeron.now_player and m.channel == ctx.channel
                try:
                    atack_num = await self.bot.wait_for('message',check=check_p1_bot,timeout=180.0)
                except asyncio.TimeoutError:
                    await ctx.send('3分間も放置しやがって！終わるわよ')
                    return
                if atack_num.content == 'end':
                    await ctx.send('ゲームを終了するっすー！')
                    return
                #numeron.judgeを活用してatack_numをリスト化する
                atack_list = numeron.judge(atack_num.content)
                if not atack_list:
                    continue
            if numeron.now_player == numeron.player_1:
                eat, bite = numeron.eat_bite(atack_list,numeron.player_2_number)
            else:
                eat, bite = numeron.eat_bite(atack_list,numeron.player_1_number) 
            if numeron.now_player.id == OWN_ID:
                numeron.bot_eat = eat
                numeron.bot_bite = bite
                numeron.bot_number = atack_list
            result_dict = numeron.rt_dict(atack_list, eat, bite)
            if numeron.now_player == numeron.player_1:
                numeron.situation_p1.append(result_dict)
            elif numeron.now_player == numeron.player_2:
                numeron.situation_p2.append(result_dict)
            if numeron.player_2.bot:
                if numeron.now_player.id != OWN_ID:
                    pass
                else:
                    embed = numeron.mk_situation(numeron.situation_p1,numeron.situation_p2)
                    await ctx.send(embed=embed)
            else:
                embed = numeron.mk_situation(numeron.situation_p1,numeron.situation_p2)
                await ctx.send(embed=embed)
            if eat == 3:
                finish_rep = numeron.now_player.name + 'の勝ちっすー！'
                str_p1_number = ''.join(map(str, numeron.player_1_number))
                str_p2_number = ''.join(map(str, numeron.player_2_number))
                tell_answer = numeron.player_1.name + ": " + str_p1_number + ', ' + numeron.player_2.name + ": " + str_p2_number
                await ctx.send(finish_rep)
                await ctx.send(tell_answer)
                break
            if numeron.now_player == numeron.player_1:
                numeron.now_player = numeron.player_2
            else:
                numeron.now_player = numeron.player_1
            
            if numeron.now_player.bot:
                pass
            else:
                turn_rep = numeron.now_player.mention + 'の番っすー！'
                await ctx.send(turn_rep)
            n += 1

    @commands.command(aliases=["nr"])
    async def nrule(self,ctx):
        """
        numeronの簡易的なルール説明をしまっすー！
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
