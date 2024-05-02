"""
All commands are made in here. For translating there is languageFile.
"""

# ¤ are points of optimasation
# ¤All sql statements can be moved into a seperate file

# Handeling the database
import sqlite3


# To get a random thanks
import random

# Used for rounding down timestamps to whole numbers and to get the max pages needed.
from math import floor, ceil

# Used for... getting time.
import time

# To validate a url
from validators import url as validurl

# To get information about system usage (ram and cpu)
import psutil

# parses the human date to a date that computer understands
import dateparser

# Main library
import interactions

# Here all components are
import components

# Import a list of all translations
from language_file import translations


# makes connCountdowns into the connected database for countdowns.
conn_countdowns_db = sqlite3.connect("Countdowns.db")


# Make the table if there is noe
conn_countdowns_db.execute(
    """CREATE TABLE IF NOT EXISTS Countdowns (timestamp int,msgid int,channelid int,guildid int,roleid int,startedby int,times int,length int,imagelink varchar(255),messagestart varchar(255),messageend varchar(255),messagecompleted varchar(255),number int, countdownname varchar(50));"""
)

# Make the table for presets if there is none
conn_preset_db = sqlite3.connect("Presets.db")
conn_preset_db.execute(
    """CREATE TABLE IF NOT EXISTS Presets (guildid int,roleid int,startedby int,times int,length int,imagelink varchar(255),messagestart varchar(255),messageend varchar(255),messagecompleted varchar(255), countdownname varchar(50),otherchannel int,alert bool,exact bool,presetid int);"""
)


# makes connPremium into the connected database for premium.
conn_premium_db = sqlite3.connect("premiumGuilds.db")
# Make the table if there is noe
conn_premium_db.execute(
    """CREATE TABLE IF NOT EXISTS Premium (guildid int,userid int,lastedit int,level int)"""
)

# To keep track of how long the bot have been up, the starttime is saved.
bot_starttime = floor(time.time())


async def premium_bot(ctx, language):
    """To keep this bot from being added to a ton of servers this makes sure it can only be used in premium servers."""
    ispremiumbot = False
    if ispremiumbot:
        if ctx.guild_id is None:
            await ctx.send(translations[(language)]["errPremiumDm"], ephemeral=True)
            return True
        guild_id = int(ctx.guild_id)

        cursor = conn_premium_db.execute(
            "SELECT guildid FROM Premium WHERE guildid = :guildid;",
            {"guildid": guild_id},
        )

        # This checks if cursor got any rows, if it does, then the guild is premium
        if len(cursor.fetchall()) != 0:
            return False
        # If the code havent returned yet, its not a premium user
        await ctx.send(
            f"""{translations[(language)]["errPremiumBot"]}""", ephemeral=False
        )
        await ctx.guild.leave()
        return True


def get_language(ctx):
    """Check what language the guild is set to. And translates bot to that language if it exsits"""
    language = str(ctx.guild.preferred_locale)
    if language in translations.keys():
        return language
    return "en-US"


async def check_no_premium(ctx, feature, language):
    """Make sure that a feature can only be used by premium users."""
    if ctx.guild_id is None:
        await ctx.send(translations[(language)]["errPremiumDm"], ephemeral=True)
        return True
    guild_id = int(ctx.guild_id)

    cursor = conn_premium_db.execute(
        "SELECT guildid FROM Premium WHERE guildid = :guildid;",
        {"guildid": guild_id},
    )

    # This checks if cursor got any rows, if it does, then the guild is premium
    if len(cursor.fetchall()) != 0:
        return False
    # If the code havent returned yet, its not a premium user
    await ctx.send(
        f"""{translations[(language)]["errPremium"]} {feature}""", ephemeral=True
    )
    return True


async def check_link(ctx, image_link, language):
    """Checks so that the link is valid."""
    if validurl(image_link):
        return False

    # If the code havent returned yet, its not a valid link
    await ctx.send(translations[(language)]["errImage"], ephemeral=True)
    return True


def get_exact_timestring(timestring, length, language):
    """Creates the Exact time from start message. Fills in the time that is left."""
    meassurement = length
    if meassurement >= 86400:
        amount = meassurement // 86400
        meassurement = meassurement - amount * 86400
        timestring = f"""{timestring} {amount} {translations[(language)]["timeDay"]}"""
    if meassurement >= 3600:
        amount = meassurement // 3600
        meassurement = meassurement - amount * 3600
        timestring = f"""{timestring} {amount} {translations[(language)]["timeHour"]}"""
    if meassurement >= 60:
        amount = meassurement // 60
        meassurement = meassurement - amount * 60
        timestring = (
            f"""{timestring} {amount} {translations[(language)]["timeMinute"]}"""
        )
    if meassurement > 0:
        amount = meassurement
        timestring = (
            f"""{timestring} {amount} {translations[(language)]["timeSecond"]}"""
        )
    return timestring


