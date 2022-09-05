# Main library
from re import sub
from types import NoneType
import interactions

# Handeling the database
import sqlite3

# parses the human date to a date that computer understands
import dateparser

# To get information about system usage (ram and cpu)
import psutil

# To validate a url
from validators import url as validurl

# Used for rounding down timestamps to whole numbers and to get the max pages needed.
from math import floor, ceil

# Used for... getting time.
import time

# Here all components are
import components

# Import a list of all premium users
from premiumGuilds import premiumGuilds

# Import a list of all translations
from languageFile import translations


# makes conn into the connected database.
conn = sqlite3.connect("Countdowns.db")

# Make the table if there is noe
conn.execute(
    """CREATE TABLE IF NOT EXISTS Countdowns (timestamp int,msgid int,channelid int,guildid int,roleid int,startedby int,times int,length int,imagelink varchar(255),messagestart varchar(255),messageend varchar(255));"""
)

# This checks so premium features can only be used by premium users.
async def checkPremium(ctx, feature):
    guild = ctx.guild.id
    if guild in premiumGuilds:
        return False

    # If the code havent returned yet, its not a premium user
    await ctx.send(
        f"Sorry, you tried to use a premium only feature: {feature}", ephemeral=True
    )
    return True


async def checkLink(ctx, imagelink):
    if validurl(imagelink):
        return False

    # If the code havent returned yet, its not a valid link
    await ctx.send("You need to send a link to the image", ephemeral=True)
    return True


# The function that adds in the countdowns in the database
async def sendAndAddToDatabase(
    timestamp, ctx, mention, times, length, messagestart, messageend, imagelink
):
    messagestart = messagestart.replace("\\n", "\n")
    messageend = messageend.replace("\\n", "\n")
    msg = await ctx.send(f"{messagestart} <t:{timestamp}:R> {messageend}")
    guildid = ctx.guild_id
    if guildid == None:
        guildid = 0
    startedby = ctx.user.id
    # Had problems with these numbers being "None" for some unknown reason, so added a check so they cant come into the database
    if msg.id == None or msg.channel_id == None or guildid == None:
        return True

    if mention != "0":
        roleid = mention.id
    else:
        roleid = 0

    conn.execute(
        "INSERT INTO Countdowns (timestamp,msgid,channelid,guildid,roleid,startedby,times,length,imagelink,messagestart,messageend) VALUES (:timestamp,:msgid,:channelid,:guildid,:mention,:startedby,:times,:length,:imagelink,:messagestart,:messageend);",
        {
            "timestamp": int(timestamp),
            "msgid": int(msg.id),
            "channelid": int(msg.channel_id),
            "guildid": int(guildid),
            "mention": int(roleid),
            "startedby": int(startedby),
            "times": int(times),
            "length": int(length),
            "imagelink": str(imagelink),
            "messagestart": str(messagestart),
            "messageend": str(messageend),
        },
    )
    conn.commit()
    return False


# Checks so that active countdowns isnt too many and that the user have permission to ping
async def checkActiveAndMention(ctx, mention):
    if ctx.guild_id == None:
        cursor = conn.execute(
            "SELECT COUNT(*) FROM Countdowns WHERE channelid=:channelid;",
            {"channelid": int(ctx.channel_id)},
        )
        for row in cursor:
            channel = int(row[0])
        if channel > 5:
            await ctx.send(
                "Max countdowns in dms reached. Delete one or wait for one to run out to add more.",
                ephemeral=True,
            )
            return True

    else:
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


async def help(ctx):
    language = "en-US"  # ctx.guild.preferred_locale <-The thing to check what language the guild is set to
    embed = interactions.Embed()
    embed.title = translations[(language)]["helpTitle"]
    embed.description = translations[(language)]["helpDesc"]
    embed.add_field(
        (translations[(language)]["helpTitle"]),
        (translations[(language)]["helpHelpDesc"]),
    )
    embed.add_field(
        (translations[(language)]["helpCountdownTitle"]),
        (translations[(language)]["helpCountdownDesc"]),
    )
    embed.add_field(
        (translations[(language)]["helpListTitle"]),
        (translations[(language)]["helpListDesc"]),
    )
    # Only show Delete if the user got MANAGE_MESSAGES Permission
    # The try is for handeling being used in dms
    try:
        if ctx.author.permissions & interactions.Permissions.MANAGE_MESSAGES:
            embed.add_field(
                (translations[(language)]["helpDeleteTitle"]),
                (translations[(language)]["helpDeleteDesc"]),
            )

        # Only show Translate if the user got ADMINISTRATOR Permission
        if ctx.author.permissions & interactions.Permissions.ADMINISTRATOR:
            embed.add_field(
                (translations[(language)]["helpTranslateTitle"]),
                (translations[(language)]["helpTranslateDesc"]),
            )
    except:
        # If they are in DM, dont show these stuff.
        pass
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


