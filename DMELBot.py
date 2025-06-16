import discord
from aiohttp.log import client_logger
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

SPREADSHEET_ID = "1ZbQFYlnaQXHkEx_pggJHVorrhI7CT2ztiwP3eT6AOWE"
RANGE_NAME = "A7:G"
SHEETKEY = ""
DISCORDKEY = ""

previous_ranking = []
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$update'.casefold()):
        print(message.channel.name)
        print(message.content)
        await update_rankings(message)

    if message.content.startswith('$ranking '.casefold()):
        print(message.channel.name)
        print(message.content)
        await find_rank(message)

    if message.content.startswith('$who_is '.casefold()):
        print(message.channel.name)
        print(message.content)
        await who_is(message)

async def who_is(message):
    rank = message.content[8:]
    print(rank)
    players = get_list()
    final = "The player(s) ranked " + rank + " are:\n"
    for player in players:
        if player[0] == rank:
            final += player[2] + "\n"
    await message.channel.send(final)

async def find_rank(message):
    name = message.content[9:]
    print(name)
    players = get_list()
    for player in players:
        if player[2].casefold() == name.casefold():
            await message.channel.send(name + " is currently ranked " + player[0] + " with " + player[3] + " League points")
            return

    print("person not found")
    await message.channel.send("This person could not be found.")



async def update_rankings(message):
    for mes in previous_ranking:
        await mes.delete()
    await message.delete()
    gold = get_first_place()
    silver = get_second_place()
    bronze = get_third_place()
    paint = get_best_painted()
    sport = get_sporting()
    rankings = ""
    players = get_list()
    for player in players:
        if player[6] == "0":
            continue
        rankings += player[0]
        rankings += "    "
        rankings += player[2]
        rankings += "    "
        rankings += player[3]
        rankings += "    "
        rankings += player[6]
        if player[2] in gold:
            rankings += ":first_place:"
        if player[2] in silver:
            rankings += ":second_place:"
        if player[2] in bronze:
            rankings += ":third_place:"
        if player[2] in paint:
            rankings += ":art:"
        if player[2] in sport:
            rankings += ":raised_hands_tone1:"
        rankings += "\n"
        if len(rankings) >= 1900:
            new_mes = await message.channel.send(rankings)
            previous_ranking.append(new_mes)
            rankings = ""
    new_mes = await message.channel.send(rankings)
    previous_ranking.append(new_mes)


def get_list():
    try:
        sheet = service.spreadsheets()
        result = (sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute())
        values = result.get("values", [])
        if not values:
            print("no data found")
            return
        return values
    except HttpError as err:
        print(err)
        exit()

def get_first_place():
    try:
        sheet = service.spreadsheets()
        result = (sheet.values().get(spreadsheetId=SPREADSHEET_ID,range="'2025 Results'!I15:AW15").execute())
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

def get_second_place():
    try:
        sheet = service.spreadsheets()
        result = (sheet.values().get(spreadsheetId=SPREADSHEET_ID,range="'2025 Results'!I16:AW16").execute())
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
    f = open(file, "r")
    SHEETKEY = f.readline().strip()
    DISCORDKEY = f.readline()


if __name__ == "__main__":
    read_keys("API_keys.txt")
    service = build("sheets", "v4", developerKey=SHEETKEY)
    client.run(DISCORDKEY)
