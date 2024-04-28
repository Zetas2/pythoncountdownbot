# Main library that makes all the bot stuff
import interactions

# Importing from interactions for v5 conversion

from interactions import SlashCommandOption

# This is where the commands are made
import command_builder

import logging

logging.basicConfig(
    filename="log.txt", level=logging.WARNING, format="%(asctime)s - %(message)s"
)

# These two are used to have the token as a .env file.
from os import getenv
from dotenv import load_dotenv

load_dotenv()
TOKENSTRING = getenv("DISCORD_TOKEN")


bot = interactions.AutoShardedClient(
    token=TOKENSTRING, intents=interactions.Intents.GUILDS
)

devservers = [1010636307216728094]


# Check this when activating shards
# This sets the bots presence to "Listening to /help"
@interactions.listen()
async def on_startup():
    timer_check.start()
    await bot.change_presence(status=interactions.Status.ONLINE, activity="/help")


@bot.event
async def on_channel_delete(channel):
    command_builder.deleted_channel(channel)


@bot.event
async def on_thread_delete(thread):
    command_builder.deleted_channel(thread)


@interactions.slash_command(
    name="help",
    description="Shows a help message",
)
async def help(ctx: interactions.SlashContext):
    await command_builder.help_information(ctx)


@interactions.slash_command(
    name="premiuminfo",
    description="Get information about how premium works",
)
async def premiuminfo(ctx: interactions.SlashContext):
    await command_builder.premium_info(ctx)


@interactions.slash_command(
    name="generatetimestamp",
    description="Generates a timestamp based of the time.",
    options=[
        SlashCommandOption(
            name="timestring",
            description="What time do you want. Default timezone is ET.",
            type=interactions.OptionType.STRING,
            max_length=100,
            required=True,
        )
    ],
)
async def generatetimestamp(
    ctx: interactions.SlashContext,
    timestring,
):
    await command_builder.generate_timestamp(ctx, timestring)


# ------------------------------------------------ TIMERS ----------------------------------------------------------
@interactions.slash_command(
    name="countdown",
    description="Countdown to what you tells it to.",
    options=[
        SlashCommandOption(
            name="timestring",
            description="What time do you want. Default timezone is ET.",
            type=interactions.OptionType.STRING,
            max_length=100,
            required=True,
        ),
        SlashCommandOption(
            name="messagestart",
            description="Custom message before timer",
            type=interactions.OptionType.STRING,
            max_length=100,
            required=False,
        ),
        SlashCommandOption(
            name="messageend",
            description="Custom message after timer",
            type=interactions.OptionType.STRING,
            max_length=100,
            required=False,
        ),
        SlashCommandOption(
            name="messageaftercomplete",
            description="Custom message when timer runs out (PREMIUM FEATURE)",
            type=interactions.OptionType.STRING,
            max_length=100,
            required=False,
        ),
        SlashCommandOption(
            name="countdownname",
            description="What should the name of the countdown be",
            type=interactions.OptionType.STRING,
            max_length=30,
            required=False,
        ),
        SlashCommandOption(
            name="mention",
            description="Who to mention",
            type=interactions.OptionType.MENTIONABLE,
            required=False,
        ),
        SlashCommandOption(
            name="repeat",
            description="Number of times to repeat (PREMIUM FEATURE)",
            type=interactions.OptionType.INTEGER,
            required=False,
            max_value=1000,
        ),
        SlashCommandOption(
            name="repeattime",
            description="The time between each repeat in HOURS. Defaults to 24(each day) (PREMIUM FEATURE)",
            type=interactions.OptionType.INTEGER,
            required=False,
            max_value=1000,
        ),
        SlashCommandOption(
            name="image",
            description="Link to image to be shown at the end (PREMIUM FEATURE)",
            type=interactions.OptionType.STRING,
            required=False,
            max_length=200,
        ),
        SlashCommandOption(
            name="otherchannel",
            description="Send the countdown to another channel",
            type=interactions.OptionType.CHANNEL,
            required=False,
        ),
        SlashCommandOption(
            name="exact",
            description="Set to false if you dont want exact date",
            type=interactions.OptionType.BOOLEAN,
            required=False,
        ),
        SlashCommandOption(
            name="alert",
            description="Set to false if you dont want to be alerted at completion",
            type=interactions.OptionType.BOOLEAN,
            required=False,
        ),
    ],
)
async def countdown(
    ctx: interactions.SlashContext,
    timestring,
    messagestart="Countdown will end",
    messageend="!",
    messageaftercomplete="",
    countdownname=None,
    mention="0",
    repeat=0,
    repeattime=24,
    image="",
    otherchannel=None,
    exact=False,
    alert=True,
    bot=bot,
):
    await command_builder.countdown(
        ctx,
        timestring,
        messagestart,
        messageend,
        messageaftercomplete,
        countdownname,
        mention,
        repeat,
        repeattime,
        image,
        otherchannel,
        exact,
        alert,
        bot,
    )


