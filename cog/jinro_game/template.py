from embed_maker import EmbedNotification
from position import Wolf, Villager, Diviner, Madman, Knight, Medium

import discord


make_embed = EmbedNotification()


class Template():
    def __init__(self):
        self.position_list = [Wolf(), Villager(), Diviner(), Madman(), Knight(), Medium()]
        self.ideal_position = ['1~3', '0~8', '0~1', '0~1', '0~1', '0~1']
        self.position_dict = {'人狼': 1, '村人': 0, '占い師': 0, '狂人': 0, '騎士': 0, '霊媒師': 0}
        self.judge_func_list = [self.wolf, self.villager, self.diviner, self.madman, self.knight, self.medium]
        self.index = 0

    def reaction_range(self, reaction, num):
        if str(reaction.emoji) != '👍':
            num -= 1


    def wolf(self, number_of_wolf, number_of_all, reaction):
        max = 3
        self.reaction_range(reaction, max)
        return 0 < number_of_wolf <= max and number_of_wolf < number_of_all / 2

    def diviner(self, number_of_diviner, _number_of_all, reaction):
        max = 1
        self.reaction_range(reaction, max)
        return 0 <= number_of_diviner <= max

    def madman(self, number_of_madman, _number_of_all, reaction):
        max = 1
        self.reaction_range(reaction, max)
        return number_of_madman <= max

    def medium(self, number_of_medium, _number_of_all, reaction):
        max = 1
        self.reaction_range(reaction, max)
        return number_of_medium <= max

    def knight(self, number_of_knight, _number_of_all, reaction):
        max = 1
        self.reaction_range(reaction, max)
        return number_of_knight <= max

    def villager(self, number_of_villager, _number_of_all, reaction):
        max = 8
        self.reaction_range(reaction, max)
        return number_of_villager <= max
    
    def next_page(self):
        self.index += 1

    def back_page(self):
        self.index -= 1

    def sum_position(self):
        sum_list = self.position_dict.values()
        sum = 0
        for num in sum_list:
            sum += num
        return sum

    def appropriate(self, players, reaction):
        wolf = self.wolf(self.position_dict['人狼'], players, reaction)
        villager = self.villager(self.position_dict['村人'], players, reaction)
        diviner = self.diviner(self.position_dict['占い師'], players, reaction)
        madman = self.madman(self.position_dict['狂人'], players, reaction)
        medium = self.medium(self.position_dict['霊媒師'], players, reaction)
        knight = self.knight(self.position_dict['騎士'], players, reaction)
        return wolf and villager and diviner and madman and medium and knight

    def judge_number(self, players, reaction):
        position = self.position_list[self.index]
        func = self.judge_func_list[self.index]
        return func(self.position_dict[position.name], players, reaction)

    def minimum_judge(self):
        minimum = 0
        if self.position_list[self.index].beWolf:
            minimum += 1
        position_name = self.position_list[self.index].name
        if self.position_dict[position_name] == minimum:
            return False
        return True

    def make_position_list(self):
        return