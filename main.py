import discord
import os
from game import Game
from player import Player
import random

# Constant message strings
start = "!and"
help_message = "ratio + cringe + take the l + you needed the help message lol"
already_in_game_message = "You're already in a game! Use \"!and leave\" to leave your current lobby!"
error_message = "Your input is wrong! Try using \"!and help\""
<<<<<<< Updated upstream
get_details_message = "There's a spy our midst! We need to confirm your identity before we can crack this case! Enter your title and your name - in two seperate messages!"
=======
get_details_message = "There's a spy our midst! We need to confirm your identity before we can crack this case! Enter your real name and then enter your code name!"
>>>>>>> Stashed changes
code_in_use = "That lobby code is already in use! Try another!"
game_in_progress = "This lobby has already started"
game_does_not_exist = "This lobby doesn't exist!"
left_lobby = "You left your lobby."
not_in_lobby = "You aren't in a lobby."
not_enough_players = "Not enough players, games must have a minimum of 3 players to start"


games = []
waiting_room = []
in_game = []

def parse_message(message):
    """"
    ### Help Command ###
    !and                   := help
    !and help              := help

    ### Lobby Commands ###
    !and gather `str`      := gather 
    !and join `str`        := join
    !and lobby `str`       := print lobby
    !and leave             := leave
    !and start             := start
    !and status            := status
    
    ### Voting command ###
    !and vote `name`

    -3    := debug
    -2    := !and followed by error
    -1    := Not valid input
    1     := Help
    2     := gather
    3     := join
    4     := print Lobby
    5     := leave
    6     := start
    """

    s = (message.lower()).split(" ")

    # Invalid
    if s[0] != start:
        return -1

    # ### Help Commands ###

    # !and
    if len(s) == 1:
        return 1
    # !and help
    elif s[1] == "help":
        return 1

    elif s[1] == "debug":
        return -3
    # ### Lobby Commands ###

    # !and gather `str`
    elif s[1] == "gather" and len(s) == 3:
        if s[2] != "":
            return 2
        return -1

    # !and join `str` `str`
    elif s[1] == "join" and len(s) == 3:
        if s[1] != "":
            return 3
        return -1

    # !and lobby `str`
    elif s[1] == "lobby" and len(s) == 3:
        if s[1] != "":
            return 4
        return -1

    #!and leave
    elif s[1] == "leave" and len(s) == 2:
        return 5
    elif s[1] == "start" and len(s) == 2:
        return 6
    
    return -2


# DISCORD JUNK

client = discord.Client()


@client.event
async def on_read():
    print("We have logged in as {0.user}".format(client))


def game_in_progress():
    return True
    #return len(games) > 0

def in_game(player):            #print(waiting_room[0][1], " >:(")

    for game in games:
        if game.playerInThisGame(player):
            return True
    else:
        return False

# get game identified by given code
def get_game(code):
    for g in games:
        if g.code == code:
            return g
    return None

def game_exists(code):
    #print("Game exists: ", code, ", ", get_game(code))
    return get_game(code) != None


def game_pending(code):
    for g in waiting_room:
        if g[1] == code:
            return True
    return False

def waiting(p):
    for i in waiting_room:
        if i[0][0] == p:
            return True
    return False

def waiting_for(p):
    for i in waiting_room:
        if i[0][0] == p:
            return i[1]
    return None


