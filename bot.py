from math import floor, ceil
import time
import interactions
from interactions.ext.tasks import IntervalTrigger, create_task
import sqlite3
#from interactions.ext.autosharder import shard
import psutil
import dateparser


conn = sqlite3.connect('Countdowns.db')
try:
    conn.execute('''CREATE TABLE Countdowns (timestamp int,msgid int,channelid int,guildid int,roleid int,startedby int,times int,length int,messagestart varchar(255),messageend varchar(255));''')
    print ("table made")
except:
    print("Table probably alredy there")

bot = interactions.Client(token="TOKEN", disable_sync=False)

def writeinfile(timestamp,msg,guildid,mention,startedby,times,length, messagestart, messageend="!"):
    if msg.id == None:
        return True
    if msg.channel_id == None:
        return True
    if guildid == None:
        return True
    if mention != "0":
        roleid = mention.id
    else:
        roleid = 0
    messagestart = messagestart.replace("'", "’")
    messageend = messageend.replace("'", "’")
    conn.execute("INSERT INTO Countdowns (timestamp,msgid,channelid,guildid,roleid,startedby,times,length,messagestart,messageend) VALUES ("+str(timestamp)+","+str(msg.id)+","+str(msg.channel_id)+","+str(guildid)+","+str(roleid)+","+str(startedby)+","+str(times)+","+str(length)+", '"+str(messagestart)+"' , '"+str(messageend)+"');")
    conn.commit()
    return False

def checkactive(guildid, channelid):
    cursor = conn.execute("SELECT COUNT(*) FROM Countdowns WHERE guildid= "+str(guildid)+";")
    for row in cursor:
        server = int(row[0])
    cursor = conn.execute("SELECT COUNT(*) FROM Countdowns WHERE channelid= "+str(channelid)+";")
    for row in cursor:
        channel = int(row[0])
    if server > 50:
        return True
    elif channel > 20:
        return True
    else:
        return False

#Check this when activating shards
@bot.event
async def on_start():
    await bot.change_presence(presence=interactions.ClientPresence(activities=[interactions.PresenceActivity(name="/help", type=interactions.PresenceActivityType.LISTENING)]))


@bot.command(
    name="help",
    description="Shows a help message",
)
async def help(ctx: interactions.CommandContext):
    embed = interactions.Embed() 
    embed.title = "Help"
    embed.description = "This bot got 5 commands: Countdown, timer, list, delete and help."
    embed.add_field("Countdown", "Countdown will show the remaining time until the date you entered, or for the duration you specify. Its timezone is UTC. They can be repeated by using the times option.")
    embed.add_field("List", "It will show you all active countdowns in the channel/server depending on subcommand.")
    embed.add_field("Delete", "To use this you need to mave the `MANAGE_MESSAGE` permission.\n*Single*\nEnter the message id for the countdown you want to delete and it will stop. You can find message id as the last number when using /list.\n*Channel*\nDeletes all countdowns in this channel.\n*Server*\nDeletes all countdowns in this server.")
    embed.add_field("Help", "Shows this help message")
    embed.add_field("Links", "[Discord Support](https://discord.com/invite/b2fY4z4xBY 'Join the support server!') | [Invite the Bot](https://top.gg/bot/710486805836988507) | [Patreon](https://www.patreon.com/livecountdownbot)")
    embed.color = int(('#%02x%02x%02x' % (90, 232, 240)).replace("#", "0x"), base=16)
    await ctx.send(embeds=embed, ephemeral=True)


@bot.command(
    name="countdown",
    description="Countdown to an exact date.",
    options = [
        interactions.Option(
            name="timestring",
            description="What time do you want",
            type=3,
            max_length=100,
            required=True,
        ),
        interactions.Option(
            name="messagestart",
            description="Custom message before timer",
            type=3,
            max_length=100,
            required=False,
        ),
        interactions.Option(
            name="messageend",
            description="Custom message after timer",
            type=3,
            max_length=100,
            required=False,
        ),
        interactions.Option(
            name="mention",
            description="Who to mention",
            type=9,
            required=False,
        ),
        interactions.Option(
            name="times",
            description="Number of times to repeat",
            type=4,
            required=False,
            max_value=50,
        ),
    ],
)

