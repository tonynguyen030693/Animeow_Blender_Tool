import maya.cmds as mc

hudNameData = {'objectDetailsVisibility':['HUDObjDetBackfaces', 'HUDObjDetSmoothness', 'HUDObjDetInstance', 'HUDObjDetDispLayer', 'HUDObjDetDistFromCam', 'HUDObjDetNumSelObjs'],
               'polyCountVisibility':['HUDPolyCountVerts', 'HUDPolyCountEdges', 'HUDPolyCountFaces', 'HUDPolyCountTriangles', 'HUDPolyCountUVs'],
               'particleCountVisibility':['HUDParticleCount'],
               'subdDetailsVisibility':['HUDSubdLevel', 'HUDSubdMode'],
               'cameraNamesVisibility':['HUDCameraNames', 'HUDHQCameraNames'],
               'focalLengthVisibility':['HUDFocalLength'],
               'frameRateVisibility':['HUDFrameRate'],
               'currentFrameVisibility':['HUDCurrentFrame'],
               'sceneTimecodeVisibility':['HUDSceneTimecode'],
               'currentContainerVisibility':['HUDCurrentContainer'],
               'viewAxisVisibility':['HUDViewAxis'],
               'fbikDetailsVisibility':['HUDFbikKeyType'],
               'hikDetailsVisibility':['HUDHikKeyingMode'],
               'selectDetailsVisibility':['HUDSoftSelectState', 'HUDReflectionState'],
               'animationDetailsVisibility':['HUDIKSolverState', 'HUDCurrentCharacter', 'HUDPlaybackSpeed']}

def hideMayaHUD():
    global hudNameData
    for k in hudNameData.keys():
        hudName = hudNameData[k]
        if mc.headsUpDisplay(hudName, ex=True):
            mc.headsUpDisplay(hudName, edit=True, vis=False)

def restoreMayaHUD():
    global hudNameData
    for k in hudNameData.keys():
        optName = k
        hudName = hudNameData[k]
        hudState = mc.optionVar(optName, q=True)
        if mc.headsUpDisplay(hudName, ex=True):
            mc.headsUpDisplay(hudName, edit=True, vis=hudState)
        