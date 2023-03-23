# Main library that makes all the bot stuff
import interactions

# Extension of interactions that handles tasks - i.e a thing that repeats at a given interval and does stuff.
from interactions.ext.tasks import IntervalTrigger, create_task

# handles shards Not active due to not needing shards.. yet
# from interactions.ext.autosharder import shard

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


bot = interactions.Client(token=TOKENSTRING, intents=interactions.Intents.GUILDS)

devservers = [1010636307216728094, 719541990580289557]


# Check this when activating shards
# This sets the bots presence to "Listening to /help"
@bot.event
async def on_start():
    await bot.change_presence(
        interactions.ClientPresence(
            status=interactions.StatusType.ONLINE,
            activities=[
                interactions.PresenceActivity(
                    name="/help", type=interactions.PresenceActivityType.LISTENING
                )
            ],
        )
    )


@bot.event
async def on_channel_delete(channel):
    command_builder.deleted_channel(channel)


@bot.event
async def on_thread_delete(thread):
    command_builder.deleted_channel(thread)


@bot.command(
    name="help",
    description="Shows a help message",
)
async def help(ctx: interactions.CommandContext):
    await command_builder.help_information(ctx)


@bot.command(
    name="premiuminfo",
    description="Get information about how premium works",
)
async def premiuminfo(ctx: interactions.CommandContext):
    await command_builder.premium_info(ctx)


@bot.command(
    name="generatetimestamp",
    description="Generates a timestamp based of the time.",
    options=[
        interactions.Option(
            name="timestring",
            description="What time do you want. Default timezone is ET.",
            type=interactions.OptionType.STRING,
            max_length=100,
            required=True,
        )
    ],
)
async def generatetimestamp(
    ctx: interactions.CommandContext,
    timestring,
):
    await command_builder.generate_timestamp(ctx, timestring)


@bot.command(
    name="countdown",
    description="Countdown to what you tells it to.",
    options=[
        interactions.Option(
            name="timestring",
            description="What time do you want. Default timezone is ET.",
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
            name="messageaftercomplete",
            description="Custom message when timer runs out (PREMIUM FEATURE)",
            type=interactions.OptionType.STRING,
            max_length=100,
            required=False,
        ),
        interactions.Option(
            name="countdownname",
            description="What should the name of the countdown be",
            type=interactions.OptionType.STRING,
            max_length=30,
            required=False,
        ),
        interactions.Option(
            name="mention",
            description="Who to mention",
            type=interactions.OptionType.MENTIONABLE,
            required=False,
        ),
        interactions.Option(
            name="repeat",
            description="Number of times to repeat (PREMIUM FEATURE)",
            type=interactions.OptionType.INTEGER,
            required=False,
            max_value=220,
        ),
        interactions.Option(
            name="repeattime",
            description="The time between each repeat in HOURS. Defaults to 24(each day) (PREMIUM FEATURE)",
            type=interactions.OptionType.INTEGER,
            required=False,
            max_value=1000,
        ),
        interactions.Option(
            name="image",
            description="Link to image to be shown at the end (PREMIUM FEATURE)",
            type=interactions.OptionType.STRING,
            required=False,
            max_length=200,
        ),
        interactions.Option(
            name="otherchannel",
            description="Send the countdown to another channel",
            type=interactions.OptionType.CHANNEL,
            required=False,
        ),
        interactions.Option(
            name="exact",
            description="Set to false if you dont want exact date",
            type=interactions.OptionType.BOOLEAN,
            required=False,
        ),
        interactions.Option(
            name="alert",
            description="Set to false if you dont want to be alerted at completion",
            type=interactions.OptionType.BOOLEAN,
            required=False,
        ),
    ],
)
async def countdown(
    ctx: interactions.CommandContext,
    timestring,
    messagestart="Countdown will end",
    messageend="!",
    messageaftercomplete="",
    countdownname="",
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
            name="messageaftercomplete",
            description="Custom message when timer runs out (PREMIUM FEATURE)",
            type=interactions.OptionType.STRING,
            max_length=100,
            required=False,
        ),
        interactions.Option(
            name="countdownname",
            description="What should the name of the countdown be",
            type=interactions.OptionType.STRING,
            max_length=30,
            required=False,
        ),
        interactions.Option(
            name="mention",
            description="Who to mention",
            type=interactions.OptionType.MENTIONABLE,
            required=False,
        ),
        interactions.Option(
            name="repeat",
            description="Number of times to repeat (PREMIUM FEATURE)",
            type=interactions.OptionType.INTEGER,
            required=False,
            max_value=220,
        ),
        interactions.Option(
            name="image",
            description="Link to image to be shown at the end (PREMIUM FEATURE)",
            type=interactions.OptionType.STRING,
            required=False,
            max_length=200,
        ),
        interactions.Option(
            name="otherchannel",
            description="Send the countdown to another channel",
            type=interactions.OptionType.CHANNEL,
            required=False,
        ),
        interactions.Option(
            name="exact",
            description="Set to false if you dont want exact date",
            type=interactions.OptionType.BOOLEAN,
            required=False,
        ),
        interactions.Option(
            name="alert",
            description="Set to false if you dont want to be alerted at completion",
            type=interactions.OptionType.BOOLEAN,
            required=False,
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
    messageaftercomplete="",
    countdownname="",
    mention="0",
    repeat=0,
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
        image,
        otherchannel,
        exact,
        alert,
        bot,
    )


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
    await command_builder.list_countdowns(ctx, sub_command, page)


