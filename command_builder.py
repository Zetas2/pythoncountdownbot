"""
All commands are made in here. For translating there is languageFile.
"""

# ¤ are points of optimasation
# +++ where I am at the first readability check
# ¤All sql statements can be moved into a seperate file
# ¤Move responses into langguage_file

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
    """CREATE TABLE IF NOT EXISTS Countdowns (timestamp int,msgid int,channelid int,guildid int,roleid int,startedby int,times int,length int,imagelink varchar(255),messagestart varchar(255),messageend varchar(255));"""
)

# makes connPremium into the connected database for premium.
conn_premium_db = sqlite3.connect("premiumGuilds.db")
# Make the table if there is noe
conn_premium_db.execute(
    """CREATE TABLE IF NOT EXISTS Premium (guildid int,userid int,lastedit int)"""
)

# To keep track of how long the bot have been up, the starttime is saved.
bot_starttime = floor(time.time())


async def check_no_premium(ctx, feature):
    """Make sure that a feature can only be used by premium users."""
    if ctx.guild_id is None:
        await ctx.send("You cant use premium features in DMs", ephemeral=True)
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
        f"Sorry, you tried to use a premium only feature: {feature}", ephemeral=True
    )
    return True


async def check_link(ctx, image_link):
    """Checks so that the link is valid."""
    if validurl(image_link):
        return False

    # If the code havent returned yet, its not a valid link
    await ctx.send("You need to send a link to the image", ephemeral=True)
    return True


def get_exact_timestring(timestring, length):
    """Creates the Exact time from start message. Fills in the time that is left."""
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


async def send_and_add_to_database(
    timestamp,
    ctx,
    mention,
    times,
    length,
    message_start,
    message_end,
    image_link,
    exact,
    alert,
    bot,
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
        if alert:
            channel = await ctx.get_channel()
            member = await interactions.get(
                bot,
                interactions.Member,
                object_id=int(bot.me.id),
                parent_id=ctx.guild_id,
            )
            got_permission = await member.has_permissions(
                interactions.Permissions.EMBED_LINKS
                ^ interactions.Permissions.SEND_MESSAGES,
                channel=channel,
            )
        else:
            got_permission = True
    except:
        await ctx.send(
            "I am missing the permission to view this channel. Please give me it!",
            ephemeral=True,
        )
    else:
        if got_permission:
            # Message is built and sent
            message_start = message_start.replace("\\n", "\n")
            # Allow for \n to be used as newline charachter
            message_end = message_end.replace("\\n", "\n")
            current_time = floor(time.time())
            time_left = int(timestamp) - int(current_time)
            timestring = ""
            if exact:
                # Since timestamps are exact to the minute the last hour,
                # only use exact if time is longer
                if time_left > 3600:
                    timestring = "\n*Exact time from start: "
                    timestring = f"{get_exact_timestring(timestring, time_left)}*"
            msg = await ctx.send(
                f"{message_start} <t:{timestamp}:R> {message_end}{timestring}"
            )

            # If the bot should notify when countdown is done - save it to database:
            if alert:
                guild_id = ctx.guild_id
                if guild_id is None:  # Will be that in DMs.
                    guild_id = 0
                started_by = ctx.user.id
                # Had problems with these numbers being "None" for some unknown reason,
                # so added a check so they cant come into the database
                if msg.id is None or msg.channel_id is None:
                    return True

                if mention != "0":
                    role_id = mention.id
                else:
                    role_id = 0

                # Add it into database
                conn_countdowns_db.execute(
                    "INSERT INTO Countdowns (timestamp,msgid,channelid,guildid,roleid,startedby,times,length,imagelink,messagestart,messageend) VALUES (:timestamp,:msgid,:channelid,:guildid,:mention,:startedby,:times,:length,:imagelink,:messagestart,:messageend);",
                    {
                        "timestamp": int(timestamp),
                        "msgid": int(msg.id),
                        "channelid": int(msg.channel_id),
                        "guildid": int(guild_id),
                        "mention": int(role_id),
                        "startedby": int(started_by),
                        "times": int(times),
                        "length": int(length),
                        "imagelink": str(image_link),
                        "messagestart": str(message_start),
                        "messageend": str(message_end),
                    },
                )
                conn_countdowns_db.commit()
            return False
        else:
            await ctx.send(
                "I am missing the permission to send embeds/messages in this channel. Please give me it!",
                ephemeral=True,
            )


async def check_length(ctx, length):
    """Check so that a countdown is at least one minute long"""
    if length < 60:
        # I am the dev and want to be able to test timers without wating, ok?
        if int(ctx.user.id) != 238006908664020993:
            await ctx.send(
                "Minimum length of a countdown is one minute", ephemeral=True
            )
            return True
    return False


async def check_active_and_mention(ctx, mention):
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
                "Max countdowns in dms reached. Delete one or wait for one to run out to add more.",
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
                "Increased amount of countdowns in this guild. Get premium or delete some of the active ones.",
            ):
                return True
        # limits number of active countdowns to 20
        elif number_of_countdowns_channel > 19:
            if await check_no_premium(
                ctx,
                "Increased amount of countdowns in this channel. Get premium or delete some of the active ones.",
            ):
                return True
        # Here the limit wasnt reached, so therefore continue checking permission
        # If you try to ping someone check that you got the permission ¤ Allow pinging of yourself
        if mention != "0" and not (
            ctx.author.permissions & interactions.Permissions.MENTION_EVERYONE
        ):
            await ctx.send("You dont have permission to ping", ephemeral=True)
            return True
        # mention is a thingy, I just want the id of it.
        if mention != "0":
            mention = mention.id

        return False