async def countdown(ctx: interactions.CommandContext,  timestring, messagestart="Countdown will end", messageend="", mention="0", times=0):
    reachedlimit = checkactive(ctx.guild_id, ctx.channel_id)
    if reachedlimit:
        return await ctx.send("Max countdowns reached. Delete one or wait for one to run out to add more.", ephemeral=True)
    
    if mention != "0" and not (ctx.author.permissions & interactions.Permissions.MENTION_EVERYONE):
        return await ctx.send("You dont have permission to ping", ephemeral=True)

    working = False
    try:
        wholedate = dateparser.parse(timestring)
        timestamp = floor(wholedate.timestamp())
        currenttime = floor(time.time())
        if int(currenttime) < int(timestamp):
            messagestart = messagestart.replace("\\n", "\n")
            messageend = messageend.replace("\\n", "\n")
            response = messagestart + " <t:" + str(timestamp) + ":R> " + messageend
            length = int(timestamp) - int(currenttime)
            working = True
        else: 
            response = "You cant set time in the past. You can try adding in more variables."
    except:
        response ="Not a valid date."

    if working == True:
        msg = await ctx.send(response)
        guildid = ctx.guild_id
        startedby = ctx.author.id
        writeerror = writeinfile(timestamp,msg,guildid,mention,startedby,times,length, messagestart, messageend)
        if writeerror:
            await ctx.send("SOMETHING WENT WRONG", ephemeral=True)
    else:
        msg = await ctx.send(response, ephemeral=True)


@bot.command(
    name="timer",
    description="Lets add a timer",
    options = [
        interactions.Option(
            name="minute",
            description="How many minutes",
            type=4,
            required=False,
            max_value=1000,
        ),
        interactions.Option(
            name="hour",
            description="How many hours",
            type=4,
            required=False,
            max_value=1000,
        ),
        interactions.Option(
            name="day",
            description="How many days",
            type=4,
            required=False,
            max_value=1000,
        ),
        interactions.Option(
            name="week",
            description="How many weeks",
            type=4,
            required=False,
            max_value=1000,
        ),
        interactions.Option(
            name="messagestart",
            description="Custom message before timer",
            type=3,
            max_length=100,
            required=False,
        ),
        interactions.Option(
            name="messageend",
            description="Custom message after timer",
            type=3,
            max_length=100,
            required=False,
        ),
        interactions.Option(
            name="mention",
            description="Who to mention",
            type=9,
            required=False,
        ),  
        interactions.Option(
            name="times",
            description="Number of times to repeat",
            type=4,
            required=False,
            max_value=50,
        ),
    ],
)