async def send_and_add_to_database(
    timestamp,
    ctx,
    mention,
    times,
    length,
    message_start,
    message_end,
    message_completed,
    countdownname,
    image_link,
    otherchannel,
    exact,
    alert,
    bot,
    language,
    preset,
):
    """
    This makes the countdown message.
    If alert is False it will just send the message about how long time it is left,
    but dont save it to the database.
    """
    # If the bot dont have the permission to view the channel, this try will fail.
    try:
        # It is only required to check if the bot can send messages/embeds if it need to alert
        # otherwise it will just reply to the command, which dont require permission.
        await ctx.defer(ephemeral=False)
        if alert:
            if otherchannel is None:
                channel = ctx.channel
            else:
                channel = bot.get_channel(otherchannel)
            if (
                interactions.Permissions.SEND_MESSAGES
                in channel.permissions_for(ctx.guild.me)
                and interactions.Permissions.EMBED_LINKS
                in channel.permissions_for(ctx.guild.me)
                and interactions.Permissions.VIEW_CHANNEL
                in channel.permissions_for(ctx.guild.me)
            ):
                got_permission = True

            else:
                got_permission = False
        else:
            got_permission = True
    except:
        await ctx.send(
            translations[(language)]["errPerms"],
            ephemeral=True,
        )
    else:
        if got_permission:
            # Message is built and sent
            message_start = message_start.replace("\\n", "\n")
            # Allow for \n to be used as newline charachter
            message_end = message_end.replace("\\n", "\n")
            # To not break delete
            if countdownname is not None:
                countdownname = countdownname.replace(":", ";")
            current_time = floor(time.time())
            time_left = int(timestamp) - int(current_time)
            timestring = ""
            if exact:
                # Since timestamps are exact to the minute the last hour,
                # only use exact if time is longer
                if time_left > 3600:
                    timestring = f"""\n*{translations[(language)]["exact"]} """
                    timestring = (
                        f"{get_exact_timestring(timestring, time_left,language)}*"
                    )
            if otherchannel is None:
                msg = await ctx.send(
                    f"{message_start} <t:{timestamp}:R> {message_end}{timestring}"
                )
            else:
                msg = await channel.send(
                    f"{message_start} <t:{timestamp}:R> {message_end}{timestring}"
                )
                await ctx.send(
                    f"""{translations[(language)]["sent"]} https://discord.com/channels/{ctx.guild_id}/{msg.channel.id}/{msg.id}"""
                )

            guild_id = ctx.guild_id
            if guild_id is None:  # Will be that in DMs.
                guild_id = 0
            started_by = ctx.user.id
            # Had problems with these numbers being "None" for some unknown reason,
            # so added a check so they cant come into the database
            if msg.id is None or msg.channel.id is None:
                return True

            if mention != "0":
                role_id = mention.id
            else:
                role_id = 0

            if preset != 0:
                if otherchannel is None:
                    otherchannelid = 0
                else:
                    otherchannelid = msg.channel.id

                cursor = conn_preset_db.execute(
                    "SELECT presetid FROM Presets WHERE guildid = :guildid AND presetid = :presetid;",
                    {
                        "guildid": int(guild_id),
                        "presetid": int(preset),
                    },
                )

                # This checks if cursor got any rows, if it does, then the guild is premium
                if len(cursor.fetchall()) != 0:
                    conn_preset_db.execute(
                        "UPDATE Presets set roleid = :roleid WHERE guildid = :guildid AND presetid = :presetid;",
                        {
                            "roleid": int(role_id),
                            "guildid": int(guild_id),
                            "presetid": int(preset),
                        },
                    )
                    conn_preset_db.execute(
                        "UPDATE Presets set startedby = :startedby WHERE guildid = :guildid AND presetid = :presetid;",
                        {
                            "startedby": int(started_by),
                            "guildid": int(guild_id),
                            "presetid": int(preset),
                        },
                    )
                    conn_preset_db.execute(
                        "UPDATE Presets set times = :times WHERE guildid = :guildid AND presetid = :presetid;",
                        {
                            "times": int(times),
                            "guildid": int(guild_id),
                            "presetid": int(preset),
                        },
                    )
                    conn_preset_db.execute(
                        "UPDATE Presets set length = :length WHERE guildid = :guildid AND presetid = :presetid;",
                        {
                            "length": int(length),
                            "guildid": int(guild_id),
                            "presetid": int(preset),
                        },
                    )
                    conn_preset_db.execute(
                        "UPDATE Presets set imagelink = :imagelink WHERE guildid = :guildid AND presetid = :presetid;",
                        {
                            "imagelink": str(image_link),
                            "guildid": int(guild_id),
                            "presetid": int(preset),
                        },
                    )
                    conn_preset_db.execute(
                        "UPDATE Presets set messagestart = :messagestart WHERE guildid = :guildid AND presetid = :presetid;",
                        {
                            "messagestart": str(message_start),
                            "guildid": int(guild_id),
                            "presetid": int(preset),
                        },
                    )
                    conn_preset_db.execute(
                        "UPDATE Presets set messageend = :messageend WHERE guildid = :guildid AND presetid = :presetid;",
                        {
                            "messageend": str(message_end),
                            "guildid": int(guild_id),
                            "presetid": int(preset),
                        },
                    )
                    conn_preset_db.execute(
                        "UPDATE Presets set messagecompleted = :messagecompleted WHERE guildid = :guildid AND presetid = :presetid;",
                        {
                            "messagecompleted": str(message_completed),
                            "guildid": int(guild_id),
                            "presetid": int(preset),
                        },
                    )
                    conn_preset_db.execute(
                        "UPDATE Presets set countdownname = :countdownname WHERE guildid = :guildid AND presetid = :presetid;",
                        {
                            "countdownname": str(countdownname),
                            "guildid": int(guild_id),
                            "presetid": int(preset),
                        },
                    )
                    conn_preset_db.execute(
                        "UPDATE Presets set otherchannel = :otherchannel WHERE guildid = :guildid AND presetid = :presetid;",
                        {
                            "otherchannel": int(otherchannelid),
                            "guildid": int(guild_id),
                            "presetid": int(preset),
                        },
                    )
                    conn_preset_db.execute(
                        "UPDATE Presets set alert = :alert WHERE guildid = :guildid AND presetid = :presetid;",
                        {
                            "alert": alert,
                            "guildid": int(guild_id),
                            "presetid": int(preset),
                        },
                    )
                    conn_preset_db.execute(
                        "UPDATE Presets set exact = :exact WHERE guildid = :guildid AND presetid = :presetid;",
                        {
                            "exact": exact,
                            "guildid": int(guild_id),
                            "presetid": int(preset),
                        },
                    )
                    conn_preset_db.commit()
                else:
                    conn_preset_db.execute(
                        "INSERT INTO Presets (guildid,roleid,startedby,times,length,imagelink,messagestart,messageend,messagecompleted,countdownname,otherchannel,alert,exact,presetid) VALUES (:guildid,:roleid,:startedby,:times,:length,:imagelink,:messagestart,:messageend,:messagecompleted,:countdownname,:otherchannel,:alert,:exact,:presetid);",
                        {
                            "guildid": int(guild_id),
                            "roleid": int(role_id),
                            "startedby": int(started_by),
                            "times": int(times),
                            "length": int(length),
                            "imagelink": str(image_link),
                            "messagestart": str(message_start),
                            "messageend": str(message_end),
                            "messagecompleted": str(message_completed),
                            "countdownname": str(countdownname),
                            "otherchannel": int(otherchannelid),
                            "alert": alert,
                            "exact": exact,
                            "presetid": int(preset),
                        },
                    )
                    conn_preset_db.commit()

            # If the bot should notify when countdown is done - save it to database:
            if alert:
                # ¤ Implement number usage
                # Add it into database
                conn_countdowns_db.execute(
                    "INSERT INTO Countdowns (timestamp,msgid,channelid,guildid,roleid,startedby,times,length,imagelink,messagestart,messageend,messagecompleted,number,countdownname) VALUES (:timestamp,:msgid,:channelid,:guildid,:mention,:startedby,:times,:length,:imagelink,:messagestart,:messageend,:messagecompleted,:number,:countdownname);",
                    {
                        "timestamp": int(timestamp),
                        "msgid": int(msg.id),
                        "channelid": int(msg.channel.id),
                        "guildid": int(guild_id),
                        "mention": int(role_id),
                        "startedby": int(started_by),
                        "times": int(times),
                        "length": int(length),
                        "imagelink": str(image_link),
                        "messagestart": str(message_start),
                        "messageend": str(message_end),
                        "messagecompleted": str(message_completed),
                        "number": (int(1)),
                        "countdownname": str(countdownname),
                    },
                )
                conn_countdowns_db.commit()
            return False
        else:
            await ctx.send(
                translations[(language)]["errPerms"],
                ephemeral=True,
            )


async def check_length(ctx, length, language):
    """Check so that a countdown is at least one minute long"""
    if length < 60:
        # I am the dev and want to be able to test timers without wating, ok?
        if int(ctx.user.id) != 238006908664020993:
            await ctx.send(translations[(language)]["errLength"], ephemeral=True)
            return True
    return False


async def check_active(ctx, language):
    """
    Checks so the limit of active countdowns isnt reached
    and that the user have permission to ping
    """
    # This is in DMs, there channelid is used instead of guildid
    if ctx.guild_id is None:
        cursor = conn_countdowns_db.execute(
            "SELECT COUNT(*) FROM Countdowns WHERE channelid=:channelid;",
            {"channelid": int(ctx.channel_id)},
        )
        for row in cursor:
            number_of_countdowns_dm = int(row[0])
        if number_of_countdowns_dm > 4:
            await ctx.send(
                translations[(language)]["maxDm"],
                ephemeral=True,
            )
            return True

    else:
        # In a guild, first grab number of countdowns from the database,
        # then check if limit is reached. ¤Check one then the other
        cursor = conn_countdowns_db.execute(
            "SELECT COUNT(*) FROM Countdowns WHERE guildid= :guildid;",
            {"guildid": int(ctx.guild_id)},
        )
        for row in cursor:
            number_of_countdowns_guild = int(row[0])
        cursor = conn_countdowns_db.execute(
            "SELECT COUNT(*) FROM Countdowns WHERE channelid=:channelid;",
            {"channelid": int(ctx.channel_id)},
        )
        for row in cursor:
            number_of_countdowns_channel = int(row[0])
        # Limits number of active countdowns to 50
        if number_of_countdowns_guild > 49:
            if await check_no_premium(
                ctx,
                translations[(language)]["maxGuild"],
                language,
            ):
                return True
        # limits number of active countdowns to 20
        elif number_of_countdowns_channel > 19:
            if await check_no_premium(
                ctx,
                translations[(language)]["maxChannel"],
                language,
            ):
                return True
        return False