async def do_all_checks(ctx, mention, image_link, times):
    """A single function for all checks required before a dountdown/timer starts"""
    if await check_active_and_mention(ctx, mention):
        return False

    if image_link != "":
        if await check_no_premium(ctx, "adding image"):
            return False
        if await check_link(ctx, image_link):
            return False

    if times != 0:
        if await check_no_premium(ctx, "repeating timer"):
            return False

    return True


async def delete_message(ctx, msg_id):
    """Send the message if a message is deleted"""
    user = ctx.user
    guild_id = ctx.guild_id
    channel_id = ctx.channel_id
    await ctx.send(
        f"Countdown [{msg_id}](https://discord.com/channels/{guild_id}/{channel_id}/{msg_id} 'Click here to jump to the message') was deleted by {user}"
    )


async def help_information(ctx):
    """
    The help command.
    This looks different than the rest since it is prepped
    for translation by using the translations file
    """
    language = "en-US"
    # ctx.guild.preferred_locale
    # The thing to check what language the guild is set to.
    # Wont do anything until bot is translated.

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
        (translations[(language)]["helpLinksTitle"]),
        (translations[(language)]["helpLinksDesc"]),
    )

    embed.footer = interactions.EmbedFooter(
        text=(translations[(language)]["helpFooter" + str(random.randint(1, 6))])
    )

    embed.color = int(
        ("#%02x%02x%02x" % (90, 232, 240)).replace("#", "0x"), base=16
    )  # Set the colour to light blue
    await ctx.send(embeds=embed, ephemeral=True)


async def countdown(
    ctx,
    timestring,
    message_start,
    message_end,
    mention,
    times,
    repeat_length,
    image_link,
    exact,
    alert,
    bot,
):
    """The countdown command. The main use of this bot. Creates a new countdown."""

    if await do_all_checks(ctx, mention, image_link, times):

        wholedate = dateparser.parse("in " + timestring)
        try:  # If wholedate cant be floored, it is not a valid date.
            timestamp = floor(wholedate.timestamp())
            valid_date = True
        except:
            await ctx.send(
                "Sorry, I dont understand that date!",
                ephemeral=True,
            )
            valid_date = False

        if valid_date:
            current_time = floor(time.time())
            if current_time < timestamp:  # Make sure the time is in the future
                length = timestamp - current_time
                if await check_length(ctx, length):
                    return
                if times != 0:
                    length = repeat_length * 3600
                write_error = await send_and_add_to_database(
                    timestamp,
                    ctx,
                    mention,
                    times,
                    length,
                    message_start,
                    message_end,
                    image_link,
                    exact,
                    alert,
                    bot,
                )
                if write_error:
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
    message_start,
    message_end,
    mention,
    times,
    image_link,
    exact,
    alert,
    bot,
):
    """For those that dont want to use countdown."""

    if await do_all_checks(ctx, mention, image_link, times):

        current_time = floor(time.time())
        length = minute * 60 + hour * 3600 + day * 86400 + week * 604800
        if await check_length(ctx, length):
            return
        timestamp = current_time + length

        write_error = await send_and_add_to_database(
            timestamp,
            ctx,
            mention,
            times,
            length,
            message_start,
            message_end,
            image_link,
            exact,
            alert,
            bot,
        )
        if write_error:
            await ctx.send("SOMETHING WENT WRONG", ephemeral=True)


