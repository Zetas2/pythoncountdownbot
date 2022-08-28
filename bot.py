# Used for rounding down timestamps to whole numbers and to get the max pages needed.
from math import floor, ceil

# Used for... getting time.
import time

# Main library that makes all the bot stuff
import interactions

# Extension of interactions that handles tasks - i.e a thing that repeats at a given interval and does stuff.
from interactions.ext.tasks import IntervalTrigger, create_task

# Handeling the database
import sqlite3

# handles shards Not active due to not needing shards.. yet
# from interactions.ext.autosharder import shard

# To get information about system usage (ram and cpu)
import psutil

# parses the human date to a date that computer understands
import dateparser

# These two are used to have the token as a .env file.
from os import getenv
from dotenv import load_dotenv

load_dotenv()
TOKENSTRING = getenv("DISCORD_TOKEN")

# makes conn into the connected database.
conn = sqlite3.connect("Countdowns.db")

# Make the table if there is noe
conn.execute(
    """CREATE TABLE IF NOT EXISTS Countdowns (timestamp int,msgid int,channelid int,guildid int,roleid int,startedby int,times int,length int,messagestart varchar(255),messageend varchar(255));"""
)


bot = interactions.Client(token=TOKENSTRING, disable_sync=False)

# This will be the place to add in all translations if they are ever added. Supported languages are: ('lt', 'el', 'es-ES', 'ar', 'pt-BR', 'en-US', 'zh-CN', 'uk', 'no', 'it', 'bg', 'hr', 'sv-SE', 'hi', 'ja', 'he', 'fr', 'ro', 'en-GB', 'vi', 'nl', 'fi', 'de', 'ko', 'da', 'ru', 'zh-TW', 'hu', 'cs', 'pl', 'tr', 'th')
translations = {
    "en-US": {
        "helpTitle": "Help",
        "helpDesc": "This bot got the following commands:",
        "helpCountdownTitle": "Countdown",
        "helpCountdownDesc": "Countdown will show the remaining time until the date you entered, or for the duration you specify. Its timezone is UTC. They can be repeated by using the times option.",
        "helpListTitle": "List",
        "helpListDesc": "It will show you all active countdowns in the channel/guild or from you depending on subcommand.",
        "helpDeleteTitle": "Delete",
        "helpDeleteDesc": "To use this you need to mave the `MANAGE_MESSAGE` permission.\n*Single*\nEnter the message id for the countdown you want to delete and it will stop. You can find message id as the last number when using /list.\n*Channel*\nDeletes all countdowns in this channel.\n*Server*\nDeletes all countdowns in this guild.",
        "helpHelpDesc": "Shows this help message",
        "helpLinksTitle": "Links",
        "helpLinksDesc": "[Discord Support](https://discord.com/invite/b2fY4z4xBY 'Join the support guild!') | [Invite the Bot](https://top.gg/bot/710486805836988507) | [Patreon](https://www.patreon.com/livecountdownbot)",
        "helpTranslateTitle": "Translate",
        "helpTranslateDesc": "Allows you as an administrator to switch the language of the bot",
        "done": "A countdown is done!",
        "created": "It was started by",
    },
}

# The function that adds in the countdowns in the database
def addtodatabase(
    timestamp,
    msg,
    guildid,
    mention,
    startedby,
    times,
    length,
    messagestart,
    messageend="!",
):
    # Had problems with these numbers being "None" for some unknown reason, so added a check so they cant come into the database
    if msg.id == None or msg.channel_id == None or guildid == None:
        return True

    # To not escape the string the ' is replaced with ’
    messagestart = messagestart.replace("'", "’")
    messageend = messageend.replace("'", "’")
    conn.execute(
        f"INSERT INTO Countdowns (timestamp,msgid,channelid,guildid,roleid,startedby,times,length,messagestart,messageend) VALUES ({timestamp},{msg.id},{msg.channel_id},{guildid},{mention},{startedby},{times},{length},'{messagestart}','{messageend}');"
    )
    conn.commit()
    return False


# This is used to not go over the limit on how many active countdowns there can be in a guild/channel
def checkactive(guildid, channelid):
    cursor = conn.execute(f"SELECT COUNT(*) FROM Countdowns WHERE guildid= {guildid};")
    for row in cursor:
        guild = int(row[0])
    cursor = conn.execute(
        f"SELECT COUNT(*) FROM Countdowns WHERE channelid={channelid};"
    )
    for row in cursor:
        channel = int(row[0])
    if guild > 50:  # Limits number of active countdowns to 51
        return True
    elif channel > 20:  # limits number of active countdowns to 21
        return True
    else:
        return False


