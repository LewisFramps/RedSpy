import random

class Game:
    host = None
    players = []
    roles = ['I', 'S']
    questionlist = []
    code = ""
    state = 0
    gm = None

    def __init__(self, code):
        self.code = code

    def add_player(self, new):
        if len(self.players) == 0:
            self.host = new
        self.players.append(new)

    def send_command(self, cmd):
        spy_titles = ["Cringe", "Spy", "lmao"]
        if cmd == 1:
            # give out roles
            self.roles = ["i"] * (len(self.players) - 1)
            self.roles += ["s"]
            print(self.roles)
            random.shuffle(self.roles)
            print(self.roles)
            for i in range(len(self.players)):
                new_role = self.roles[i]
                self.players[i].set_role(new_role)
            return



    def get_code(self):
        return self.code

    # Is a players account in this game already?
    def playerInThisGame(self, player):
        for p in self.players:
            if p.acc == player:
                return True
        return False
    
    def removePlayer(self, player):
        for p in self.players:
            if p.acc == player:
                self.players.remove(p)


        return # DO THIS ONCE PLAYERS HAVE BEEN IMPLEMENTED !!!!

    def print(self):
        print("Game:")
        print(self.host)
        print(self.players)
        print(self.roles)
        print(self.code)
        print(self.state)
        print("\n")
    

