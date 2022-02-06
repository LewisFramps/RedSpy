import discord
import os
from game import Game
from player import Player
import random

# Constant message strings
start = "!and"
help_message = "HELP MENU PAGE 1 (of 1):\n\nCommands\n\n!and help\t := you are here\n!and gather <password>\t := create a game room\n!and join <password>\t := join a game room\n!and start\t := start the game"
already_in_game_message = "You're already in a game! Use \"!and leave\" to leave your current lobby!"
error_message = "Your input is wrong! Try using \"!and help\""
get_details_message = "There's a spy in our midst! We need to confirm your identity before we can crack this case! Enter your title and your name - in two seperate messages!"
code_in_use = "That lobby code is already in use! Try another!"
game_in_progress = "This lobby has already started"
game_does_not_exist = "This lobby doesn't exist!"
left_lobby = "You left your lobby."
not_in_lobby = "You aren't in a lobby."
not_enough_players = "Not enough players, games must have a minimum of 3 players to start"
alphabet = 'abcdefghijklmnopqrstuvwxyz'
games = []
waiting_room = []
in_game = []


def parse_message(message):
    """"
    ### Help Command ###
    !red                   := help
    !red help              := help

    ### Lobby Commands ###
    !red gather `str`      := gather
    !red join `str`        := join
    !red lobby `str`       := print lobby
    !red leave             := leave
    !red start             := start
    !red status            := status

    ### Voting command ###
    !red vote `name`

    -3    := debug
    -2    := !red followed by error
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

    # !red
    if len(s) == 1:
        return 1
    # !red help
    elif s[1] == "help":
        return 1

    elif s[1] == "debug":
        return -3
    # ### Lobby Commands ###

    elif s[1] == "instructions" and len(s) == 2:
        return 0

    # !red gather `str`
    elif s[1] == "gather" and len(s) == 3:
        if s[2] != "":
            return 2
        return -1

    # !red join `str` `str`
    elif s[1] == "join" and len(s) == 3:
        if s[1] != "":
            return 3
        return -1

    # !red lobby `str`
    elif s[1] == "lobby" and len(s) == 3:
        if s[1] != "":
            return 4
        return -1

    # !red leave
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
    # return len(games) > 0


def in_game(player):  # print(waiting_room[0][1], " >:(")

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
    # print("Game exists: ", code, ", ", get_game(code))
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
    for g in games:
        if g.state == 3 and message.guild is not None:
            for p in g.players:
                if auth == p.acc and not p.voted and message.content in alphabet[0:len(g.players)]:
                    print(message.content)
                    g.votes.append(message.content)
                    print(g.votes)
                    p.voted = True
                    if len(g.votes) == len(g.players):
                        g.state = 4
                        await message.channel.send(g.votes)
                        votes = [0] * len(g.players)
                        for i in range(len(g.players)):
                            votes[alphabet.index(g.votes[i])] += 1
                        max_votes = max(votes)
                        if votes.count(max_votes) > 1:
                            g.state = 2
                            await message.channel.send("It's a tie! The has cause too much confusion, they win!")
                            return
                        else:
                            choice = votes.index(max_votes)
                            g.votes = []
                            await message.channel.send(g.players[choice].name + " has been voted off!")
                            if(g.players[choice].role == "i"):
                                await message.channel.send("They were innocent!")
                                del g.players[choice]
                                if len(g.players) == 2:
                                    await message.channel.send("The spy wins!")
                                    g.players = []
                                    g.code = ""
                                    g.host = None
                                    g.state = 0
                                    g.gm = None
                                    return
                                else:
                                    g.state = 2
                                    players = g.players
                                    g.votes = [None] * g.players
                                    random.shuffle(players)
                                    g.gm = players[0]
                                    await g.gm.acc.send(
                                        "You're the game master, to go to the next question enter anything into the server chat!")
                                    g.questionlist = players + [players[0]]
                                    random.shuffle(g.questionlist)
                                    await message.channel.send(
                                        str(g.questionlist[0].name) + " you're first! Ask " + str(
                                            g.questionlist[
                                                1].name) + " a question! If they're a spy, they don't know their title. Try and find that spy!")
                                    g.send_command(2)
                                    return
                            else:
                                await message.channel.send("You caught the AndSpy!")
                                del g
                                return

                        return
            return
        print("We got here")
        print(g.gm)
        if g.gm is not None:
            if auth == g.gm.acc and message.guild is not None:
                print("and got here")
                if len(g.questionlist) == 2:
                    await message.channel.send("Who do you think the spy is? Vote now!\n")
                    g.state = 3
                    s = ""
                    for i in range(len(g.players)):
                        s += alphabet[i] + "\t" + g.players[i].name + "\n"
                    await message.channel.send(s)
                    return
                g.questionlist.pop(0)
                await message.channel.send((str(g.questionlist[0].name) + " you're up! Ask " + str(
                    g.questionlist[
                        1].name) + " a question! If they're a spy, they don't know their title. Try and find that spy!"))
                return

    if message.author == client.user:  # if bot sent message...
        return  # ...don't read

    if game_in_progress():
        case = parse_message(message.content)
        s = message.content.split(" ")
        print(str(case))

        if message.guild is None:
            if waiting_for(auth):
                for i in waiting_room:
                    if i[0][0] == auth:  # if i is waitng & messaged RedSpy
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
                            new_player = Player(auth, message.content, title, code)
                            get_game(code).add_player(new_player)
                            await message.channel.send(str(name) + " has joined lobby: " + str(code))
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

        elif case == 0:
            await message.channel.send("Instructions = “So you want to play AND Spy? Here’s what you need to know!\n\nAND Spy! Is a turn-based Mafia-style game. Once a lobby has been created and players join (for command support try !and help), you will receive a message from the bot asking for an AND TITLE and NAME. Send these in two separate messages. From there, you will be sent a role - innocent or spy - and a list of all the players roles with the exception of the spy who will not know their own role. Questioning will then begin, with every player having the opportunity to ask and answer a question. Once everyone has been asked, they will then have the chance to vote off the player they feel is most suspicious! If the spy manages to make it to the end of the game with only one innocent left, they win. If the innocents vote out the spy, they win! If there's a tie, the spy has caused too much confusion and wins in the chaos! Good luck and have fun!NEW")

        # help case
        elif case == 1:
            await message.channel.send(help_message)
            return

            # create lobby case
        elif case == 2:
            new_player = message.author
            # if player is already in a game, they can't make a new one
            print("in_game:", in_game(new_player))
            print("waiting:", waiting(new_player))
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
                await message.channel.send("Lobby hasn't started yet!")  #
                return
            else:
                await message.channel.send("Lobby doesn't exist!")  #
                return
                # leave case
        elif case == 5:
            new_player = message.author
            # if player is waiting...
            left = False
            code = None
            for i in range(len(waiting_room)):
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
                        await acc.send("You're innocent! Your job is to weed out the spy in your midst! Your title is: " + title + "\n")
                        s = ""
                        for person in starting_game.players:
                            s += str(person.name) + "\t:" + str(person.title) + "\n"
                        await acc.send(s)
                    if pl.role == "s":
                        await acc.send(
                            "You're a spy! You don't know your title, so bluff your way through questions and try not get caught!")
                        s = ""
                        for person in starting_game.players:
                            if person.role == "s":
                                s += str(person.name) + "\t:" + "SPY - Title UNKNOWN\n"
                            else:
                                s += str(person.name) + "\t:" + str(person.title) + "\n"
                        await acc.send(s)
                players = starting_game.players
                random.shuffle(players)
                starting_game.gm = players[0]
                await starting_game.gm.acc.send(
                    "You're the game master, to go to the next question enter anything into the server chat!")
                starting_game.questionlist = players + [players[0]]
                print(starting_game.questionlist)
                await message.channel.send(str(starting_game.questionlist[0].name) + " you're first! Ask " + str(
                    starting_game.questionlist[
                        1].name) + " a question! If they're a spy, they don't know their title. Try and find that spy!")
                starting_game.send_command(2)
                return
            pass
        # await message.channel.send("Howdy")
client.run("OTM5NjgwNDUyMzI1ODM0Nzgy.Yf8Xng.0Bc-Wo2jKHCxcHwsrKzdYxtAnP0")