# +++
async def list_countdowns(ctx, sub_command, page):
    """List command. List all active countdowns based on sub command."""
    if ctx.guild_id is None and sub_command != "channel":
        return await ctx.send("Sorry, only /list channel works in DMs", ephemeral=True)
    # Links for DMs are @me instead of the guildid
    if ctx.guild_id is None:
        guild_id = "@me"
    else:
        guild_id = int(ctx.guild_id)
    channel_id = int(ctx.channel_id)

    if sub_command == "channel":
        place = "in this channel"
        cursor = conn_countdowns_db.execute(
            "SELECT COUNT (*) FROM Countdowns WHERE channelid = :channelid;",
            {"channelid": channel_id},
        )

        for row in cursor:
            number_of_countdowns = int(row[0])
        cursor = conn_countdowns_db.execute(
            "SELECT timestamp,msgid,channelid,startedby FROM Countdowns WHERE channelid = :channelid ORDER BY timestamp ASC;",
            {"channelid": channel_id},
        )

    elif sub_command == "guild":
        place = "in this guild"
        cursor = conn_countdowns_db.execute(
            "SELECT COUNT (*) FROM Countdowns WHERE guildid = :guildid;",
            {"guildid": guild_id},
        )
        for row in cursor:
            number_of_countdowns = int(row[0])
        cursor = conn_countdowns_db.execute(
            "SELECT timestamp,msgid,channelid,startedby FROM Countdowns WHERE guildid = :guildid ORDER BY timestamp ASC;",
            {"guildid": guild_id},
        )

    elif sub_command == "mine":
        place = "from you"
        user_id = int(ctx.user.id)
        cursor = conn_countdowns_db.execute(
            "SELECT COUNT (*) FROM Countdowns WHERE guildid = :guildid AND startedby = :userid;",
            {"guildid": guild_id, "userid": user_id},
        )
        for row in cursor:
            number_of_countdowns = int(row[0])
        cursor = conn_countdowns_db.execute(
            "SELECT timestamp,msgid,channelid,startedby FROM Countdowns WHERE guildid = :guildid AND startedby = :userid ORDER BY timestamp ASC;",
            {"guildid": guild_id, "userid": user_id},
        )

    # since there are 5 countdowns per page
    max_page = ceil(number_of_countdowns / 5)

    # If requested is higher just make it to the max
    if max_page < page:
        page = max_page

    embed = interactions.Embed()
    embed.title = "ACTIVE COUNTDOWNS"
    embed.description = "These are the countdowns active " + place

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
            embed.add_field(
                f"{current_line}: <t:{timestamp}:R>",
                f"[{msg_id}](https://discord.com/channels/{guild_id}/{channel_id}/{msg_id} 'Click here to jump to the message') Started by <@!{started_by}>\n",
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
    await ctx.send(embeds=embed, ephemeral=True)


async def delete(
    ctx, sub_command, sub_command_group, delete_mine, delete_channel, delete_guild
):
    """Deletes a countdown based on subcommand.""" 
    # ¤ Make a function that can fit all of these
    if sub_command == "mine":
        if sub_command_group == "single":
            cursor = get_possible_countdowns(ctx, "mine")
            try:
                msg_id = delete_mine.split(": ")[1]
            except:
                return await ctx.send("Please use one of the options ", ephemeral=True)
            allowed_delete = False
            for row in cursor:
                if int(row[0]) == int(msg_id):
                    allowed_delete = True
                    pass
            if not allowed_delete:
                return await ctx.send("Please use one of the options", ephemeral=True)

            check = conn_countdowns_db.total_changes
            conn_countdowns_db.execute(
                "DELETE from Countdowns WHERE msgid = :msgid;", {"msgid": msg_id}
            )
            conn_countdowns_db.commit()
            if check == conn_countdowns_db.total_changes:
                await ctx.send(
                    "An error occurred (could be that there is none to delete)",
                    ephemeral=True,
                )
            else:

                await delete_message(ctx, msg_id)
        else:
            await ctx.send(
                "Are you sure you want to delete all your countdowns in this guild?",
                components=[components.delete_mine, components.delete_cancel],
                ephemeral=True,
            )

    elif ctx.author.permissions & interactions.Permissions.MANAGE_MESSAGES:
        if sub_command_group == "single":
            if sub_command == "channel":
                cursor = get_possible_countdowns(ctx, "channel")
                try:
                    msg_id = delete_channel.split(": ")[1]
                except:
                    return await ctx.send(
                        "Please use one of the options ", ephemeral=True
                    )
                allowed_delete = False
                for row in cursor:
                    if int(row[0]) == int(msg_id):
                        allowed_delete = True
                        pass
                if not allowed_delete:
                    return await ctx.send(
                        "Please use one of the options ", ephemeral=True
                    )
            if sub_command == "guild":
                cursor = get_possible_countdowns(ctx, "guild")
                try:
                    msg_id = delete_guild.split(": ")[1]
                except:
                    return await ctx.send(
                        "Please use one of the options ", ephemeral=True
                    )
                allowed_delete = False
                for row in cursor:
                    if int(row[0]) == int(msg_id):
                        allowed_delete = True
                        pass
                if not allowed_delete:
                    return await ctx.send(
                        "Please use one of the options ", ephemeral=True
                    )
            check = conn_countdowns_db.total_changes
            conn_countdowns_db.execute(
                "DELETE from Countdowns WHERE msgid = :msgid;", {"msgid": msg_id}
            )
            conn_countdowns_db.commit()

            if check == conn_countdowns_db.total_changes:
                await ctx.send(
                    "An error occurred (could be that there is none to delete)",
                    ephemeral=True,
                )
            else:
                await delete_message(ctx, msg_id)

        else:
            if sub_command == "channel":
                await ctx.send(
                    "Are you sure you want to delete all the countdowns in this channel?",
                    components=[components.delete_channel, components.delete_cancel],
                    ephemeral=True,
                )
            elif sub_command == "guild":
                await ctx.send(
                    "Are you sure you want to delete all the countdowns in this guild?",
                    components=[components.delete_guild, components.delete_cancel],
                    ephemeral=True,
                )

    else:
        await ctx.send(
            "Sorry, you need `MANAGE_MESSAGES` to use this, unless you want to delete your own",
            ephemeral=True,
        )


async def delete_this(ctx):
    """App command for deleting. Use on a active countdown message and it will be deleted."""
    msg_id = int(ctx.target.id)
    user_id = int(ctx.user.id)
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
            "You can ony use this on active countdowns.",
            ephemeral=True,
        )
    # Make sure user have permission to delete.
    if (
        started_by != user_id
        and not ctx.author.permissions & interactions.Permissions.MANAGE_MESSAGES
    ):
        return await ctx.send(
            "Sorry, you need `MANAGE_MESSAGES` to use this, unless you want to delete your own",
            ephemeral=True,
        )

    check = conn_countdowns_db.total_changes
    conn_countdowns_db.execute(
        "DELETE from Countdowns WHERE msgid = :msgid;", {"msgid": msg_id}
    )
    conn_countdowns_db.commit()
    if check == conn_countdowns_db.total_changes:
        return await ctx.send(
            "An error occurred (could be that there is none to delete)",
            ephemeral=True,
        )

    await delete_message(ctx, msg_id)


