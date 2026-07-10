from maya import cmds


def tweenMachine(tween):

    #resource
    node = "v02_Baby_Rig_Hand_Global:RootX_M"
    animAtt= "translateY"
    animnode = '{}.{}'.format(node,animAtt)

    previousKey = cmds.findKeyframe(node,at= animAtt, which="previous")
    nextKey = cmds.findKeyframe(node,at= animAtt, which="next" )


    previousKeyValue = cmds.getAttr(animnode, t = previousKey)
    nextKeyValue = cmds.getAttr(animnode, t = nextKey)
    
    
    spacing = nextKeyValue - previousKeyValue
    if spacing < 0:
        newspacing = -(spacing)
    else:
        newspacing = spacing
    tweenspacing = ((newspacing)*(tween))/100

    if previousKeyValue >= nextKeyValue:
        newAnimAtt = previousKeyValue - tweenspacing
    elif previousKeyValue < nextKeyValue:
        newAnimAtt = previousKeyValue + tweenspacing

    tweenaction= cmds.setAttr(animnode, newAnimAtt)
    tweenaction

    print ("ctr:",node)
    print ("attribute:",animAtt)
    print ("fullname:",animnode)		
    print ("previousKeyValue:", previousKeyValue, "at previousKey:",previousKey)
    print ("nextKeyValue", nextKeyValue, "at nextKey::",nextKey)
    print("Spacing:", spacing)
    print("New Spacing", newspacing)
    print ("tween spacing value", tweenspacing)
    print ("New Attribute:",newAnimAtt)
    print ("Tween", tween)
        
    # tweenMachine()