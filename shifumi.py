import serial
import os
import enum
import argparse
import socket
from time import sleep
from enum import Enum


class State(Enum):
    READY_PY_CLIENT = "1"
    READY_SERVER = "2"
    READY_READY = "3"
    RUNNING = "4"
    WAIT_CLIENT_ACK = "5"
    END = "6"


class Choice(Enum):
    PAPER = 0
    CISSORS = 1
    ROCK = 2
    EMPTY = 3


def waitDigit():
    return ord(ser.read(1))


def sendState(state: State):
    ser.write((state.value).encode())


def sendInt(i: int):
    ser.write(chr(i).encode())

# La règle du shifumi à plusieurs est simple : 
# En cas d'égalité, ce sont les signes les moins fréquents qui perdent.
# Par conséquent on ne dit pas quels sont les joueurs gagnants et perdants, on dit quels signes perdent.
def chooseWinner(playerChoices):
    anyCissors = False
    anyPaper = False
    anyRock = False
    nbRock = 0
    nbPaper = 0
    nbCissors = 0

    for i in range(nb_player):
        if playerChoices[i] == Choice.ROCK.value:
            anyRock = True
            nbRock += 1

        if playerChoices[i] == Choice.PAPER.value:
            anyPaper = True
            nbPaper += 1

        if playerChoices[i] == Choice.CISSORS.value:
            anyCissors = True
            nbCissors += 1

    if anyRock == True and anyPaper == True and anyCissors == True:
        if nbCissors > nbPaper and nbCissors > nbRock:
            playerChoices = setToLose(Choice.EMPTY.value, playerChoices)
            playerChoices = setToLose(Choice.PAPER.value, playerChoices)
            playerChoices = setToLose(Choice.ROCK.value, playerChoices)
            return playerChoices

        if nbPaper > nbCissors and nbPaper > nbCissors:
            playerChoices = setToLose(Choice.CISSORS.value, playerChoices)
            playerChoices = setToLose(Choice.EMPTY.value, playerChoices)
            playerChoices = setToLose(Choice.ROCK.value, playerChoices)
            return playerChoices

        if nbRock > nbPaper and nbRock > nbCissors:
            playerChoices = setToLose(Choice.EMPTY.value, playerChoices)
            playerChoices = setToLose(Choice.PAPER.value, playerChoices)
            playerChoices = setToLose(Choice.CISSORS.value, playerChoices)

            return playerChoices
        else :
            return playerChoices

    if anyRock == True and anyPaper == False:
        playerChoices = setToLose(Choice.CISSORS.value, playerChoices)
        playerChoices = setToLose(Choice.EMPTY.value, playerChoices)
        return playerChoices

    if anyCissors == True and anyRock == False:
        playerChoices = setToLose(Choice.PAPER.value, playerChoices)
        playerChoices = setToLose(Choice.EMPTY.value, playerChoices)
        return playerChoices

    if anyPaper == True and anyCissors == False:
        playerChoices = setToLose(Choice.ROCK.value, playerChoices)
        playerChoices = setToLose(Choice.EMPTY.value, playerChoices)
        return playerChoices

# Définit un signe comme perdant
def setToLose(weapon, playerChoices):
    for i in range(nb_player):
        if playerChoices[i] == weapon:
            playerChoices[i] = "LOOSE"
    return playerChoices

# Retourne la liste des id gagnants d'une manche
def getWinnerRound(playerChoices):
    winners=[]
    playerChoices = chooseWinner(playerChoices)
    print("Liste des choix après correction : ", playerChoices)
    for i in range(nb_player):
        if playerChoices[i] != "LOOSE":
            winners.append(i)
    return winners



parser = argparse.ArgumentParser()
parser.add_argument("-s", "--server", action="store_true",
                    help="this machine is server socket with '-s'")
parser.add_argument("host", type=str,
                    help="IP of server")
parser.add_argument("port", type=int,
                    help="port used to communicate")
parser.add_argument("serial", type=str, help="serial port of the arduino")
parser.add_argument("player", type=int,
                    help="Number of players")
parser.add_argument("round", type=int,
                    help="Number of rounds")

args = parser.parse_args()


ser = serial.Serial(args.serial, timeout=None, baudrate=9600, rtscts=True, dsrdtr=True)

hote = args.host
port = args.port

nb_player = args.player
players_array = []


