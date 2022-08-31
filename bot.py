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
        "helpFooter": "Thanks Zetas2 for translating to English",
        "done": "A countdown is done!",
        "created": "It was started by",
    },
}

# The function that adds in the countdowns in the database
async def sendAndAddToDatabase(
    timestamp,
    ctx,
    mention,
    times,
    length,
    messagestart,
    messageend,
):
    messagestart = messagestart.replace("\\n", "\n")
    messageend = messageend.replace("\\n", "\n")
    msg = await ctx.send(f"{messagestart} <t:{timestamp}:R> {messageend}")
    guildid = ctx.guild_id
    startedby = ctx.author.id
    # Had problems with these numbers being "None" for some unknown reason, so added a check so they cant come into the database
    if msg.id == None or msg.channel_id == None or guildid == None:
        return True

    conn.execute(
        "INSERT INTO Countdowns (timestamp,msgid,channelid,guildid,roleid,startedby,times,length,messagestart,messageend) VALUES (:timestamp,:msgid,:channelid,:guildid,:mention,:startedby,:times,:length,:messagestart,:messageend);",
        {
            "timestamp": int(timestamp),
            "msgid": int(msg.id),
            "channelid": int(msg.channel_id),
            "guildid": int(guildid),
            "mention": int(mention),
            "startedby": int(startedby),
            "times": int(times),
            "length": int(length),
            "messagestart": str(messagestart),
            "messageend": str(messageend),
        },
    )
    conn.commit()
    return False