async def fill_choices(ctx, cursor, value):
    """
    This function is used for the autocompletion of what
    active countdowns there is to delete in all categories.
    How it really works? Good question...
    """
    countdowns = []
    countdown_id = 0
    for row in cursor:
        # Need to be limited due to discord not allowing more than 25 options
        if (countdown_id < 24):  
            countdowns.append(str(countdown_id) + ": " + str(row[0]))
            countdown_id += 1
        else:
            break
    
    choices = [
        interactions.Choice(name=item, value=item)
        for item in countdowns
        if value in item
    ]
    await ctx.populate(choices)


def get_possible_countdowns(ctx, option):
    """Generates a cursor for the option picked with all active countdowns in it."""
    if option == "mine":
        user_id = int(ctx.user.id)
        if ctx.guild_id is None:
            channel_id = int(ctx.channel_id)
            cursor = conn_countdowns_db.execute(
                "SELECT msgid FROM Countdowns WHERE startedby = :userid AND channelid = :channelid ORDER BY timestamp ASC;",
                {"userid": user_id, "channelid": channel_id},
            )
        else:
            guild_id = int(ctx.guild_id)
            cursor = conn_countdowns_db.execute(
                "SELECT msgid FROM Countdowns WHERE startedby = :userid AND guildid = :guildid ORDER BY timestamp ASC;",
                {"userid": user_id, "guildid": guild_id},
            )

    elif option == "channel":
        channel_id = int(ctx.channel_id)
        cursor = conn_countdowns_db.execute(
            "SELECT msgid FROM Countdowns WHERE channelid = :channelid ORDER BY timestamp ASC;",
            {"channelid": channel_id},
        )
    elif option == "guild":
        # The guild_id can be None if it is used in DMs
        if ctx.guild_id is None:
            channel_id = int(ctx.channel_id)
            cursor = conn_countdowns_db.execute(
                "SELECT msgid FROM Countdowns WHERE channelid = :channelid ORDER BY timestamp ASC;",
                {"channelid": channel_id},
            )
        else:
            guild_id = int(ctx.guild_id)
            cursor = conn_countdowns_db.execute(
                "SELECT msgid FROM Countdowns WHERE guildid = :guildid ORDER BY timestamp ASC;",
                {"guildid": guild_id},
            )
    return cursor