@bot.command(
    name="timeleft",
    description="Shows the exact time left of a countdown",
    options=[
        interactions.Option(
            name="mine",
            description="Shows one of your countdowns",
            type=interactions.OptionType.SUB_COMMAND,
            options=[
                interactions.Option(
                    type=interactions.OptionType.STRING,
                    name="showmine",
                    description="Which of your countdowns do you want to be shown?",
                    required=True,
                    autocomplete=True,
                ),
                interactions.Option(
                    name="hidden",
                    description="Set to false if you want everyone to see",
                    type=interactions.OptionType.BOOLEAN,
                    required=False,
                ),
            ],
        ),
        interactions.Option(
            name="channel",
            description="Show one of this channels countdowns",
            type=interactions.OptionType.SUB_COMMAND,
            options=[
                interactions.Option(
                    type=interactions.OptionType.STRING,
                    name="showchannel",
                    description="Which of this channels countdowns do you want to be shown?",
                    required=True,
                    autocomplete=True,
                ),
                interactions.Option(
                    name="hidden",
                    description="Set to false if you want everyone to see",
                    type=interactions.OptionType.BOOLEAN,
                    required=False,
                ),
            ],
        ),
        interactions.Option(
            name="guild",
            description="Show one of this guilds countdowns",
            type=interactions.OptionType.SUB_COMMAND,
            options=[
                interactions.Option(
                    type=interactions.OptionType.STRING,
                    name="showguild",
                    description="Which of this guilds countdowns do you want to be shown?",
                    required=True,
                    autocomplete=True,
                ),
                interactions.Option(
                    name="hidden",
                    description="Set to false if you want everyone to see",
                    type=interactions.OptionType.BOOLEAN,
                    required=False,
                ),
            ],
        ),
    ],
)
async def timeleft(
    ctx: interactions.CommandContext,
    sub_command: str,
    showmine: str = "",
    showchannel: str = "",
    showguild: str = "",
    hidden=True,
):

    await command_builder.time_left(
        ctx, sub_command, showmine, showchannel, showguild, hidden
    )


@bot.autocomplete("timeleft", "showmine")
async def autocompleteMine(ctx: interactions.CommandContext, value: str = ""):
    await command_builder.autocomplete_countdowns(ctx, value, "mine")


@bot.autocomplete("timeleft", "showchannel")
async def autocompleteMine(ctx: interactions.CommandContext, value: str = ""):
    await command_builder.autocomplete_countdowns(ctx, value, "channel")


@bot.autocomplete("timeleft", "showguild")
async def autocompleteMine(ctx: interactions.CommandContext, value: str = ""):
    await command_builder.autocomplete_countdowns(ctx, value, "guild")


