# Main library
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

# Import a list of all translations
from languageFile import translations


# makes connCountdowns into the connected database for countdowns.
connCountdowns = sqlite3.connect("Countdowns.db")


# Make the table if there is noe
connCountdowns.execute(
    """CREATE TABLE IF NOT EXISTS Countdowns (timestamp int,msgid int,channelid int,guildid int,roleid int,startedby int,times int,length int,imagelink varchar(255),messagestart varchar(255),messageend varchar(255));"""
)

# makes connPremium into the connected database for premium.
connPremium = sqlite3.connect("premiumGuilds.db")
# Make the table if there is noe
connPremium.execute(
    """CREATE TABLE IF NOT EXISTS Premium (guildid int,userid int,lastedit int)"""
)

botstarttime = floor(time.time())


# This checks so premium features can only be used by premium users.
async def checkNoPremium(ctx, feature):
    if ctx.guild_id == None:
        await ctx.send("You cant use premium features in DMs", ephemeral=True)
        return True
    guildid = int(ctx.guild_id)

    cursor = connPremium.execute(
        "SELECT guildid FROM Premium WHERE guildid = :guildid;",
        {"guildid": guildid},
    )

    for row in cursor:
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


def getExactTimestring(timestring, length):
    meassurement = length
    if meassurement >= 86400:
        amount = meassurement // 86400
        meassurement = meassurement - amount * 86400
        timestring = timestring + " " + str(amount) + " day(s)"
    if meassurement >= 3600:
        amount = meassurement // 3600
        meassurement = meassurement - amount * 3600
        timestring = timestring + " " + str(amount) + " hour(s)"
    if meassurement >= 60:
        amount = meassurement // 60
        meassurement = meassurement - amount * 60
        timestring = timestring + " " + str(amount) + " minute(s)"
    if meassurement > 0:
        amount = meassurement
        timestring = timestring + " " + str(amount) + " second(s)"
    return timestring