async def countdown(
    ctx, timestring, messagestart, messageend, mention, times, imagelink
):

    if await checkActiveAndMention(ctx, mention):
        return

    if imagelink != "":
        if await checkPremium(ctx, "adding image"):
            return
        if await checkLink(ctx, imagelink):
            return

    if times != 0:
        if await checkPremium(ctx, "repeating timer"):
            return

    try:
        wholedate = dateparser.parse("in " + timestring)
        timestamp = floor(wholedate.timestamp())
        validDate = True
    except:
        try:
            wholedate = dateparser.parse(timestring)
            timestamp = floor(wholedate.timestamp())
            validDate = True
        except:
            await ctx.send("Not a valid date.", ephemeral=True)
            validDate = False

    if validDate:
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
                imagelink,
            )
            if writeerror:
                await ctx.send("SOMETHING WENT WRONG", ephemeral=True)
        else:
            await ctx.send(
                "You cant set time in the past. Try adding **in** or be more specific about your time",
                ephemeral=True,
            )


async def timer(
    ctx, day, week, hour, minute, messagestart, messageend, mention, times, imagelink
):
    if await checkActiveAndMention(ctx, mention):
        return

    if imagelink != "":
        if await checkPremium(ctx, "adding image"):
            return
        if await checkLink(ctx, imagelink):
            return

    if times != 0:
        if await checkPremium(ctx, "repeating timer"):
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
        imagelink,
    )
    if writeerror:
        await ctx.send("SOMETHING WENT WRONG", ephemeral=True)