@bot.command(
    name="delete",
    description="Deletes countdowns",
    dm_permission=False,
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
            name="mine",
            description="Delete all your countdowns in this guild",
            type=interactions.OptionType.SUB_COMMAND,
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
    await command_builder.delete(
        bot, ctx, sub_command, sub_command_group, deletemine, deletechannel, deleteguild
    )


@bot.autocomplete("delete", "deletemine")
async def autocompleteMine(ctx: interactions.CommandContext, value: str = ""):
    await command_builder.autocomplete_countdowns(ctx, value, "mine")


@bot.autocomplete("delete", "deletechannel")
async def autocompleteMine(ctx: interactions.CommandContext, value: str = ""):
    await command_builder.autocomplete_countdowns(ctx, value, "channel")


@bot.autocomplete("delete", "deleteguild")
async def autocompleteMine(ctx: interactions.CommandContext, value: str = ""):
    await command_builder.autocomplete_countdowns(ctx, value, "guild")


# Here are the functions that runs when the verify/cancel buttons are pressed
@bot.component("deleteguild")
async def button_response(ctx):
    await command_builder.delete_button(bot, ctx, "guild")


@bot.component("deletechannel")
async def button_response(ctx):
    await command_builder.delete_button(bot, ctx, "channel")


@bot.component("deletemine")
async def button_response(ctx):
    await command_builder.delete_button(bot, ctx, "mine")


@bot.component("deletecancel")
async def button_response(ctx):
    await command_builder.delete_button(ctx, "cancel")


@bot.command(
    name="botstats",
    description="Shows stats of bot",
)
async def botstats(ctx: interactions.CommandContext):
    await command_builder.botstats(ctx, bot)


@bot.command(
    name="fixperms",
    description="Fixes the permissions for this channel",
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
)
async def fixperms(ctx: interactions.CommandContext):
    await command_builder.fixperms(ctx, bot)


# This command is not entierly active yet. It is just a prototype for when the bot is availible in multiple languages.
@bot.command(
    name="translate",
    description="Translate the bot",
    scope=devservers,
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    dm_permission=False,
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
    await command_builder.translate(ctx, language)


# a dev program
@bot.command(
    name="log",
    description="Show the log",
    scope=devservers,
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
)
async def log(ctx: interactions.CommandContext):
    await command_builder.log(ctx)


@bot.command(
    name="addpremium",
    description="add a premium guild",
    scope=devservers,
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    options=[
        interactions.Option(
            name="userid",
            description="Whos the user",
            type=interactions.OptionType.STRING,
            max_length=50,
            required=True,
        ),
        interactions.Option(
            name="guildid",
            description="What guild do you want it to?",
            type=interactions.OptionType.STRING,
            max_length=50,
            required=False,
        ),
        interactions.Option(
            name="level",
            description="What level?",
            type=interactions.OptionType.INTEGER,
            required=False,
            max_value=50,
        ),
    ],
)
async def addpremium(ctx: interactions.CommandContext, userid, guildid=0, level=1):
    await command_builder.add_premium(ctx, userid, guildid, level)


@bot.command(
    name="deletepremium",
    description="Delete a premium user",
    scope=devservers,
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    options=[
        interactions.Option(
            name="userid",
            description="Whos the user",
            type=interactions.OptionType.STRING,
            max_length=50,
            required=True,
        ),
        interactions.Option(
            name="level",
            description="Up to what level?",
            type=interactions.OptionType.INTEGER,
            required=False,
            max_value=50,
        ),
    ],
)
async def deletepremium(ctx: interactions.CommandContext, userid, level=1):
    await command_builder.delete_premium(ctx, userid, level)


@bot.command(
    name="makethispremium",
    description="Changes so this guild becomes your premium guild",
    dm_permission=False,
)
async def makethispremium(ctx: interactions.CommandContext):
    await command_builder.make_this_premium(ctx)


@bot.command(
    name="listpremium",
    description="List all premium guild",
    scope=devservers,
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
    options=[
        interactions.Option(
            name="page",
            description="What page number",
            type=interactions.OptionType.INTEGER,
            required=False,
            max_value=100,
        ),
    ],
)
async def listpremium(ctx: interactions.CommandContext, page=1):
    await command_builder.list_premium(ctx, page)


# Here are message commands - commands that are activated by a message
@bot.command(
    name="deletethis",
    description="Delete this countdown",
    type=interactions.ApplicationCommandType.MESSAGE,
)
async def deletethis(ctx: interactions.CommandContext):
    await command_builder.delete_this(bot, ctx)


@bot.command(
    name="timeleftthis",
    description="See exact time left of this countdown",
    type=interactions.ApplicationCommandType.MESSAGE,
)
async def timeleftthis(ctx: interactions.CommandContext):
    await command_builder.timeleft_this(ctx)


# Jokes
@bot.command(
    name="whoisthegreatest",
    description="If you are curious about who the greatest is",
)
async def timeleftthis(ctx: interactions.CommandContext):
    await ctx.send("<@729791860674920488>")


@bot.command(
    name="whoistheboss",
    description="If you are curious about who the boss is",
)
async def timeleftthis(ctx: interactions.CommandContext):
    await ctx.send(
        "<@360084558265450496>",
        ephemeral=True,
    )


# This is the task that keeps looking if any countdowns are done.
@create_task(IntervalTrigger(5))  # 5 means execute task each 5 second
async def timer_check():
    await command_builder.check_done(bot)


timer_check.start()

# shard(bot)

# Start the bot!
bot.start()