@client.event
async def on_message(message):
    auth = message.author
    if message.author == client.user:  # if bot sent message...
        return  # ...don't read
    
    if game_in_progress():
        case = parse_message(message.content)
        s = message.content.split(" ")
        print(str(case))
        
        if message.guild is None:
            if waiting_for(auth):
                for i in waiting_room:
                    if i[0][0] == auth:        # if i is waitng & messaged andSpy
                        print(":)")
                        if i[0][1] == None:
                            waiting_room.remove(i)
                            waiting_room.append(((i[0][0], message.content, None), i[1]))
                            return
                        else:
                            waiting_room.remove(i)
                            i = ((i[0][0], i[0][1], message.content), i[1])
                            name = i[0][0]
                            title = i[0][1]
                            code = i[1]
                            new_player = Player(auth, name, title, code)
                            get_game(code).add_player(new_player)
                            return
            return

        if case == -3:
            print("<Debugging>")
            print(games)
            print("\n")
            print(waiting_room)
            print("</Debugging>")
        # mistake case
        if case == -2:
            await message.channel.send(error_message)
            return 

        # error case
        elif case == -1:
            return

        # help case
        elif case == 1:
            await message.channel.send(help_message)
            return 
        
        # create lobby case
        elif case == 2:
            new_player = message.author
            # if player is already in a game, they can't make a new one
            if in_game(new_player) or waiting(new_player):
                await message.channel.send(already_in_game_message)
                return 
            
            code = s[2]

            if game_exists(code) or game_pending(code):
                await message.channel.send(code_in_use)
                return
            
            else:
                waiting_room.append(((new_player, None, None), code))
                new_game = Game(code)
                games.append(new_game)
                await message.author.send(get_details_message)
                await message.channel.send("Lobby created with passcode: " + code)
                return


        # join lobby case 
        elif case == 3: 
            new_player = message.author
            # Players can't be in more than one game at a time
            if in_game(new_player) or waiting(new_player):
                await message.channel.send(already_in_game_message)
                return
            code = s[2]

            if game_exists(code):
                g = get_game(code)
                if g.state != 0:
                    await message.channel.send(game_in_progress)
                    return
                else:
                    print("ruh roh")
                    waiting_room.append(((new_player, None, None), code))
                    await message.author.send(get_details_message)
                    return
            if game_pending(code):
                waiting_room.append(((new_player, None, None), code))
                await message.author.send(get_details_message)
                return
            else:
                await message.channel.send(game_does_not_exist)
                return

        # print lobby case 
        elif case == 4:
            code = s[2]
            if game_exists(code):
                await message.channel.send(game_in_progress)
                return
            elif game_pending(code):
                await message.channel.send("Lobby hasn't started yet!")#
                return
            else:
                await message.channel.send("Lobby doesn't exist!")#
                return                 
        
        # leave case
        elif case == 5:
            new_player = message.author
            # if player is waiting...
            left = False
            code = None
            for i in range(len(waiting_room)):
                print(waiting_room)
                print(waiting_room[i])
                print(waiting_room[i][0])
                print(waiting_room[i][0][0])
                if waiting_room[i][0][0] == new_player:
                    code = waiting_room[i][1]
                    print("Found IT")
                    del waiting_room[i]
                    left = True
            # if player is in game...
            for i in range(len(games)):
                if games[i].code == code:
                    del games[i]
                    await message.channel.send("Lobby shut down as player left!")
                    left = True
            if left:
                return
            # if player isn't in lobby
            else:
                await message.channel.send(not_in_lobby)
                return 

        # Start case
        # WRONG NOW VERY WRONG FUCK SAKE
        elif case == 6:
            p = message.author
            starting_game = None
            for g in games:
                if g.playerInThisGame(p):
                    starting_game = g
            if starting_game == None:
                await message.channel.send("Respond to the private message to enter your details!")
                return
            elif starting_game.host.acc != p:
                print(starting_game.host.name)
                await message.channel.send("You aren't the host of this game!")
                return
            elif len(starting_game.players) < 3:
                await message.channel.send(not_enough_players)
                return
            else:
                await message.channel.send("Starting game!")
                starting_game.send_command(1)
                for pl in starting_game.players:
                    role = pl.role
                    title = pl.title
                    acc = pl.acc
                    if pl.role == "i":
                        await acc.send("You're innocent! Find that spy! Your title is: " + title)
                    if pl.role == "s":
                        await acc.send("You're a spy! Keep hidden! Your disguise is: " + "TRAITOR TEST MESSAGE")
                players = starting_game.players
                random.shuffle(players)
                starting_game.gm = players[0]
                await starting_game.gm.acc.send("You're the game master, to go to the next question enter anything into the chat!")
                starting_game.questionlist = players + [players[0]]
                await message.channel.send((str(starting_game.questionlist[0].name) + " you're first! Ask " + str(starting_game.questionlist[1].name) + " a question! If they're a spy, they don't know their title. Try and find that spy!"))
                return

            pass


            


            
        #await message.channel.send("Howdy")



client.run("OTM5NjgwNDUyMzI1ODM0Nzgy.Yf8Xng.fNs0LxnX2XBJq7DrcKQWhNt2aCA")
