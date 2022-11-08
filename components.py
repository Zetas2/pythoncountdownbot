import interactions

# Buttons that are added as a verification step when multiple countdowns will be deleted.
delete_guild = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="Delete",
    custom_id="deleteguild",
)

delete_channel = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="Delete",
    custom_id="deletechannel",
)

delete_mine = interactions.Button(
    style=interactions.ButtonStyle.DANGER,
    label="Delete",
    custom_id="deletemine",
)

delete_cancel = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Keep countdowns",
    custom_id="deletecancel",
)
