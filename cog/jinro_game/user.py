class User():
    def __init__(self, user):
        self.id = user.id
        self.name = user.name
        self.dead = False
        self.vote_count = 0
        self.discord_user = user

    def playerName(self, user):
        return user.name

    def playerId(self, _user):
        return self.id

    def killed(self):
        self.dead = True

    def getPosition(self, position):
        self.position = position

    def givenVote(self):
        self.vote_count += 1

    def vote_count_reset(self):
        self.vote_count = 0