async def check_mention(ctx, mention, language):
    # If you try to ping someone check that you got the permission
    # You can ping yourself or if you got MENTION_EVERYONE, or if its a role that is mentionble.

    if mention != "0" and (
        (not interactions.Permissions.MENTION_EVERYONE in ctx.author.guild_permissions)
        and (not mention.id == ctx.user.id)
    ):
        if hasattr(mention, "mentionable"):
            if not mention.mentionable:
                await ctx.send(translations[(language)]["errMention"], ephemeral=True)
                return True
        # $ This else is used if the bot shouldnt allow users to ping individuals
        # else:
        #    await ctx.send("You dont have permission to ping", ephemeral=True)
        #    return True
    # mention is a thingy, I just want the id of it.
    if mention != "0":
        mention = mention.id
    return False


async def do_all_checks(
    ctx, mention, image_link, times, message_completed, language, preset
):
    """A single function for all checks required before a dountdown/timer starts"""
    if await check_active(ctx, language):
        return False

    if await check_mention(ctx, mention, language):
        return False

    if image_link != "":
        if await check_no_premium(
            ctx, translations[(language)]["errPremiumImage"], language
        ):
            return False
        if await check_link(ctx, image_link, language):
            return False

    if times != 0:
        if await check_no_premium(
            ctx, translations[(language)]["errPremiumRepeat"], language
        ):
            return False

    if message_completed != "":
        if await check_no_premium(
            ctx, translations[(language)]["errPremiumCustomMsg"], language
        ):
            return False

    if preset != 0:
        if await check_no_premium(
            ctx, translations[(language)]["errPremiumPreset"], language
        ):
            return False

    return True


async def delete_message(ctx, msg_id, language):
    """Send the message if a message is deleted"""
    user = ctx.user.username
    guild_id = ctx.guild_id
    channel_id = ctx.channel_id
    await ctx.send(
        f"""{translations[(language)]["countdown"]} [{msg_id}](https://discord.com/channels/{guild_id}/{channel_id}/{msg_id} '{translations[(language)]["jump"]}') {translations[(language)]["wasDeleted"]} {user}"""
    )


async def help_information(ctx):
    """
    The help command.
    This looks different than the rest since it is prepped
    for translation by using the translations file
    """
    language = get_language(ctx)

    # Create a embed and add in all fields to it.
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
    try:  # This try will fail in DM
        # Only show Translate if the user got ADMINISTRATOR Permission
        if ctx.author.permissions & interactions.Permissions.ADMINISTRATOR:
            embed.add_field(
                (translations[(language)]["helpTranslateTitle"]),
                (translations[(language)]["helpTranslateDesc"]),
            )
    except:
        # If they are in DM, dont show it.
        pass
    embed.add_field(
        (translations[(language)]["helpCommonTimeTile"]),
        (translations[(language)]["helpCommonTimeDesc"]),
    )
    embed.add_field(
        (translations[(language)]["helpLinksTitle"]),
        (translations[(language)]["helpLinksDesc"]),
    )

    random_thanks = random.randint(0, 8)

    if random_thanks != 0:
        embed.footer = interactions.EmbedFooter(
            text=(translations[(language)]["helpFooter" + str(random_thanks)])
        )
    else:
        embed.footer = interactions.EmbedFooter(
            text=(
                translations[("universal")]["names"][
                    random.randint(1, len(translations[("universal")]["names"])) - 1
                ]
                + translations[(language)]["helpFooter0"]
            )
        )

    embed.color = int(
        ("#%02x%02x%02x" % (90, 232, 240)).replace("#", "0x"), base=16
    )  # Set the colour to light blue
    await ctx.send(embeds=embed, ephemeral=True)


async def generate_timestamp(ctx, timestring):
    """Generates timestamps in the different formats given a timestring"""
    language = get_language(ctx)
    if await premium_bot(ctx, language):
        return
    wholedate = dateparser.parse("in " + timestring)
    if wholedate is None:
        # If wholedate is None, it is not a valid date. This should be caught in the try... but apparently not
        await ctx.send(
            f"""{translations[(language)]["errDate"]}""",
            ephemeral=True,
        )
        return
    try:  # If wholedate cant be floored, it is not a valid date.
        timestamp = floor(wholedate.timestamp())
    except:
        return await ctx.send(
            f"""{translations[(language)]["errDate"]}""",
            ephemeral=True,
        )
    else:
        embed = interactions.Embed()

        embed.title = translations[(language)]["timestamp"]
        embed.description = translations[(language)]["timestampList"]
        embed.add_field(
            translations[(language)]["timeRemain"],
            f"<t:{timestamp}:R> = `<t:{timestamp}:R>`",
        )
        embed.add_field(
            translations[(language)]["dateTime"], f"<t:{timestamp}> = `<t:{timestamp}>`"
        )
        embed.add_field(
            translations[(language)]["date"], f"<t:{timestamp}:d> = `<t:{timestamp}:d>`"
        )
        embed.add_field(
            translations[(language)]["dateMonth"],
            f"<t:{timestamp}:D> = `<t:{timestamp}:D>`",
        )
        embed.add_field(
            translations[(language)]["time"], f"<t:{timestamp}:t> = `<t:{timestamp}:t>`"
        )
        embed.add_field(
            translations[(language)]["timeWithSecond"],
            f"<t:{timestamp}:T> = `<t:{timestamp}:T>`",
        )
        embed.add_field(
            translations[(language)]["dateTimeWeek"],
            f"<t:{timestamp}:F> = `<t:{timestamp}:F>`",
        )
        await ctx.send(embeds=embed, ephemeral=True)


async def countdown(
    ctx,
    timestring,
    message_start,
    message_end,
    message_completed,
    countdownname,
    mention,
    times,
    repeat_length,
    image_link,
    otherchannel,
    exact,
    alert,
    bot,
):
    """The countdown command. The main use of this bot. Creates a new countdown."""
    language = get_language(ctx)
    if await premium_bot(ctx, language):
        return
    preset = 0
    if await do_all_checks(
        ctx, mention, image_link, times, message_completed, language, preset
    ):
        wholedate = dateparser.parse("in " + timestring)
        try:  # If wholedate cant be floored, it is not a valid date.
            timestamp = floor(wholedate.timestamp())
        except:
            return await ctx.send(
                translations[(language)]["errDate"],
                ephemeral=True,
            )

        current_time = floor(time.time())
        if current_time < timestamp:  # Make sure the time is in the future
            length = timestamp - current_time
            if await check_length(ctx, length, language):
                return
            if times != 0:
                length = repeat_length * 3600
            if otherchannel is not None:
                otherchannel = otherchannel.id
            write_error = await send_and_add_to_database(
                timestamp,
                ctx,
                mention,
                times,
                length,
                message_start,
                message_end,
                message_completed,
                countdownname,
                image_link,
                otherchannel,
                exact,
                alert,
                bot,
                language,
                preset,
            )
            if write_error:
                await ctx.send(translations[(language)]["error"], ephemeral=True)
        else:
            await ctx.send(
                translations[(language)]["errPast"],
                ephemeral=True,
            )