# The function that adds in the countdowns in the database
async def sendAndAddToDatabase(
    timestamp,
    ctx,
    mention,
    times,
    length,
    messagestart,
    messageend,
    imagelink,
    exact,
    alert,
    bot,
):
    try:
        if alert:
            channel = await ctx.get_channel()
            member = await interactions.get(
                    bot, interactions.Member, object_id=int(bot.me.id), parent_id=ctx.guild_id
                )
            gotpermission = await member.has_permissions(
            interactions.Permissions.EMBED_LINKS^interactions.Permissions.SEND_MESSAGES, channel=channel
            )        
        else:
            gotpermission = True
    except:
        await ctx.send(
            f"I am missing the permission to view this channel. Please give me it!",
            ephemeral=True,
        )
    else:
        if gotpermission:
            messagestart = messagestart.replace("\\n", "\n")
            messageend = messageend.replace("\\n", "\n")
            currenttime = floor(time.time())
            timeleft = int(timestamp) - int(currenttime)
            timestring = ""
            if exact:
                if timeleft > 3600:
                    timestring = "\n*Exact time from start: "
                    timestring = getExactTimestring(timestring, timeleft)
                    timestring = timestring + "*"
            msg = await ctx.send(
                f"{messagestart} <t:{timestamp}:R> {messageend}{timestring}"
            )

            if alert:
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

                connCountdowns.execute(
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
                connCountdowns.commit()
            return False
        else:
            await ctx.send(
                f"I am missing the permission to send embeds/messages in this channel. Please give me it!",
                ephemeral=True,
            )


async def checkLength(ctx, length):
    if length < 60:
        if int(ctx.user.id) != 238006908664020993:
            await ctx.send(
                "Minimum length of a countdown is one minute", ephemeral=True
            )
            return True
    return False


# Checks so that active countdowns isnt too many and that the user have permission to ping
async def checkActiveAndMention(ctx, mention):
    if ctx.guild_id == None:
        cursor = connCountdowns.execute(
            "SELECT COUNT(*) FROM Countdowns WHERE channelid=:channelid;",
            {"channelid": int(ctx.channel_id)},
        )
        for row in cursor:
            channel = int(row[0])
        if channel > 4:
            await ctx.send(
                "Max countdowns in dms reached. Delete one or wait for one to run out to add more.",
                ephemeral=True,
            )
            return True

    else:

        cursor = connCountdowns.execute(
            "SELECT COUNT(*) FROM Countdowns WHERE guildid= :guildid;",
            {"guildid": int(ctx.guild_id)},
        )
        for row in cursor:
            guild = int(row[0])
        cursor = connCountdowns.execute(
            "SELECT COUNT(*) FROM Countdowns WHERE channelid=:channelid;",
            {"channelid": int(ctx.channel_id)},
        )
        for row in cursor:
            channel = int(row[0])
        if guild > 48:  # Limits number of active countdowns to 50
            if await checkNoPremium(
                ctx,
                "Increased amount of countdowns in this guild. Get premium or delete some of the active ones.",
            ):
                return True
        elif channel > 19:  # limits number of active countdowns to 20
            if await checkNoPremium(
                ctx,
                "Increased amount of countdowns in this channel. Get premium or delete some of the active ones.",
            ):
                return True
        # Here the limit wasnt reached, so therefore continue checking permission
        if mention != "0" and not (
            ctx.author.permissions & interactions.Permissions.MENTION_EVERYONE
        ):
            await ctx.send("You dont have permission to ping", ephemeral=True)
            return True

        if mention != "0":
            mention = mention.id

        return False


async def help(ctx):
    language = "en-US"  # ctx.guild.preferred_locale <-The thing to check what language the guild is set to
    embed = interactions.Embed()
    embed.title = translations[(language)]["helpHeader"]
    embed.description = (
        (translations[(language)]["helpHover"])
        + "\n"
        + translations[(language)]["helpDesc"]
    )
    embed.add_field(
        (translations[(language)]["helpHelpTitle"]),
        (translations[(language)]["helpHelpDesc"]),
    )
    embed.add_field(
        (translations[(language)]["helpCountdownTitle"]),
        (translations[(language)]["helpCountdownDesc"]),
    )
    embed.add_field(
        (translations[(language)]["helpLeftTitle"]),
        (translations[(language)]["helpLeftDesc"]),
    )
    embed.add_field(
        (translations[(language)]["helpListTitle"]),
        (translations[(language)]["helpListDesc"]),
    )
    embed.add_field(
        (translations[(language)]["helpDeleteTitle"]),
        (translations[(language)]["helpDeleteDesc"]),
    )
    try:
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
        translations[(language)]["helpLinksDesc"]
    )

    embed.footer = interactions.EmbedFooter(
        text=(translations[(language)]["helpFooter"])
    )

    embed.color = int(
        ("#%02x%02x%02x" % (90, 232, 240)).replace("#", "0x"), base=16
    )  # Set the colour to light blue
    await ctx.send(embeds=embed, ephemeral=True)


async def countdown(
    ctx,
    timestring,
    messagestart,
    messageend,
    mention,
    times,
    repeattime,
    imagelink,
    exact,
    alert,
    bot,
):

    if await checkActiveAndMention(ctx, mention):
        return

    if imagelink != "":
        if await checkNoPremium(ctx, "adding image"):
            return
        if await checkLink(ctx, imagelink):
            return

    if times != 0:
        if await checkNoPremium(ctx, "repeating timer"):
            return

    wholedate = dateparser.parse("in " + timestring)
    try:
        timestamp = floor(wholedate.timestamp())
        validDate = True
    except:
        await ctx.send(
            f"Sorry, I dont understand that date!",
            ephemeral=True,
        )
        validDate = False
    
    if validDate:
        currenttime = floor(time.time())
        if currenttime < timestamp:  # Make sure the time is in the future
            length = timestamp - currenttime
            if await checkLength(ctx, length):
                return
            if times != 0:
                length = repeattime * 3600
            writeerror = await sendAndAddToDatabase(
                timestamp,
                ctx,
                mention,
                times,
                length,
                messagestart,
                messageend,
                imagelink,
                exact,
                alert,
                bot,
            )
            if writeerror:
                await ctx.send("SOMETHING WENT WRONG", ephemeral=True)
        else:
            await ctx.send(
                "You cant set time in the past. Try be more specific about your time.",
                ephemeral=True,
            )