if waitDigit() == 0:
    print("INIT")

# Make a socket for this machine
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

player_id = 0

print("Debut du programme\n")

#Coté Server
try:
    if args.server:
        s.bind((hote, port))
        s.listen(nb_player)
        print("En attente de joueurs")
        # On récupère les autres joueurs par socket
        players_array.append([0, 0])  # joueur serveur
        for i in range(1, nb_player):
            clientSocket, address = s.accept()
            print("new player connected")
            #On définit l'id de chaque joueur et on leur envoie
            clientSocket.send(i.to_bytes(1, "little"))
            #On leur envoie aussi le nombre de joueurs
            clientSocket.send(nb_player.to_bytes(1, "little"))
            players_array.append([clientSocket, address])

        sendState(State.READY_PY_CLIENT)
        sendState(State.READY_SERVER)

        # On envoie à l'arduino le nombre de joueur et notre id
        sendInt(nb_player)
        sendInt(0)

        # check host ACK
        ack = chr(waitDigit())
        print(f"ack: {ack}")
        if ack != State.WAIT_CLIENT_ACK.value:
            print("HOST broken !!!")
            ser.close()
            exit()
        # wait ack all clients
        for i in range(1, nb_player):
            clientAck = players_array[i][0].recv(1)

        sendState(State.READY_READY)

        finalScore = [0] * nb_player

        #Début d'une manche
        for i in range(args.round):
            print()
            # On va stocker les choix de tout les joueurs dans un tableau
            playerChoices = [Choice.EMPTY.value] * nb_player

            #On envoie le lancement de la manche à chaque joueur
            for j in range(1, nb_player):
                players_array[j][0].send(State.RUNNING.value.encode())

            sendState(State.RUNNING)

            playerChoices[0] = waitDigit()
            print(f"host choice: {playerChoices[0]}")

            for j in range(1, nb_player):
                playerChoices[j] = int.from_bytes(players_array[j][0].recv(1),"little")

            print("Liste des choix: ",playerChoices)
            # apply rules and find round winner
            winner_id = getWinnerRound(playerChoices)

            print("Liste des gagnants : ",winner_id)

            # Envoi le gagnant a tout les joueurs
            sendInt(winner_id[0]) 
            for j in range(1, nb_player):
                players_array[j][0].send(winner_id[0].to_bytes(1, "little"))
            sleep(1.5)
            

            # update scores
            for i in range(nb_player):
                if i in winner_id:
                    finalScore[i] += 1

        sendState(State.END)
        #On envoie la fin de la partie aux joueurs
        for j in range(1, nb_player):
            players_array[j][0].send((State.END.value).encode())

        # Envoi du gagnant de la partie aux joueurs
        final_winner = finalScore.index(max(finalScore))
        sendInt(final_winner)  
        for j in range(1, nb_player):
            players_array[j][0].send(final_winner.to_bytes(1, "little"))

        print("Fin du game\n")
        ser.close()
        exit()



    # Make it a client socket
    else:
        sendState(State.READY_PY_CLIENT)
        s.connect((hote, port))  # Connexion server
        sendState(State.READY_SERVER)

        player_id = int.from_bytes(s.recv(1), 'little')
        nb_player = int.from_bytes(s.recv(1), 'little')

        sendInt(nb_player)
        sendInt(player_id)

        # check host ACK
        ack = chr(waitDigit())
        print(f"ack: {ack}")
        if ack != State.WAIT_CLIENT_ACK.value:
            print("HOST broken !!!")
            ser.close()
            exit()

        s.send((5).to_bytes(1, "little"))

        sendState(State.READY_READY)

        #Debut d'une manche
        while (s.recv(1).decode() == State.RUNNING.value):
            sendState(State.RUNNING)
            print("isEnd")
            #Recuperation du choix et envoi au serveur
            choice = waitDigit()
            s.send(choice.to_bytes(1, "little"))

            #Recuperation des resultats de la manche
            winner_id = int.from_bytes(s.recv(1), 'little')
            print("winner is")
            print(winner_id)
            sendInt(winner_id)
            sleep(1.5)


        sendState(State.END)
        #Fin de la partie et affichage du gagnant
        final_winner = int.from_bytes(s.recv(1), 'little')
        sendInt(final_winner)

        print("Fin du game\n")

        ser.close()
        exit()
except Exception:
    ser.close()
    exit()