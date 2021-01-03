from cog.jinro_game.embed_maker import EmbedNotification
from cog.jinro_game.gamemaster import GameMaster
from cog.jinro_game.template import Template
from cog.jinro_game.position import PositionMaster
from cog.jinro_game.user import User

import asyncio

import discord
from discord.ext import commands


make_embed = EmbedNotification()
gamemaster = GameMaster()
positionmaster = PositionMaster()



class Main(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reaction_list = ['👍', '👎', '⭐']
        self.template_reaction_list = ['⬅️', '➡️', '⬆️', '⬇️', '👍']
    
    @commands.command()
    async def jinro(self, ctx, decide='auto'):
        turn = 1
        player_list = [ctx.author]
        situation = '募集中'
        recruit_content = 'このメッセージに👍をリアクションで参加、👎で参加をキャンセル、⭐で募集締め切り\n(10分放置するとゲームが破棄されます)'
        recruit = await ctx.send(content=recruit_content, embed=make_embed.recruit(situation, player_list, gamemaster))
        for reaction in self.reaction_list:
            await recruit.add_reaction(reaction)
        def check(reaction, user):
            return reaction.message.channel == recruit.channel and reaction.message.id ==recruit.id and not user.bot
        while True:
            #参加者を募集します
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=600, check=check)
            except asyncio.TimeoutError:
                await recruit.edit(content='ゲームを終了します')
                return
            player_list, end_recruit_bool = gamemaster.recruit(str(reaction.emoji), user, player_list)
            if end_recruit_bool:
                situation, recruit_content = '(締め切り)', '募集は終了しました'
            await recruit.edit(content=recruit_content, embed=make_embed.recruit(situation, player_list, gamemaster))
            if end_recruit_bool:
                break
            continue
        #参加者をクラスとして新しくリスト化
        user_list = []
        for player in player_list:
            user_list.append(User(player))
        if len(user_list) < 4:
            await ctx.send('ゲームの開始には最低4人必要です')
            return
        target_list = voter_list = survivor_list = user_list.copy()
        # 役職数の設定
        if decide != 'auto':
            template = Template()
            players = len(user_list)
            embed = make_embed.position(template.position_list[0], True, template.index)
            make_embed.position_field(embed, template.index, players, template)
            message = await ctx.send(embed=embed)
            for reaction in self.template_reaction_list:
                await message.add_reaction(reaction)
            def reaction_check(reaction, user):
                return reaction.message == message and str(reaction.emoji) in self.template_reaction_list and not user.bot
            while True:
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=600, check=reaction_check)
                except asyncio.TimeoutError:
                    await ctx.send('ゲームを破棄しました')
                await reaction.remove(user)
                gamemaster.edit_index(template, reaction, players, template.index)
                embed = make_embed.position(template.position_list[template.index], True, template.index)
                make_embed.position_field(embed, template.index, players, template)
                gamemaster.cant_edit(template, reaction, players, template.index, embed)
                await message.edit(embed=embed)
                embed.clear_fields()
                if gamemaster.complete_decide_position(reaction, players, template):
                    break
        # 役職の配布
                positions = positionmaster.manual_make_positions(template.position_dict)
        else:
            positions = gamemaster.makePositionList(player_list, positionmaster.make_position_list(len(user_list)))
        gamemaster.distribute(user_list, positions)
        wolf_list = gamemaster.make_wolf_list(user_list)
        #役職を通達
        for user in user_list:
            if user.discord_user.dm_channel is None:
                await user.discord_user.create_dm()
            await user.discord_user.dm_channel.send(embed=make_embed.notification(user))
            if user in wolf_list and len(wolf_list) > 1:
                wolf_list.remove(user)
                wolf_member_name = f"\n".join(name for name in list(map(user.playerName, wolf_list)))
                await user.discord_user.dm_channel.send(f'仲間の人狼は{wolf_member_name}')
                wolf_list.append(user)
        await ctx.send(embed=make_embed.whole_notification(template))
        await asyncio.sleep(20)

        while True:
            """ 昼のターン """
            # 決選投票も含めて一日の最大投票回数は3回
            survivor_list = gamemaster.make_survivor_list(user_list).copy()
            target_list = voter_list = survivor_list.copy()
            await ctx.send(f'昼のターン({turn}日目)')
            def vote_check(m):
                if m.content.isdecimal():
                    return 1 <= int(m.content) <= len(target_list)
                return False
            # 投票カウントのリセット
            for user in user_list:
                user.vote_count_reset()
            for num in range(3):
                """投票"""
                for index, user in enumerate(voter_list):
                    gamemaster.first_vote_remove(num, target_list, user)
                    name_list = [target.name for target in target_list]
                    await user.discord_user.dm_channel.send(embed=make_embed.vote(name_list))
                    try:
                        vote_message = await self.bot.wait_for('message', timeout=600, check=vote_check)
                    except asyncio.TimeoutError:
                        await ctx.send('ゲームを終了します')
                        return
                    target_list[int(vote_message.content)-1].givenVote()
                    gamemaster.first_vote_insert(num, target_list, user, index)
                #一番多く票を集めた人物のリストを受けとる
                will_kill_list = gamemaster.vote(survivor_list).copy()
                if len(will_kill_list) == 1:
                    killed_user = will_kill_list[0]
                    killed_user.killed()
                    await ctx.send(f'投票の結果、**{killed_user.name}**が処刑されました')
                    break
                elif len(will_kill_list) > 1 and (num == 2 or len(voter_list) == 0):
                    await ctx.send('投票の結果、処刑は行わないことになりました')
                else:
                    await ctx.send('決選投票になりました、再度投票をしてください')
                    voter_list = [voter for voter in survivor_list if not voter in will_kill_list]
                    target_list = will_kill_list.copy()
                    continue
            await ctx.send(embed=make_embed.situation(user_list, gamemaster))
            survivor_list = gamemaster.make_survivor_list(user_list)
            if gamemaster.finish_judge(wolf_list, survivor_list):
                break
            
            """ 夜のターン """
            survivor_list = gamemaster.make_survivor_list(user_list)
            await ctx.send(f'夜のターンになりました({turn}日目)')
            #殺害を実行する人狼の決定
            killer = gamemaster.skip_or_kill(wolf_list)
            def psychic_check(m):
                if m.content.isdecimal():
                    return 1 <= int(m.content) <= len(psychic_target_list)
                return False
            for psychic in gamemaster.make_psychic_list(survivor_list):
                if psychic.dead:
                    continue
                if psychic.position.beWolf:
                    if killer != psychic:
                        continue
                embed, psychic_target_list = gamemaster.psychic_target(psychic, user_list)
                await psychic.discord_user.dm_channel.send(embed=embed)
                try:
                    target_index = await self.bot.wait_for('message', timeout=600, check=psychic_check)
                except asyncio.TimeoutError:
                    await ctx.send('ゲームを終了します')
                    return
                if psychic.position.name == '占い師' or psychic.position.name == '霊媒師':
                    embed = make_embed.check_position(psychic_target_list, int(target_index.content)-1)
                    await psychic.discord_user.dm_channel.send(embed=embed)
                else: # name == '人狼' or name == '騎士'
                    gamemaster.will_received(psychic_target_list, int(target_index.content)-1, psychic)
                    await target_index.add_reaction('👍')
            await ctx.send(embed=gamemaster.daybreak())
            await ctx.send(embed=make_embed.situation(user_list, gamemaster))
            turn += 1
            await asyncio.sleep(30)
        winners, team_name = gamemaster.winner_judge(user_list, wolf_list)
        await ctx.send(embed=make_embed.win(team_name, winners, gamemaster))

def setup(bot):
    bot.add_cog(Main(bot))