async def list(ctx, sub_command, page):
    if ctx.guild_id == None and sub_command != "channel":
        return await ctx.send("Sorry, only /list channel works in DMs", ephemeral=True)
    # Links for DMs are @me instead of the guildid
    if ctx.guild_id == None:
        guildid = "@me"
    else:
        guildid = int(ctx.guild_id)
    channelid = int(ctx.channel_id)
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
        user = int(ctx.user.id)
        cursor = conn.execute(
            "SELECT COUNT (*) FROM Countdowns WHERE guildid = :guildid AND startedby = :user;",
            {"guildid": guildid, "user": user},
        )
        for row in cursor:
            numberofcountdown = int(row[0])
        cursor = conn.execute(
            "SELECT timestamp,msgid,channelid,startedby FROM Countdowns WHERE guildid = :guildid AND startedby = :user ORDER BY timestamp ASC;",
            {"guildid": guildid, "user": user},
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


async def delete(
    ctx, sub_command, sub_command_group, deletemine, deletechannel, deleteguild
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
        user = ctx.user
        if check == conn.total_changes:
            await ctx.send("An error occurred ", ephemeral=True)
        else:
            await ctx.send(f"Countdown{msgid} was deleted by {user}")

    else:
        if sub_command == "channel":
            await ctx.send(
                "Are you sure you want to delete all the countdowns in this channel?",
                components=[components.deleteChannel, components.deleteCancel],
                ephemeral=True,
            )
        elif sub_command == "guild":
            await ctx.send(
                "Are you sure you want to delete all the countdowns in this guild?",
                components=[components.deleteGuild, components.deleteCancel],
                ephemeral=True,
            )


# this function is used for the autocompletion of what active countdowns there is to delete in all categories.
async def fillChoices(ctx, cursor, value):
    countdowns = []
    id = 0
    for row in cursor:
        if (
            id < 24
        ):  # Need to be limited due to discord not allowing more than 25 options
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


async def autocompleteDelete(ctx, value, whattodelete):
    if whattodelete == "mine":
        user = int(ctx.user.id)
        cursor = conn.execute(
            "SELECT msgid FROM Countdowns WHERE startedby = :user ORDER BY timestamp ASC;",
            {"user": user},
        )
    elif whattodelete == "channel":
        channelid = int(ctx.channel_id)
        cursor = conn.execute(
            "SELECT msgid FROM Countdowns WHERE channelid = :channelid ORDER BY timestamp ASC;",
            {"channelid": channelid},
        )
    elif whattodelete == "guild":

        if ctx.guild_id == None:
            cursor = conn.execute(
                "SELECT msgid FROM Countdowns WHERE channelid = :channelid ORDER BY timestamp ASC;",
                {"channelid": channelid},
            )
        else:
            guildid = int(ctx.guild_id)
            cursor = conn.execute(
                "SELECT msgid FROM Countdowns WHERE guildid = :guildid ORDER BY timestamp ASC;",
                {"guildid": guildid},
            )
    await fillChoices(ctx, cursor, value)


async def deletebutton(ctx, whattodelete):
    if whattodelete == "guild":
        if ctx.guild_id == None:
            return ctx.send("You cant use this in DMs", ephemeral=True)
        guildid = int(ctx.guild_id)
        check = conn.total_changes
        conn.execute(
            "DELETE from Countdowns WHERE guildid = :guildid;", {"guildid": guildid}
        )
        conn.commit()
        user = ctx.user
        if check == conn.total_changes:
            await ctx.send("An error occurred ", ephemeral=True)
        else:
            await ctx.send(f"Servers Countdown(s) Deleted by {user}")
    elif whattodelete == "channel":
        channelid = int(ctx.channel_id)
        check = conn.total_changes
        conn.execute(
            "DELETE from Countdowns WHERE channelid = :channelid;",
            {"channelid": channelid},
        )
        conn.commit()
        user = ctx.user
        if check == conn.total_changes:
            await ctx.send("An error occurred ", ephemeral=True)
        else:
            await ctx.send(f"Channels Countdown(s) Deleted by {user}")
    elif whattodelete == "cancel":
        # Just edit away the buttons and say that contdowns are kept
        await ctx.edit("All countdowns are kept", components=[])


async def botstats(ctx, bot):
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


async def translate(ctx, language, bot):
    if ctx.author.permissions & interactions.Permissions.ADMINISTRATOR:
        try:
            await ctx.guild.set_preferred_locale(language)
            await ctx.send(f"{ctx.user} translated the bot to {language}")
        except:
            await ctx.send(
                "Sorry, I need to be able to manage guild to use this command",
                ephemeral=True,
            )
    else:
        await ctx.send(
            "Sorry, you need to be administrator to use this command", ephemeral=True
        )


async def checkDone(bot):
    currenttime = int(floor(time.time()))
    cursor = conn.execute(
        "SELECT timestamp,msgid,channelid,guildid,roleid,startedby,times,length,imagelink,messagestart,messageend FROM Countdowns WHERE timestamp < :currenttime;",
        {"currenttime": currenttime},
    )
    # There will just be an empty row in cursor if theres no countdowns that are active.
    # Therefore this wont run multiple times.
    for row in cursor:
        messageend = str(row[10])
        messagestart = str(row[9])
        imagelink = str(row[8])
        length = int(row[7])
        times = int(row[6])
        startedby = int(row[5])
        roleid = int(row[4])
        guildid = int(row[3])
        channelid = int(row[2])
        msgid = int(row[1])
        timestamp = int(row[0])
        try:
            channel = await interactions.get(
                bot, interactions.Channel, object_id=channelid
            )
        except:
            conn.execute(
                "DELETE from Countdowns WHERE msgid = :msgid AND channelid = :channelid;",
                {"msgid": msgid, "channelid": channelid},
            )
            conn.commit()
            return

        # guild = await interactions.get(bot, interactions.Guild, object_id=int(channel.guild_id))
        language = "en-US"  # guild.preferred_locale

        embed = interactions.Embed()

        embed.title = translations[(language)]["done"]

        embed.description = f"{(translations[(language)]['created'])} <@!{startedby}>"

        if imagelink != "":
            embed.set_image(url=imagelink)

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
