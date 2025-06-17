import discord
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

SPREADSHEET_ID = "1ZbQFYlnaQXHkEx_pggJHVorrhI7CT2ztiwP3eT6AOWE" #2025 master sheet ID
RANGE_NAME = "A7:G" # Range of player list
SHEETKEY = "" #Will be loaded in from text file
DISCORDKEY = "" #Will be loaded in from text file


#Set discord intents. Only message_content currently needed.
intents = discord.Intents.default()
intents.message_content = True

#prepare discord client
client = discord.Client(intents=intents)


#Event gets called on startup
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

#Event gets called when a message is recieved
@client.event
async def on_message(message):

    #if message was sent by bot, ignore it.
    if message.author == client.user:
        return

    #permission control, if message sender has TO or Admin role allow restricted commands
    permissions = False
    for role in message.author.roles:
        if role.name == "Tournament Organiser" or role.name == "Admin":
            permissions = True
            break

    #command $update, restricted
    if message.content.startswith('$update'.casefold()) & permissions:
        await update_rankings(message)

    #command $ranking, unrestricted
    if message.content.startswith('$ranking '.casefold()):
        await find_rank(message)


    #command $who_is, unrestricted
    if message.content.startswith('$who_is '.casefold()):
        await who_is(message)


#Function called when $who_is is sent
async def who_is(message):
    #message beyond command
    rank = message.content[8:]

    #get all players
    players = get_list()

    #setup response message
    final = "The player(s) ranked " + rank + " are:\n"

    #look for message argument in player list
    for player in players:
        if player[0] == rank:
            #Add all players at requested rank to message on separate lines
            final += player[2] + "\n"

    #send final message
    await message.channel.send(final)

#Function called when $ranking is sent
async def find_rank(message):
    # message beyond command
    name = message.content[9:]

    # get all players
    players = get_list()

    #look through players for requested name
    for player in players:
        if player[2].casefold() == name.casefold():
            #when name is found, send message.
            await message.channel.send(name + " is currently ranked " + player[0] + " with " + player[3] + " League points")
            return

    #if name not in sheet log and respond that person wasn't found
    print("person not found")
    await message.channel.send("This person could not be found.")


#function when $update is sent
async def update_rankings(message):
    #get channel where ranking was requested
    channel = message.channel
    #Messages stored in txt file with channel id as name
    filename = str(channel.id) + ".txt"

    #Try to open file with previous messages, and remove messages if present
    try:
        f = open(filename, "r")
        i = int(f.readline().strip())
        for _ in range(i):
            mes_id = f.readline().strip()
            temp = await channel.fetch_message(int(mes_id))
            await temp.delete()
        f.close()
    except IOError:
        print("no such file yet")

    #to keep track of the messages sent in this update
    sent_messages = []

    #remove $update command
    await message.delete()

    #get all players that won first place
    gold = get_first_place()
    #get all players that won second place
    silver = get_second_place()
    #get all players that won third place
    bronze = get_third_place()
    #get all players that won best painted
    paint = get_best_painted()
    #get all players that won most sporting
    sport = get_sporting()

    #message to contain message to be sent
    rankings = ""

    #get list of players
    players = get_list()

    #loop through each player to create their line in rankings message
    for player in players:

        #if player hasn't played any tournaments skip
        if player[6] == "0":
            continue
        #add rank to the line
        rankings += player[0]
        rankings += "    "

        #add player name to line
        rankings += player[2]
        rankings += "    "

        #add league points to line
        rankings += player[3]
        rankings += "    "

        #add total tournaments to line
        rankings += player[6]

        #add gold medals for tournament winners
        for winner in gold:
            if winner == player[2]:
                rankings += ":first_place:"

        #add silver medals for second places in tournaments
        for winner in silver:
            if player[2] == winner:
                rankings += ":second_place:"

        #add bronze medals for third places in tournaments
        for winner in bronze:
            if player[2] == winner:
                rankings += ":third_place:"

        #add painting awards
        for winner in paint:
            if player[2] == winner:
                rankings += ":art:"

        # add sporting awards
        for winner in sport:
            if player[2] == winner:
                rankings += ":raised_hands_tone1:"

        #newline before next player
        rankings += "\n"

        #if near message character send message
        if len(rankings) >= 1900:
            new_mes = await message.channel.send(rankings)

            #save sent message for writing to file
            sent_messages.append(new_mes)

            #reset message content for next message to be sent
            rankings = ""

    #send rankings
    new_mes = await message.channel.send(rankings)

    #save sent message for writing to file
    sent_messages.append(new_mes)

    #write message ids to file
    g = open(filename, "w")
    g.write(str(len(sent_messages)) + "\n")
    for mes in sent_messages:
        g.write(str(mes.id) + "\n")
    g.close()