# Check this when activating shards
# This sets the bots presence to "Listening to /help"
@bot.event
async def on_start():
    await bot.change_presence(
        presence=interactions.ClientPresence(
            activities=[
                interactions.PresenceActivity(
                    name="/help", type=interactions.PresenceActivityType.LISTENING
                )
            ]
        )
    )


# This looks way different compared to other commands since its prepped for translation..
@bot.command(
    name="help",
    description="Shows a help message",
)
async def help(ctx: interactions.CommandContext):
    language = "en-US"  # ctx.guild.preferred_locale <-The thing to check what language the server is set to
    embed = interactions.Embed()
    embed.title = translations[(language)]["helpTitle"]
    embed.description = translations[(language)]["helpDesc"]
    embed.add_field(
        (translations[(language)]["helpCountdownTitle"]),
        (translations[(language)]["helpCountdownDesc"]),
    )
    embed.add_field(
        (translations[(language)]["helpListTitle"]),
        (translations[(language)]["helpListDesc"]),
    )
    # Only show Delete if the user got MANAGE_MESSAGES Permission
    if ctx.author.permissions & interactions.Permissions.MANAGE_MESSAGES:
        embed.add_field(
            (translations[(language)]["helpDeleteTitle"]),
            (translations[(language)]["helpDeleteDesc"]),
        )
    embed.add_field(
        (translations[(language)]["helpTitle"]),
        (translations[(language)]["helpHelpDesc"]),
    )
    # Only show Translate if the user got ADMINISTRATOR Permission
    if ctx.author.permissions & interactions.Permissions.ADMINISTRATOR:
        embed.add_field(
            (translations[(language)]["helpTranslateTitle"]),
            (translations[(language)]["helpTranslateDesc"]),
        )
    embed.add_field(
        (translations[(language)]["helpLinksTitle"]),
        (translations[(language)]["helpLinksDesc"]),
    )
    embed.color = int(
        ("#%02x%02x%02x" % (90, 232, 240)).replace("#", "0x"), base=16
    )  # Set the colour to light blue
    await ctx.send(embeds=embed, ephemeral=True)


@bot.command(
    name="countdown",
    description="Countdown to what you tells it to.",
    options=[
        interactions.Option(
            name="timestring",
            description="What time do you want",
            type=interactions.OptionType.STRING,
            max_length=100,
            required=True,
        ),
        interactions.Option(
            name="messagestart",
            description="Custom message before timer",
            type=interactions.OptionType.STRING,
            max_length=100,
            required=False,
        ),
        interactions.Option(
            name="messageend",
            description="Custom message after timer",
            type=interactions.OptionType.STRING,
            max_length=100,
            required=False,
        ),
        interactions.Option(
            name="mention",
            description="Who to mention",
            type=interactions.OptionType.MENTIONABLE,
            required=False,
        ),
        interactions.Option(
            name="times",
            description="Number of times to repeat",
            type=interactions.OptionType.INTEGER,
            required=False,
            max_value=50,
        ),
    ],
)
async def countdown(
    ctx: interactions.CommandContext,
    timestring,
    messagestart="Countdown will end",
    messageend="",
    mention="0",
    times=0,
):

    reachedlimit = checkactive(ctx.guild_id, ctx.channel_id)
    if reachedlimit:
        return await ctx.send(
            "Max countdowns reached. Delete one or wait for one to run out to add more.",
            ephemeral=True,
        )

    if mention != "0" and not (
        ctx.author.permissions & interactions.Permissions.MENTION_EVERYONE
    ):
        return await ctx.send("You dont have permission to ping", ephemeral=True)

    if mention != "0":
        mention = mention.id

    working = False
    try:
        wholedate = dateparser.parse(timestring)
        timestamp = floor(wholedate.timestamp())
        currenttime = floor(time.time())
        if currenttime < timestamp:
            messagestart = messagestart.replace("\\n", "\n")
            messageend = messageend.replace("\\n", "\n")
            response = f"{messagestart} <t:{timestamp}:R> {messageend}"
            length = timestamp - currenttime
            working = True
        else:
            response = "You cant set time in the past. Try adding **in** or be more specific about your time"
    except:
        response = "Not a valid date."

    if working == True:
        msg = await ctx.send(response)
        guildid = ctx.guild_id
        startedby = ctx.author.id
        writeerror = addtodatabase(
            timestamp,
            msg,
            guildid,
            mention,
            startedby,
            times,
            length,
            messagestart,
            messageend,
        )
        if writeerror:
            await ctx.send("SOMETHING WENT WRONG", ephemeral=True)
    else:
        msg = await ctx.send(response, ephemeral=True)