async def preset(ctx, preset, bot):
    """Uses one of the presets"""
    language = get_language(ctx)
    if await premium_bot(ctx, language):
        return
    cursor = conn_preset_db.execute(
        "SELECT roleid,times,length,imagelink,messagestart,messageend,messagecompleted,countdownname,otherchannel,alert,exact FROM Presets WHERE presetid = :preset AND guildid = :guildid;",
        {"guildid": int(ctx.guild_id), "preset": preset},
    )

    # Well... This class is since send_and_add_to_database needs mention.id
    class Mention:
        def __init__(self, id):
            self.id = id

    for row in cursor:
        exact = row[10]
        alert = row[9]
        otherchannel = int(row[8])
        countdownname = str(row[7])
        message_completed = str(row[6])
        message_end = str(row[5])
        message_start = str(row[4])
        image_link = str(row[3])
        length = int(row[2])
        times = int(row[1])
        mention = Mention(int(row[0]))

        current_time = floor(time.time())
        timestamp = current_time + length
        if otherchannel == 0:
            otherchannel = None
        preset = 0
        # no .id on this otherchannel since its alredy an int
        write_error = await send_and_add_to_database(
            timestamp,
            ctx,
            mention,
            times,
            length,
            message_start,
            message_end,
            message_completed,
            countdownname,
            image_link,
            otherchannel,
            exact,
            alert,
            bot,
            language,
            preset,
        )
        if write_error:
            await ctx.send(translations[(language)]["error"], ephemeral=True)


async def list_preset(ctx, page):
    """List all presets"""
    language = get_language(ctx)
    if await premium_bot(ctx, language):
        return
    cursor = conn_preset_db.execute(
        "SELECT COUNT(*) FROM Presets WHERE guildid= :guildid;",
        {"guildid": int(ctx.guild_id)},
    )
    for row in cursor:
        number_of_countdown = int(row[0])

    cursor = conn_preset_db.execute(
        "SELECT roleid,times,length,imagelink,messagestart,messageend,messagecompleted,countdownname,otherchannel,alert,exact,presetid,startedby FROM Presets WHERE guildid = :guildid ORDER BY presetid ASC;",
        {"guildid": int(ctx.guild_id)},
    )
    lines = 5
    max_page = ceil(number_of_countdown / lines)
    if max_page < page:
        page = max_page

    embed = interactions.Embed()
    embed.title = "Presets"
    current_line = 0
    goal_line = page * lines
    # Loops through all presets to pick out the ones that should be on specified page
    for row in cursor:
        if current_line >= goal_line - lines:
            createdby = str(row[12])
            presetid = str(row[11])
            exact = row[10]
            alert = row[9]
            otherchannel = str(row[8])
            countdownname = str(row[7])
            message_completed = str(row[6])
            message_end = str(row[5])
            message_start = str(row[4])
            image_link = str(row[3])
            length = str(row[2])
            times = str(row[1])
            mention = str(row[0])
            # To not write out extra stuff theres an if for each
            # ¤Move to LangFile
            presetstring = f"Creator: <@{createdby}>, Length: {length}(s) "
            if exact:
                presetstring = presetstring + "Exact, "
            if not alert:
                presetstring = presetstring + "No Alert, "
            if times != "0":
                presetstring = presetstring + f"Repeats {times}, "
            if mention != "0":
                presetstring = presetstring + f"Mentions {mention}, "
            if otherchannel != "0":
                presetstring = presetstring + f"Sent to <#{otherchannel}>, "
            if message_start != "Timer will end":
                presetstring = presetstring + f"Starts with '{message_start}', "
            if message_end != "!":
                presetstring = presetstring + f"Ends with '{message_end}', "
            if message_completed != "":
                presetstring = (
                    presetstring + f"Complete message is '{message_completed}', "
                )
            if image_link != "":
                presetstring = presetstring + f"Has image: {image_link}"

            presetstringheader = f"Preset {presetid}"
            if countdownname != "None":
                presetstringheader = presetstringheader + f" | {countdownname}"
            embed.add_field(
                presetstringheader,
                presetstring,
            )
        # If it is before, go to next one
        elif current_line < goal_line - lines:
            pass
        current_line = current_line + 1
        if current_line >= goal_line:
            break

    embed.footer = interactions.EmbedFooter(text=f"Page {page} of {max_page}")
    embed.color = int(("#%02x%02x%02x" % (255, 153, 51)).replace("#", "0x"), base=16)
    await ctx.send(embeds=embed, ephemeral=True)


async def timer(
    ctx,
    day,
    week,
    hour,
    minute,
    message_start,
    message_end,
    message_completed,
    countdownname,
    mention,
    times,
    preset,
    image_link,
    otherchannel,
    exact,
    alert,
    bot,
):
    """For those that dont want to use countdown."""
    language = get_language(ctx)
    if await premium_bot(ctx, language):
        return
    if await do_all_checks(
        ctx, mention, image_link, times, message_completed, language, preset
    ):
        current_time = floor(time.time())
        length = minute * 60 + hour * 3600 + day * 86400 + week * 604800
        if await check_length(ctx, length, language):
            return
        timestamp = current_time + length
        if otherchannel is not None:
            otherchannel = otherchannel.id
        write_error = await send_and_add_to_database(
            timestamp,
            ctx,
            mention,
            times,
            length,
            message_start,
            message_end,
            message_completed,
            countdownname,
            image_link,
            otherchannel,
            exact,
            alert,
            bot,
            language,
            preset,
        )
        if write_error:
            await ctx.send(translations[(language)]["error"], ephemeral=True)


async def list_countdowns(ctx, sub_command, page, hidden):
    """List command. List all active countdowns based on sub command."""
    language = get_language(ctx)
    if await premium_bot(ctx, language):
        return
    if ctx.guild_id is None and sub_command != "channel":
        return await ctx.send(translations[(language)]["errListDm"], ephemeral=True)
    # Links for DMs are @me instead of the guildid
    if ctx.guild_id is None:
        guild_id = "@me"
    else:
        guild_id = int(ctx.guild_id)
    channel_id = int(ctx.channel_id)

    if sub_command == "channel":
        place = f"""{translations[(language)]["place"]} {translations[(language)]["channel"]}"""
        cursor = conn_countdowns_db.execute(
            "SELECT COUNT (*) FROM Countdowns WHERE channelid = :channelid;",
            {"channelid": channel_id},
        )

        for row in cursor:
            number_of_countdowns = int(row[0])
        cursor = conn_countdowns_db.execute(
            "SELECT timestamp,msgid,channelid,startedby,countdownname FROM Countdowns WHERE channelid = :channelid ORDER BY timestamp ASC;",
            {"channelid": channel_id},
        )

    elif sub_command == "guild":
        place = f"""{translations[(language)]["place"]} {translations[(language)]["guild"]}"""
        cursor = conn_countdowns_db.execute(
            "SELECT COUNT (*) FROM Countdowns WHERE guildid = :guildid;",
            {"guildid": guild_id},
        )
        for row in cursor:
            number_of_countdowns = int(row[0])
        cursor = conn_countdowns_db.execute(
            "SELECT timestamp,msgid,channelid,startedby,countdownname FROM Countdowns WHERE guildid = :guildid ORDER BY timestamp ASC;",
            {"guildid": guild_id},
        )

    elif sub_command == "mine":
        place = translations[(language)]["placeUser"]
        user_id = int(ctx.user.id)
        cursor = conn_countdowns_db.execute(
            "SELECT COUNT (*) FROM Countdowns WHERE guildid = :guildid AND startedby = :userid;",
            {"guildid": guild_id, "userid": user_id},
        )
        for row in cursor:
            number_of_countdowns = int(row[0])
        cursor = conn_countdowns_db.execute(
            "SELECT timestamp,msgid,channelid,startedby,countdownname FROM Countdowns WHERE guildid = :guildid AND startedby = :userid ORDER BY timestamp ASC;",
            {"guildid": guild_id, "userid": user_id},
        )

    # since there are 5 countdowns per page
    max_page = ceil(number_of_countdowns / 5)

    # If requested is higher just make it to the max
    if max_page < page:
        page = max_page

    embed = interactions.Embed()
    embed.title = translations[(language)]["activeTitle"]
    embed.description = f"""{translations[(language)]["activeDesc"]} {place}"""

    current_line = 0
    goal_line = page * 5

    # Loops through all active countowns in the correct place
    # to pick out the ones that should be on specified page
    for row in cursor:
        if current_line >= goal_line - 5:
            timestamp = int(row[0])
            msg_id = int(row[1])
            channel_id = int(row[2])
            started_by = int(row[3])
            countdownname = str(row[4])
            if countdownname == "None":
                embed.add_field(
                    f"{current_line}: <t:{timestamp}:R>",
                    f"""[{msg_id}](https://discord.com/channels/{guild_id}/{channel_id}/{msg_id} '{translations[(language)]["jump"]}') {translations[(language)]["created"]} <@!{started_by}>\n""",
                )
            else:
                embed.add_field(
                    f"{countdownname}: <t:{timestamp}:R>",
                    f"""[{msg_id}](https://discord.com/channels/{guild_id}/{channel_id}/{msg_id} '{translations[(language)]["jump"]}') {translations[(language)]["created"]} <@!{started_by}>\n""",
                )
        elif current_line < goal_line - 5:
            pass
        else:
            break
        current_line = current_line + 1
        if current_line >= goal_line:
            break

    embed.footer = interactions.EmbedFooter(text=f"Page {page} of {max_page}")
    embed.color = int(("#%02x%02x%02x" % (255, 153, 51)).replace("#", "0x"), base=16)
    if hidden:
        await ctx.send(embeds=embed, ephemeral=True)
    else:
        await ctx.send(embeds=embed, ephemeral=False)