@interactions.slash_command(
    name="timer",
    description="Lets add a timer",
    options=[
        SlashCommandOption(
            name="minute",
            description="How many minutes",
            type=interactions.OptionType.INTEGER,
            required=False,
            max_value=1000,
        ),
        SlashCommandOption(
            name="hour",
            description="How many hours",
            type=interactions.OptionType.INTEGER,
            required=False,
            max_value=1000,
        ),
        SlashCommandOption(
            name="day",
            description="How many days",
            type=interactions.OptionType.INTEGER,
            required=False,
            max_value=1000,
        ),
        SlashCommandOption(
            name="week",
            description="How many weeks",
            type=interactions.OptionType.INTEGER,
            required=False,
            max_value=1000,
        ),
        SlashCommandOption(
            name="messagestart",
            description="Custom message before timer",
            type=interactions.OptionType.STRING,
            max_length=100,
            required=False,
        ),
        SlashCommandOption(
            name="messageend",
            description="Custom message after timer",
            type=interactions.OptionType.STRING,
            max_length=100,
            required=False,
        ),
        SlashCommandOption(
            name="messageaftercomplete",
            description="Custom message when timer runs out (PREMIUM FEATURE)",
            type=interactions.OptionType.STRING,
            max_length=100,
            required=False,
        ),
        SlashCommandOption(
            name="countdownname",
            description="What should the name of the countdown be",
            type=interactions.OptionType.STRING,
            max_length=30,
            required=False,
        ),
        SlashCommandOption(
            name="mention",
            description="Who to mention",
            type=interactions.OptionType.MENTIONABLE,
            required=False,
        ),
        SlashCommandOption(
            name="repeat",
            description="Number of times to repeat (PREMIUM FEATURE)",
            type=interactions.OptionType.INTEGER,
            required=False,
            max_value=1000,
        ),
        SlashCommandOption(
            name="preset",
            description="Save this timer as a preset (PREMIUM FEATURE)",
            type=interactions.OptionType.INTEGER,
            required=False,
            min_value=1,
            max_value=20,
        ),
        SlashCommandOption(
            name="image",
            description="Link to image to be shown at the end (PREMIUM FEATURE)",
            type=interactions.OptionType.STRING,
            required=False,
            max_length=200,
        ),
        SlashCommandOption(
            name="otherchannel",
            description="Send the countdown to another channel",
            type=interactions.OptionType.CHANNEL,
            required=False,
        ),
        SlashCommandOption(
            name="exact",
            description="Set to false if you dont want exact date",
            type=interactions.OptionType.BOOLEAN,
            required=False,
        ),
        SlashCommandOption(
            name="alert",
            description="Set to false if you dont want to be alerted at completion",
            type=interactions.OptionType.BOOLEAN,
            required=False,
        ),
    ],
)
async def timer(
    ctx: interactions.SlashContext,
    day=0,
    week=0,
    hour=0,
    minute=0,
    messagestart="Timer will end",
    messageend="!",
    messageaftercomplete="",
    countdownname=None,
    mention="0",
    repeat=0,
    preset=0,
    image="",
    otherchannel=None,
    exact=False,
    alert=True,
    bot=bot,
):
    await command_builder.timer(
        ctx,
        day,
        week,
        hour,
        minute,
        messagestart,
        messageend,
        messageaftercomplete,
        countdownname,
        mention,
        repeat,
        preset,
        image,
        otherchannel,
        exact,
        alert,
        bot,
    )