@bot.command(
    name="timer",
    description="Lets add a timer",
    options=[
        interactions.Option(
            name="minute",
            description="How many minutes",
            type=interactions.OptionType.INTEGER,
            required=False,
            max_value=1000,
        ),
        interactions.Option(
            name="hour",
            description="How many hours",
            type=interactions.OptionType.INTEGER,
            required=False,
            max_value=1000,
        ),
        interactions.Option(
            name="day",
            description="How many days",
            type=interactions.OptionType.INTEGER,
            required=False,
            max_value=1000,
        ),
        interactions.Option(
            name="week",
            description="How many weeks",
            type=interactions.OptionType.INTEGER,
            required=False,
            max_value=1000,
        ),
        interactions.Option(
            name="messagestart",
            description="Custom message before timer",
            type=interactions.OptionType.STRING,
            max_length=100,
            required=False,
        ),
        interactions.Option(
            name="messageend",
            description="Custom message after timer",
            type=interactions.OptionType.STRING,
            max_length=100,
            required=False,
        ),
        interactions.Option(
            name="mention",
            description="Who to mention",
            type=interactions.OptionType.MENTIONABLE,
            required=False,
        ),
        interactions.Option(
            name="times",
            description="Number of times to repeat",
            type=interactions.OptionType.INTEGER,
            required=False,
            max_value=50,
        ),
    ],
)
async def timer(
    ctx: interactions.CommandContext,
    day="0",
    week="0",
    hour="0",
    minute="0",
    messagestart="Timer will end",
    messageend="",
    mention="0",
    times="0",
):

    reachedlimit = checkactive(ctx.guild_id, ctx.channel_id)
    if reachedlimit:
        return await ctx.send(
            "Max countdowns reached. Delete one or wait for one to run out to add more.",
            ephemeral=True,
        )

    if mention != "0" and not (
        ctx.author.permissions & interactions.Permissions.MENTION_EVERYONE
    ):
        return await ctx.send("You dont have permission to ping", ephemeral=True)

    if mention != "0":
        mention = mention.id

    currenttime = floor(time.time())
    length = int(minute) * 60 + int(hour) * 3600 + int(day) * 86400 + int(week) * 604800
    timestamp = currenttime + length
    messagestart = messagestart.replace("\\n", "\n")
    messageend = messageend.replace("\\n", "\n")
    response = f"{messagestart} <t:{timestamp}:R> {messageend}"
    msg = await ctx.send(f"{response}!")
    guildid = ctx.guild_id
    startedby = ctx.author.id
    writeerror = addtodatabase(
        timestamp,
        msg,
        guildid,
        mention,
        startedby,
        times,
        length,
        messagestart,
        messageend,
    )
    if writeerror:
        await ctx.send("SOMETHING WENT WRONG", ephemeral=True)