async def autocomplete_countdowns(ctx, value, option):
    """Fills the options when using timeleft or delete commands"""
    cursor = get_possible_countdowns(ctx, option)
    await fill_choices(ctx, cursor, value)


# ¤Expand to threads as well
def deleted_channel(channel):
    """Delete countdowns from database if the channel they were in get deleted."""
    channel_id = int(channel.id)
    conn_countdowns_db.execute(
        "DELETE from Countdowns WHERE channelid = :channelid;",
        {"channelid": channel_id},
    )
    conn_countdowns_db.commit()


async def delete_button(ctx, option):
    """If a button used for deleting is used."""
    user = ctx.user
    if option == "guild":
        if ctx.guild_id is None:
            return ctx.send("You cant use this in DMs", ephemeral=True)
        guild_id = int(ctx.guild_id)
        check = conn_countdowns_db.total_changes
        conn_countdowns_db.execute(
            "DELETE from Countdowns WHERE guildid = :guildid;", {"guildid": guild_id}
        )
        conn_countdowns_db.commit()

        if check == conn_countdowns_db.total_changes:
            await ctx.send(
                "An error occurred (could be that there is none to delete)",
                ephemeral=True,
            )
        else:
            await ctx.edit(components=[])
            await ctx.send(f"Guilds Countdown(s) Deleted by {user}")
    elif option == "channel":
        channel_id = int(ctx.channel_id)
        check = conn_countdowns_db.total_changes
        conn_countdowns_db.execute(
            "DELETE from Countdowns WHERE channelid = :channelid;",
            {"channelid": channel_id},
        )
        conn_countdowns_db.commit()
        if check == conn_countdowns_db.total_changes:
            await ctx.send(
                "An error occurred (could be that there is none to delete)",
                ephemeral=True,
            )
        else:
            await ctx.edit(components=[])
            await ctx.send(f"Channels Countdown(s) Deleted by {user}")
    elif option == "mine":
        if ctx.guild_id is None:
            return ctx.send("You cant use this in DMs", ephemeral=True)
        guild_id = int(ctx.guild_id)
        user_id = int(ctx.user.id)
        check = conn_countdowns_db.total_changes
        conn_countdowns_db.execute(
            "DELETE from Countdowns WHERE guildid = :guildid AND startedby = :userid; ",
            {"guildid": guild_id, "userid": user_id},
        )
        conn_countdowns_db.commit()
        if check == conn_countdowns_db.total_changes:
            await ctx.send(
                "An error occurred (could be that there is none to delete)",
                ephemeral=True,
            )
        else:
            # Remove the buttons from the ephemeral message
            # and send a message announcing.
            await ctx.edit(components=[])
            await ctx.send(f"All {user} Countdown(s) Deleted")
    elif option == "cancel":
        # Just edit away the buttons and say that contdowns are kept
        await ctx.edit("All countdowns are kept", components=[])


