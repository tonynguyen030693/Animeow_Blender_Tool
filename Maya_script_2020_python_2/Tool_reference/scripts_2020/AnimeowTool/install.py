import maya.cmds as cmds
import os

IM = os.path.join(os.path.dirname(__file__), "Icons")

Animeow_tool = cmds.shelfButton(
    command="import AnimeowTool.Ui as AmwUi\nreload (AmwUi)\n\nAmwUi.Ui()",
    label="Animeow Tool",
    #annotation="import AnimeowTool.Ui as AmwUi\nreload (AmwUi)\n\nAmwUi.Ui()",
    image=IM + "/AnimeowLogo.jpg",
    parent="Custom"
)
