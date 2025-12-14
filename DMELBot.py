from pydoc import describe

import discord
from discord import app_commands
from discord.ext import commands
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

SPREADSHEET_ID = "" #Will be loaded from file
RANGE_NAME = "A7:G" # Range of player list
SHEETKEY = "" #Will be loaded in from text file
DISCORDKEY = "" #Will be loaded in from text file
RESULTSHEET = "'2026 Results'!"

#Set discord intents. Only message_content currently needed.

intents = discord.Intents.default()
intents.message_content = True

#prepare discord client
client = commands.Bot(intents=intents, command_prefix="$")


#Event gets called on startup
@client.event
async def on_ready():
    synched = await client.tree.sync()
    print(len(synched))
    print(f'We have logged in as {client.user}')

@client.tree.command(name = "whois", description="Gives the name of the player on the rank given")
@app_commands.describe(rank = "rank to look up")
@app_commands.guild_only
async def who_is(interaction : discord.Interaction, rank: int):
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
    await interaction.response.send_message(final)

@client.tree.command(name = "findrank", description="Gives the rank of the player given")
@app_commands.describe(name = "player to look up")
@app_commands.guild_only
async def find_rank(interaction: discord.Interaction, name : str):

    # get all players
    players = get_list()

    #look through players for requested name

    for player in players:
        if player[2].casefold() == name.casefold():
            #when name is found, send message.
            await interaction.response.send_message(name + " is currently ranked " + player[0] + " with " + player[3] + " League points")
            return

    #if name not in sheet log and respond that person wasn't found
    print("person not found")
    await interaction.response.send_message("This person could not be found.")


#function when $update is sent
@client.tree.command(description="Update ranking display", name="update")
@app_commands.guild_only
@app_commands.default_permissions(discord.Permissions(administrator = True))
async def update(interaction: discord.Interaction):
    #get channel where ranking was requested
    channel = interaction.channel
    #Messages stored in txt file with channel id as name
    filename = str(channel.id) + ".txt"

    #Try to open file with previous messages, and remove messages if present
    try:
        f = open(filename, "r")
        i = int(f.readline().strip())
        for j in range(i):
            mes_id = f.readline().strip()
            temp = await channel.fetch_message(int(mes_id))
            await temp.delete()

        f.close()
    except IOError:
        print("no such file yet")

    medals = get_medals()
    #get all players that won best painted
    paint = get_best_painted()
    #get all players that won most sporting
    sport = get_sporting()

    #message to contain message to be sent
    rankings = ""
    #list to get around character limits
    messages = []

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

        for winner in medals[0]:
            if player[2] == winner:
                rankings += ":first_place:"

        for winner in medals[1]:
            if player[2] == winner:
                rankings += ":second_place:"

        for winner in medals[2]:
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

        #avoid character limit
        if len(rankings) >= 1900:

            #set built message into list
            messages.append(rankings)

            #reset working string for refilling
            rankings = ""


    #await interaction.message.delete()

    #send rankings and save ids to file for deletion
    g = open(filename, "w")
    g.write(str(len(messages)))
    g.write("\n")

    for i in messages:
        g.write(str((await interaction.channel.send(i)).id))
        g.write("\n")
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


def get_best_painted():
    try:
        sheet = service.spreadsheets()
        result = (sheet.values().get(spreadsheetId=SPREADSHEET_ID,range=RESULTSHEET + "I10:AW10").execute())
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
        result = (sheet.values().get(spreadsheetId=SPREADSHEET_ID,range=RESULTSHEET + "I11:AW11").execute())
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

def get_medals():
    medals = [[],[],[]]

    sheet = service.spreadsheets()
    result = (sheet.values().get(spreadsheetId=SPREADSHEET_ID,range=RESULTSHEET + "H15:AW21").execute())
    values = result.get("values", [])
    print (values)
    rank = 0
    for _ in values:
        i=0
        for value in _:
            match i:
                case 0:
                    rank = int(value)
                    i+=1
                    continue
                case 1:
                    match rank:
                        case 1:
                            medals[0].append(value)
                        case 2:
                            medals[1].append(value)
                        case 3:
                            medals[2].append(value)
                    rank = 0
                    i+=1
                    continue
                case 2:
                    i+=1
                    continue
                case 3:
                    i = 0
                    continue
    return medals



def read_keys(file):
    global SHEETKEY
    global DISCORDKEY
    global SPREADSHEET_ID

    #open keyfile
    f = open(file, "r")

    #set keys, as read from file
    SHEETKEY = f.readline().strip()
    DISCORDKEY = f.readline().strip()
    SPREADSHEET_ID = f.readline().strip()


    #close file like a good boy
    f.close()

if __name__ == "__main__":
    #load in api keys
    read_keys("API_keys.txt")

    #prepare google sheet api
    service = build("sheets", "v4", developerKey=SHEETKEY)

    #log in as discord client
    client.run(DISCORDKEY)