from maya import cmds
from pprint import pprint 



def selection(*args):
    selection_list =[]
    selection = cmds.ls(selection=True)
    if len(selection) ==0:
        print ("Please choose controller")
    else:
        selection_list.append(selection)
        pprint (selection_list)
    return selection_list  

def transfer_selected():
    #selected namespace
    namespaces = get_selected_namespaces()
    #validate selection
    if len(namespaces) == 0:
        cmds.warning('please select something!')
        return
    if len(namespaces) == 1:
        cmds.warning('please select more than 1 rig!!')
        return
    source_namespace = namespaces[0]
    target_namespace = namespaces[1:]
    #get pose dictionary from source
    pose_dict = get_pose_dict(source_namespace)
    for target in target_namespace:
        apply_pose(pose_dict,target)

def get_selected_namespaces():
    """ Get list of namespaces for selected rigs.

        Returns: 
            list """

    selection = cmds.ls(selection=True)
    if len(selection) == 0:
        return []
    

    namespace_list = []
    # loop over selection
    for ctrl in selection:
        # extract namespace from control
        namespace = ctrl.split(':')[0]
         # add name space to list of namespace
        if namespace not in namespace_list:
            namespace_list.append(namespace)

    return namespace_list

def get_attrs_from_nodes(ctrl_node):
    """Get attribute name frome node
        Arg:
        ctr_node(str): Name of the node
        Return: 
         list: List of short attribute names Attr_name"""
    
    
   
    attributes = cmds.listAnimatable(ctrl_node)
    if not attributes:
        return []

    attr_names = []
    for full_attr in attributes:
        attr_name = full_attr.split('.')[-1]
        attr_names.append(attr_name)
	
    return attr_names


def get_pose_dict(namespace):
     """Get the pose dictionary without namspaces
     
     args: namespace(s): Filter this selection by namespace
     
     Return:
        dict
     """ 
     selection = cmds.ls(selection=True) 
     if not selection:
          return{}
     
     pose_dict = {}
     for ctrl in selection:
        if not ctrl.startswith(namespace):
               continue
        
        animatable_attrs = get_attrs_from_nodes(ctrl)
        if not animatable_attrs:
             continue
        #populate dictionary    
        for attr in animatable_attrs:
             ctrl_name = ctrl.split(':')[-1]  
             full_attr_no_ns = '{}.{}'.format(ctrl_name, attr)
             ctrl_with_attr = '{}.{}'.format(ctrl, attr)
             attr_value = cmds.getAttr(ctrl_with_attr)
             pose_dict[full_attr_no_ns] = attr_value
     return pose_dict
        
def apply_pose(pose_dict, namespace):
    """Apply provided pose to the provided namespace
     
     Args: pose_dict:(dict): dictionary with pose data
        namespace(str): target namespace to apply the pose to.
     
     Return:"""

    # get attribute names
    for attr_name in pose_dict.keys():
        #need to add namespace
        attr_value = pose_dict[attr_name]
        #severus:hat.rotateY
        full_attr_name = '{}:{}'.format(namespace, attr_name)
        
        #error checking
        #check attribute exists
        #check if attribute settable
        node, attr_short_name = full_attr_name.split('.')
        #atributes check attribute
        if not cmds.objExists(node)  or not cmds.attributeQuery(attr_short_name, node=node, exists= True) or not cmds.getAttr(full_attr_name, settable = True) :
            continue
        #set attribute
        cmds.setAttr(full_attr_name, attr_value)


