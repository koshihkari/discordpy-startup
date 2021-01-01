import discord


#役職の基となる親クラス
class Position():
    def setName(self, name):
        self.name = name

    def setBeWolf(self, beWolf: bool):
        self.beWolf = beWolf

    def setHaveAbility(self, haveAbility: bool):
        self.ability = haveAbility

    def setExplanation(self, explanation):
        self.explanation = explanation

    def setColor(self, color):
        self.color = color

    def set_ability_title(self, title):
        self.ability_title = title

    def getHaveAbility(self):
        return self.ability


#村人
class Villager(Position):
    def __init__(self):
        super().__init__()
        super().setBeWolf(False)
        super().setName('村人')
        super().setHaveAbility(False)
        super().setExplanation('・人狼の嘘を見抜きましょう')
        super().setColor(discord.Color.green())


#人狼
class Wolf(Position):
    def __init__(self):
        super().__init__()
        super().setBeWolf(True)
        super().setName('人狼')
        super().setHaveAbility(True)
        super().setExplanation("・夜に村人1人を襲撃します\n・複数人狼が存在する場合は順番に襲撃を行います\n注意：役職数設定時、プレイヤー数の過半数以下である必要があります")
        super().set_ability_title('殺害対象')
        super().setColor(discord.Color.red())


#騎士
class Knight(Position):
    def __init__(self):
        super().__init__()
        super().setBeWolf(False)
        super().setName('騎士')
        super().setHaveAbility(True)
        super().setExplanation('・誰か一人を人狼の襲撃から守ります')
        super().set_ability_title('保護する対象')
        super().setColor(discord.Color.green())


#占い師
class Diviner(Position):
    def __init__(self):
        super().__init__()
        super().setBeWolf(False)
        super().setName('占い師')
        super().setHaveAbility(True)
        super().setExplanation('夜に1人の役職を確認することができます')
        super().set_ability_title('占い対象')
        super().setColor(discord.Color.purple())
        self.confirmed = []

#狂人
class Madman(Position):
    def __init__(self):
        super().__init__()
        super().setBeWolf(False)
        super().setName('狂人')
        super().setHaveAbility(False)
        super().setExplanation('人狼チームが勝つと同時に勝利となります')
        super().setColor(discord.Color.red())


#霊媒師
class Medium(Position):
    def __init__(self):
        super().__init__()
        super().setBeWolf(False)
        super().setName('霊媒師')
        super().setHaveAbility(True)
        super().setExplanation('・退場したプレイヤーの役職を確認できます')
        super().set_ability_title('占い対象')
        super().setColor(discord.Color.purple())
        self.confirmed = []


class PositionMaster():
    def make_position_list(self, players):
        if players == 4:
            return [Wolf(), Villager(), Diviner(), Knight()]
        if players == 5:
            return [Wolf(), Villager(), Diviner(), Knight(), Madman()]
        else:
            return [Wolf(), Villager(), Diviner(), Knight(), Madman(), Medium()]


    def str_change_class(self, str_position):
        if str_position == '人狼':
            return Wolf()
        elif str_position == '村人':
            return Villager()
        elif str_position == '占い師':
            return Diviner()
        elif str_position == '狂人':
            return Madman()
        elif str_position == '騎士':
            return Knight()
        elif str_position == '霊媒師':
            return Medium()
    
    def manual_make_positions(self, position_dict):
        positions = []
        for key, value in position_dict.items():
            for _ in range(value):
                positions.append(self.str_change_class(key))
        return positions