async def timer(
    ctx,
    day,
    week,
    hour,
    minute,
    messagestart,
    messageend,
    mention,
    times,
    imagelink,
    exact,
    alert,
    bot,
):
    if await checkActiveAndMention(ctx, mention):
        return

    if imagelink != "":
        if await checkNoPremium(ctx, "adding image"):
            return
        if await checkLink(ctx, imagelink):
            return

    if times != 0:
        if await checkNoPremium(ctx, "repeating timer"):
            return

    currenttime = floor(time.time())
    length = minute * 60 + hour * 3600 + day * 86400 + week * 604800
    if await checkLength(ctx, length):
        return
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
        exact,
        alert,
        bot,
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
        cursor = connCountdowns.execute(
            "SELECT COUNT (*) FROM Countdowns WHERE channelid = :channelid;",
            {"channelid": channelid},
        )

        for row in cursor:
            numberofcountdown = int(row[0])
        cursor = connCountdowns.execute(
            "SELECT timestamp,msgid,channelid,startedby FROM Countdowns WHERE channelid = :channelid ORDER BY timestamp ASC;",
            {"channelid": channelid},
        )
    elif sub_command == "guild":
        place = "in this guild"
        cursor = connCountdowns.execute(
            "SELECT COUNT (*) FROM Countdowns WHERE guildid = :guildid;",
            {"guildid": guildid},
        )
        for row in cursor:
            numberofcountdown = int(row[0])
        cursor = connCountdowns.execute(
            "SELECT timestamp,msgid,channelid,startedby FROM Countdowns WHERE guildid = :guildid ORDER BY timestamp ASC;",
            {"guildid": guildid},
        )
    elif sub_command == "mine":
        place = "from you"
        userid = int(ctx.user.id)
        cursor = connCountdowns.execute(
            "SELECT COUNT (*) FROM Countdowns WHERE guildid = :guildid AND startedby = :userid;",
            {"guildid": guildid, "userid": userid},
        )
        for row in cursor:
            numberofcountdown = int(row[0])
        cursor = connCountdowns.execute(
            "SELECT timestamp,msgid,channelid,startedby FROM Countdowns WHERE guildid = :guildid AND startedby = :userid ORDER BY timestamp ASC;",
            {"guildid": guildid, "userid": userid},
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
    if sub_command == "mine":
        if sub_command_group == "single":
            cursor = getPossibleCountdowns(ctx, "mine")
            try:
                msgid = deletemine.split(": ")[1]
            except:
                return await ctx.send("Please use one of the options ", ephemeral=True)
            allowedDelete = False
            for row in cursor:
                if int(row[0]) == int(msgid):
                    allowedDelete = True
                    pass
            if not allowedDelete:
                return await ctx.send("Please use one of the options", ephemeral=True)

            check = connCountdowns.total_changes
            connCountdowns.execute(
                "DELETE from Countdowns WHERE msgid = :msgid;", {"msgid": msgid}
            )
            connCountdowns.commit()
            if check == connCountdowns.total_changes:
                await ctx.send(
                    "An error occurred (could be that there is none to delete)",
                    ephemeral=True,
                )
            else:

                user = ctx.user
                guildid = ctx.guild_id
                channelid = ctx.channel_id
                await ctx.send(f"Countdown [{msgid}](https://discord.com/channels/{guildid}/{channelid}/{msgid} 'Click here to jump to the message') was deleted by {user}")
        else:
            await ctx.send(
                "Are you sure you want to delete all your countdowns in this guild?",
                components=[components.deleteMine, components.deleteCancel],
                ephemeral=True,
            )

    elif ctx.author.permissions & interactions.Permissions.MANAGE_MESSAGES:
        if sub_command_group == "single":
            if sub_command == "channel":
                cursor = getPossibleCountdowns(ctx, "channel")
                try:
                    msgid = deletechannel.split(": ")[1]
                except:
                    return await ctx.send(
                        "Please use one of the options ", ephemeral=True
                    )
                allowedDelete = False
                for row in cursor:
                    if int(row[0]) == int(msgid):
                        allowedDelete = True
                        pass
                if not allowedDelete:
                    return await ctx.send(
                        "Please use one of the options ", ephemeral=True
                    )
            if sub_command == "guild":
                cursor = getPossibleCountdowns(ctx, "guild")
                try:
                    msgid = deleteguild.split(": ")[1]
                except:
                    return await ctx.send(
                        "Please use one of the options ", ephemeral=True
                    )
                allowedDelete = False
                for row in cursor:
                    if int(row[0]) == int(msgid):
                        allowedDelete = True
                        pass
                if not allowedDelete:
                    return await ctx.send(
                        "Please use one of the options ", ephemeral=True
                    )
            check = connCountdowns.total_changes
            connCountdowns.execute(
                "DELETE from Countdowns WHERE msgid = :msgid;", {"msgid": msgid}
            )
            connCountdowns.commit()

            if check == connCountdowns.total_changes:
                await ctx.send(
                    "An error occurred (could be that there is none to delete)",
                    ephemeral=True,
                )
            else:
                user = ctx.user
                guildid = ctx.guild_id
                channelid = ctx.channel_id
                await ctx.send(f"Countdown [{msgid}](https://discord.com/channels/{guildid}/{channelid}/{msgid} 'Click here to jump to the message') was deleted by {user}")

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

    else:
        await ctx.send(
            "Sorry, you need `MANAGE_MESSAGES` to use this, unless you want to delete your own",
            ephemeral=True,
        )


async def deleteThis(ctx):
    msgid = int(ctx.target.id)
    userid = int(ctx.user.id)
    startedby = 0
    cursor = connCountdowns.execute(
        "SELECT startedby,msgid FROM Countdowns WHERE msgid = :msgid;",
        {"msgid": msgid},
    )
    for row in cursor:
        startedby = int(row[0])
    if startedby == 0:
        return await ctx.send(
            "You can ony use this on active countdowns.",
            ephemeral=True,
        )
    if (
        startedby != userid
        and not ctx.author.permissions & interactions.Permissions.MANAGE_MESSAGES
    ):
        return await ctx.send(
            "Sorry, you need `MANAGE_MESSAGES` to use this, unless you want to delete your own",
            ephemeral=True,
        )
    else:
        check = connCountdowns.total_changes
        connCountdowns.execute(
            "DELETE from Countdowns WHERE msgid = :msgid;", {"msgid": msgid}
        )
        connCountdowns.commit()
        if check == connCountdowns.total_changes:
            return await ctx.send(
                "An error occurred (could be that there is none to delete)",
                ephemeral=True,
            )
        else:
            user = ctx.user
            guildid = ctx.guild_id
            channelid = ctx.channel_id
            return await ctx.send(f"Countdown [{msgid}](https://discord.com/channels/{guildid}/{channelid}/{msgid} 'Click here to jump to the message') was deleted by {user}")


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


def getPossibleCountdowns(ctx, option):
    if option == "mine":
        userid = int(ctx.user.id)
        if ctx.guild_id == None:
            channelid = int(ctx.channel_id)
            cursor = connCountdowns.execute(
                "SELECT msgid FROM Countdowns WHERE startedby = :userid AND channelid = :channelid ORDER BY timestamp ASC;",
                {"userid": userid, "channelid": channelid},
            )
        else:
            guildid = int(ctx.guild_id)
            cursor = connCountdowns.execute(
                "SELECT msgid FROM Countdowns WHERE startedby = :userid AND guildid = :guildid ORDER BY timestamp ASC;",
                {"userid": userid, "guildid": guildid},
            )

    elif option == "channel":
        channelid = int(ctx.channel_id)
        cursor = connCountdowns.execute(
            "SELECT msgid FROM Countdowns WHERE channelid = :channelid ORDER BY timestamp ASC;",
            {"channelid": channelid},
        )
    elif option == "guild":

        if ctx.guild_id == None:
            channelid = int(ctx.channel_id)
            cursor = connCountdowns.execute(
                "SELECT msgid FROM Countdowns WHERE channelid = :channelid ORDER BY timestamp ASC;",
                {"channelid": channelid},
            )
        else:
            guildid = int(ctx.guild_id)
            cursor = connCountdowns.execute(
                "SELECT msgid FROM Countdowns WHERE guildid = :guildid ORDER BY timestamp ASC;",
                {"guildid": guildid},
            )
    return cursor


async def autocompleteCountdowns(ctx, value, option):
    cursor = getPossibleCountdowns(ctx, option)

    await fillChoices(ctx, cursor, value)


def deletedChannel(channel):
    channelid = int(channel.id)
    connCountdowns.execute(
        "DELETE from Countdowns WHERE channelid = :channelid;",
        {"channelid": channelid},
    )
    connCountdowns.commit()


async def deletebutton(ctx, option):
    if option == "guild":
        if ctx.guild_id == None:
            return ctx.send("You cant use this in DMs", ephemeral=True)
        guildid = int(ctx.guild_id)
        check = connCountdowns.total_changes
        connCountdowns.execute(
            "DELETE from Countdowns WHERE guildid = :guildid;", {"guildid": guildid}
        )
        connCountdowns.commit()
        user = ctx.user
        if check == connCountdowns.total_changes:
            await ctx.send(
                "An error occurred (could be that there is none to delete)",
                ephemeral=True,
            )
        else:
            await ctx.edit(components=[])
            await ctx.send(f"Guilds Countdown(s) Deleted by {user}")
    elif option == "channel":
        channelid = int(ctx.channel_id)
        check = connCountdowns.total_changes
        connCountdowns.execute(
            "DELETE from Countdowns WHERE channelid = :channelid;",
            {"channelid": channelid},
        )
        connCountdowns.commit()
        if check == connCountdowns.total_changes:
            await ctx.send(
                "An error occurred (could be that there is none to delete)",
                ephemeral=True,
            )
        else:
            user = ctx.user
            await ctx.edit(components=[])
            await ctx.send(f"Channels Countdown(s) Deleted by {user}")
    elif option == "mine":
        if ctx.guild_id == None:
            return ctx.send("You cant use this in DMs", ephemeral=True)
        guildid = int(ctx.guild_id)
        userid = int(ctx.user.id)
        check = connCountdowns.total_changes
        connCountdowns.execute(
            "DELETE from Countdowns WHERE guildid = :guildid AND startedby = :userid; ",
            {"guildid": guildid, "userid": userid},
        )
        connCountdowns.commit()
        user = ctx.user
        if check == connCountdowns.total_changes:
            await ctx.send(
                "An error occurred (could be that there is none to delete)",
                ephemeral=True,
            )
        else:
            await ctx.edit(components=[])
            await ctx.send(f"All {user} Countdown(s) Deleted")
    elif option == "cancel":
        # Just edit away the buttons and say that contdowns are kept
        await ctx.edit("All countdowns are kept", components=[])


async def timeleft(ctx, sub_command, showmine, showchannel, showguild):

    if sub_command == "mine":
        try:
            msgid = showmine.split(": ")[1]
        except:
            return await ctx.send("Please use one of the options ", ephemeral=True)
    elif sub_command == "channel":
        try:
            msgid = showchannel.split(": ")[1]
        except:
            return await ctx.send("Please use one of the options ", ephemeral=True)
    elif sub_command == "guild":
        try:
            msgid = showguild.split(": ")[1]
        except:
            return await ctx.send("Please use one of the options ", ephemeral=True)

    timestamp = 0

    cursor = connCountdowns.execute(
        "SELECT timestamp,channelid,guildid from Countdowns WHERE msgid = :msgid;",
        {"msgid": msgid},
    )
    for row in cursor:
        timestamp = int(row[0])
        channelid = int(row[1])
        guildid = int(row[2])

    if timestamp == 0:
        return await ctx.send("Please use one of the options ", ephemeral=True)

    currenttime = floor(time.time())
    length = timestamp - currenttime

    timestring = f"Exact time left for countdown [{msgid}](https://discord.com/channels/{guildid}/{channelid}/{msgid} 'Click here to jump to the message'): "
    timestring = getExactTimestring(timestring, length)
    await ctx.send(timestring, ephemeral=True)


async def timeleftThis(ctx):

    msgid = int(ctx.target.id)

    timestamp = 0

    cursor = connCountdowns.execute(
        "SELECT timestamp from Countdowns WHERE msgid = :msgid;", {"msgid": msgid}
    )
    for row in cursor:
        timestamp = int(row[0])

    if timestamp == 0:
        return await ctx.send(
            "Please only use this on active countdowns", ephemeral=True
        )

    currenttime = floor(time.time())
    length = timestamp - currenttime

    timestring = "Exact time left: "
    timestring = getExactTimestring(timestring, length)
    await ctx.send(timestring, ephemeral=True)


async def botstats(ctx, bot):
    await ctx.defer(ephemeral=True)
    cpu = psutil.cpu_percent(4)
    ram = psutil.virtual_memory()[2]
    disk = psutil.disk_usage("/").percent
    cursor = connCountdowns.execute("SELECT COUNT(*) FROM Countdowns;")
    for row in cursor:
        number = int(row[0])

    with open("log.txt", "r") as file:
        for count, line in enumerate(file):
            pass
        logsize = count + 1

    guilds = len(bot.guilds)

    # Check this when activating shards
    ping = round(bot.latency)

    embed = interactions.Embed()
    embed.title = "BOT STATS"
    embed.description = "This is the current status of the bot"
    embed.add_field("CPU :fire:", f"{cpu}%")
    embed.add_field("RAM :floppy_disk:", f"{ram}%")
    embed.add_field("Disk :minidisc:", f"{disk}%")
    embed.add_field("Active countdowns :clock1:", f"{number}")
    embed.add_field("Guilds :timer:", f"{guilds}")
    embed.add_field("Uptime :up:", f"Since <t:{botstarttime}:R>")
    embed.add_field("Ping! :satellite:", f"{ping} ms")
    embed.add_field("Log size :scroll:", f"{logsize} rows")
    embed.color = int(("#%02x%02x%02x" % (255, 132, 140)).replace("#", "0x"), base=16)
    await ctx.send(embeds=embed)


async def translate(ctx, language):
    if ctx.author.permissions & interactions.Permissions.ADMINISTRATOR:
        try:
            await ctx.guild.set_preferred_locale(language)
        except:
            await ctx.send(
                "Sorry, I need to be able to manage guild to use this command",
                ephemeral=True,
            )
        else:
            await ctx.send(f"{ctx.user} translated the bot to {language}")
    else:
        await ctx.send(
            "Sorry, you need to be administrator to use this command", ephemeral=True
        )


async def makethispremium(ctx):
    guildid = ctx.guild_id
    currenttime = floor(time.time())
    allowedtime = currenttime - 86400 * 2
    premiumUsers = []
    cursor = connPremium.execute(
        "SELECT userid FROM Premium WHERE lastedit < :allowedtime;",
        {"allowedtime": allowedtime},
    )
    for row in cursor:
        premiumUsers.append(row[0])

    userid = int(ctx.user.id)
    if userid in premiumUsers:
        check = connPremium.total_changes
        connPremium.execute(
            "UPDATE Premium set guildid = :guildid WHERE userid = :userid;",
            {"userid": userid, "guildid": int(guildid)},
        )
        connPremium.execute(
            "UPDATE Premium set lastedit = :currenttime WHERE userid = :userid;",
            {"userid": userid, "currenttime": int(currenttime)},
        )
        connPremium.commit()

        if check == connPremium.total_changes:
            await ctx.send(
                "An error occurred",
                ephemeral=True,
            )
        else:
            await ctx.send(f"Guild was updated to: {guildid}", ephemeral=True)

    else:
        await ctx.send(
            "Sorry, you need to be a premium user to use this command. Or wait 2 days since you last used it",
            ephemeral=True,
        )


async def premiuminfo(ctx):
    embed = interactions.Embed()
    embed.title = "Premium info"
    embed.description = "To get premium you can head over to [Patreon](https://www.patreon.com/livecountdownbot)"
    embed.add_field(
        "Why premium?",
        "Premium gives you access to:\n• More countdowns in a guild\n• Adding images at the end of a countdown\n• Repeating countdowns",
    )
    embed.add_field(
        "How do I activate it?",
        "Unfortunatly there isnt a good way of doing this yet. For now ping either <@238006908664020993> or <@729791860674920488> after reciving the patreon role in the [Discord Support Guild](https://discord.com/invite/b2fY4z4xBY)",
    )
    embed.add_field(
        "How do I pick what guild?",
        "You can use the command /makethispremium and it will make the guild you use it in to be premium. \n**BEWARE!** There is a cooldown between uses of it.",
    )
    embed.add_field(
        "Can I have premium in multiple guilds?",
        "No. Not yet at least. Currently it is limited to one guild per user.",
    )

    embed.footer = interactions.EmbedFooter(
        text=("Thanks for considering supporting this bot")
    )

    embed.color = int(
        ("#%02x%02x%02x" % (255, 20, 147)).replace("#", "0x"), base=16
    )  # Set the colour to pink
    await ctx.send(embeds=embed, ephemeral=True)


# HERE COME DEVS COMMANDS
devs = [238006908664020993, 360084558265450496, 729791860674920488]


async def log(ctx):
    if int(ctx.user.id) in devs:
        logs = ""
        with open("log.txt", "r") as file:
            for line in file.readlines()[-15:]:
                logs = logs + line

        await ctx.send(f"Logs are:\n```{logs}```", ephemeral=True)

    else:
        await ctx.send(
            "Sorry, you need to be the dev to use this command", ephemeral=True
        )


async def addpremium(ctx, userid, guildid):
    if int(ctx.user.id) in devs:
        premiumUsers = []
        cursor = connPremium.execute("SELECT userid FROM Premium")
        for row in cursor:
            premiumUsers.append(row[0])

        if int(userid) not in premiumUsers:
            connPremium.execute(
                "INSERT INTO Premium (userid,guildid,lastedit) VALUES (:userid,:guildid,0);",
                {
                    "userid": int(userid),
                    "guildid": int(guildid),
                },
            )
            connPremium.commit()
            await ctx.send(f"User <@{userid}> was added", ephemeral=True)
        else:
            await ctx.send(f"User <@{userid}> is alredy premium", ephemeral=True)

    else:
        await ctx.send(
            "Sorry, you need to be the dev to use this command", ephemeral=True
        )


async def deletepremium(ctx, userid):

    if int(ctx.user.id) in devs:
        check = connPremium.total_changes
        connPremium.execute(
            "DELETE from Premium WHERE userid = :userid;",
            {"userid": userid},
        )
        connPremium.commit()

        if check == connPremium.total_changes:
            await ctx.send(
                "An error occurred (could be that there is none to delete)",
                ephemeral=True,
            )
        else:
            await ctx.send(
                f"User <@{userid}> was deleted from premium users", ephemeral=True
            )

    else:
        await ctx.send(
            "Sorry, you need to be the dev to use this command", ephemeral=True
        )


async def listpremium(ctx, page):
    if int(ctx.user.id) in devs:
        cursor = connPremium.execute("SELECT COUNT (*) FROM Premium")
        for row in cursor:
            numberofcountdown = int(row[0])
        cursor = connPremium.execute("SELECT guildid,userid,lastedit FROM Premium")
        lines = 15
        maxpage = ceil(numberofcountdown / lines)
        if maxpage < page:
            page = maxpage

        embed = interactions.Embed()
        embed.title = "Premium users"
        currentLine = 0
        goalLine = page * lines
        # Loops through all premiums to pick out the ones that should be on specified page
        for row in cursor:
            if currentLine >= goalLine - lines:
                guildid = int(row[0])
                userid = int(row[1])
                lastedit = int(row[2])
                embed.add_field(
                    f"-----", f"<@{userid}> have guild {guildid}. Edited <t:{lastedit}>"
                )
            elif currentLine < goalLine - lines:
                pass
            else:
                break
            currentLine = currentLine + 1
            if currentLine >= goalLine:
                break

        embed.footer = interactions.EmbedFooter(text=f"Page {page} of {maxpage}")
        embed.color = int(
            ("#%02x%02x%02x" % (255, 153, 51)).replace("#", "0x"), base=16
        )
        await ctx.send(embeds=embed, ephemeral=True)

    else:
        await ctx.send(
            "Sorry, you need to be the dev to use this command", ephemeral=True
        )


async def checkDone(bot):
    currenttime = int(floor(time.time()))
    cursor = connCountdowns.execute(
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
            connCountdowns.execute(
                "DELETE from Countdowns WHERE msgid = :msgid;",
                {"msgid": msgid},
            )
            connCountdowns.commit()
            return

        # guild = await interactions.get(bot, interactions.Guild, object_id=int(channel.guild.id))
        language = "en-US"  # guild.preferred_locale

        embed = interactions.Embed()

        embed.title = translations[(language)]["done"]

        embed.description = f"{(translations[(language)]['created'])} <@!{startedby}>"

        if imagelink != "":
            embed.set_image(url=imagelink)

        content = f"{messagestart} <t:{timestamp}> {messageend}"
        embed.add_field("Countdown", content)
        embed.color = int(("#%02x%02x%02x" % (0, 255, 0)).replace("#", "0x"), base=16)

        embed.add_field(
            "Original message",
            f"[{msgid}](https://discord.com/channels/{guildid}/{channelid}/{msgid} 'Click here to jump to the message')",
        )

        # If it is repeating, it should decrease the number of times to repeat
        if times != 0:
            timestamp = timestamp + length
            embed.add_field(
                "Reapeating",
                f"This countdown will be repeated {times} time(s) more. Next time is: <t:{timestamp}:R>",
            )
            times = times - 1
            connCountdowns.execute(
                "UPDATE Countdowns set times = :times where msgid = :msgid;",
                {"times": times, "msgid": msgid},
            )
            connCountdowns.execute(
                "UPDATE Countdowns set timestamp = :timestamp where msgid = :msgid;",
                {"timestamp": timestamp, "msgid": msgid},
            )
            connCountdowns.commit()
        # If its not repeating, it should get deleted from the database
        else:
            connCountdowns.execute(
                "DELETE from Countdowns WHERE msgid = :msgid AND channelid = :channelid;",
                {"msgid": msgid, "channelid": channelid},
            )
            connCountdowns.commit()

        if roleid != 0:
            notSent = True
            try:
                guildinfo = await interactions.get(
                    bot, interactions.Guild, object_id=guildid
                )
            except:
                connCountdowns.execute(
                    "DELETE from Countdowns WHERE msgid = :msgid;",
                    {"msgid": msgid},
                )
                connCountdowns.commit()
                return
            else:
                listofid = guildinfo.roles
                for roleids in listofid:
                    if roleid == int(roleids.id):
                        await channel.send(
                            f"{'<@&' + str(roleid) + '>' if roleid != guildid else '@everyone'}",
                            embeds=embed,
                            allowed_mentions={"parse": ["roles", "everyone"]},
                        )
                        notSent = False
                if notSent:
                    await channel.send(f"<@{roleid}>", embeds=embed)
        else:
            await channel.send(embeds=embed)
