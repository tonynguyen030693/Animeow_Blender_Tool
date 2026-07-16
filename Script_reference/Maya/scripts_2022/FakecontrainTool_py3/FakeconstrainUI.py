def copy(*arg):
    import fake_constraint;fake_constraint.copy_offset()
     
def fake(*arg):
    import fake_constraint;fake_constraint.paste_offset()
if cmds.window("vietkhoiwin", exists=True):
    cmds.deleteUI("vietkhoiwin")
cmds.window("vietkhoiwin", title="FakeConstrain", w=303, h=25, sizeable=False)

cmds.columnLayout(w=300)
cmds.rowLayout(w=300, nc=2 )
cmds.button(l="Copy", w=150, bgc=[0,1,1], c=copy) 
cmds.button(l="Fake", w=150, bgc=[1,0,0], c=fake) 
cmds.showWindow("vietkhoiwin")


def copy(*arg):
    import fake_constraint;fake_constraint.copy_offset()
     
def fake(*arg):
    import fake_constraint;fake_constraint.paste_offset()