# ------------------------------------------------ PRESETS ----------------------------------------------------------


@interactions.slash_command(
    name="preset",
    description="Use a preset timer",
    options=[
        SlashCommandOption(
            name="presetid",
            description="What id of the preset",
            type=interactions.OptionType.INTEGER,
            required=True,
            max_value=20,
            min_value=1,
        )
    ],
)
async def preset(ctx: interactions.SlashContext, presetid=0, bot=bot):
    await command_builder.preset(ctx, presetid, bot)


@interactions.slash_command(
    name="listpreset",
    description="List all presets",
    options=[
        SlashCommandOption(
            name="page",
            description="What page number",
            type=interactions.OptionType.INTEGER,
            required=False,
            max_value=100,
        )
    ],
)
async def listpreset(ctx: interactions.SlashContext, page=1):
    await command_builder.list_preset(ctx, page)


# ------------------------------------------------ LISTS ----------------------------------------------------------
@interactions.slash_command(
    name="listchannel",
    description="List all countdowns in a channel",
    options=[
        SlashCommandOption(
            name="page",
            description="What page number",
            type=interactions.OptionType.INTEGER,
            required=False,
        ),
        SlashCommandOption(
            name="hidden",
            description="Set to false if you want everyone to see",
            type=interactions.OptionType.BOOLEAN,
            required=False,
        ),
    ],
)
async def listchannel(ctx: interactions.SlashContext, page=1, hidden=True):
    await command_builder.list_countdowns(ctx, "channel", page, hidden)


@interactions.slash_command(
    name="listguild",
    description="List all countdowns in a guild",
    options=[
        SlashCommandOption(
            name="page",
            description="What page number",
            type=interactions.OptionType.INTEGER,
            required=False,
        ),
        SlashCommandOption(
            name="hidden",
            description="Set to false if you want everyone to see",
            type=interactions.OptionType.BOOLEAN,
            required=False,
        ),
    ],
)
async def listguild(ctx: interactions.SlashContext, page=1, hidden=True):
    await command_builder.list_countdowns(ctx, "guild", page, hidden)


@interactions.slash_command(
    name="listmine",
    description="List all your contdowns countdowns",
    options=[
        SlashCommandOption(
            name="page",
            description="What page number",
            type=interactions.OptionType.INTEGER,
            required=False,
        ),
        SlashCommandOption(
            name="hidden",
            description="Set to false if you want everyone to see",
            type=interactions.OptionType.BOOLEAN,
            required=False,
        ),
    ],
)
async def listmine(ctx: interactions.SlashContext, page=1, hidden=True):
    await command_builder.list_countdowns(ctx, "mine", page, hidden)


# ------------------------------------------------ TIMELEFT ----------------------------------------------------------
@interactions.slash_command(
    name="timeleftmine",
    description="Shows the exact time left of a countdown you created",
    options=[
        SlashCommandOption(
            type=interactions.OptionType.STRING,
            name="showmine",
            description="Which of your countdowns do you want to be shown?",
            required=True,
            autocomplete=True,
        ),
        SlashCommandOption(
            name="hidden",
            description="Set to false if you want everyone to see",
            type=interactions.OptionType.BOOLEAN,
            required=False,
        ),
    ],
)
async def timeleftmine(
    ctx: interactions.SlashContext,
    showmine: str = "",
    hidden=True,
):
    await command_builder.time_left(ctx, showmine, hidden)


@timeleftmine.autocomplete("showmine")
async def autocomplete_timeleftmine(
    ctx: interactions.AutocompleteContext, value: str = ""
):
    await command_builder.autocomplete_countdowns(ctx, value, "mine")


