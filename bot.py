# Main library that makes all the bot stuff
import interactions

# Extension of interactions that handles tasks - i.e a thing that repeats at a given interval and does stuff.
from interactions.ext.tasks import IntervalTrigger, create_task

# handles shards Not active due to not needing shards.. yet
# from interactions.ext.autosharder import shard

# This is where the commands are made
import commandBuilder

import logging
logging.basicConfig(filename='log.txt', level=logging.WARNING, format='')


# These two are used to have the token as a .env file.
from os import getenv
from dotenv import load_dotenv

load_dotenv()
TOKENSTRING = getenv("DISCORD_TOKEN")


bot = interactions.Client(token=TOKENSTRING, disable_sync=False)


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
    await commandBuilder.help(ctx)


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
        interactions.Option(
            name="image",
            description="Link to image to be shown at the end (PREMIUM FEATURE)",
            type=interactions.OptionType.STRING,
            required=False,
            max_length=200,
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
    image=""
):
    await commandBuilder.countdown(
        ctx, timestring, messagestart, messageend, mention, times, image
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
        interactions.Option(
            name="image",
            description="Link to image to be shown at the end (PREMIUM FEATURE)",
            type=interactions.OptionType.STRING,
            required=False,
            max_length=200,
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
    image=""
):

    await commandBuilder.timer(
        ctx, day, week, hour, minute, messagestart, messageend, mention, times, image
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
    await commandBuilder.list(ctx, sub_command, page)


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
    await commandBuilder.delete(
        ctx, sub_command, sub_command_group, deletemine, deletechannel, deleteguild
    )


@bot.autocomplete("delete", "deletemine")
async def autocompleteMine(ctx: interactions.CommandContext, value: str = ""):
    await commandBuilder.autocompleteDelete(ctx, value, "mine")


@bot.autocomplete("delete", "deletechannel")
async def autocompleteMine(ctx: interactions.CommandContext, value: str = ""):
    await commandBuilder.autocompleteDelete(ctx, value, "channel")


@bot.autocomplete("delete", "deleteguild")
async def autocompleteMine(ctx: interactions.CommandContext, value: str = ""):
    await commandBuilder.autocompleteDelete(ctx, value, "guild")


# Here are the functions that runs when the verify/cancel buttons are pressed
@bot.component("deleteguild")
async def button_response(ctx):
    await commandBuilder.deletebutton(ctx, "guild")


@bot.component("deletechannel")
async def button_response(ctx):
    await commandBuilder.deletebutton(ctx, "channel")


@bot.component("deletecancel")
async def button_response(ctx):
    await commandBuilder.deletebutton(ctx, "cancel")


@bot.command(
    name="botstats",
    description="Shows stats of bot",
)
async def botstats(ctx: interactions.CommandContext):
    await commandBuilder.botstats(ctx, bot)


# This command is not entierly active yet. It is just a prototype for when the bot is availible in multiple languages.
@bot.command(
    name="translate",
    description="Translate the bot",
    scope=1010636307216728094,
    default_member_permissions=interactions.Permissions.ADMINISTRATOR,
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
    await commandBuilder.translate(ctx, language, bot)


# This is the task that keeps looking if any countdowns are done.
@create_task(IntervalTrigger(5))  # 5 means execute task each 5 second
async def timer_check():
    await commandBuilder.checkDone(bot)


timer_check.start()

# shard(bot)

# Start the bot!
bot.start()
