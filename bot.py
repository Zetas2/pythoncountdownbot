# Main library that makes all the bot stuff
import interactions

# Importing from interactions for v5 conversion
from interactions import (
    slash_command,
    SlashContext,
    OptionType,
    SlashCommandChoice,
    AutocompleteContext,
    slash_default_member_permission,
    slash_option,
    SlashCommandOption,
    slash_int_option,
)

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
            max_value=220,
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
            max_value=220,
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


# @interactions.slash_command(
#    name="list",
#    description="List all countdowns",
#    options=[
#        SlashCommandOption(
#            name="channel",
#            description="List all countdowns in channel",
#            type=interactions.OptionType.SUB_COMMAND,
#            options=[
#                SlashCommandOption(
#                    name="page",
#                    description="What page number",
#                    type=interactions.OptionType.INTEGER,
#                    required=False,
#               ),
#                SlashCommandOption(
#                    name="hidden",
#                    description="Set to false if you want everyone to see",
#                    type=interactions.OptionType.BOOLEAN,
#                    required=False,
#                )
#            ]
#        ),
#        SlashCommandOption(
#            name="guild",
#            description="List all countdowns in guild",
#            type=interactions.OptionType.SUB_COMMAND,
#            options=[
#                SlashCommandOption(
#                    name="page",
#                    description="What page number",
#                    type=interactions.OptionType.INTEGER,
#                    required=False,
#                    max_value=50,
#                ),
#                SlashCommandOption(
#                    name="hidden",
#                    description="Set to false if you want everyone to see",
#                    type=interactions.OptionType.BOOLEAN,
#                    required=False,
#                )
#            ]
#        ),
#        SlashCommandOption(
#            name="mine",
#            description="List all countdowns activated by you",
#            type=interactions.OptionType.SUB_COMMAND,
#            options=[
#                SlashCommandChoice(
#                    name="page",
#                    description="What page number",
#                    type=interactions.OptionType.INTEGER,
#                    required=False,
#                    max_value=50,
#                ),
#                SlashCommandChoice(
#                    name="hidden",
#                    description="Set to false if you want everyone to see",
#                    type=interactions.OptionType.BOOLEAN,
#                    required=False,
#                )
#            ]
#        )
#    ]
# )
# async def list(ctx: interactions.SlashContext, sub_command: str, page=1, hidden=True):
#    await command_builder.list_countdowns(ctx, sub_command, page, hidden)


# @interactions.slash_command(
#    name="timeleft",
#    description="Shows the exact time left of a countdown",
#    options=[
#        SlashCommandOption(
#            name="mine",
#            description="Shows one of your countdowns",
#            type=interactions.OptionType.SUB_COMMAND,
#            options=[
#                SlashCommandOption(
#                    type=interactions.OptionType.STRING,
#                    name="showmine",
#                    description="Which of your countdowns do you want to be shown?",
#                    required=True,
#                    autocomplete=True,
#                ),
#                SlashCommandOption(
#                    name="hidden",
#                    description="Set to false if you want everyone to see",
#                    type=interactions.OptionType.BOOLEAN,
#                    required=False,
#                )
#            ]
#        ),
#        SlashCommandOption(
#            name="channel",
#            description="Show one of this channels countdowns",
#            type=interactions.OptionType.SUB_COMMAND,
#            options=[
#                SlashCommandOption(
#                    type=interactions.OptionType.STRING,
#                    name="showchannel",
#                    description="Which of this channels countdowns do you want to be shown?",
#                    required=True,
#                    autocomplete=True,
#                ),
#                SlashCommandChoice(
#                    name="hidden",
#                    description="Set to false if you want everyone to see",
#                    type=interactions.OptionType.BOOLEAN,
#                    required=False,
#                )
#            ]
#        ),
#        SlashCommandOption(
#            name="guild",
#            description="Show one of this guilds countdowns",
#            type=interactions.OptionType.SUB_COMMAND,
#            options=[
#                SlashCommandOption(
#                    type=interactions.OptionType.STRING,
#                    name="showguild",
#                    description="Which of this guilds countdowns do you want to be shown?",
#                    required=True,
#                    autocomplete=True,
#                ),
#                SlashCommandOption(
#                    name="hidden",
#                    description="Set to false if you want everyone to see",
#                    type=interactions.OptionType.BOOLEAN,
#                    required=False,
#                )
#            ]
#        )
#    ]
# )
# async def timeleft(
#    ctx: interactions.SlashContext,
#    sub_command: str,
#    showmine: str = "",
#    showchannel: str = "",
#    showguild: str = "",
#    hidden=True,
# ):
#    await command_builder.time_left(
#        ctx, sub_command, showmine, showchannel, showguild, hidden
#    )


# @bot.autocomplete("timeleft", "showmine")
# async def autocomplete(self, ctx: interactions.AutocompleteContext, value: str = ""):
#    await command_builder.autocomplete_countdowns(ctx, value, "mine")


# @bot.autocomplete("timeleft", "showchannel")
# async def autocomplete(self, ctx: interactions.AutocompleteContext, value: str = ""):
#    await command_builder.autocomplete_countdowns(ctx, value, "channel")


# @bot.autocomplete("timeleft", "showguild")
# async def autocomplete(self, ctx: interactions.AutocompleteContext, value: str = ""):
#    await command_builder.autocomplete_countdowns(ctx, value, "guild")


