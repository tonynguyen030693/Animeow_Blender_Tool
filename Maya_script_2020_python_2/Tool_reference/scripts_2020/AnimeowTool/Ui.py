import maya.cmds as cmds
import os
# import AnimeowTool.SourceTool.Overlaper as Overlaper

IM = os.path.join(os.path.dirname(__file__), "Icons")

import AnimeowTool.Tool as tool
reload(tool)

import AnimeowTool.SourceTool.createLocator as stLoc
reload(stLoc)

# import AnimeowTool.SourceTool.Bake_locator_anim as balonim
# reload (balonim)

import AnimeowTool.AnimeowUtilities as uti
reload (uti)

cmds.inViewMessage( amg='<hl>Welcome to Animeow Studio!!! \(^!^)/</hl>', pos='midCenter',f = True, fst=500, fts = 25 )


def Ui():
    if cmds.window("Animeow", exists=True):
        cmds.deleteUI("Animeow")
#tao ra windown Animeow
#thiet lap lai cau hinh window
    wd = cmds.window("Animeow", title="AnimeowAnim", w=250, h=430, sizeable=False)
    cmds.windowPref("Animeow", remove=True)
#tao tab layout
    tab_layout = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)

###tab_01
    #tab_01_tool
    tab_01 = cmds.columnLayout(rs =5)
    cmds.setParent(tab_01)
    cmds.frameLayout (label="Super_Tool", w = 250)
    tab_01_tool = cmds.rowColumnLayout("Super_Tool", w=250, numberOfColumns=5)
    cmds.symbolButton(image = IM + "/tweenMachine.png", w=50, h=50, c = tool.TW)
    cmds.symbolButton(image = IM + "/workbake.png", w=50, h=50,c = tool.WB)
    cmds.symbolButton(image = IM + "/bakeAll_2s.bmp", w=50, h=50, c= tool.bakeKey)
    cmds.symbolButton(image = IM + "/LMlocator_Icon.png", w=50, h=50, c = stLoc.createLocatorAtSelection)
    cmds.symbolButton(image = IM + "/Croissants_tokenizLoop_3.ico", w=50, h=50, c = "import dwpicker\ndwpicker.show()")

    #tab_02_tool
    cmds.setParent(tab_01)
    cmds.frameLayout (label="Normal_Tool", w = 250)
    tab_02_tool = cmds.rowColumnLayout("Normal_Tool", w=250, numberOfColumns=5)
    cmds.setParent(tab_02_tool)
    cmds.symbolButton(image = IM + "/Atool", w=50, h=50,c = "from aTools.animTools.animBar import animBarUI; animBarUI.show('toggle')")
    cmds.symbolButton(image = IM + "/GraphEditor.png", w=50, h=50, c = tool.openGraph)
    cmds.symbolButton(image = IM + "/Bake_location_anim.png", w=50, h=50, c = "import AnimeowTool.SourceTool.Bake_locator_anim as balonim\nreload (balonim)\ncreateLocatorAtSelectionAndBakeAnim()")
    cmds.symbolButton(image = IM + "/Reference_Call", w=50, h=50, c= tool.refEditor)
    cmds.symbolButton(image = IM + "/Arc_tracker.png", w=1, h=1, c=tool.arcTracker)
    cmds.symbolButton(image = IM + "/Arc_to_curve.png", w=50, h=50, c = tool.motoCurves)
    cmds.symbolButton(image = IM + "/out_liner.png", w=50, h=50, c = tool.outLiner)
    cmds.symbolButton(image = IM + "/mirror_curve", w=50, h=50, c= tool.revertKey)
    cmds.symbolButton(image = IM + "/Linear_curve", w=30, h=30, c = tool.infiCurves)
    cmds.symbolButton(image = IM + "/StudioLibrary", w=50, h=50, c= "import AnimeowTool.SourceTool.studiolibrary.stu_install_Animeow as c\nreload(c)")
    cmds.symbolButton(image = IM + "/bh_animProxy", w=50, h=50, c = tool.bhProxy)
    cmds.symbolButton(image = IM + "/Constrain", w=50, h=50, c= tool.constrain)
    cmds.symbolButton(image = IM + "/HumanIK", w=50, h=50, c= tool.advPicker)
    cmds.symbolButton(image = IM + "/Three_pane.png", w=50, h=50, c= tool.Three_panes)
    cmds.symbolButton(image = IM + "/Two_pane.png", w=50, h=50, c = tool.Two_panes)
    cmds.symbolButton(image = IM + "/Clean_scene.png", w=50, h=50, c ="import AnimeowTool.SourceTool.cleanFile as cleanFile\nreload (cleanFile)")
    cmds.symbolButton(image = IM + "/All_node_copy.png", w=50, h=50, c ="import AnimeowTool.SourceTool.All_node_copy as All_node_copy\nreload (All_node_copy)")
    cmds.symbolButton(image = IM + "/Overlapper.png", w=50, h=50, c =tool.overlapper)
    cmds.symbolButton(image = IM + "/PlayBlast.png", w=50, h=50, c =tool.playblast)



    cmds.setParent(tab_01)
    cmds.frameLayout (label="Auto Animate",li = 80, w = 250, h =250)   
    cmds.symbolButton(image = IM + "/AnimeowLogo.jpg", w=50, h=120, c = tool.autoAnim)
    cmds.text(label= "Copyright [2024] by Animeow Animation Studio")




#tab_02
    cmds.setParent(wd)
    tab_02 = cmds.columnLayout()
    cmds.symbolButton(image = IM + "/AnimeowLogo.jpg", w=250, h=250,)
    cmds.frameLayout (label="This Tool is developing",li = 50, w = 250, h =250) 

    cmds.tabLayout( tab_layout, edit=True, tabLabel=((tab_01, 'Tool'),(tab_02, 'Other')))

    cmds.showWindow("Animeow")

Ui()