@interactions.slash_command(
    name="timeleftchannel",
    description="Shows the exact time left of a countdown in the channel",
    options=[
        SlashCommandOption(
            type=interactions.OptionType.STRING,
            name="showchannel",
            description="Which of the channels countdowns do you want to be shown?",
            required=True,
            autocomplete=True,
        ),
        SlashCommandOption(
            name="hidden",
            description="Set to false if you want everyone to see",
            type=interactions.OptionType.BOOLEAN,
            required=False,
        ),
    ],
)
async def timeleftchannel(
    ctx: interactions.SlashContext,
    showchannel: str = "",
    hidden=True,
):
    await command_builder.time_left(ctx, showchannel, hidden)


@timeleftchannel.autocomplete("showchannel")
async def autocomplete_timeleftchannel(
    ctx: interactions.AutocompleteContext, value: str = ""
):
    await command_builder.autocomplete_countdowns(ctx, value, "channel")


@interactions.slash_command(
    name="timeleftguild",
    description="Shows the exact time left of a countdown in the guild",
    options=[
        SlashCommandOption(
            type=interactions.OptionType.STRING,
            name="showguild",
            description="Which of the guilds countdowns do you want to be shown?",
            required=True,
            autocomplete=True,
        ),
        SlashCommandOption(
            name="hidden",
            description="Set to false if you want everyone to see",
            type=interactions.OptionType.BOOLEAN,
            required=False,
        ),
    ],
)
async def timeleftguild(
    ctx: interactions.SlashContext,
    showguild: str = "",
    hidden=True,
):
    await command_builder.time_left(ctx, showguild, hidden)


@timeleftguild.autocomplete("showguild")
async def autocomplete_timeleftguild(
    ctx: interactions.AutocompleteContext, value: str = ""
):
    await command_builder.autocomplete_countdowns(ctx, value, "guild")


# ------------------------------------------------ DELETE ----------------------------------------------------------
delete_mine_command = interactions.SlashCommand(
    name="deletemine",
    description="Delete one or all of your countdowns",
    dm_permission=False,
)


@delete_mine_command.subcommand(
    sub_cmd_name="single",
    sub_cmd_description="Deletes a single of your countdowns",
    options=[
        SlashCommandOption(
            type=interactions.OptionType.STRING,
            name="deleteid",
            description="Which of your countdowns do you want to be deleted?",
            required=True,
            autocomplete=True,
        )
    ],
)
async def delete_single_mine(ctx: interactions.SlashContext, deleteid: str = ""):
    await command_builder.delete(bot, ctx, "mine", "single", deleteid)


@delete_single_mine.autocomplete("deleteid")
async def autocomplete_mine(ctx: interactions.AutocompleteContext):
    await command_builder.autocomplete_countdowns(ctx, ctx.input_text, "mine")


@delete_mine_command.subcommand(
    sub_cmd_name="all",
    sub_cmd_description="Deletes all of your countdowns",
)
async def delete_mine(ctx: interactions.SlashContext):
    await command_builder.delete(bot, ctx, "mine", "all", "NA")


delete = interactions.SlashCommand(
    name="delete",
    description="Delete one or all of the countdowns in this channel/guild",
    dm_permission=False,
    default_member_permissions=interactions.Permissions.MANAGE_MESSAGES,
)

delete_channel_command = delete.group(
    name="channel", description="Delete one or all of the countdowns in this channel"
)


@delete_channel_command.subcommand(
    sub_cmd_name="single",
    sub_cmd_description="Deletes a single of the channels countdowns",
    options=[
        SlashCommandOption(
            type=interactions.OptionType.STRING,
            name="deleteid",
            description="Which of the channels countdowns do you want to be deleted?",
            required=True,
            autocomplete=True,
        )
    ],
)
async def delete_single_channel(ctx: interactions.SlashContext, deleteid: str = ""):
    await command_builder.delete(bot, ctx, "mine", "channel", deleteid)