# @interactions.slash_command(
#    name="delete",
#    description="Deletes countdowns",
#    dm_permission=False,
#    options=[
#        SlashCommandOption(
#            name="single",
#            description="delete a single countdown",
#            type=interactions.OptionType.SUB_COMMAND_GROUP,
#            options=[
#                SlashCommandOption(
#                    name="mine",
#                    description="delete one of your countdowns",
#                    type=interactions.OptionType.SUB_COMMAND,
#                    options=[
#                        SlashCommandOption(
#                            type=interactions.OptionType.STRING,
#                            name="deletemine",
#                            description="Which of your countdowns do you want to be deleted?",
#                            required=True,
#                            autocomplete=True,
#                        )
#                    ]
#                ),
#                SlashCommandOption(
#                    name="channel",
#                    description="delete one of this channels countdowns",
#                    type=interactions.OptionType.SUB_COMMAND,
#                    options=[
#                        SlashCommandOption(
#                            type=interactions.OptionType.STRING,
#                            name="deletechannel",
#                            description="Which of this channels countdowns do you want to be deleted?",
#                            required=True,
#                            autocomplete=True,
#                        )
#                    ]
#                ),
#                SlashCommandOption(
#                    name="guild",
#                    description="delete one of this guilds countdowns",
#                    type=interactions.OptionType.SUB_COMMAND,
#                    options=[
#                        SlashCommandOption(
#                            type=interactions.OptionType.STRING,
#                            name="deleteguild",
#                            description="Which of this guilds countdowns do you want to be deleted?",
#                            required=True,
#                            autocomplete=True,
#                        )
#                    ]
#                )
#            ]
#        ),
#        SlashCommandOption(
#            name="mine",
#            description="Delete all your countdowns in this guild",
#            type=interactions.OptionType.SUB_COMMAND,
#        ),
#        SlashCommandOption(
#            name="channel",
#            description="Delete all countdowns in this channel",
#            type=interactions.OptionType.SUB_COMMAND,
#        ),
#        SlashCommandOption(
#            name="guild",
#            description="Delete all countdowns in this guild",
#            type=interactions.OptionType.SUB_COMMAND,
#        )
#    ]
# )
# async def delete(
#    ctx: interactions.SlashContext,
#    sub_command: str,
#    sub_command_group: str = "",
#    deletemine: str = "",
#    deletechannel: str = "",
#    deleteguild: str = "",
# ):
#    await command_builder.delete(
#        bot, ctx, sub_command, sub_command_group, deletemine, deletechannel, deleteguild
#    )


# @bot.autocomplete("delete", "deletemine")
# async def autocomplete(self, ctx: interactions.AutocompleteContext, value: str = ""):
#    await command_builder.autocomplete_countdowns(ctx, value, "mine")


# @bot.autocomplete("delete", "deletechannel")
# async def autocomplete(self, ctx: interactions.AutocompleteContext, value: str = ""):
#    await command_builder.autocomplete_countdowns(ctx, value, "channel")


# @bot.autocomplete("delete", "deleteguild")
# async def autocomplete(self, ctx: interactions.AutocompleteContext, value: str = ""):
#    await command_builder.autocomplete_countdowns(ctx, value, "guild")


# Here are the functions that runs when the verify/cancel buttons are pressed
# @bot.component("deleteguild")
# async def button_response(ctx):
#    await command_builder.delete_button(ctx, "guild")


# @bot.component("deletechannel")
# async def button_response(ctx):
#    await command_builder.delete_button(ctx, "channel")


# @bot.component("deletemine")
# async def button_response(ctx):
#    await command_builder.delete_button(ctx, "mine")


# @bot.component("deletecancel")
# async def button_response(ctx):
#    await command_builder.delete_button(ctx, "cancel")


@interactions.slash_command(
    name="botstats",
    description="Shows stats of bot",
)
async def botstats(ctx: interactions.SlashContext):
    await command_builder.botstats(ctx, bot)


@interactions.slash_command(
    name="fixperms",
    description="Fixes the permissions for this channel",
    #    default_member_permission=interactions.Permissions.ADMINISTRATOR,
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


# @bot.autocomplete("editmention", "countdown")
# async def autocomplete(self, ctx: interactions.AutocompleteContext, value: str = ""):
#    await command_builder.autocomplete_countdowns(ctx, value, "mine")


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


# a dev program
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


# Here are message commands - commands that are activated by a message


@interactions.message_context_menu(name="deletethis")
async def deletethis(ctx: interactions.ContextMenuContext):
    await command_builder.delete_this(bot, ctx)


@interactions.message_context_menu(name="timeleftthis")
async def timeleftthis(ctx: interactions.ContextMenuContext):
    await command_builder.timeleft_this(ctx)


# Jokes
@interactions.slash_command(
    name="whoisthegreatest",
    description="If you are curious about who the greatest is",
)
async def timeleftthis(ctx: interactions.SlashContext):
    await ctx.send("<@729791860674920488>")


@interactions.slash_command(
    name="whoistheboss",
    description="If you are curious about who the boss is",
)
async def timeleftthis(ctx: interactions.SlashContext):
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


# shard(bot)

# Start the bot!
bot.start()
