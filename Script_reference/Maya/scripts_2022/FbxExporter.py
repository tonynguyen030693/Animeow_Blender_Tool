import maya.cmds as cmds
import pymel.core as pm
import importlib
import maya.mel as mel
import os
import time

eva_mode = pm.evaluationManager( mode=1,q=1 )
if eva_mode[0] !='parallel':
    pm.evaluationManager( mode='parallel') 
    pm.warning("Switch to Parallel mode")
    
class PlayerUi():
    def __init__(self):
        self.match_db_path = None
        self.player_db_path = None
        self.game_opta_path  = None
        
        self.scalex_mainctl = None
        self.scaley_mainctl = None
        self.scalez_mainctl = None
        self.ball_group = "Ball_Grp"
        
    def export_fbx_file(self, *args):
        #Query the option menu
        namespace = cmds.optionMenu('playerRef_option_menu',v=1, query=True)
        multipleFilters ="Fbx (*.fbx)"
        exported_players_list = []
        try:
            file_path = cmds.fileDialog2(fileFilter=multipleFilters,fileMode=3)[0]
          
            
        except TypeError:
            pm.warning("Export is cancelled")
            return
        if not file_path:
            return
        else: 
            minTL = pm.playbackOptions (q =1, minTime =1)
            maxTL = pm.playbackOptions (q =1, maxTime =1)
            #If users want to export seperate rig not all
            if namespace == "Ball":
                self.bake_ball(file_path)
                
            elif namespace != "All":
                #dUPLICATE the skeleton that need to export
                exported_skeleton = self.duplicate_skeleton_exported(namespace)
                
                
               
                self.fbxExport(exported_skeleton, file_path)
                
            
            else:
                
                menu_Items = cmds.optionMenu('playerRef_option_menu', q=True, itemListLong=True)
           
           
                all_items= [cmds.menuItem(i, query=True, label=True) for i in menu_Items]
            
                for namespace in all_items:
                    if namespace not in ["All", "Ball"]:
                        # Duplicate the skeleton that need exported
                        exported_skeleton = self.duplicate_skeleton_exported(namespace)
                        # Append each skeleton to a list
                        self.fbxExport(exported_skeleton, file_path)
                    elif namespace =="Ball":
                        self.bake_ball(file_path)
                    else:
                        continue
                # After duplicate skeleton, select them and export all


    def bake_ball(self, file_path):
        ball_skel = pm.listRelatives(self.ball_group,ad=1, c=1, type = "joint" )
        
           
        if ball_skel:
            dupSkel = pm.duplicate (ball_skel[-1],rr=1, renameChildren=0,  st=1, ic=1)[0]
            pm.parent(dupSkel, w=1)
            joint = pm.rename(dupSkel, "Ball_root") 
        else:
            pm.error("Cannot find Ball_Grp to export")
            return
        self.fbxExport(joint, file_path)
        
    def addnameSpace(self, namespace, objList):
        if not pm.namespace( exists=  namespace):
            #pm.warning(f"{namespace} was added in the ns list")
            pm.namespace(add=namespace)    
            
     
        new_joint_list = []
        for i in objList:
            #pm.warning(f"Start to iterate the item -- {i}")
            
            joint_name = namespace +":"+  str(i)
            #print(f'Add new joint name {joint_name}')
            newName = pm.rename( i, joint_name)
         
            new_joint_list.append(newName)
            #print(f'This new joint name created {newName}')
            
        return new_joint_list
            
    def duplicate_skeleton_exported(self, namespace):
      #Get the correct name to export
        
        outputname = pm.ls(namespace + ":" + "DeformationSystem")
        mainCtl = pm.ls(namespace + ":" + "Main")



        if pm.objExists(outputname):
            scaleX =outputname[0].sx.get()
            scaleY =outputname[0].sx.get()
            scaleZ =outputname[0].sx.get()
            
            
            pm.select(cl=1)
            
            rigSkel =[i for i in pm.listRelatives(outputname,children=1)]
            dupSkel = pm.duplicate (rigSkel,rr=1, renameChildren=0,  st=1, ic=1)[0]
            
            #pm.warning(f"here is the dupskel -- {dupSkel}")
            objList = pm.listRelatives(dupSkel, children=1, ad=1)
        
            #pm.warning(f"here are all joints that need to export -- {objList}")
            objList.insert(0,dupSkel)
 
            for i in objList:
                if str(i).startswith(('Shoulder', 'ShoulderPart1', 'Elbow', 'ElbowPart1','Wrist')):
                    mel.eval(f'source channelBoxCommand; CBdeleteConnection "{str(i)}.tx";')
                    mel.eval(f'source channelBoxCommand;CBdeleteConnection "{str(i)}.ty";')
                    mel.eval(f'source channelBoxCommand;CBdeleteConnection "{str(i)}.tz";')
                    
                    #pm.warning(f"here is joints that need to be cut key-- {i}")
                    
            #pm.warning(f"here are the namespace need to add -- {namespace}")
            #Give the diplicated  an unique name for export process
            dupSkel = self.addnameSpace("duplicated_" + namespace, objList)
            
            mainCtl[0].sx.set(1)
            mainCtl[0].sy.set(1)
            mainCtl[0].sz.set(1)
            try:
                dupSkel[0].sx.set(scaleX)
                dupSkel[0].sy.set(scaleY)
                dupSkel[0].sz.set(scaleZ)
                
            except Exception:
                
                nodeScalex = pm.listConnections(dupSkel[0].sx,d=0,p=1)[0]
                nodeScaley = pm.listConnections(dupSkel[0].sy,d=0,p=1)[0]
                nodeScalez = pm.listConnections(dupSkel[0].sz,d=0,p=1)[0]
                
                nodeScalex // dupSkel[0].sx
                nodeScaley // dupSkel[0].sy
                nodeScalez // dupSkel[0].sz
                
                dupSkel[0].sx.set(scaleX)
                dupSkel[0].sy.set(scaleY)
                dupSkel[0].sz.set(scaleZ)
            
            pm.parent(dupSkel[0], w=1)
            
            mainCtl[0].sx.set(scaleX)
            mainCtl[0].sy.set(scaleY)
            mainCtl[0].sz.set(scaleZ)
                
        else:
            pm.warning(f"Cannot find {outputname}. Please select a valid Advanced Skeleton")
            return
        #print ("This is the root name with new scale - ",dupSkel[0])
        return dupSkel[0]
        
    def rename_joint_list(self, objList):
        new_joint_list = []
        for i in objList:
            newName  = str(i).split(":")[-1]
            #print(f'{newName} renamed to export')
            joint_name = pm.rename(i, newName)
            new_joint_list.append(joint_name)  
        return new_joint_list
     
    def define_team_name( self, playername):
       
        filter_obj = pm.ls(f"{playername}*", exactType = "transform" )
        player_grp = [i for i in filter_obj if i.endswith(("home_Grp", "away_Grp"))]
        
        if player_grp:
            team_name = pm.listRelatives(player_grp[0], parent =1, type = "transform")
            if team_name[0].endswith("_Preview"):
                
                team = team_name[0].replace("_Preview","")
                return team
        else: 
          
            
            player_away_grp_list= pm.ls("*away_Grp")
            player_home_grp_list= pm.ls("*home_Grp")
            player_grp_list = player_away_grp_list + player_home_grp_list
            
            for i in player_grp_list:
               
                player_name_list = str(i).split("_")
                del player_name_list[-3::]
                #print("player_name_list ", player_name_list)
                if playername.endswith(player_name_list[-1]) and playername.startswith(player_name_list[0]):
                    team_name = pm.listRelatives(i, parent =1, type = "transform")
                    #print("parent group is ", team_name)
                    if str(team_name[0]).endswith("_Preview"):
                
                        player_grp  = str(team_name[0]).replace("_Preview","")
                        #print("team found is ", player_grp)
                        return player_grp 
                    else: 
                        return str(team_name[0])
                        
                else:
                    player_grp = []
                    continue

                return player_grp

    def fbxExport(self, exported_players, file_path):
        
        if not exported_players.startswith("Ball"):
            filename = str(exported_players.split(":")[0].replace("duplicated_",""))
            
            pm.select(cl=1)
            pm.select(exported_players)
            
            objList = pm.listRelatives(pm.selected(), children=1, ad=1)
            objList.insert(0, exported_players) 
                    

            new_joint_list = self.rename_joint_list(objList)
            
            #Create the folder path for the fbx files
            export_dir = ""
            #Look up the team name by search the matching baked skel' name
           
            team_name = self.define_team_name(filename)
            
            if team_name:
               
                export_dir = file_path + "/" + team_name + "/" + filename 
                
            else:
                export_dir  = file_path + "/" + filename 

            pm.select(cl=1)
            pm.select(new_joint_list)
                
                #Check if we can find the team name to create a separate folder, otherwise export to the main one:
        else:
            team_name = "Ball"
            new_joint_list  = exported_players
            filename  = "Ball"
            export_dir = file_path + "/" + team_name
    
            
            pm.select(cl=1)
            pm.select(new_joint_list)
        
        
        if not os.path.exists(export_dir):
            try:
                os.makedirs(export_dir)
            except OSError:
                pm.error("Please check again if root joint exists in scene")
                
        mel.eval('FBXResetExport')
        mel.eval('FBXExportUpAxis y')
        mel.eval("FBXExportLights -v false")
        mel.eval('FBXExportBakeComplexAnimation -v 1')
        mel.eval('FBXExportBakeResampleAnimation -v 1')

        mel.eval('FBXExportInAscii -v 0')
        mel.eval('FBXExportInputConnections -v 0')
        mel.eval('FBXExport -f "{}" -s'.format(export_dir +  "/" + filename))
        
        pm.warning(f"{filename}.fbx was exported to {export_dir}")
        
      
        pm.delete(new_joint_list)
        
        
        if cmds.checkBox("delete_static_channels",v=1, q=1) and not filename.endswith("Ball"):
            # pm.warning(f" delete_static_channelsis ticked, {exported_players} is selected")
            path = export_dir +  "/" + filename 
            self.delete_static_channels(path)
        else:
            return
            
       
        
    def delete_static_channels(self, path):
        

        if pm.objExists("root"):
            obj = pm.ls("root")
            try:
                new_obj = pm.rename(obj[0], 'root#')
            except Error:
                pm.error(f"Cannot rename to {obj} to delete static channels")
                return
        import_path = path +".fbx"
        mel.eval('FBXImportMode -v add')
        mel.eval(f'FBXImport -f "{import_path}"')
        
        pm.select('root',hi=1)
        pm.delete(staticChannels=1)
        
        pm.select('root')
        mel.eval('FBXExport -f "{}" -s'.format(path))
        pm.select('root')
        pm.delete()
        
    def update_player_ref(self, *args):
        
        namespaces = [i for i in cmds.namespaceInfo(lon=True) if i not in ['UI','shared']]
        cmds.optionMenu('playerRef_option_menu', edit=True, deleteAllItems=True)
        cmds.menuItem(parent='playerRef_option_menu', label="All")
        if pm.objExists("Ball_Main_position"):
            cmds.menuItem(parent='playerRef_option_menu', label="Ball")
        for i in namespaces:
            node = str(i)+":DeformationSystem"
            
            if pm.objExists(node):
                label = f"{i}"
                cmds.menuItem(parent='playerRef_option_menu', label=label)
    
    
    @staticmethod
    def init():
        '''
        Load required comelands and plugins
        '''
        # Get Maya App Location
        MAYA_LOCATION = os.environ['MAYA_LOCATION']
        
        # Source Mel Files
        mel.eval('source "'+MAYA_LOCATION+'/scripts/others/hikGlobalUtils.mel"')
        mel.eval('source "'+MAYA_LOCATION+'/scripts/others/hikCharacterControlsUI.mel"')
        mel.eval('source "'+MAYA_LOCATION+'/scripts/others/hikDefinitionOperations.mel"')
        mel.eval('source "'+MAYA_LOCATION+'/scripts/others/hikBakeOperation.mel"')


        # Load Plugins
        if not cmds.pluginInfo('mayaHIK',q=True,l=True):
            cmds.loadPlugin('mayaHIK')
        if not cmds.pluginInfo('mayaCharacterization',q=True,l=True):
            cmds.loadPlugin('mayaCharacterization')
        if not cmds.pluginInfo('retargeterNodes',q=True,l=True):
            cmds.loadPlugin('retargeterNodes')
        
        # HIK Character Controls Tool
        mel.eval('HIKCharacterControlsTool')

    @staticmethod
    def GetCharList():
        mel.eval("HIKCharacterControlsTool;")
        _HUMAN_IK_SOURCE_MENU = "hikCharacterList"
        _HUMAN_IK_SOURCE_MENU_OPTION = _HUMAN_IK_SOURCE_MENU + "|OptionMenu"
        items = cmds.optionMenuGrp(_HUMAN_IK_SOURCE_MENU, q=True, ill=True)

        hikList = []
        for i in range(0, len(items)):
            label = cmds.menuItem(items[i], q=True, l=True)
            hikList.append(label)

        return hikList
    @staticmethod
    def isCharacterDefinition(char):
        # Check Node Exists
        if not cmds.objExists(char): return False
        
        
        # Check Node Type
        if cmds.objectType(char) != 'HIKCharacterNode': return False
        
        return True
    @staticmethod
    def getCharacterNodes(char):
    # Check Node
        
        if char.endswith('(custom rig)'):
            char = char.replace('(custom rig)', "")
            
        
        if not PlayerUi.isCharacterDefinition(char):
            raise Exception(
                'Invalid character definition node! Object "'
                + char
                + '" does not exist or is not a valid HIKCharacterNode!'
            )

        # Get Character Nodes
        if ":" in char:
            ns = char.split(":")[0] + ":"
        else:
            raise Exception(
                'Invalid character to find the controller for baking: "'
                + char
                
            )
     
        customNodes = [f'{ns}IKLeg_L',f'{ns}IKLeg_R', f'{ns}PoleLeg_R', f'{ns}PoleLeg_L']
        charNodes = mel.eval('hikGetSkeletonNodes "' + char + '"')
        charNodes += customNodes
        # print(charNodes)
     
        jointList = []
     
        for node in charNodes:
            if node.endswith(("RootX_M", 'IKLeg_R','IKLeg_L','PoleLeg_L', 'PoleLeg_R' )):
                joint = [node + i for i in [".rotate", ".translate"] ]
                jointList += joint
            else:
                joint = node + ".rotate"
                jointList.append(joint)
                
                
        # Return Result
        return jointList
    @staticmethod
    def bake(char, start, end):
      
        print(char)
        # Bake Animation
        pm.bakeResults(
            char,
            simulation=True,
            t=(start, end),
            sampleBy=1,
            oversamplingRate=1,
            disableImplicitControl=True,
            preserveOutsideKeys=True,
            sparseAnimCurveBake=False,
            removeBakedAttributeFromLayer=False,
            removeBakedAnimFromLayer=False,
            bakeOnOverrideLayer=False,
            minimizeRotation=True, 
            controlPoints = False,
            shape  = True,
            
        )
    @staticmethod
    def SetHikSourceChar(source):
        _HUMAN_IK_SOURCE_MENU = "hikSourceList"
        _HUMAN_IK_SOURCE_MENU_OPTION = _HUMAN_IK_SOURCE_MENU + "|OptionMenu"
        items = cmds.optionMenuGrp(_HUMAN_IK_SOURCE_MENU, q=True, ill=True)
        for i in range(0, len(items)):
            label = cmds.menuItem(items[i], q=True, l=True)

            # ??????????????
            if label.lstrip() == source:
                cmds.optionMenu(_HUMAN_IK_SOURCE_MENU_OPTION, e=True, sl=i + 1)
                mel.eval("hikUpdateCurrentSourceFromUI()")
                mel.eval("hikUpdateContextualUI()")
                #mel.eval("hikControlRigSelectionChangedCallback")
                break
    @staticmethod
    def hikUpdateTool():
        melCode = """
            if ( hikIsCharacterizationToolUICmdPluginLoaded() )
            {
                hikUpdateCharacterList();
                hikUpdateCurrentCharacterFromUI();
                hikUpdateContextualUI();
                
                hikUpdateSourceList();
                hikUpdateCurrentSourceFromUI();
                hikUpdateContextualUI();
                
            }
            """
        try:
            mel.eval(melCode)
        except:
            pass
        
    @staticmethod
   
    def SetHikChar(targetChar):
        if targetChar.endswith('(custom rig)'):
            targetChar = targetChar.replace('(custom rig)', "")
        mel.eval("HIKCharacterControlsTool;")
        mel.eval('hikSetCurrentCharacter("{0}")'.format(targetChar))
        PlayerUi.hikUpdateTool()
        
    @staticmethod
    def SetHikSourceChar(source):
        _HUMAN_IK_SOURCE_MENU = "hikSourceList"
        _HUMAN_IK_SOURCE_MENU_OPTION = _HUMAN_IK_SOURCE_MENU + "|OptionMenu"
        items = cmds.optionMenuGrp(_HUMAN_IK_SOURCE_MENU, q=True, ill=True)
        for i in range(0, len(items)):
            label = cmds.menuItem(items[i], q=True, l=True)

            
            if label.lstrip() == source:
                cmds.optionMenu(_HUMAN_IK_SOURCE_MENU_OPTION, e=True, sl=i + 1)
                mel.eval("hikUpdateCurrentSourceFromUI()")
                mel.eval("hikUpdateContextualUI()")
                #mel.eval("hikControlRigSelectionChangedCallback")
                break   
                
            
    def showProgress(self,name,*args):
        progressBar_window = "Baking_progressWindow"
        progressBar_bar = "Baking_progressBar"
        try:
            if cmds.window(progressBar_window , exists=True):
                cmds.deleteUI(progressBar_window  )
        except RuntimeError:
            pass
        
        progressBar_window  = cmds.window(progressBar_window , title=f"Baking... Please wait.", widthHeight=(300, 100), parent = self.mainWindow, menuBarCornerWidget = (self.mainWindow, "topRight"))
        cmds.columnLayout(adjustableColumn=True)
        player_text = cmds.text(label=f'Baking {name}')
        cmds.separator( h=10, style='none')
        statusBar = cmds.progressBar(progressBar_bar,maxValue=100, width=300, height=20,isInterruptable=True, isMainProgressBar=True)
        cmds.showWindow(progressBar_window )
        
        return statusBar, player_text, progressBar_window
    
    def import_custom_char(self,char):
        
        namespace = char.split(":")[0]
        refList = pm.listReferences()
        for ref in refList:
            ref_ns = ref.namespace
            if ref_ns == namespace:
                ref.importContents() 
                
        allNode = pm.ls(f"{namespace}:CustomRigDefaultMappingNode*") 
        allState = pm.ls(f'{namespace}:HIKState*' )
        pm.delete(allState)
        pm.delete(allNode)
        
        PlayerUi.SetHikChar(char)
        PlayerUi.SetHikSourceChar("None")
     
               
    def bake_all_char(self, *args):
        menu_Items = cmds.optionMenu('playerRef_option_menu', q=True, itemListLong=True)
        all_items= [cmds.menuItem(i, query=True, label=True) for i in menu_Items]
  
        statusBar,player_text,progressBar_window = self.showProgress(name= "Starting..")
        percent = 0
  
        all_items= [cmds.menuItem(i, query=True, label=True) for i in menu_Items]
        baked_char_list = []
        char_list = PlayerUi.GetCharList()
        for char in char_list:
            if char.endswith('(custom rig)'):
                char = char.replace('(custom rig)', "")
            if ":" in char:
                char_name = char.split (":")[0]
                if char_name in all_items:
                    bones = PlayerUi.getCharacterNodes(char)
                    
                    add_ctl = [f"{char_name}:FKHead_M.translate",
                    f"{char_name}:FKElbow_L.translate",
                    f"{char_name}:FKWrist_L.translate",
                    f"{char_name}:FKElbow_R.translate",
                    f"{char_name}:FKWrist_R.translate",
                    f"{char_name}:IKLeg_L.rotate",
                    f"{char_name}:IKLeg_L.translate",
                    f"{char_name}:PoleLeg_R.rotate",
                    f"{char_name}:PoleLeg_R.translate",
                    f"{char_name}:PoleLeg_L.rotate",
                    f"{char_name}:PoleLeg_L.translate",
                    f"{char_name}:IKLeg_R.rotate",
                    f"{char_name}:IKLeg_R.translate",
                    f"{char_name}:FKChest_M.translate",
                    f"{char_name}:FKKnee_R.translate",
                    f"{char_name}:FKKnee_L.translate",
                    f"{char_name}:FKAnkle_L.translate",
                    f"{char_name}:FKAnkle_R.translate"]
                    
                    bones += add_ctl
                    baked_char_list += bones
        percent = 20
        cmds.text(player_text, edit=True, label=f'Baking all players (1/3)..' ) 
        cmds.progressBar(statusBar, edit=True, progress=percent)
        
        start = pm.playbackOptions(q=1, minTime=1)
        end = pm.playbackOptions(q=1, maxTime=1)
        PlayerUi.bake(baked_char_list,start, end)
        
        
        percent = 40
        cmds.text(player_text, edit=True, label=f'Unloading all character sources (2/3)...') 
        cmds.progressBar(statusBar, edit=True, progress=percent)
        
        
        for char in range(len(char_list)):
            percent += int(char*50/len(char_list))
            print(f"{char_list[char]}")
            if ":" in char_list[char]:
                char_name = char_list[char].split (":")[0]
                cmds.text(player_text, edit=True, label=f"Unloading {char_name}'s source...")
                
                if char_name in all_items:
                    
                    PlayerUi.SetHikChar(char_list[char])
                    PlayerUi.SetHikSourceChar("None")
                    cmds.progressBar(statusBar, edit=True, progress=percent)
        
        
        percent = 90
        cmds.text(player_text, edit=True, label=f'Breaking connection (3/3)...' ) 
        
        cmds.progressBar(statusBar, edit=True, progress=percent)
        
        
        char_ctl_list = [i.split(".")[0] for i in baked_char_list if i.endswith('rotate')]
        # pm.warning(f' this is bake list {baked_char_list} {len(baked_char_list)}')
        for ctl in char_ctl_list:
            ctl_name = ctl.split(".")[0]
            # pm.warning(f"{ctl_name} is selected")
            if not ctl_name.endswith(('PoleLeg_L', 'PoleLeg_R', 'RootX_M', 'IKLeg_R', 'IKLeg_L')):
                pm.warning(f"{ctl_name} translate is removed")
                mel.eval(f'source channelBoxCommand;CBdeleteConnection "{str(ctl)}.tx";')
                mel.eval(f'source channelBoxCommand;CBdeleteConnection "{str(ctl)}.ty";')
                mel.eval(f'source channelBoxCommand;CBdeleteConnection "{str(ctl)}.tz";')
         
                mel.eval(f'source channelBoxCommand;CBdeleteConnection "{str(ctl)}.sx";')
                mel.eval(f'source channelBoxCommand;CBdeleteConnection "{str(ctl)}.sy";')
                mel.eval(f'source channelBoxCommand;CBdeleteConnection "{str(ctl)}.sz";')
            else:
                mel.eval(f'source channelBoxCommand;CBdeleteConnection "{str(ctl)}.sx";')
                mel.eval(f'source channelBoxCommand;CBdeleteConnection "{str(ctl)}.sy";')
                mel.eval(f'source channelBoxCommand;CBdeleteConnection "{str(ctl)}.sz";')
            
        
        cmds.progressBar(statusBar, edit=True, progress=100)
        cmds.text(player_text, edit=True, label=f'Finishing..' ) 
        time.sleep(2)
            
        try:
            if cmds.window(progressBar_window, exists=True):
                print("Baking_progressWindow is existing")
                cmds.deleteUI(statusBar)
                cmds.deleteUI(progressBar_window)
                
        except RuntimeError:
            pass
      
    
    def create_ui(self):
        if cmds.window("playerUI", exists=True):
            cmds.deleteUI("playerUI")

        self.mainWindow =cmds.window("playerUI", title="MP Fbx Exporter v1.11", widthHeight=(550, 100), sizeable=0)
        self.form = cmds.formLayout()
        self.column = cmds.columnLayout(adjustableColumn=True, parent=self.form)
        
        
        # Export FBX
        fbx_export_row = cmds.rowLayout(numberOfColumns=6, adjustableColumn=2)
     
        cmds.text(label="  Select characters to export: ")
        
        #cmds.textField('export_fbx_textfield', pht= "Enter a name")
        cmds.optionMenu('playerRef_option_menu' )
        cmds.separator(width=10, style="none")
        cmds.button(label="FBX export", command=self.export_fbx_file)
        cmds.separator(width=10, style="none")
        cmds.checkBox("delete_static_channels",label='Delete Static Channels', enable =1, value =1)
        cmds.setParent('..')
        cmds.separator(h=20, style='single')
        
        extra_function_row = cmds.rowLayout(numberOfColumns=3, adjustableColumn=2)
        cmds.separator(width=30, style="none")
        cmds.button(label="Bake all HIK characters", command=self.bake_all_char)
        cmds.separator(width=30, style="none")
        cmds.setParent('..')
        
        
        # Form Layout Attachments
        cmds.formLayout(self.form, edit=True, attachForm=[(self.column, 'top', 5), (self.column, 'left', 5), (self.column, 'right', 5), (self.column, 'bottom', 5)])

        cmds.showWindow()
     
        self.update_player_ref()
        # PlayerUi.init()
      


                
   