@delete_single_channel.autocomplete("deleteid")
async def autocomplete_channel(ctx: interactions.AutocompleteContext):
    await command_builder.autocomplete_countdowns(ctx, ctx.input_text, "channel")


@delete_channel_command.subcommand(
    sub_cmd_name="all",
    sub_cmd_description="Deletes all of the channels countdowns",
)
async def delete_channel_command(ctx: interactions.SlashContext):
    await command_builder.delete(bot, ctx, "channel", "all", "NA")


delete_guild_command = delete.group(
    name="guild", description="Delete one or all of the countdowns in this guild"
)


@delete_guild_command.subcommand(
    sub_cmd_name="single",
    sub_cmd_description="Deletes a single of the guilds countdowns",
    options=[
        SlashCommandOption(
            type=interactions.OptionType.STRING,
            name="deleteid",
            description="Which of the guilds countdowns do you want to be deleted?",
            required=True,
            autocomplete=True,
        )
    ],
)
async def delete_single_guild(ctx: interactions.SlashContext, deleteid: str = ""):
    await command_builder.delete(bot, ctx, "mine", "guild", deleteid)


@delete_single_guild.autocomplete("deleteid")
async def autocomplete_guild(ctx: interactions.AutocompleteContext):
    await command_builder.autocomplete_countdowns(ctx, ctx.input_text, "guild")


@delete_guild_command.subcommand(
    sub_cmd_name="all",
    sub_cmd_description="Deletes all of the guilds countdowns",
)
async def delete_guild_command(ctx: interactions.SlashContext):
    await command_builder.delete(bot, ctx, "guild", "all", "NA")


@interactions.listen(interactions.api.events.Component)
async def on_component(event: interactions.api.events.Component):
    ctx = event.ctx
    match ctx.custom_id:
        case "deletemine":
            await command_builder.delete_button(ctx, "mine")
        case "deletechannel":
            await command_builder.delete_button(ctx, "channel")
        case "deleteguild":
            await command_builder.delete_button(ctx, "guild")
        case "deletecancel":
            await command_builder.delete_button(ctx, "cancel")


# ------------------------------------------------ OTHER ----------------------------------------------------------
@interactions.slash_command(
    name="botstats",
    description="Shows stats of bot",
)
async def botstats(ctx: interactions.SlashContext):
    await command_builder.botstats(ctx, bot)


@interactions.slash_command(
    name="fixperms",
    description="Fixes the permissions for this channel",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
)
async def fixperms(ctx: interactions.SlashContext):
    await command_builder.fixperms(ctx, bot)


@interactions.slash_command(
    name="editmention",
    description="Change who to mention at the end of a countdown",
    options=[
        SlashCommandOption(
            type=interactions.OptionType.STRING,
            name="countdown",
            description="Which of your countdowns do you want to be shown?",
            required=True,
            autocomplete=True,
        ),
        SlashCommandOption(
            name="mention",
            description="Who to mention",
            type=interactions.OptionType.MENTIONABLE,
            required=True,
        ),
    ],
)
async def editmention(
    ctx: interactions.SlashContext,
    countdown="",
    mention="0",
):
    await command_builder.edit_mention(ctx, countdown, mention)


@editmention.autocomplete("countdown")
async def autocomplete_editmention(
    ctx: interactions.AutocompleteContext, value: str = ""
):
    await command_builder.autocomplete_countdowns(ctx, value, "mine")


# This command is not entierly active yet. It is just a prototype for when the bot is availible in multiple languages.
# @interactions.slash_command(
#    name="translate",
#    description="Translate the bot",
#    scope=devservers,
#    dm_permission=False,
#    slash_default_member_permission=interactions.Permissions.ADMINISTRATOR,
#    options=[
#        SlashCommandOption(
#        name="language",
#        description="What language do you want to translate to?",
#        type=interactions.OptionType.STRING,
#        required=True,
#        choices=[interactions.Choice(name="English", value="en-US")],
#        )
#    ]
# )
# async def translate(ctx: interactions.SlashContext, language):
#    await command_builder.translate(ctx, language)


