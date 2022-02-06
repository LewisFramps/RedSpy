class Player:
    acc = None
    role = None
    name = None
    title = None
    current_game = None
    voted = False

    def __init__(self, acc, name, title, current_game):
        self.acc = acc
        self.name = name
        self.title = title
        self.current_game = current_game
    
    def get_acc(self):
        return self.acc
    
    def get_role(self):
        return self.role
    
    def get_name(self):
        return self.name
    
    def get_title(self):
        return self.title

    def set_role(self, new):
        self.role = new
    
    def set_title(self, new):
        self.title = new

    def isReady(self):
        return self.acc != None and self.name != None and self.title != None and self.current_game != None
    

    