async def delete(bot, ctx, sub_command, sub_command_group, delete_id):
    """Deletes a countdown based on subcommand."""
    language = get_language(ctx)
    if await premium_bot(ctx, language):
        return
    # ¤ Make a function that can fit all of these
    if sub_command == "mine":
        if sub_command_group == "single":
            cursor = get_possible_countdowns(ctx, "mine")
            try:
                msg_id = delete_id.split(": ")[1]
            except:
                return await ctx.send(
                    translations[(language)]["errOption"], ephemeral=True
                )
            allowed_delete = False
            for row in cursor:
                if int(row[0]) == int(msg_id):
                    allowed_delete = True
                    pass
            if not allowed_delete:
                return await ctx.send(
                    translations[(language)]["errOption"], ephemeral=True
                )

            check = conn_countdowns_db.total_changes
            conn_countdowns_db.execute(
                "DELETE from Countdowns WHERE msgid = :msgid;", {"msgid": msg_id}
            )
            conn_countdowns_db.commit()
            if check == conn_countdowns_db.total_changes:
                await ctx.send(
                    translations[(language)]["errDelete"],
                    ephemeral=True,
                )
            else:
                await delete_message(ctx, msg_id, language)
        else:
            await ctx.send(
                translations[(language)]["deleteConfirmMine"],
                components=[components.delete_mine, components.delete_cancel],
                ephemeral=True,
            )

    else:
        if sub_command_group == "single":
            if sub_command == "channel":
                cursor = get_possible_countdowns(ctx, "channel")
                try:
                    msg_id = delete_id.split(": ")[1]
                except:
                    return await ctx.send(
                        translations[(language)]["errOption"], ephemeral=True
                    )
                allowed_delete = False
                for row in cursor:
                    if int(row[0]) == int(msg_id):
                        allowed_delete = True
                        pass
                if not allowed_delete:
                    return await ctx.send(
                        translations[(language)]["errOption"], ephemeral=True
                    )
            if sub_command == "guild":
                cursor = get_possible_countdowns(ctx, "guild")
                try:
                    msg_id = delete_id.split(": ")[1]
                except:
                    return await ctx.send(
                        translations[(language)]["errOption"], ephemeral=True
                    )
                allowed_delete = False
                for row in cursor:
                    if int(row[0]) == int(msg_id):
                        allowed_delete = True
                        pass
                if not allowed_delete:
                    return await ctx.send(
                        translations[(language)]["errOption"], ephemeral=True
                    )
            check = conn_countdowns_db.total_changes
            conn_countdowns_db.execute(
                "DELETE from Countdowns WHERE msgid = :msgid;", {"msgid": msg_id}
            )
            conn_countdowns_db.commit()

            if check == conn_countdowns_db.total_changes:
                await ctx.send(
                    translations[(language)]["errDelete"],
                    ephemeral=True,
                )
            else:
                await delete_message(ctx, msg_id, language)

        else:
            if sub_command == "channel":
                await ctx.send(
                    translations[(language)]["deleteConfirmChannel"],
                    components=[components.delete_channel, components.delete_cancel],
                    ephemeral=True,
                )
            elif sub_command == "guild":
                await ctx.send(
                    translations[(language)]["deleteConfirmGuild"],
                    components=[components.delete_guild, components.delete_cancel],
                    ephemeral=True,
                )


async def delete_this(bot, ctx):
    """App command for deleting. Use on a active countdown message and it will be deleted."""
    msg_id = int(ctx.target.id)
    user_id = int(ctx.user.id)
    language = get_language(ctx)
    started_by = 0
    cursor = conn_countdowns_db.execute(
        "SELECT startedby,msgid FROM Countdowns WHERE msgid = :msgid;",
        {"msgid": msg_id},
    )
    for row in cursor:
        started_by = int(row[0])
    # If there was no entry in the database
    # it is not an active countdown.
    if started_by == 0:
        return await ctx.send(
            translations[(language)]["errNoActive"],
            ephemeral=True,
        )

    check = conn_countdowns_db.total_changes
    conn_countdowns_db.execute(
        "DELETE from Countdowns WHERE msgid = :msgid;", {"msgid": msg_id}
    )
    conn_countdowns_db.commit()
    if check == conn_countdowns_db.total_changes:
        return await ctx.send(
            translations[(language)]["errDelete"],
            ephemeral=True,
        )

    await delete_message(ctx, msg_id, language)


async def fill_choices(ctx, cursor, value):
    """
    This function is used for the autocompletion of what
    active countdowns there is to delete in all categories.
    How it really works? Good question...
    """
    countdowns = []
    countdown_id = 0
    for row in cursor:
        countdownname = str(row[1])
        # Need to be limited due to discord not allowing more than 25 options
        if countdown_id < 24:
            if countdownname == "None":
                countdowns.append(str(countdown_id) + ": " + str(row[0]))
            else:
                countdowns.append(countdownname + ": " + str(row[0]))
            countdown_id += 1
        else:
            break

    choices = [dict(name=item, value=item) for item in countdowns if value in item]
    await ctx.send(choices)


def get_possible_countdowns(ctx, option):
    """Generates a cursor for the option picked with all active countdowns in it."""
    if option == "mine":
        user_id = int(ctx.user.id)
        if ctx.guild_id is None:
            channel_id = int(ctx.channel_id)
            cursor = conn_countdowns_db.execute(
                "SELECT msgid,countdownname FROM Countdowns WHERE startedby = :userid AND channelid = :channelid ORDER BY timestamp ASC;",
                {"userid": user_id, "channelid": channel_id},
            )
        else:
            guild_id = int(ctx.guild_id)
            cursor = conn_countdowns_db.execute(
                "SELECT msgid,countdownname FROM Countdowns WHERE startedby = :userid AND guildid = :guildid ORDER BY timestamp ASC;",
                {"userid": user_id, "guildid": guild_id},
            )

    elif option == "channel":
        channel_id = int(ctx.channel_id)
        cursor = conn_countdowns_db.execute(
            "SELECT msgid,countdownname FROM Countdowns WHERE channelid = :channelid ORDER BY timestamp ASC;",
            {"channelid": channel_id},
        )
    elif option == "guild":
        # The guild_id can be None if it is used in DMs
        if ctx.guild_id is None:
            channel_id = int(ctx.channel_id)
            cursor = conn_countdowns_db.execute(
                "SELECT msgid,countdownname FROM Countdowns WHERE channelid = :channelid ORDER BY timestamp ASC;",
                {"channelid": channel_id},
            )
        else:
            guild_id = int(ctx.guild_id)
            cursor = conn_countdowns_db.execute(
                "SELECT msgid,countdownname FROM Countdowns WHERE guildid = :guildid ORDER BY timestamp ASC;",
                {"guildid": guild_id},
            )
    return cursor