# ------------------------------------------------ DEV ----------------------------------------------------------
@interactions.slash_command(
    name="log",
    description="Show the log",
    scopes=devservers,
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
)
async def log(ctx: interactions.SlashContext):
    await command_builder.log(ctx)


@interactions.slash_command(
    name="addpremium",
    description="add a premium guild",
    scopes=devservers,
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    options=[
        SlashCommandOption(
            name="userid",
            description="Whos the user",
            type=interactions.OptionType.STRING,
            max_length=50,
            required=True,
        ),
        SlashCommandOption(
            name="guildid",
            description="What guild do you want it to?",
            type=interactions.OptionType.STRING,
            max_length=50,
            required=False,
        ),
        SlashCommandOption(
            name="level",
            description="What level?",
            type=interactions.OptionType.INTEGER,
            required=False,
            max_value=50,
        ),
    ],
)
async def addpremium(ctx: interactions.SlashContext, userid, guildid=0, level=1):
    await command_builder.add_premium(ctx, userid, guildid, level)


@interactions.slash_command(
    name="deletepremium",
    description="Delete a premium user",
    scopes=devservers,
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    options=[
        SlashCommandOption(
            name="userid",
            description="Whos the user",
            type=interactions.OptionType.STRING,
            max_length=50,
            required=True,
        ),
        SlashCommandOption(
            name="level",
            description="Down to what level?",
            type=interactions.OptionType.INTEGER,
            required=False,
            max_value=50,
        ),
    ],
)
async def deletepremium(ctx: interactions.SlashContext, userid, level=1):
    await command_builder.delete_premium(ctx, userid, level)


@interactions.slash_command(
    name="makethispremium",
    description="Changes so this guild becomes your premium guild",
    dm_permission=False,
    options=[
        SlashCommandOption(
            name="index",
            description="What premium number",
            type=interactions.OptionType.INTEGER,
            min_value=1,
            required=True,
        )
    ],
)
async def makethispremium(ctx: interactions.SlashContext, index=1):
    await command_builder.make_this_premium(ctx, index)


@interactions.slash_command(
    name="listpremium",
    description="List all premium guild",
    scopes=devservers,
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    options=[
        SlashCommandOption(
            name="page",
            description="What page number",
            type=interactions.OptionType.INTEGER,
            required=False,
            max_value=100,
        )
    ],
)
async def listpremium(ctx: interactions.SlashContext, page=1):
    await command_builder.list_premium(ctx, page)


@interactions.slash_command(
    name="latencies",
    description="List all latencies",
    scopes=devservers,
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
)
async def latencies(ctx: interactions.SlashContext):
    result = bot.latencies
    await ctx.send(f"{result}")


@interactions.slash_command(
    name="killitwithfire",
    description="Restarts the bot hopefully",
    scopes=devservers,
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
)
async def killitwithfire(ctx: interactions.SlashContext):
    await ctx.send("restarting")
    await bot.stop()


# Here are message commands - commands that are activated by a message
@interactions.message_context_menu(
    name="deletethis",
)
async def deletethis(ctx: interactions.SlashContext):
    await command_builder.delete_this(bot, ctx)


@interactions.message_context_menu(
    name="timeleftthis",
)
async def timeleftthis(ctx: interactions.SlashContext):
    await command_builder.timeleft_this(ctx)


# Jokes
@interactions.slash_command(
    name="whoisthegreatest",
    description="If you are curious about who the greatest is",
)
async def whoisthegreatest(ctx: interactions.SlashContext):
    await ctx.send("<@729791860674920488>")


@interactions.slash_command(
    name="whoistheboss",
    description="If you are curious about who the boss is",
)
async def whoistheboss(ctx: interactions.SlashContext):
    await ctx.send(
        "<@360084558265450496>",
        ephemeral=True,
    )


# This is the task that keeps looking if any countdowns are done.
@interactions.Task.create(
    interactions.IntervalTrigger(5)
)  # 5 means execute task each 5 second
async def timer_check():
    await command_builder.check_done(bot)


# Start the bot!
bot.start()