async def time_left_message(ctx, msg_id):
    """Send the message for time left"""
    timestamp = 0
    cursor = conn_countdowns_db.execute(
        "SELECT timestamp,channelid,guildid from Countdowns WHERE msgid = :msgid;",
        {"msgid": msg_id},
    )
    for row in cursor:
        timestamp = int(row[0])
        channel_id = int(row[1])
        guild_id = int(row[2])

    if timestamp == 0:
        return await ctx.send("The countdown was not found. ", ephemeral=True)

    current_time = floor(time.time())
    length = timestamp - current_time

    timestring = f"Exact time left for countdown [{msg_id}](https://discord.com/channels/{guild_id}/{channel_id}/{msg_id} 'Click here to jump to the message'): "
    timestring = get_exact_timestring(timestring, length)
    await ctx.send(timestring, ephemeral=True)


async def time_left(ctx, sub_command, show_mine, show_channel, show_guild):
    """Show how long time it is left for a countdown"""
    # show_mine, show_channel and show_guild contains the ID
    # To process it easier, it is moved into show
    if sub_command == "mine":
        show = show_mine
    elif sub_command == "channel":
        show = show_channel
    elif sub_command == "guild":
        show = show_guild

    try:
        msg_id = show.split(": ")[1]
    except:
        return await ctx.send("Please use one of the options ", ephemeral=True)

    await time_left_message(ctx, msg_id)


async def timeleft_this(ctx):
    """App command for timeleft."""
    msg_id = int(ctx.target.id)
    await time_left_message(ctx, msg_id)


async def botstats(ctx, bot):
    """Botstat command. Gathers a bunch of information about the bot."""
    await ctx.defer(ephemeral=True)
    cpu = psutil.cpu_percent(4)
    ram = psutil.virtual_memory()[2]
    disk = psutil.disk_usage("/").percent
    guilds = len(bot.guilds)

    # Get the number of active countdowns
    cursor = conn_countdowns_db.execute("SELECT COUNT(*) FROM Countdowns;")
    number = len(cursor.fetchall())

    # Get size of log file
    with open("log.txt", "r") as file:
        logsize = len(file.readlines())

    # Check this when activating shards - might break
    # (not that it alredy isnt)
    ping = round(bot.latency)

    embed = interactions.Embed()
    embed.title = "BOT STATS"
    embed.description = "This is the current status of the bot"
    embed.add_field("CPU :fire:", f"{cpu}%")
    embed.add_field("RAM :floppy_disk:", f"{ram}%")
    embed.add_field("Disk :minidisc:", f"{disk}%")
    embed.add_field("Active countdowns :clock1:", f"{number}")
    embed.add_field("Guilds :timer:", f"{guilds}")
    embed.add_field("Uptime :up:", f"Since <t:{bot_starttime}:R>")
    embed.add_field("Ping! :satellite:", f"{ping} ms")
    embed.add_field("Log size :scroll:", f"{logsize} rows")
    embed.color = int(("#%02x%02x%02x" % (255, 132, 140)).replace("#", "0x"), base=16)
    await ctx.send(embeds=embed)


async def translate(ctx, language):
    """Allows for tranlsating the bot to another language. NOT YET SUPPORTED"""
    if ctx.author.permissions & interactions.Permissions.ADMINISTRATOR:
        try:
            await ctx.guild.set_preferred_locale(language)
        except:
            await ctx.send(
                "Sorry, I need to be able to manage guild to use this command. I use the guilds language to know what language to operate on.",
                ephemeral=True,
            )
        else:
            await ctx.send(f"{ctx.user} translated the bot to {language}")
    else:
        await ctx.send(
            "Sorry, you need to be administrator to use this command", ephemeral=True
        )