# Checks so that active countdowns isnt too many and that the user have permission to ping
async def checkActiveAndMention(ctx, mention):
    cursor = conn.execute(
        "SELECT COUNT(*) FROM Countdowns WHERE guildid= :guildid;",
        {"guildid": int(ctx.guild_id)},
    )
    for row in cursor:
        guild = int(row[0])
    cursor = conn.execute(
        "SELECT COUNT(*) FROM Countdowns WHERE channelid=:channelid;",
        {"channelid": int(ctx.channel_id)},
    )
    for row in cursor:
        channel = int(row[0])
    if guild > 50:  # Limits number of active countdowns to 51
        await ctx.send(
            "Max countdowns in guild reached. Delete one or wait for one to run out to add more.",
            ephemeral=True,
        )
        return True
    elif channel > 20:  # limits number of active countdowns to 21
        await ctx.send(
            "Max countdowns in channel reached. Delete one or wait for one to run out to add more.",
            ephemeral=True,
        )
        return True
    else:
        # Here the limit wasnt reached, so therefore continue checking permission
        if mention != "0" and not (
            ctx.author.permissions & interactions.Permissions.MENTION_EVERYONE
        ):
            await ctx.send("You dont have permission to ping", ephemeral=True)

        if mention != "0":
            mention = mention.id

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

    embed.footer = interactions.EmbedFooter(
        text=(translations[(language)]["helpFooter"])
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
    messageend="!",
    mention="0",
    times=0,
):

    reachedLimit = await checkActiveAndMention(ctx, mention)

    if reachedLimit:
        return

    try:
        wholedate = dateparser.parse(
            timestring
        )  # This is the line that can cause the error in this try/except. It causes an error if the timestring isnt a valid date.
        timestamp = floor(wholedate.timestamp())
        currenttime = floor(time.time())
        if currenttime < timestamp:  # Make sure the time is in the future
            length = timestamp - currenttime
            writeerror = await sendAndAddToDatabase(
                timestamp,
                ctx,
                mention,
                times,
                length,
                messagestart,
                messageend,
            )
            if writeerror:
                await ctx.send("SOMETHING WENT WRONG", ephemeral=True)
        else:
            await ctx.send(
                "You cant set time in the past. Try adding **in** or be more specific about your time",
                ephemeral=True,
            )
    except:
        await ctx.send("Not a valid date.", ephemeral=True)


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
    day=0,
    week=0,
    hour=0,
    minute=0,
    messagestart="Timer will end",
    messageend="!",
    mention="0",
    times=0,
):

    reachedLimit = await checkActiveAndMention(ctx, mention)

    if reachedLimit:
        return

    currenttime = floor(time.time())
    length = minute * 60 + hour * 3600 + day * 86400 + week * 604800
    timestamp = currenttime + length

    writeerror = await sendAndAddToDatabase(
        timestamp,
        ctx,
        mention,
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

    channelid = int(ctx.channel_id)
    guildid = int(ctx.guild_id)
    if sub_command == "channel":
        place = "in this channel"
        cursor = conn.execute(
            "SELECT COUNT (*) FROM Countdowns WHERE channelid = :channelid;",
            {"channelid": channelid},
        )

        for row in cursor:
            numberofcountdown = int(row[0])
        cursor = conn.execute(
            "SELECT timestamp,msgid,channelid,startedby FROM Countdowns WHERE channelid = :channelid ORDER BY timestamp ASC;",
            {"channelid": channelid},
        )
    elif sub_command == "guild":
        place = "in this guild"
        cursor = conn.execute(
            "SELECT COUNT (*) FROM Countdowns WHERE guildid = :guildid;",
            {"guildid": guildid},
        )
        for row in cursor:
            numberofcountdown = int(row[0])
        cursor = conn.execute(
            "SELECT timestamp,msgid,channelid,startedby FROM Countdowns WHERE guildid = :guildid ORDER BY timestamp ASC;",
            {"guildid": guildid},
        )
    elif sub_command == "mine":
        place = "from you"
        author = int(ctx.author.id)
        cursor = conn.execute(
            "SELECT COUNT (*) FROM Countdowns WHERE guildid = :guildid AND startedby = :author;",
            {"guildid": guildid, "author": author},
        )
        for row in cursor:
            numberofcountdown = int(row[0])
        cursor = conn.execute(
            "SELECT timestamp,msgid,channelid,startedby FROM Countdowns WHERE guildid = :guildid AND startedby = :author ORDER BY timestamp ASC;",
            {"guildid": guildid, "author": author},
        )
    maxpage = ceil(numberofcountdown / 5)
    if maxpage < page:
        page = maxpage

    embed = interactions.Embed()
    embed.title = "ACTIVE COUNTDOWNS"
    embed.description = "These are the countdowns active " + place

    currentLine = 0
    goalLine = page * 5

    # Loops through all active countowns in the correct place to pick out the ones that should be on specified page
    for row in cursor:
        if currentLine >= goalLine - 5:
            timeid = int(row[0])
            msgid = int(row[1])
            channelid = int(row[2])
            startedby = int(row[3])
            embed.add_field(
                f"{currentLine}: <t:{timeid}:R>",
                f"[{msgid}](https://discord.com/channels/{guildid}/{channelid}/{msgid} 'Click here to jump to the message') Started by <@!{startedby}>\n",
            )
        elif currentLine < goalLine - 5:
            pass
        else:
            break
        currentLine = currentLine + 1
        if currentLine >= goalLine:
            break

    embed.footer = interactions.EmbedFooter(text=f"Page {page} of {maxpage}")
    embed.color = int(("#%02x%02x%02x" % (255, 153, 51)).replace("#", "0x"), base=16)
    await ctx.send(embeds=embed, ephemeral=True)


# Buttons that are added as a verification step when multiple countdowns will be deleted.
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
            name="single",
            description="delete a single countdown",
            type=interactions.OptionType.SUB_COMMAND_GROUP,
            options=[
                interactions.Option(
                    name="mine",
                    description="delete one of your countdowns",
                    type=interactions.OptionType.SUB_COMMAND,
                    options=[
                        interactions.Option(
                            type=interactions.OptionType.STRING,
                            name="deletemine",
                            description="Which of your countdowns do you want to be deleted?",
                            required=True,
                            autocomplete=True,
                        )
                    ],
                ),
                interactions.Option(
                    name="channel",
                    description="delete one of this channels countdowns",
                    type=interactions.OptionType.SUB_COMMAND,
                    options=[
                        interactions.Option(
                            type=interactions.OptionType.STRING,
                            name="deletechannel",
                            description="Which of this channels countdowns do you want to be deleted?",
                            required=True,
                            autocomplete=True,
                        )
                    ],
                ),
                interactions.Option(
                    name="guild",
                    description="delete one of this guilds countdowns",
                    type=interactions.OptionType.SUB_COMMAND,
                    options=[
                        interactions.Option(
                            type=interactions.OptionType.STRING,
                            name="deleteguild",
                            description="Which of this guilds countdowns do you want to be deleted?",
                            required=True,
                            autocomplete=True,
                        )
                    ],
                ),
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
async def delete(
    ctx: interactions.CommandContext,
    sub_command: str,
    sub_command_group: str = "",
    deletemine: str = "",
    deletechannel: str = "",
    deleteguild: str = "",
):

    if sub_command_group == "single":
        if sub_command == "mine":
            msgid = deletemine.split(":")[1]
        if sub_command == "channel":
            msgid = deletechannel.split(":")[1]
        if sub_command == "guild":
            msgid = deleteguild.split(":")[1]
        check = conn.total_changes
        conn.execute("DELETE from Countdowns WHERE msgid = :msgid;", {"msgid": msgid})
        conn.commit()
        user = ctx.author
        if check == conn.total_changes:
            await ctx.send("An error occurred ", ephemeral=True)
        else:
            await ctx.send(f"Countdown {msgid} was deleted by {user}")

    else:
        if sub_command == "channel":
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

#this function is used for the autocompletion of what active countdowns there is to delete in all categories.
async def fillChoices(ctx, cursor, value):
    countdowns = []
    id = 0
    for row in cursor:
        if id < 24: #Need to be limited due to discord not allowing more than 25 options
            countdowns.append(str(id) + ": " + str(row[0]))
            id = id + 1
        else:
            break
    choices = [
        interactions.Choice(name=item, value=item)
        for item in countdowns
        if value in item
    ]
    await ctx.populate(choices)


@bot.autocomplete("delete", "deletemine")
async def autocompleteMine(ctx: interactions.CommandContext, value: str = ""):
    author = int(ctx.author.id)
    cursor = conn.execute(
        "SELECT msgid FROM Countdowns WHERE startedby = :author ORDER BY timestamp ASC;",
        {"author": author},
    )
    await fillChoices(ctx, cursor, value)


@bot.autocomplete("delete", "deletechannel")
async def autocompleteMine(ctx: interactions.CommandContext, value: str = ""):
    channelid = int(ctx.channel_id)
    cursor = conn.execute(
        "SELECT msgid FROM Countdowns WHERE channelid = :channelid ORDER BY timestamp ASC;",
        {"channelid": channelid},
    )
    await fillChoices(ctx, cursor, value)


@bot.autocomplete("delete", "deleteguild")
async def autocompleteMine(ctx: interactions.CommandContext, value: str = ""):
    guildid = int(ctx.guild_id)
    cursor = conn.execute(
        "SELECT msgid FROM Countdowns WHERE guildid = :guildid ORDER BY timestamp ASC;",
        {"guildid": guildid},
    )
    await fillChoices(ctx, cursor, value)

#Here are the functions that runs when the verify/cancel buttons are pressed
@bot.component("deleteguild")
async def button_response(ctx):
    guildid = int(ctx.guild_id)
    check = conn.total_changes
    conn.execute(
        "DELETE from Countdowns WHERE guildid = :guildid;", {"guildid": guildid}
    )
    conn.commit()
    user = ctx.author
    if check == conn.total_changes:
        await ctx.send("An error occurred ", ephemeral=True)
    else:
        await ctx.send(f"Servers Countdown(s) Deleted by {user}")


@bot.component("deletechannel")
async def button_response(ctx):

    channelid = int(ctx.channel_id)
    check = conn.total_changes
    conn.execute(
        "DELETE from Countdowns WHERE channelid = :channelid;", {"channelid": channelid}
    )
    conn.commit()
    user = ctx.author
    if check == conn.total_changes:
        await ctx.send("An error occurred ", ephemeral=True)
    else:
        await ctx.send(f"Channels Countdown(s) Deleted by {user}")


@bot.component("deletecancel")
async def button_response(ctx):
    #Just edit away the buttons and say that contdowns are kept
    await ctx.edit("All countdowns are kept", components=[])



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


# This command is not entierly active yet. It is just a prototype for when the bot is availible in multiple languages.
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


# This is the task that keeps looking if any countdowns are done.
@create_task(IntervalTrigger(5))  # 5 means execute task each 5 second
async def timer_check():
    currenttime = int(floor(time.time()))
    cursor = conn.execute(
        "SELECT timestamp,msgid,channelid,guildid,roleid,startedby,times,length,messagestart,messageend FROM Countdowns WHERE timestamp < :currenttime;",
        {"currenttime": currenttime},
    )
    # There will just be an empty row in cursor if theres no countdowns that are active.
    # Therefore this wont run multiple times.
    for row in cursor:
        messageend = str(row[9])
        messagestart = str(row[8])
        length = int(row[7])
        times = int(row[6])
        startedby = int(row[5])
        roleid = int(row[4])
        guildid = int(row[3])
        channelid = int(row[2])
        msgid = int(row[1])
        timestamp = int(row[0])
        channel = interactions.Channel(
            **await bot._http.get_channel(channelid), _client=bot._http
        )

        # guild = await interactions.get(bot, interactions.Guild, object_id=int(channel.guild_id))
        language = "en-US"  # guild.preferred_locale

        embed = interactions.Embed()

        embed.title = translations[(language)]["done"]

        embed.description = f"{(translations[(language)]['created'])} <@!{startedby}>"

        # If it is repeating, it should decrease the number of times to repeat
        if times != 0:
            timestamp = timestamp + length
            embed.add_field(
                "Reapeating",
                f"This countdown will be repeated {times} time(s) more. Next time is: <t:{timestamp}:R>",
            )
            times = times - 1
            conn.execute(
                "UPDATE Countdowns set times = :times where msgid = :msgid;",
                {"times": times, "msgid": msgid},
            )
            conn.execute(
                "UPDATE Countdowns set timestamp = :timestamp where msgid = :msgid;",
                {"timestamp": timestamp, "msgid": msgid},
            )
            conn.commit()
        # If its not repeating, it should get deleted from the database
        else:
            conn.execute(
                "DELETE from Countdowns WHERE msgid = :msgid AND channelid = :channelid;",
                {"msgid": msgid, "channelid": channelid},
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
