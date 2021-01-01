from cog.jinro_game.user import User

import discord


user_class = User(discord.User)


class EmbedNotification():
    def make(self, title, description, color):
        embed = discord.Embed(
            title = title,
            description = description,
            color = color
            )
        return embed
    
    def recruit(self, situation, player_list, gamemaster):
        title = f'参加者リスト({situation})'
        description = gamemaster.participants_list(player_list)
        color = discord.Color.purple()
        return self.make(title, description, color)

    def position(self, position, page: bool, index):
        title = position.name
        if page:
            title += f'({index + 1}/6ページ)'
        description = position.explanation
        color = position.color
        return self.make(title, description, color)

    def position_field(self, embed, index, players, template):
        embed.add_field(
            name = '役職数',
            value = f'現在の設定数：{template.position_dict[template.position_list[index].name]}\n設定可能範囲：{template.ideal_position[index]}',
            inline=False
        )
        embed.add_field(
            name = '総役職数',
            value = f'現在の総役職数：{template.sum_position()}\n総プレイヤー数：{players}',
            inline = False
        )
    
    def nonsense(self, embed, reaction):
        embed.add_field(name='注意', value=f'{reaction}は使用できません！')

    def notification(self, user):
        title = 'あなたの役職は・・・'
        description = f'**{user.position.name}**です！'
        color = user.position.color
        embed = self.make(title, description, color)
        embed.add_field(name='役職の説明', value=user.position.explanation, inline=False)
        return embed

    def vote(self, name_list):
        title = '処刑投票'
        description = f"\n".join([str(index) + '：' + name for index, name in enumerate(name_list, 1)])
        color = discord.Color.magenta()
        return self.make(title, description, color)

    def psychic_target(self, psychic, target_list):
        title = psychic.position.ability_title + 'を選択'
        description = f"\n".join([str(index) + '：' + target.name for index, target in enumerate(target_list, 1)])
        color = psychic.position.color
        return self.make(title, description, color)

    def win(self, win_team, winners, gamemaster):
        title = f'{win_team}チームの勝利です'
        description = gamemaster.winner(winners)
        color = discord.Color.red()
        return self.make(title, description, color)

    def situation(self, user_list, gamemaster):
        survivors = gamemaster.make_survivor_list(user_list).copy()
        corposes = gamemaster.make_corpse_list(user_list).copy()
        title = '生存状況'
        description = ''
        color = discord.Color.blue()
        embed = self.make(title, description, color)
        embed.add_field(
            name = f'生存者（{len(survivors)}名）',
            value = f"\n".join('・' + name for name in list(map(user_class.playerName, survivors))),
            inline=False
            )
        embed.add_field(
            name = f'死亡者（{len(corposes)}名）',
            value = f"\n".join('・' + name for name in list(map(user_class.playerName, corposes))),
            inline = False
            )
        return embed
