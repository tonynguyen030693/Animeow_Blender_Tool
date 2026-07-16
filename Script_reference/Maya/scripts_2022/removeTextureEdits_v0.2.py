##Script made by Ottoni Bastos for Hype.cg at 04/05/2018.
## Remove changes on texture references.

import maya.cmds as mc


def getUniqueRefs():
    
    uniqueRefs = []
    objects = mc.ls(sl = True)
    
    for obj in objects:
        
        if mc.referenceQuery(obj,inr = True):
            
            ref = mc.referenceQuery(obj,rfn = True)
            if ref not in uniqueRefs:
                uniqueRefs.append(ref)
    return uniqueRefs


#List selected refs
references = getUniqueRefs()

for reference in references:
    
    #List all edits in the current reference
    edits = mc.referenceQuery(reference , es = True , scs = True)
    
    for edit in edits:
        
        #if it is a texture edit,remove it!
        if 'sourceimages' in edit:
            mc.referenceEdit(edit.split(' ')[1], editCommand = str(edit.split(' ')[0]),failedEdits = True,successfulEdits = True,removeEdits = True)