async def timer(ctx: interactions.CommandContext, day="0", week="0", hour="0", minute="0", messagestart="Timer will end", messageend="", mention="0", times="0"):
    reachedlimit = checkactive(ctx.guild_id, ctx.channel_id)
    if reachedlimit:
        return await ctx.send("Max countdowns reached. Delete one or wait for one to run out to add more.", ephemeral=True)

    if mention != "0" and not (ctx.author.permissions & interactions.Permissions.MENTION_EVERYONE):
        return await ctx.send("You dont have permission to ping", ephemeral=True)


    currenttime = floor(time.time())
    length = int(minute) * 60 + int(hour) * 3600 + int(day) * 86400 + int(week) * 604800
    timestamp = currenttime + length
    messagestart = messagestart.replace("\\n", "\n")
    messageend = messageend.replace("\\n", "\n")
    response = messagestart + " <t:" + str(timestamp) + ":R> " + messageend
    msg = await ctx.send(f"{response}!")
    guildid = ctx.guild_id
    startedby= ctx.author.id
    writeerror = writeinfile(timestamp,msg,guildid,mention,startedby,times,length, messagestart, messageend)
    if writeerror:
        await ctx.send(f"SOMETHING WENT WRONG", ephemeral=True)

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
                    type=4,
                    required=False,
                ),
            ]
        ),
        interactions.Option(
            name="server",
            description="List all countdowns in server",
            type=interactions.OptionType.SUB_COMMAND,
            options=[
                interactions.Option(
                    name="page",
                    description="What page number",
                    type=4,
                    required=False,
                    max_value=50,
                ),
            ]
        ),
        
    ],
)
async def list(ctx: interactions.CommandContext, sub_command: str, page=1):
    channelid = str(ctx.channel_id)
    guildid = str(ctx.guild_id)
    if sub_command == "channel":
        place = "channel"
        cursor = conn.execute("SELECT COUNT (*) FROM Countdowns WHERE channelid = "+str(channelid)+";")
        for row in cursor:
            numberofcountdown = int(row[0])
        cursor = conn.execute("SELECT timestamp,msgid,channelid FROM Countdowns WHERE channelid = "+str(channelid)+" ORDER BY timestamp ASC;")
    elif sub_command == "server":
        place = "server"
        cursor = conn.execute("SELECT COUNT (*) FROM Countdowns WHERE guildid = "+str(guildid)+";")
        for row in cursor:
            numberofcountdown = int(row[0])
        cursor = conn.execute("SELECT timestamp,msgid,channelid FROM Countdowns WHERE guildid = "+str(guildid)+" ORDER BY timestamp ASC;")
    maxpage = ceil(numberofcountdown/5)
    if maxpage < page:
        page = maxpage
    embed = interactions.Embed() 
    embed.title = "ACTIVE COUNTDOWNS"
    embed.description = "These are the countdowns active in this " + place

    currentLine = 0
    goal = page * 5
    for row in cursor:
        
        if currentLine >= goal-5:        
            msgid = int(row[1])
            timeid = int(row[0])
            channelid = int(row[2])
            embed.add_field("<t:"+str(timeid)+":R>", "["+str(msgid)+"](https://discord.com/channels/" + str(guildid) +"/"+str(channelid)+"/"+str(msgid)+" 'Click here to jump to the message')\n")
        elif currentLine < goal-5:
            pass
        else:
            break
        currentLine = currentLine +1
        if currentLine >= goal:
            break 

    embed.footer = interactions.EmbedFooter(text="Page " + str(page) + " of " + str(maxpage))
    embed.color = int(('#%02x%02x%02x' % (255, 153, 51)).replace("#", "0x"), base=16)
    await ctx.send(embeds=embed, ephemeral=True)


deleteserver = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Verify",
    emoji=interactions.Emoji(name="✅"),
    custom_id="deleteserver",
)

deletechannel = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Verify",
    emoji=interactions.Emoji(name="✅"),
    custom_id="deletechannel",
)

@bot.command(
    name="delete",
    description="Deletes countdowns",
    default_member_permissions=interactions.Permissions.MANAGE_MESSAGES,
    options=[
        interactions.Option(
            name="single",
            description="delete a single countdown",
            type=interactions.OptionType.SUB_COMMAND,
            options=[
                interactions.Option(
                name="msgid",
                description="Enter message ID that you want to delete.",
                type=3,
                required=True
        )
            ],
        ),
        interactions.Option(
            name="channel",
            description="Delete all countdowns in this channel",
            type=interactions.OptionType.SUB_COMMAND,
        ),
        interactions.Option(
            name="server",
            description="Delete all countdowns in this server",
            type=interactions.OptionType.SUB_COMMAND,
        ),
    ],
)