async def make_this_premium(ctx):
    """Change the premium guild to the one where the command is used. Cooldown of 2 days."""
    guild_id = ctx.guild_id
    current_time = floor(time.time())
    # 172800 seconds is two days.
    allowed_time = current_time - 172800
    user_id = int(ctx.user.id)
    # Find those that are from the user
    # that havent been recently edited.
    cursor = conn_premium_db.execute(
        "SELECT userid FROM Premium WHERE lastedit < :allowedtime AND userid = :userid;",
        {"allowedtime": allowed_time, "userid": user_id},
    )

    # Somehow checks if there is a result or not.
    # If there is a result, update it to current guild and time
    if len(cursor.fetchall()) != 0:
        check = conn_premium_db.total_changes
        conn_premium_db.execute(
            "UPDATE Premium set guildid = :guildid WHERE userid = :userid;",
            {"userid": user_id, "guildid": int(guild_id)},
        )
        conn_premium_db.execute(
            "UPDATE Premium set lastedit = :currenttime WHERE userid = :userid;",
            {"userid": user_id, "currenttime": int(current_time)},
        )
        conn_premium_db.commit()

        if check == conn_premium_db.total_changes:
            await ctx.send(
                "An error occurred",
                ephemeral=True,
            )
        else:
            await ctx.send(f"Guild was updated to: {guild_id}", ephemeral=True)

    else:
        await ctx.send(
            "Sorry, you need to be a premium user to use this command. Or wait 2 days since you last used it",
            ephemeral=True,
        )



async def premium_info(ctx):
    """Sends some info about premium."""
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
    embed.color = int(("#%02x%02x%02x" % (255, 20, 147)).replace("#", "0x"), base=16)
    await ctx.send(embeds=embed, ephemeral=True)


# HERE COME DEVS COMMANDS
devs = (238006908664020993, 360084558265450496, 729791860674920488)


async def log(ctx):
    """Shows the log"""
    if int(ctx.user.id) in devs:
        logs = ""
        with open("log.txt", "r") as file:
            # Read the last lines in the log file
            for line in file.readlines()[-19:]:
                logs = logs + line

        await ctx.send(f"Logs are:\n```{logs}```", ephemeral=True)

    else:
        await ctx.send(
            "Sorry, you need to be the dev to use this command", ephemeral=True
        )


async def add_premium(ctx, user_id, guild_id):
    """Add a premium user."""
    if int(ctx.user.id) in devs:
        cursor = conn_premium_db.execute(
            "SELECT userid FROM Premium WHERE userid = :userid;", {"userid": user_id}
        )
        if len(cursor.fetchall()) == 0:
            conn_premium_db.execute(
                "INSERT INTO Premium (userid,guildid,lastedit) VALUES (:userid,:guildid,0);",
                {
                    "userid": int(user_id),
                    "guildid": int(guild_id),
                },
            )
            conn_premium_db.commit()
            await ctx.send(f"User <@{user_id}> was added", ephemeral=True)
        else:
            await ctx.send(f"User <@{user_id}> is alredy premium", ephemeral=True)

    else:
        await ctx.send(
            "Sorry, you need to be the dev to use this command", ephemeral=True
        )


async def delete_premium(ctx, user_id):
    """Delete a premium user."""
    if int(ctx.user.id) in devs:
        check = conn_premium_db.total_changes
        conn_premium_db.execute(
            "DELETE from Premium WHERE userid = :userid;",
            {"userid": user_id},
        )
        conn_premium_db.commit()

        if check == conn_premium_db.total_changes:
            await ctx.send(
                "An error occurred (could be that there is none to delete)",
                ephemeral=True,
            )
        else:
            await ctx.send(
                f"User <@{user_id}> was deleted from premium users", ephemeral=True
            )

    else:
        await ctx.send(
            "Sorry, you need to be the dev to use this command", ephemeral=True
        )


async def list_premium(ctx, page):
    """List all premium users."""
    if int(ctx.user.id) in devs:
        cursor = conn_premium_db.execute("SELECT COUNT (*) FROM Premium")
        for row in cursor:
            number_of_countdown = int(row[0])
        cursor = conn_premium_db.execute("SELECT guildid,userid,lastedit FROM Premium")
        lines = 15
        max_page = ceil(number_of_countdown / lines)
        if max_page < page:
            page = max_page

        embed = interactions.Embed()
        embed.title = "Premium users"
        current_line = 0
        goal_line = page * lines
        # Loops through all premiums to pick out the ones that should be on specified page
        for row in cursor:
            if current_line >= goal_line - lines:
                guild_id = int(row[0])
                user_id = int(row[1])
                last_edit = int(row[2])
                embed.add_field(
                    "-----",
                    f"<@{user_id}> have guild {guild_id}. Edited <t:{last_edit}>",
                )
            elif current_line < goal_line - lines:
                pass
            else:
                break
            current_line = current_line + 1
            if current_line >= goal_line:
                break

        embed.footer = interactions.EmbedFooter(text=f"Page {page} of {max_page}")
        embed.color = int(
            ("#%02x%02x%02x" % (255, 153, 51)).replace("#", "0x"), base=16
        )
        await ctx.send(embeds=embed, ephemeral=True)

    else:
        await ctx.send(
            "Sorry, you need to be the dev to use this command", ephemeral=True
        )