async def autocomplete_countdowns(ctx, value, option):
    """Fills the options when using timeleft or delete commands"""
    cursor = get_possible_countdowns(ctx, option)
    await fill_choices(ctx, cursor, value)


def deleted_channel(channel):
    """Delete countdowns from database if the channel they were in get deleted."""
    # No need to edit the messages, since the channel is gone.
    channel_id = int(channel.id)
    conn_countdowns_db.execute(
        "DELETE from Countdowns WHERE channelid = :channelid;",
        {"channelid": channel_id},
    )
    conn_countdowns_db.commit()


async def delete_button(ctx, option):
    """If a button used for deleting is used."""
    language = get_language(ctx)
    user = ctx.user.username
    match option:
        case "guild":
            if ctx.guild_id is None:
                return ctx.send(translations[(language)]["errDm"], ephemeral=True)
            guild_id = int(ctx.guild_id)
            cursor = conn_countdowns_db.execute(
                "SELECT channelid,msgid from Countdowns WHERE guildid = :guildid;",
                {"guildid": guild_id},
            )
            for row in cursor:
                channel_id = str(row[0])

            check = conn_countdowns_db.total_changes
            conn_countdowns_db.execute(
                "DELETE from Countdowns WHERE guildid = :guildid;",
                {"guildid": guild_id},
            )
            conn_countdowns_db.commit()

            if check == conn_countdowns_db.total_changes:
                await ctx.send(
                    translations[(language)]["errDelete"],
                    ephemeral=True,
                )
            else:
                await ctx.send(
                    f"""{translations[(language)]["guild"]} {translations[(language)]["countdown"]}{translations[(language)]["multiple"]} {translations[(language)]["wasDeleted"]} {user}"""
                )
        case "channel":
            channel_id = int(ctx.channel_id)
            cursor = conn_countdowns_db.execute(
                "SELECT msgid from Countdowns WHERE channelid = :channelid;",
                {"channelid": channel_id},
            )
            for row in cursor:
                msg_id = str(row[0])
            check = conn_countdowns_db.total_changes
            conn_countdowns_db.execute(
                "DELETE from Countdowns WHERE channelid = :channelid;",
                {"channelid": channel_id},
            )
            conn_countdowns_db.commit()
            if check == conn_countdowns_db.total_changes:
                await ctx.send(
                    translations[(language)]["errDelete"],
                    ephemeral=True,
                )
            else:
                await ctx.send(
                    f"""{translations[(language)]["channel"]} {translations[(language)]["countdown"]}{translations[(language)]["multiple"]} {translations[(language)]["wasDeleted"]} {user}"""
                )
        case "mine":
            if ctx.guild_id is None:
                return ctx.send(translations[(language)]["errDm"], ephemeral=True)
            guild_id = int(ctx.guild_id)
            user_id = int(ctx.user.id)
            cursor = conn_countdowns_db.execute(
                "SELECT channelid,msgid from Countdowns WHERE guildid = :guildid AND startedby = :userid;",
                {"guildid": guild_id, "userid": user_id},
            )
            for row in cursor:
                channel_id = str(row[0])
                msg_id = str(row[1])

            check = conn_countdowns_db.total_changes
            conn_countdowns_db.execute(
                "DELETE from Countdowns WHERE guildid = :guildid AND startedby = :userid; ",
                {"guildid": guild_id, "userid": user_id},
            )
            conn_countdowns_db.commit()
            if check == conn_countdowns_db.total_changes:
                await ctx.send(
                    translations[(language)]["errDelete"],
                    ephemeral=True,
                )
            else:
                # Send a message announcing.
                await ctx.send(
                    f"""{user} {translations[(language)]["countdown"]}{translations[(language)]["multiple"]} {translations[(language)]["deleted"]}"""
                )
        case "cancel":
            # Just edit away the buttons and say that contdowns are kept
            await ctx.edit_origin(
                content=translations[(language)]["kept"], components=[]
            )


async def time_left_message(ctx, msg_id, language, hidden):
    """Send the message for time left"""
    timestamp = 0
    cursor = conn_countdowns_db.execute(
        "SELECT timestamp,channelid,guildid,countdownname from Countdowns WHERE msgid = :msgid;",
        {"msgid": msg_id},
    )
    for row in cursor:
        timestamp = int(row[0])
        channel_id = int(row[1])
        guild_id = int(row[2])
        countdownname = str(row[3])

    if timestamp == 0:
        return await ctx.send(translations[(language)]["errNotFound"], ephemeral=True)

    current_time = floor(time.time())
    length = timestamp - current_time
    if countdownname == "None":
        timestring = f"""{translations[(language)]["exactLeft"]} [{msg_id}](https://discord.com/channels/{guild_id}/{channel_id}/{msg_id} '{translations[(language)]["jump"]}'): """
    else:
        timestring = f"""{translations[(language)]["exactLeft"]} [{countdownname}](https://discord.com/channels/{guild_id}/{channel_id}/{msg_id} '{translations[(language)]["jump"]}'): """
    timestring = get_exact_timestring(timestring, length, language)
    await ctx.send(timestring, ephemeral=hidden)


async def time_left(ctx, show, hidden):
    """Show how long time it is left for a countdown"""
    language = get_language(ctx)
    if await premium_bot(ctx, language):
        return

    try:
        msg_id = show.split(": ")[1]
    except:
        return await ctx.send(translations[(language)]["errOption"], ephemeral=True)

    await time_left_message(ctx, msg_id, language, hidden)


async def timeleft_this(ctx):
    """App command for timeleft."""
    language = get_language(ctx)
    msg_id = int(ctx.target.id)
    await time_left_message(ctx, msg_id, language, True)


async def botstats(ctx, bot):
    """Botstat command. Gathers a bunch of information about the bot."""
    language = get_language(ctx)
    if await premium_bot(ctx, language):
        return
    await ctx.defer(ephemeral=True)
    cpu = psutil.cpu_percent(4)
    ram = psutil.virtual_memory()[2]
    disk = psutil.disk_usage("/").percent
    guilds = len(bot.guilds)
    shards = ctx.client.total_shards
    # Get the number of active countdowns
    cursor = conn_countdowns_db.execute("SELECT COUNT(*) FROM Countdowns;")
    for row in cursor:
        number = int(row[0])

    # Get size of log file
    with open("log.txt", "r") as file:
        logsize = len(file.readlines())

    # Check this when activating shards - might break
    # (not that it alredy isnt)
    ping = round(bot.latency)

    embed = interactions.Embed()
    embed.title = translations[(language)]["botstatTitle"]
    embed.description = translations[(language)]["botstatDesc"]
    embed.add_field(f"""{translations[(language)]["CPU"]} :fire:""", f"{cpu}%")
    embed.add_field(f"""{translations[(language)]["RAM"]} :floppy_disk:""", f"{ram}%")
    embed.add_field(f"""{translations[(language)]["storage"]} :minidisc:""", f"{disk}%")
    embed.add_field(f"""{translations[(language)]["active"]} :clock1:""", f"{number}")
    embed.add_field(f"""{translations[(language)]["guild"]} :timer:""", f"{guilds}")
    embed.add_field(f"""{translations[(language)]["shards"]} :jigsaw:""", f"{shards}")
    embed.add_field(
        f"""{translations[(language)]["uptime"]} :up:""", f"<t:{bot_starttime}:R>"
    )
    embed.add_field(
        f"""{translations[(language)]["ping"]} :satellite:""",
        f"""{ping} {translations[(language)]["ms"]}""",
    )
    embed.add_field(
        f"""{translations[(language)]["log"]} :scroll:""",
        f"""{logsize} {translations[(language)]["rows"]}""",
    )
    embed.color = int(("#%02x%02x%02x" % (255, 132, 140)).replace("#", "0x"), base=16)
    await ctx.send(embeds=embed)