async def delete(ctx: interactions.CommandContext, sub_command: str, msgid: int = None):
    if sub_command == "single":
        guildid = str(ctx.guild_id)
        check = conn.total_changes
        conn.execute("DELETE from Countdowns WHERE msgid = "+str(msgid)+" AND guildid = "+str(guildid)+";")
        conn.commit()
        user = ctx.author
        if check == conn.total_changes:
            await ctx.send("An error occourd", ephemeral=True)
        else:
            await ctx.send("Countdown Deleted by " + str(user))
    elif sub_command == "channel":
        await ctx.send("Are you sure you want to delete all the countdowns in this channel?", components=deletechannel, ephemeral=True)
    elif sub_command == "server":
        await ctx.send("Are you sure you want to delete all the countdowns in this server?", components=deleteserver, ephemeral=True)
        

@bot.component("deleteserver")
async def button_response(ctx):
    guildid = str(ctx.guild_id)
    check = conn.total_changes
    conn.execute("DELETE from Countdowns WHERE guildid = "+str(guildid)+";")
    conn.commit()
    user = ctx.author
    if check == conn.total_changes:
        await ctx.send("An error occourd", ephemeral=True)
    else:
        await ctx.send("Servers Countdown(s) Deleted by " + str(user))

@bot.component("deletechannel")
async def button_response(ctx):
    channelid = str(ctx.channel_id)
    check = conn.total_changes
    conn.execute("DELETE from Countdowns WHERE channelid = "+str(channelid)+";")
    conn.commit()
    user = ctx.author
    if check == conn.total_changes:
        await ctx.send("An error occourd", ephemeral=True)
    else:
        await ctx.send("Channels Countdown(s) Deleted by " + str(user))


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

    #Check this when activating shards
    ping = round(bot.latency)

    embed = interactions.Embed() 
    embed.title = "BOT STATS"
    embed.description = "This is the current status of the bot"
    embed.add_field("CPU :fire:", str(cpu)+"%")
    embed.add_field("RAM :floppy_disk:", str(ram)+"%")
    embed.add_field("Active countdowns :clock1:", str(number))
    embed.add_field("Ping! :satellite:", str(ping))
    embed.color = int(('#%02x%02x%02x' % (255, 132, 140)).replace("#", "0x"), base=16)
    await ctx.send(embeds=embed)


@create_task(IntervalTrigger(5))
async def timer_check():
    currenttime = time.time()
    cursor = conn.execute("SELECT timestamp,msgid,channelid,guildid,roleid,startedby,times,length,messagestart,messageend FROM Countdowns WHERE timestamp < "+str(currenttime)+";")
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
        channel = interactions.Channel(**await bot._http.get_channel(channelid), _client=bot._http)

        embed = interactions.Embed() 
        embed.title = "A countdown is done!"
        

        embed.description = "It was started by <@!" + str(startedby) + ">"

        if times != 0:
            timestamp = timestamp + length
            embed.add_field("Reapeating", "This countdown will be repeated " + str(times) + " time(s) more. Next time is: <t:" + str(timestamp) + ":R>")
            times = times-1
            conn.execute("UPDATE Countdowns set times = "+str(times)+" where msgid = "+str(msgid)+";")
            conn.execute("UPDATE Countdowns set timestamp = "+str(timestamp)+" where msgid = "+str(msgid)+";")
            conn.commit()
        else:
            conn.execute("DELETE from Countdowns WHERE msgid = "+str(msgid)+" AND channelid = "+str(channelid)+";")
            conn.commit()

        content = messagestart + " <t:" + str(timestamp) + "> " + messageend
        embed.add_field("Countdown", content)
        embed.color = int(('#%02x%02x%02x' % (0, 255, 0)).replace("#", "0x"), base=16)

        if roleid != 0:
            try:
                await interactions.get(bot, interactions.User, object_id=roleid)
                await channel.send("<@" + str(roleid)+">", embeds=embed)
            except:
                await channel.send(f"{'<@&' + str(roleid) + '>' if roleid != guildid else '@everyone'}", embeds=embed, allowed_mentions={"parse":["roles", "everyone"]})
        else:
            await channel.send(embeds=embed)
        

timer_check.start()

#shard(bot)

bot.start()