async def check_done(bot):
    """Checks if a countdown is done. If it is, send the countdown completed message."""
    current_time = int(floor(time.time()))
    cursor = conn_countdowns_db.execute(
        "SELECT timestamp,msgid,channelid,guildid,roleid,startedby,times,length,imagelink,messagestart,messageend FROM Countdowns WHERE timestamp < :currenttime;",
        {"currenttime": current_time},
    )
    # There will just be an empty row in cursor if theres no countdowns that are active.
    # Therefore this wont run multiple times.
    for row in cursor:
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
            channel = await interactions.get(
                bot, interactions.Channel, object_id=channel_id
            )
        except:
            conn_countdowns_db.execute(
                "DELETE from Countdowns WHERE msgid = :msgid;",
                {"msgid": msg_id},
            )
            conn_countdowns_db.commit()
            return
        member = await interactions.get(
                bot,
                interactions.Member,
                object_id=int(bot.me.id),
                parent_id=guild_id,
            )
        got_permission = await member.has_permissions(
                interactions.Permissions.EMBED_LINKS
                ^ interactions.Permissions.SEND_MESSAGES ^ interactions.Permissions.VIEW_CHANNEL,
                channel=channel,
            )
        
        if not got_permission:
            conn_countdowns_db.execute(
                "DELETE from Countdowns WHERE msgid = :msgid;",
                {"msgid": msg_id},
            )
            conn_countdowns_db.commit()
            return
        

        # guild = await interactions.get(bot, interactions.Guild, object_id=int(channel.guild.id))
        language = "en-US"  # guild.preferred_locale

        embed = interactions.Embed()

        embed.title = translations[(language)]["done"]

        embed.description = f"{(translations[(language)]['created'])} <@!{started_by}>"

        if image_link != "":
            embed.set_image(url=image_link)

        content = f"{message_start} <t:{timestamp}> {message_end}"
        embed.add_field("Countdown", content)
        embed.color = int(("#%02x%02x%02x" % (0, 255, 0)).replace("#", "0x"), base=16)

        embed.add_field(
            "Original message",
            f"[{msg_id}](https://discord.com/channels/{guild_id}/{channel_id}/{msg_id} 'Click here to jump to the message')",
        )

        # If it is repeating, it should decrease the number of times to repeat
        if times != 0:
            timestamp = timestamp + length
            embed.add_field(
                "Reapeating",
                f"This countdown will be repeated {times} time(s) more. Next time is: <t:{timestamp}:R>",
            )
            times = times - 1
            conn_countdowns_db.execute(
                "UPDATE Countdowns set times = :times where msgid = :msgid;",
                {"times": times, "msgid": msg_id},
            )
            conn_countdowns_db.execute(
                "UPDATE Countdowns set timestamp = :timestamp where msgid = :msgid;",
                {"timestamp": timestamp, "msgid": msg_id},
            )
            conn_countdowns_db.commit()
        # If its not repeating, it should get deleted from the database
        else:
            conn_countdowns_db.execute(
                "DELETE from Countdowns WHERE msgid = :msgid AND channelid = :channelid;",
                {"msgid": msg_id, "channelid": channel_id},
            )
            conn_countdowns_db.commit()

        if role_id != 0:
            not_sent = True
            try:
                guild_info = await interactions.get(
                    bot, interactions.Guild, object_id=guild_id
                )
            except:
                conn_countdowns_db.execute(
                    "DELETE from Countdowns WHERE msgid = :msgid;",
                    {"msgid": msg_id},
                )
                conn_countdowns_db.commit()
                return
            else:
                list_of_id = guild_info.roles
                for role_ids in list_of_id:
                    if role_id == int(role_ids.id):
                        await channel.send(
                            f"{'<@&' + str(role_id) + '>' if role_id != guild_id else '@everyone'}",
                            embeds=embed,
                            allowed_mentions={"parse": ["roles", "everyone"]},
                        )
                        not_sent = False
                if not_sent:
                    await channel.send(f"<@{role_id}>", embeds=embed)
        else:
            await channel.send(embeds=embed)