async def edit_mention(ctx, countdownid, mention):
    """For editing a mention of a running countdown"""
    language = get_language(ctx)
    if await premium_bot(ctx, language):
        return
    if await check_mention(ctx, mention, language):
        return False

    if mention != "0":
        role_id = mention.id
    else:
        role_id = 0

    cursor = get_possible_countdowns(ctx, "mine")
    try:
        msg_id = countdownid.split(": ")[1]
    except:
        return await ctx.send(translations[(language)]["errOption"], ephemeral=True)
    allowed_delete = False
    for row in cursor:
        if int(row[0]) == int(msg_id):
            allowed_delete = True
            pass
    if not allowed_delete:
        return await ctx.send(translations[(language)]["errOption"], ephemeral=True)

    conn_countdowns_db.execute(
        "UPDATE Countdowns set roleid = :roleid where msgid = :msgid;",
        {"msgid": msg_id, "roleid": int(role_id)},
    )

    await ctx.send(translations[(language)]["editMention"], ephemeral=True)


async def translate(ctx, new_language):
    """Allows for tranlsating the bot to another language."""
    language = get_language(ctx)
    if await premium_bot(ctx, language):
        return
    if ctx.author.permissions & interactions.Permissions.ADMINISTRATOR:
        try:
            await ctx.guild.set_preferred_locale(new_language)
        except:
            await ctx.send(
                translations[(language)]["errManageGuild"],
                ephemeral=True,
            )
        else:
            await ctx.send(
                f"""{ctx.user.username} {translations[(new_language)]["translated"]} {new_language}"""
            )
    else:
        await ctx.send(translations[(language)]["errNoAdmin"], ephemeral=True)


async def make_this_premium(ctx, index):
    """Change the premium guild to the one where the command is used. Cooldown of 2 days."""
    language = get_language(ctx)
    guild_id = ctx.guild_id
    current_time = floor(time.time())
    # 172800 seconds is two days.
    allowed_time = current_time - 172800
    user_id = int(ctx.user.id)
    # Find those that are from the user
    # that havent been recently edited.
    cursor = conn_premium_db.execute(
        "SELECT level,lastedit FROM Premium WHERE userid = :userid AND level = :index;",
        {"userid": user_id, "index": index},
    )
    maxlevel = 0
    for row in cursor:
        lastedit = int(row[1])
        maxlevel = int(row[0])
        break

    # If there is 0 results there is no to edit.
    if maxlevel != 0:
        if lastedit < allowed_time:
            check = conn_premium_db.total_changes
            conn_premium_db.execute(
                "UPDATE Premium set guildid = :guildid WHERE userid = :userid AND level = :index;",
                {"userid": user_id, "guildid": int(guild_id), "index": index},
            )
            conn_premium_db.execute(
                "UPDATE Premium set lastedit = :currenttime WHERE userid = :userid AND level = :index;",
                {"userid": user_id, "currenttime": int(current_time), "index": index},
            )
            conn_premium_db.commit()

            if check == conn_premium_db.total_changes:
                await ctx.send(
                    translations[(language)]["error"],
                    ephemeral=True,
                )
                return
            else:
                await ctx.send(
                    f"""{translations[(language)]["guild"]} {translations[(language)]["updated"]} {guild_id}""",
                    ephemeral=True,
                )
                return

    else:
        # Check if user got a higher level
        cursor = conn_premium_db.execute(
            "SELECT level,lastedit FROM Premium WHERE userid = :userid ORDER BY level DESC;",
            {"userid": user_id},
        )
        for row in cursor:
            lastedit = int(row[1])
            maxlevel = int(row[0])
            break
        if maxlevel > index:
            if lastedit < allowed_time:
                check = conn_premium_db.total_changes
                conn_premium_db.execute(
                    "INSERT INTO Premium (userid,guildid,lastedit,level) VALUES (:userid,:guildid,:lastedit,:level);",
                    {
                        "userid": int(user_id),
                        "guildid": int(guild_id),
                        "lastedit": int(current_time),
                        "level": int(index),
                    },
                )
                conn_premium_db.commit()

                if check == conn_premium_db.total_changes:
                    await ctx.send(
                        translations[(language)]["error"],
                        ephemeral=True,
                    )
                else:
                    await ctx.send(
                        f"""{translations[(language)]["guild"]} {translations[(language)]["updated"]} {guild_id}""",
                        ephemeral=True,
                    )
                return
    await ctx.send(
        translations[(language)]["errPremiumReuse"],
        ephemeral=True,
    )


async def premium_info(ctx):
    """Sends some info about premium."""
    language = get_language(ctx)
    embed = interactions.Embed()
    embed.title = translations[(language)]["premiumTitle"]
    embed.description = translations[(language)]["premiumDesc"]
    embed.add_field(
        translations[(language)]["premiumWhyTitle"],
        translations[(language)]["premiumWhyDesc"],
    )
    embed.add_field(
        translations[(language)]["premiumActivateTitle"],
        translations[(language)]["premiumActivateDesc"],
    )
    embed.add_field(
        translations[(language)]["premiumPickTitle"],
        translations[(language)]["premiumPickDesc"],
    )
    embed.add_field(
        translations[(language)]["premiumMultipleTitle"],
        translations[(language)]["premiumMultipleDesc"],
    )

    embed.footer = interactions.EmbedFooter(
        text=(translations[(language)]["premiumFooter"])
    )
    embed.color = int(("#%02x%02x%02x" % (255, 20, 147)).replace("#", "0x"), base=16)
    await ctx.send(embeds=embed, ephemeral=True)


async def fixperms(ctx, bot):
    """Adds the permissions of the bot to the channel"""
    language = get_language(ctx)
    if await premium_bot(ctx, language):
        return
    channel = ctx.channel

    try:
        await channel.set_permission(
            target=bot._user, view_channel=True, embed_links=True, send_messages=True
        )
    except:
        await ctx.send(translations[(language)]["permsNotFixed"])
    else:
        await ctx.send(translations[(language)]["permsFixed"])


# HERE COME DEVS COMMANDS
devs = (238006908664020993, 729791860674920488)


async def log(ctx):
    """Shows the log"""
    language = get_language(ctx)
    if await premium_bot(ctx, language):
        return
    if int(ctx.user.id) in devs:
        logs = ""
        with open("log.txt", "r") as file:
            # Read the last lines in the log file
            for line in file.readlines()[::-1]:
                if len(line + logs) > 1900:
                    break
                else:
                    logs = line + logs

        await ctx.send(f"Logs are:\n```{logs}```", ephemeral=True)

    else:
        await ctx.send(translations[(language)]["errDev"], ephemeral=True)