#function to get all players
def get_list():
    try:
        #request range with players from spreadsheet
        sheet = service.spreadsheets()
        result = (sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute())

        #transfer result to usable values
        values = result.get("values", [])

        #make sure data is delivered
        if not values:
            print("no data found")
            return
        return values
    except HttpError as err:
        print(err)
        exit()


#get all players who came first in a tournament
def get_first_place():
    try:
        #request range from spreadsheet. Requests first row of the results for each tournament
        sheet = service.spreadsheets()
        result = (sheet.values().get(spreadsheetId=SPREADSHEET_ID,range="'2025 Results'!I15:AW15").execute())

        #transfer result to usable values
        values = result.get("values", [])

        #every 4th is actually a first placed player, remove unneeded values
        row = values[0]
        names = []
        temp = 3
        for cell in row:
            if temp == 3:
                names.append(cell)
                temp = 0
                continue
            temp += 1

        #return trimmed first place
        return names

    except HttpError as err:
        print(err)
        exit()

def get_second_place():
    try:
        #request range from spreadsheet. Requests second row of the results for each tournament
        sheet = service.spreadsheets()
        result = (sheet.values().get(spreadsheetId=SPREADSHEET_ID,range="'2025 Results'!I16:AW16").execute())

        #transfer result to usable values
        values = result.get("values", [])

        #every 4th is actually a first placed player, remove unneeded values
        row = values[0]
        names = []
        temp = 3
        for cell in row:
            if temp == 3:
                names.append(cell)
                temp = 0
                continue
            temp += 1

        # return trimmed second place
        return names

    except HttpError as err:
        print(err)
        exit()

def get_third_place():
    try:
        sheet = service.spreadsheets()
        result = (sheet.values().get(spreadsheetId=SPREADSHEET_ID,range="'2025 Results'!I17:AW17").execute())
        values = result.get("values", [])
        row = values[0]
        names = []
        temp = 3
        for cell in row:
            if temp == 3:
                names.append(cell)
                temp = 0
                continue
            temp += 1

        return names

    except HttpError as err:
        print(err)
        exit()

def get_best_painted():
    try:
        sheet = service.spreadsheets()
        result = (sheet.values().get(spreadsheetId=SPREADSHEET_ID,range="'2025 Results'!I10:AW10").execute())
        values = result.get("values", [])
        row = values[0]
        names = []
        temp = 3
        for cell in row:
            if temp == 3:
                names.append(cell)
                temp = 0
                continue
            temp += 1

        return names

    except HttpError as err:
        print(err)
        exit()

def get_sporting():
    try:
        sheet = service.spreadsheets()
        result = (sheet.values().get(spreadsheetId=SPREADSHEET_ID,range="'2025 Results'!I11:AW11").execute())
        values = result.get("values", [])
        row = values[0]
        names = []
        temp = 3
        for cell in row:
            if temp == 3:
                names.append(cell)
                temp = 0
                continue
            temp += 1

        return names

    except HttpError as err:
        print(err)
        exit()

def read_keys(file):
    global SHEETKEY
    global DISCORDKEY

    #open keyfile
    f = open(file, "r")

    #set keys, as read from file
    SHEETKEY = f.readline().strip()
    DISCORDKEY = f.readline()

    #close file like a good boy
    f.close()


if __name__ == "__main__":
    #load in api keys
    read_keys("API_keys.txt")

    #prepare google sheet api
    service = build("sheets", "v4", developerKey=SHEETKEY)

    #log in as discord client
    client.run(DISCORDKEY)