@bot.command(
    name="list",
    description="List all countdowns",
    options=[
        interactions.Option(
            name="channel",
            description="List all countdowns in channel",
            type=interactions.OptionType.SUB_COMMAND,
            options=[
                interactions.Option(
                    name="page",
                    description="What page number",
                    type=interactions.OptionType.INTEGER,
                    required=False,
                ),
            ],
        ),
        interactions.Option(
            name="guild",
            description="List all countdowns in guild",
            type=interactions.OptionType.SUB_COMMAND,
            options=[
                interactions.Option(
                    name="page",
                    description="What page number",
                    type=interactions.OptionType.INTEGER,
                    required=False,
                    max_value=50,
                ),
            ],
        ),
        interactions.Option(
            name="mine",
            description="List all countdowns activated by you",
            type=interactions.OptionType.SUB_COMMAND,
            options=[
                interactions.Option(
                    name="page",
                    description="What page number",
                    type=interactions.OptionType.INTEGER,
                    required=False,
                    max_value=50,
                ),
            ],
        ),
    ],
)
async def list(ctx: interactions.CommandContext, sub_command: str, page=1):

    channelid = ctx.channel_id
    guildid = ctx.guild_id
    if sub_command == "channel":
        place = "in this channel"
        cursor = conn.execute(
            f"SELECT COUNT (*) FROM Countdowns WHERE channelid = {channelid};"
        )
        for row in cursor:
            numberofcountdown = int(row[0])
        cursor = conn.execute(
            f"SELECT timestamp,msgid,channelid,startedby FROM Countdowns WHERE channelid = {channelid} ORDER BY timestamp ASC;"
        )
    elif sub_command == "guild":
        place = "in this guild"
        cursor = conn.execute(
            f"SELECT COUNT (*) FROM Countdowns WHERE guildid = {guildid};"
        )
        for row in cursor:
            numberofcountdown = int(row[0])
        cursor = conn.execute(
            f"SELECT timestamp,msgid,channelid,startedby FROM Countdowns WHERE guildid = {guildid} ORDER BY timestamp ASC;"
        )
    elif sub_command == "mine":
        place = "from you"
        authour = ctx.author.id
        cursor = conn.execute(
            f"SELECT COUNT (*) FROM Countdowns WHERE guildid = {guildid} AND startedby = {authour};"
        )
        for row in cursor:
            numberofcountdown = int(row[0])
        cursor = conn.execute(
            f"SELECT timestamp,msgid,channelid,startedby FROM Countdowns WHERE guildid = {guildid} AND startedby = {authour} ORDER BY timestamp ASC;"
        )
    maxpage = ceil(numberofcountdown / 5)
    if maxpage < page:
        page = maxpage
    embed = interactions.Embed()
    embed.title = "ACTIVE COUNTDOWNS"
    embed.description = "These are the countdowns active " + place

    currentLine = 0
    goal = page * 5
    for row in cursor:

        if currentLine >= goal - 5:
            timeid = int(row[0])
            msgid = int(row[1])
            channelid = int(row[2])
            startedby = int(row[3])
            embed.add_field(
                f"<t:{timeid}:R>",
                f"[{msgid}](https://discord.com/channels/{guildid}/{channelid}/{msgid} 'Click here to jump to the message') Started by <@!{startedby}>\n",
            )
        elif currentLine < goal - 5:
            pass
        else:
            break
        currentLine = currentLine + 1
        if currentLine >= goal:
            break

    embed.footer = interactions.EmbedFooter(text=f"Page {page} of {maxpage}")
    embed.color = int(("#%02x%02x%02x" % (255, 153, 51)).replace("#", "0x"), base=16)
    await ctx.send(embeds=embed, ephemeral=True)


deleteGuild = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="Delete",
    custom_id="deleteguild",
)

deleteChannel = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="Delete",
    custom_id="deletechannel",
)

deleteCancel = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Keep countdowns",
    custom_id="deletecancel",
)


@bot.command(
    name="delete",
    description="Deletes countdowns",
    default_member_permissions=interactions.Permissions.MANAGE_MESSAGES,
    options=[
        interactions.Option(
            name="singgle",
            description="delete a single countdown",
            type=interactions.OptionType.SUB_COMMAND,
            options=[
                interactions.Option(
                    name="msgid",
                    description="Enter message ID that you want to delete.",
                    type=interactions.OptionType.STRING,
                    required=True,
                )
            ],
        ),
        interactions.Option(
            name="channel",
            description="Delete all countdowns in this channel",
            type=interactions.OptionType.SUB_COMMAND,
        ),
        interactions.Option(
            name="guild",
            description="Delete all countdowns in this guild",
            type=interactions.OptionType.SUB_COMMAND,
        ),
    ],
)
async def delete(ctx: interactions.CommandContext, sub_command: str, msgid: int = None):

    if sub_command == "single":
        guildid = ctx.guild_id
        check = conn.total_changes
        try:
            int(msgid)
            conn.execute(
                f"DELETE from Countdowns WHERE msgid = {msgid} AND guildid = {guildid};"
            )
            conn.commit()
            user = ctx.author
            if check == conn.total_changes:
                await ctx.send("An error occourd", ephemeral=True)
            else:
                await ctx.send(f"Countdown Deleted by {user}")
        except:
            await ctx.send("You need to send a messageid", ephemeral=True)

    elif sub_command == "channel":
        await ctx.send(
            "Are you sure you want to delete all the countdowns in this channel?",
            components=[deleteChannel, deleteCancel],
            ephemeral=True,
        )
    elif sub_command == "guild":
        await ctx.send(
            "Are you sure you want to delete all the countdowns in this guild?",
            components=[deleteGuild, deleteCancel],
            ephemeral=True,
        )


@bot.component("deleteguild")
async def button_response(ctx):

    guildid = ctx.guild_id
    check = conn.total_changes
    conn.execute(f"DELETE from Countdowns WHERE guildid = {guildid};")
    conn.commit()
    user = ctx.author
    if check == conn.total_changes:
        await ctx.send("An error occourd", ephemeral=True)
    else:
        await ctx.send(f"Servers Countdown(s) Deleted by {user}")


