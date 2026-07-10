'''
The MIT License (MIT)

Copyright (c) 2016 Michael Shiao Chen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Author: Michael Shiao Chen
Version: 1.0.0
Date: 9/12/2016
Copyright: Copyright (c) 2016 Michael Shiao Chen

MC_Bakery is a tool that helps speed up baking keyframes for animation.

To use this tool, simply source this script in the Maya's Script Editor or alternatively copy and execute this code as Python.
'''


import maya.cmds as cmds
import maya.mel as mel
from functools import partial
import os, sys, math

_pmpath = 'mc/MCBake/'
currentTheme = ''
icoWidth = 35
icoHeight = 35
winWidth = 358
winHeight = 45

t1=0
t2=0
sample = 1
selectedAttr = []

try:
	_pmpath = os.path.join([s for s in sys.path if os.path.exists(os.path.join(s, _pmpath))][0], _pmpath)
except:
	pass


def ChenBake(posX=56, posY=180, width=winWidth, height=winHeight):
	winName = 'ChenBake'
	if cmds.window(winName, exists=True):
		cmds.deleteUI(winName, window=True)
	
	cmds.window(winName, title='MC Bakery', tlb=True)
	cmds.shelfLayout(bgc=(0.3, 0.3, 0.3))
	
	cmds.iconTextButton(style='iconOnly', h=icoHeight, w=icoWidth, bgc=(0.3, 0.3, 0.3), image=_pmpath + currentTheme +'bakeAll_1s.bmp', c= 'bakeFrames(1, False)', ann='Bake all on 1s')
	cmds.popupMenu(mm=True)
	cmds.menuItem(l='Change Theme - Blu', c='changeTheme("blu")', rp='NE')
	cmds.menuItem(l='Change Theme - Pink', c='changeTheme("")', rp='E')
	cmds.menuItem(l='Change Theme - Yellow', c='changeTheme("yellow")', rp='SE')
	
	cmds.iconTextButton(style='iconOnly', h=icoHeight, w=icoWidth, bgc=(0.3, 0.3, 0.3), image=_pmpath + currentTheme +'bakeAll_2s.bmp', c='bakeFrames(2, False)', ann='Bake all on 2s')
	cmds.popupMenu(mm=True)
	cmds.menuItem(l='Window Horizontal - Compact', c='changeSize(35,35,358,45)', rp='NE')
	cmds.menuItem(l='Window Horizontal- Large', c='changeSize(55,55,560,85)', rp='E')
	cmds.menuItem(l='Window Vertical - Compact', c='changeSize(35,35,43,360)', rp='NW')
	cmds.menuItem(l='Window Vertical - Large', c='changeSize(55,55,63,580)', rp='W')
	
	cmds.iconTextButton(style='iconOnly', h=icoHeight, w=icoWidth, bgc=(0.3, 0.3, 0.3), image=_pmpath + currentTheme +'bakeAll_3s.bmp', c='bakeFrames(3, False)', ann='Bake all on 3s')
	cmds.iconTextButton(style='iconOnly', h=icoHeight, w=icoWidth, bgc=(0.3, 0.3, 0.3), image=_pmpath + currentTheme +'bakeAll_4s.bmp', c='bakeFrames(4, False)', ann='Bake all on 4s')
	cmds.iconTextButton(style='iconOnly', h=icoHeight, w=icoWidth, bgc=(0.3, 0.3, 0.3), image=_pmpath + currentTheme +'bakeAll_5s.bmp', c='bakeFrames(5, False)', ann='Bake all on 5s')
	
	cmds.iconTextButton(style='iconOnly', h=icoHeight, w=icoWidth, bgc=(0.3, 0.3, 0.3), image=_pmpath + currentTheme +'bakeCh_1s.bmp', c= 'bakeFrames(1, True)', ann='Bake selected channels on 1s')
	cmds.iconTextButton(style='iconOnly', h=icoHeight, w=icoWidth, bgc=(0.3, 0.3, 0.3), image=_pmpath + currentTheme +'bakeCh_2s.bmp', c='bakeFrames(2, True)', ann='Bake selected channels on 2s')
	cmds.iconTextButton(style='iconOnly', h=icoHeight, w=icoWidth, bgc=(0.3, 0.3, 0.3), image=_pmpath + currentTheme +'bakeCh_3s.bmp', c='bakeFrames(3, True)', ann='Bake selected channels on 3s')
	cmds.iconTextButton(style='iconOnly', h=icoHeight, w=icoWidth, bgc=(0.3, 0.3, 0.3), image=_pmpath + currentTheme +'bakeCh_4s.bmp', c='bakeFrames(4, True)', ann='Bake selected channels on 4s')
	cmds.iconTextButton(style='iconOnly', h=icoHeight, w=icoWidth, bgc=(0.3, 0.3, 0.3), image=_pmpath + currentTheme +'bakeCh_5s.bmp', c='bakeFrames(5, True)', ann='Bake selected channels on 5s')

	
	cmds.showWindow(winName)
	cmds.window(winName, edit=True, widthHeight=(width, height), topLeftCorner=(posY, posX))


def getSelectedChannels (*args):
    gChannelBoxName = mel.eval('$temp=$gChannelBoxName')
    global selectedAttr
    chList = cmds.channelBox (gChannelBoxName, q=True, sma = True)
    selectedAttr = chList
    if chList:
        for channel in chList:
            print('selected channels = .'+channel)
    else:
        print 'No channels selected!'
        return False



def doBakeChannels():
    global sample
    global t2
    bakeUntil = cmds.currentTime( query=True )
    t2 = float(bakeUntil)
    print("bake selected channels")
    
    getSelectedChannels()
    
    objects = cmds.ls(sl=True)
    cmds.bakeResults( objects, t=(t1,t2), sb=sample, simulation=True,preserveOutsideKeys=True, at=selectedAttr )


def doBakeAll():
    global sample
    global t2
    bakeUntil = cmds.currentTime( query=True )
    t2 = float(bakeUntil)
    print("bake all")
    
    getSelectedChannels()
    
    objects = cmds.ls(sl=True)
    cmds.bakeResults( objects, t=(t1,t2), sb=sample,preserveOutsideKeys=True, simulation=True )



def bakeFrames(smp, chbake):
    global sample
    global t1
    t1 = cmds.currentTime( query=True )
    sample=smp
    if chbake == True:
        cmds.scriptJob(ro=True, event=['timeChanged',doBakeChannels])
    else:
        cmds.scriptJob(ro=True, event=['timeChanged',doBakeAll])


def changeSize(iconW, iconH, windW, windH ):
    global icoWidth
    global icoHeight
    global winWidth
    global winHeight
    
    icoWidth=iconW
    icoHeight=iconH
    
    winWidth=windW
    winHeight=windH
    
    ChenBake(posX=56, posY=180, width=winWidth, height=winHeight)
        
def changeTheme(theme):
    global currentTheme
    newtheme = ''+theme+'/'
    currentTheme = newtheme
    ChenBake(posX=56, posY=180, width=winWidth, height=winHeight)
    
ChenBake()

