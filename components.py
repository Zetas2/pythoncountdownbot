import interactions

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
