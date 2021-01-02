from cog.jinro_game.embed_maker import EmbedNotification

import random

import discord


make_embed = EmbedNotification()


class GameMaster():
    def __init__(self):
        self.will_be_killed = None
        self.will_be_protected = None

    def participants_list(self, player_list):
        description = ''
        for player in player_list:
            description += f'・{player.name}\n'
        return description

    def recruit(self, emoji, user, players):
        """募集メッセージへのリアクションに対して動作します"""
        player_list = players.copy()
        if emoji == '👍':
            if not user in player_list:
                player_list.append(user)
            return player_list, False
        elif emoji == '👎':
            if user in player_list:
                player_list.remove(user)
            return player_list, False
        elif emoji == "⭐":
            return player_list, True
        elif emoji == "🔁":
            player_list.clear()
            return player_list, False
        else:
            return player_list, False

    def edit_index(self, template, reaction, players, index):
        emoji = str(reaction.emoji)
        if emoji == '⬅️':
            if template.index != 0:
                template.back_page()
        elif emoji == '➡️':
            if template.index != players + 1:
                template.next_page()
        elif emoji == '⬆️':
            if template.judge_number(players, reaction):
                template.position_dict[template.position_list[index].name] += 1
        elif emoji == '⬇️':
            if template.minimum_judge():
                template.position_dict[template.position_list[index].name] -= 1
        else:
            pass

    def cant_edit(self, template, reaction, players, index, embed):
        emoji = str(reaction.emoji)
        if emoji == '⬅️':
            if template.index == 0:
                make_embed.nonsense(embed, emoji)
        elif emoji == '➡️':
            if template.index == 5:
                make_embed.nonsense(embed, emoji)
        elif emoji == '⬆️':
            if not template.judge_number(players, reaction):
                make_embed.nonsense(embed, emoji)
        elif emoji == '⬇️':
            if not template.minimum_judge():
                make_embed.nonsense(embed, emoji)
        elif emoji == '👍':
            if players != template.sum_position() or not template.appropriate(players, reaction):
                make_embed.nonsense(embed, emoji)
            else:
                pass

    def complete_decide_position(self, reaction, players, template):
        return str(reaction.emoji) == '👍' and template.appropriate(players, reaction) and players == template.sum_position()

    def makePositionList(self, players, positions):
        """人数に合わせて村人を追加します"""
        players_number, positions_number = len(players), len(positions)
        add = players_number - positions_number
        if add < 0:
            return positions
        for _ in range(add):
            #positions[0]はVillagers
            positions.append(positions[0])
        return positions

    def distribute(self, players, positions):
        """役職を配布します"""
        self.makePositionList(players, positions)
        random.shuffle(positions)
        for player, position in zip(players, positions):
            player.getPosition(position)

    def make_wolf_list(self, user_list):
        return list(filter(self.I_am_wolf, user_list))

    def vote(self, user_list):
        """投票処理を行います"""
        max_count = 0
        max_list = []
        for user in user_list:
            if user.vote_count > max_count:
                max_list.clear()
                max_list.append(user)
                max_count = user.vote_count
            elif user.vote_count == max_count:
                max_list.append(user)
        return max_list

    def first_vote_remove(self, num, target_list, user):
        """通常投票時(決選投票でないとき)にuserをtarget_listから除きます"""
        # 通常投票時は num = 0
        if not num:
            target_list.remove(user)

    def first_vote_insert(self, num, target_list, user, index):
        """first_vote_removeで加えた変更を元に戻します"""
        if not num:
            target_list.insert(index, user)

    def make_survivor_list(self, user_list):
        """生存者リストを作成します"""
        return [user for user in user_list if not user.dead]

    def make_corpse_list(self, user_list):
        """死亡者リストを作成します"""
        return [user for user in user_list if user.dead]
    
    def I_am_wolf(self, user):
        return user.position.beWolf

    def make_psychic_list(self, survivor_list):
        """能力者リストを返します"""
        return [survivor for survivor in survivor_list if survivor.position.ability]

    def remove_confrimed(self, target_list, confrimed_list):
        for confrimed in confrimed_list:
            target_list.remove(confrimed)

    def psychic_target(self, psychic, user_list):
        """能力者の夜のターンの対象のリストを作成し埋め込みにする"""
        if psychic.name == '霊媒師':
            target_list = [user for user in user_list if user.dead and user != psychic]
        else:
            target_list = [user for user in user_list if not user.dead and user != psychic]
        embed = make_embed.psychic_target(psychic, target_list)
        return embed, target_list

    def skip_or_kill(self, wolf_list):
        """順番に殺害を行います"""
        while True:
            killer = wolf_list[0]
            wolf_list.pop(0)
            wolf_list.append(killer)
            if not killer.dead:
                break
        return killer

    def will_received(self, target_list, index, psychic):
        """人狼と騎士の対象を保持します"""
        if psychic.position.name == '人狼':
            self.will_be_killed = target_list[index]
        else: # psychic.pposition.name == '騎士'
            self.will_be_protected = target_list[index]
        

    def daybreak(self):
        """人狼と騎士の対象に合わせて殺害処理を行います"""
        title = '夜が明けました・・・'
        if self.will_be_killed == self.will_be_protected:
            description = '誰も襲われませんでした！'
            color = discord.Color.green()
        else:
            self.will_be_killed.killed()
            description = f'**{self.will_be_killed.name}**が襲われてしまいました！'
            color = discord.Color.red()
        embed = discord.Embed(title=title, description=description, color=color)
        return embed

    def finish_judge(self, wolf_list, survivor_list):
        """ゲームを継続するかの判定をします"""
        survive_wolf_list = [wolf for wolf in wolf_list if not wolf.dead]
        number_of_wolf = len(survive_wolf_list)
        number_of_survivor = len(survivor_list)
        # 生存者の過半数を人狼が占める・人狼が0人になる
        if number_of_survivor / 2 <= number_of_wolf or number_of_wolf == 0:
            return True
        return False

    def winner_judge(self, user_list, wolf_list):
        survive_wolf_list = [wolf for wolf in wolf_list if not wolf.dead]
        if len(survive_wolf_list) == 0:
            return [user for user in user_list if not user.position.beWolf], '村人'
        else:
            return wolf_list, '人狼'
        
    def winner(self, winners):
        description = ''
        for winner in winners:
            description += f'・{winner.name}(役職：{winner.position.name})\n'
        return description