async def add_premium(ctx, user_id, guild_id, level):
    """Add a premium user."""
    language = get_language(ctx)
    if await premium_bot(ctx, language):
        return
    if int(ctx.user.id) in devs:
        cursor = conn_premium_db.execute(
            "SELECT userid FROM Premium WHERE userid = :userid AND level <= :level;",
            {
                "userid": int(user_id),
                "level": int(level),
            },
        )
        currlevel = len(cursor.fetchall())
        # Check that the user isnt alredy there
        if currlevel < int(level):
            for i in range(currlevel + 1, int(level) + 1):
                conn_premium_db.execute(
                    "INSERT INTO Premium (userid,guildid,lastedit,level) VALUES (:userid,:guildid,0,:level);",
                    {
                        "userid": int(user_id),
                        "guildid": int(guild_id),
                        "level": (i),
                    },
                )
            conn_premium_db.commit()
            await ctx.send(f"User <@{user_id}> was added", ephemeral=True)
        else:
            await ctx.send(f"User <@{user_id}> is alredy premium", ephemeral=True)
    else:
        await ctx.send(translations[(language)]["errDev"], ephemeral=True)


async def remove_premium(ctx, user_id, level):
    """Removes a premium user."""
    language = get_language(ctx)
    if await premium_bot(ctx, language):
        return
    if int(ctx.user.id) in devs:
        check = conn_premium_db.total_changes
        conn_premium_db.execute(
            "DELETE from Premium WHERE userid = :userid AND level > :level;",
            {"userid": user_id, "level": level},
        )
        conn_premium_db.commit()

        if check == conn_premium_db.total_changes:
            await ctx.send(
                translations[(language)]["errDelete"],
                ephemeral=True,
            )
        else:
            await ctx.send(
                f"User <@{user_id}> was deleted from premium users", ephemeral=True
            )

    else:
        await ctx.send(translations[(language)]["errDev"], ephemeral=True)


async def list_premium(ctx, page):
    """List all premium users."""
    language = get_language(ctx)
    if await premium_bot(ctx, language):
        return
    if int(ctx.user.id) in devs:
        cursor = conn_premium_db.execute("SELECT COUNT (*) FROM Premium")
        for row in cursor:
            number_of_countdown = int(row[0])
        cursor = conn_premium_db.execute(
            "SELECT guildid,userid,lastedit,level FROM Premium ORDER BY userid,level"
        )
        lines = 25
        max_page = ceil(number_of_countdown / lines)
        if max_page < page:
            page = max_page

        current_line = 0
        goal_line = page * lines
        resultstring = ""
        # Loops through all premiums to pick out the ones that should be on specified page
        for row in cursor:
            if current_line >= goal_line - lines:
                guild_id = int(row[0])
                user_id = int(row[1])
                last_edit = int(row[2])
                level = int(row[3])
                resultstring = (
                    resultstring
                    + f"<@{user_id}> {level} - {guild_id} <t:{last_edit}>\n"
                )
            # If it is before, go to next one
            elif current_line < goal_line - lines:
                pass
            current_line = current_line + 1
            if current_line >= goal_line:
                break

        resultstring = resultstring + f"\nPage {page} of {max_page}"
        await ctx.send(resultstring, ephemeral=True)

    else:
        await ctx.send(translations[(language)]["errDev"], ephemeral=True)


async def check_done(bot):
    """Checks if a countdown is done. If it is, send the countdown completed message."""
    current_time = int(floor(time.time()))
    cursor = conn_countdowns_db.execute(
        "SELECT timestamp,msgid,channelid,guildid,roleid,startedby,times,length,imagelink,messagestart,messageend,messagecompleted,number,countdownname FROM Countdowns WHERE timestamp < :currenttime;",
        {"currenttime": current_time},
    )
    # There will 0 rows in cursor if theres no countdowns that are done.
    # Therefore this wont run multiple times.
    for row in cursor:
        countdown_name = str(row[13])
        number = str(row[12])
        message_completed = str(row[11])
        message_end = str(row[10])
        message_start = str(row[9])
        image_link = str(row[8])
        length = int(row[7])
        times = int(row[6])
        started_by = int(row[5])
        role_id = int(row[4])
        guild_id = int(row[3])
        channel_id = int(row[2])
        msg_id = int(row[1])
        timestamp = int(row[0])
        try:
            # Check that the channel exsist
            channel = await bot.fetch_channel(channel_id)
            # Check that the bot have permission to
            # send message, embeds and see the channel.
            got_permission = False
            if (
                interactions.Permissions.SEND_MESSAGES
                in channel.permissions_for(bot._user.id)
                and interactions.Permissions.EMBED_LINKS
                in channel.permissions_for(bot._user.id)
                and interactions.Permissions.VIEW_CHANNEL
                in channel.permissions_for(bot._user.id)
            ):
                got_permission = True
        except:
            conn_countdowns_db.execute(
                "DELETE from Countdowns WHERE msgid = :msgid;",
                {"msgid": msg_id},
            )
            conn_countdowns_db.commit()
            return
        else:
            if not got_permission:
                conn_countdowns_db.execute(
                    "DELETE from Countdowns WHERE msgid = :msgid AND number = :number;",
                    {"msgid": msg_id, "number": number},
                )
                conn_countdowns_db.commit()
                return

        language = bot.get_guild(guild_id).preferred_locale
        if language not in translations.keys():
            language = "en-US"

        embed = interactions.Embed()
        embedtitle = translations[(language)]["done"]
        if countdown_name == "None":
            embed.title = embedtitle
        else:
            embed.title = f"{embedtitle} - {countdown_name}"
        embed.description = f"{(translations[(language)]['created'])} <@!{started_by}>"

        if image_link != "":
            embed.set_image(url=image_link)

        embed.add_field(
            translations[(language)]["countdown"],
            f"{message_start} <t:{timestamp}> {message_end}",
        )
        if message_completed != "":
            embed.add_field(translations[(language)]["message"], f"{message_completed}")

        embed.color = int(("#%02x%02x%02x" % (0, 255, 0)).replace("#", "0x"), base=16)

        embed.add_field(
            translations[(language)]["original"],
            f"""[{msg_id}](https://discord.com/channels/{guild_id}/{channel_id}/{msg_id} '{translations[(language)]["jump"]}')""",
        )

        # If it is repeating, it should decrease the number of times to repeat
        if times != 0:
            timestamp = timestamp + length
            embed.add_field(
                translations[(language)]["repeat"],
                f"""{translations[(language)]["repeatStart"]} {times} {translations[(language)]["repeatEnd"]}: <t:{timestamp}:R>""",
            )
            times = times - 1
            conn_countdowns_db.execute(
                "UPDATE Countdowns set times = :times where msgid = :msgid AND number = :number;",
                {"times": times, "msgid": msg_id, "number": number},
            )
            conn_countdowns_db.execute(
                "UPDATE Countdowns set timestamp = :timestamp where msgid = :msgid AND number = :number;",
                {"timestamp": timestamp, "msgid": msg_id, "number": number},
            )
            conn_countdowns_db.commit()
        # If its not repeating, it should get deleted from the database
        else:
            conn_countdowns_db.execute(
                "DELETE from Countdowns WHERE msgid = :msgid AND channelid = :channelid AND number = :number;",
                {"msgid": msg_id, "channelid": channel_id, "number": number},
            )
            conn_countdowns_db.commit()

        # Mention the role/user
        if role_id != 0:
            not_sent = True
            # Go through all roles to see if it is a role to mention
            for role_ids in bot.get_guild(guild_id).roles:
                if role_id == int(role_ids.id):
                    # Formatting of mentioning a role and everyone is different.
                    await channel.send(
                        f"{'<@&' + str(role_id) + '>' if role_id != guild_id else '@everyone'}",
                        embeds=embed,
                        allowed_mentions={"parse": ["roles", "everyone"]},
                    )
                    not_sent = False
            if not_sent:
                # Here its a user that get mentioned.
                await channel.send(f"<@{role_id}>", embeds=embed)
        else:
            # no mention.
            await channel.send(embeds=embed)