@bot.component("deletechannel")
async def button_response(ctx):

    channelid = ctx.channel_id
    check = conn.total_changes
    conn.execute(f"DELETE from Countdowns WHERE channelid = {channelid};")
    conn.commit()
    user = ctx.author
    if check == conn.total_changes:
        await ctx.send("An error occourd", ephemeral=True)
    else:
        await ctx.send(f"Channels Countdown(s) Deleted by {user}")


@bot.component("deletecancel")
async def button_response(ctx):
    await ctx.edit("Wont delete anything", components=[])


@bot.command(
    name="botstats",
    description="Shows stats of bot",
)
async def botstats(ctx: interactions.CommandContext):

    await ctx.defer(ephemeral=True)
    cpu = psutil.cpu_percent(4)
    ram = psutil.virtual_memory()[2]
    cursor = conn.execute("SELECT COUNT(*) FROM Countdowns;")
    for row in cursor:
        number = int(row[0])

    # Check this when activating shards
    ping = round(bot.latency)

    embed = interactions.Embed()
    embed.title = "BOT STATS"
    embed.description = "This is the current status of the bot"
    embed.add_field("CPU :fire:", f"{cpu}%")
    embed.add_field("RAM :floppy_disk:", f"{ram}%")
    embed.add_field("Active countdowns :clock1:", f"{number}")
    embed.add_field("Ping! :satellite:", f"{ping} ms")
    embed.color = int(("#%02x%02x%02x" % (255, 132, 140)).replace("#", "0x"), base=16)
    await ctx.send(embeds=embed)


@bot.command(
    name="translate",
    description="Translate the bot",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    scope=1010636307216728094,
    options=[
        interactions.Option(
            name="language",
            description="What language do you want to translate to?",
            type=interactions.OptionType.STRING,
            required=True,
            choices=[interactions.Choice(name="English", value="en-US")],
        ),
    ],
)
async def translate(ctx: interactions.CommandContext, language):
    await ctx.guild.set_preferred_locale(language)
    await ctx.send("Translated to " + language, ephemeral=True)


@create_task(IntervalTrigger(5))
async def timer_check():
    currenttime = time.time()
    cursor = conn.execute(
        f"SELECT timestamp,msgid,channelid,guildid,roleid,startedby,times,length,messagestart,messageend FROM Countdowns WHERE timestamp < {currenttime};"
    )
    for row in cursor:
        messageend = row[9]
        messagestart = row[8]
        length = int(row[7])
        times = int(row[6])
        startedby = row[5]
        roleid = row[4]
        guildid = row[3]
        channelid = row[2]
        msgid = row[1]
        timestamp = int(row[0])
        channel = interactions.Channel(
            **await bot._http.get_channel(channelid), _client=bot._http
        )

        # guild = await interactions.get(bot, interactions.Guild, object_id=int(channel.guild_id))
        language = "en-US"  # guild.preferred_locale

        embed = interactions.Embed()

        embed.title = translations[(language)]["done"]

        embed.description = f"{(translations[(language)]['created'])} <@!{startedby}>"

        if times != 0:
            timestamp = timestamp + length
            embed.add_field(
                "Reapeating",
                f"This countdown will be repeated {times} time(s) more. Next time is: <t:{timestamp}:R>",
            )
            times = times - 1
            conn.execute(
                f"UPDATE Countdowns set times = {times} where msgid = {msgid};"
            )
            conn.execute(
                f"UPDATE Countdowns set timestamp = {timestamp} where msgid = {msgid};"
            )
            conn.commit()
        else:
            conn.execute(
                f"DELETE from Countdowns WHERE msgid = {msgid} AND channelid = {channelid};"
            )
            conn.commit()

        content = f"{messagestart} <t:{timestamp}> {messageend}"
        embed.add_field("Countdown", content)
        embed.color = int(("#%02x%02x%02x" % (0, 255, 0)).replace("#", "0x"), base=16)

        if roleid != 0:
            try:
                await interactions.get(bot, interactions.User, object_id=roleid)
                await channel.send(f"<@{roleid}>", embeds=embed)
            except:
                await channel.send(
                    f"{'<@&' + str(roleid) + '>' if roleid != guildid else '@everyone'}",
                    embeds=embed,
                    allowed_mentions={"parse": ["roles", "everyone"]},
                )
        else:
            await channel.send(embeds=embed)


timer_check.start()

# shard(bot)

bot.start()
