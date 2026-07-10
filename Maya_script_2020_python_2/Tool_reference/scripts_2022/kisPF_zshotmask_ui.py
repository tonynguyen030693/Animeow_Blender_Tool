###############################################################################
#
# Modified by:
#
#   Gorae (Choi Sangho / cucumber128@naver.com)
#
###############################################################################

import maya.cmds as cmds
import maya.OpenMaya as om

#from kisPF_zshotmask_ui import kisPF_ZShotMask, kisPF_ZShotMaskUi
#kisPF_ZShotMaskUi.display()


class kisPF_ZShotMask(object):

    PLUG_IN_NAME = "kisPF_zshotmask.py"
    NODE_NAME = "kisPF_zshotmask"

    TRANSFORM_NODE_NAME = "kisPF_zshotmask"
    SHAPE_NODE_NAME = "kisPF_zshotmask_shape"

    DEFAULT_BORDER_COLOR = [0.0, 0.0, 0.0, 1.0]
    DEFAULT_LABEL_COLOR = [1.0, 1.0, 1.0, 1.0]

    LABEL_COUNT = 6
    MIN_COUNTER_PADDING = 1
    MAX_COUNTER_PADDING = 6
    DEFAULT_COUNTER_PADDING = 4
    
    LABELS_TEXT_INIT= ["ep00",      "sc000_c000",  "Type",       "Focal Length", "I am Groot.",    "Frame"]
    FONT_SCALE_INIT = 0.7

    OPT_VAR_CAMERA_NAME     = "zurShotMaskCameraNameOptVar"
    OPT_VAR_LABEL_TEXT      = "zurShotMaskLabelTextOptVar"
    OPT_VAR_LABEL_FONT      = "zurShotMaskLabelFontOptVar"
    OPT_VAR_LABEL_COLOR     = "zurShotMaskLabelColorOptVar"
    OPT_VAR_LABEL_SCALE     = "zurShotMaskLabelScaleOptVar"
    OPT_VAR_BORDER_VISIBLE  = "zurShotMaskBorderVisibleOptVar"
    OPT_VAR_BORDER_COLOR    = "zurShotMaskBorderColorOptVar"
    OPT_VAR_BORDER_SCALE    = "zurShotMaskBorderScaleOptVar"
    OPT_VAR_COUNTER_POSITION= "zurShotMaskCounterPositionOptVar"
    OPT_VAR_COUNTER_PADDING = "zurShotMaskCounterPaddingOptVar"

    @classmethod
    def create_mask(cls):
        if not cmds.pluginInfo(cls.PLUG_IN_NAME, q=True, loaded=True):
            try:
                cmds.loadPlugin(cls.PLUG_IN_NAME)
            except:
                om.MGlobal.displayError("Failed to load kisPF_ZShotMask plug-in: {0}".format(cls.PLUG_IN_NAME))
                return

        if not cls.get_mask():
            transform_node = cmds.createNode("transform", name=cls.TRANSFORM_NODE_NAME)
            cmds.createNode(cls.NODE_NAME, name=cls.SHAPE_NODE_NAME, parent=transform_node)

        cls.refresh_mask()

    @classmethod
    def delete_mask(cls):
        mask = cls.get_mask()
        if mask:
            transform = cmds.listRelatives(mask, fullPath=True, parent=True)
            if transform:
                cmds.delete(transform)
            else:
                cmds.delete(mask)

    @classmethod
    def get_mask(cls):
        if cmds.pluginInfo(cls.PLUG_IN_NAME, q=True, loaded=True):
            nodes = cmds.ls(type=cls.NODE_NAME)
            if len(nodes) > 0:
                return nodes[0]

        return None

    @classmethod
    def refresh_mask(cls):
        mask = cls.get_mask()
        if not mask:
            return

        cmds.setAttr("{0}.camera".format(mask), cls.get_camera_name(), type="string")

        try:
            label_text = cls.get_label_text()
            cmds.setAttr("{0}.topLeftText".format(mask), label_text[0], type="string")
            cmds.setAttr("{0}.topCenterText".format(mask), label_text[1], type="string")
            cmds.setAttr("{0}.topRightText".format(mask), label_text[2], type="string")
            cmds.setAttr("{0}.bottomLeftText".format(mask), label_text[3], type="string")
            cmds.setAttr("{0}.bottomCenterText".format(mask), label_text[4], type="string")
            cmds.setAttr("{0}.bottomRightText".format(mask), label_text[5], type="string")
        except:
            pass

        label_color = cls.get_label_color()
        cmds.setAttr("{0}.fontName".format(mask), cls.get_label_font(), type="string")
        cmds.setAttr("{0}.fontColor".format(mask), label_color[0], label_color[1], label_color[2], type="double3")
        cmds.setAttr("{0}.fontAlpha".format(mask), label_color[3])
        cmds.setAttr("{0}.fontScale".format(mask), cls.get_label_scale())

        border_visibility = cls.get_border_visible()
        border_color = cls.get_border_color()
        cmds.setAttr("{0}.topBorder".format(mask), border_visibility[0])
        cmds.setAttr("{0}.bottomBorder".format(mask), border_visibility[1])
        cmds.setAttr("{0}.borderColor".format(mask), border_color[0], border_color[1], border_color[2], type="double3")
        cmds.setAttr("{0}.borderAlpha".format(mask), border_color[3])
        cmds.setAttr("{0}.borderScale".format(mask), cls.get_border_scale())

        cmds.setAttr("{0}.counterPosition".format(mask), cls.get_counter_position())
        cmds.setAttr("{0}.counterPadding".format(mask), cls.get_counter_padding())

    @classmethod
    def set_camera_name(cls, name):
        cmds.optionVar(sv=[cls.OPT_VAR_CAMERA_NAME, name])

    @classmethod
    def get_camera_name(cls):
        if cmds.optionVar(exists=cls.OPT_VAR_CAMERA_NAME):
            return cmds.optionVar(q=cls.OPT_VAR_CAMERA_NAME)
        else:
            return ""

    @classmethod
    def set_label_text(cls, text_array):
        array_len = len(text_array)
        if array_len != cls.LABEL_COUNT:
            om.MGlobal.displayError("Failed to set label text. Invalid number of text values in array: {0} (expected 6)".format(array_len))
            return

        cmds.optionVar(sv=[cls.OPT_VAR_LABEL_TEXT, text_array[0]])
        for i in range(1, array_len):
            cmds.optionVar(sva=[cls.OPT_VAR_LABEL_TEXT, text_array[i]])

    @classmethod
    def get_label_text(cls):
        if cmds.optionVar(exists=cls.OPT_VAR_LABEL_TEXT):
            return cmds.optionVar(q=cls.OPT_VAR_LABEL_TEXT)

        return cls.LABELS_TEXT_INIT

    @classmethod
    def set_label_font(cls, font):
        cmds.optionVar(sv=[cls.OPT_VAR_LABEL_FONT, font])

    @classmethod
    def get_label_font(cls):
        if cmds.optionVar(exists=cls.OPT_VAR_LABEL_FONT):
            label_font = cmds.optionVar(q=cls.OPT_VAR_LABEL_FONT)
            if label_font:
                return label_font

        if cmds.about(win=True):
            return "Times New Roman"
        elif cmds.about(mac=True):
            return "Times New Roman-Regular"
        elif cmds.about(linux=True):
            return "Courier"
        else:
            return "Times-Roman"

    @classmethod
    def set_label_color(cls, red, green, blue, alpha):
        cmds.optionVar(fv=[cls.OPT_VAR_LABEL_COLOR, red])
        cmds.optionVar(fva=[cls.OPT_VAR_LABEL_COLOR, green])
        cmds.optionVar(fva=[cls.OPT_VAR_LABEL_COLOR, blue])
        cmds.optionVar(fva=[cls.OPT_VAR_LABEL_COLOR, alpha])

    @classmethod
    def get_label_color(cls):
        if cmds.optionVar(exists=cls.OPT_VAR_LABEL_COLOR):
            return cmds.optionVar(q=cls.OPT_VAR_LABEL_COLOR)
        else:
            return cls.DEFAULT_LABEL_COLOR

    @classmethod
    def set_label_scale(cls, scale):
        cmds.optionVar(fv=[cls.OPT_VAR_LABEL_SCALE, scale])

    @classmethod
    def get_label_scale(cls):
        if cmds.optionVar(exists=cls.OPT_VAR_LABEL_SCALE):
            return cmds.optionVar(q=cls.OPT_VAR_LABEL_SCALE)
        else:
            return 0.7

    @classmethod
    def set_border_visible(cls, top, bottom):
        cmds.optionVar(iv=[cls.OPT_VAR_BORDER_VISIBLE, top])
        cmds.optionVar(iva=[cls.OPT_VAR_BORDER_VISIBLE, bottom])

    @classmethod
    def get_border_visible(cls):
        if cmds.optionVar(exists=cls.OPT_VAR_BORDER_VISIBLE):
            border_visibility = cmds.optionVar(q=cls.OPT_VAR_BORDER_VISIBLE)
            try:
                if len(border_visibility) == 2:
                    return border_visibility
            except:
                pass

        return [1, 1]

    @classmethod
    def set_border_color(cls, red, green, blue, alpha):
        cmds.optionVar(fv=[cls.OPT_VAR_BORDER_COLOR, red])
        cmds.optionVar(fva=[cls.OPT_VAR_BORDER_COLOR, green])
        cmds.optionVar(fva=[cls.OPT_VAR_BORDER_COLOR, blue])
        cmds.optionVar(fva=[cls.OPT_VAR_BORDER_COLOR, alpha])

    @classmethod
    def get_border_color(cls):
        if cmds.optionVar(exists=cls.OPT_VAR_BORDER_COLOR):
            return cmds.optionVar(q=cls.OPT_VAR_BORDER_COLOR)
        else:
            return cls.DEFAULT_BORDER_COLOR

    @classmethod
    def set_border_scale(cls, scale):
        cmds.optionVar(fv=[cls.OPT_VAR_BORDER_SCALE, scale])

    @classmethod
    def get_border_scale(cls):
        if cmds.optionVar(exists=cls.OPT_VAR_BORDER_SCALE):
            return cmds.optionVar(q=cls.OPT_VAR_BORDER_SCALE)
        else:
            return 1.0

    @classmethod
    def set_counter_position(cls, pos):
        cmds.optionVar(iv=[cls.OPT_VAR_COUNTER_POSITION, pos])

    @classmethod
    def get_counter_position(cls):
        if cmds.optionVar(exists=cls.OPT_VAR_COUNTER_POSITION):
            pos = cmds.optionVar(q=cls.OPT_VAR_COUNTER_POSITION)
            if pos >= 0 and pos <= 6:
                return pos

        return 6

    @classmethod
    def set_counter_padding(cls, padding):
        cmds.optionVar(iv=[cls.OPT_VAR_COUNTER_PADDING, padding])

    @classmethod
    def get_counter_padding(cls):
        if cmds.optionVar(exists=cls.OPT_VAR_COUNTER_PADDING):
            pos = cmds.optionVar(q=cls.OPT_VAR_COUNTER_PADDING)
            if pos >= cls.MIN_COUNTER_PADDING and pos <= cls.MAX_COUNTER_PADDING:
                return pos

        return cls.DEFAULT_COUNTER_PADDING

    @classmethod
    def reset_settings(cls):
        cmds.optionVar(remove=cls.OPT_VAR_BORDER_COLOR)
        cmds.optionVar(remove=cls.OPT_VAR_BORDER_SCALE)
        cmds.optionVar(remove=cls.OPT_VAR_BORDER_VISIBLE)
        cmds.optionVar(remove=cls.OPT_VAR_CAMERA_NAME)
        cmds.optionVar(remove=cls.OPT_VAR_COUNTER_PADDING)
        cmds.optionVar(remove=cls.OPT_VAR_COUNTER_POSITION)
        cmds.optionVar(remove=cls.OPT_VAR_LABEL_COLOR)
        cmds.optionVar(remove=cls.OPT_VAR_LABEL_FONT)
        cmds.optionVar(remove=cls.OPT_VAR_LABEL_SCALE)
        cmds.optionVar(remove=cls.OPT_VAR_LABEL_TEXT)



class kisPF_ZShotMaskUi (object) :
    
    VERSION         = "0.1"
    WINDOW_NAME     = "kisPF_ZShotMaskUi"
    APP_NAME        = "Pinkfong Shot Mask"
    
    LABELS          = [" Episode ", " Shot Name ", " Progress ", " Focal Length ", " Artist ", " Frame "]
    LABELS_TEXT_INIT= ["ep00",      "sc000_c000",  "Type",       "Focal Length", "I am Groot.",    "Frame"]
    FONT            = "Tahoma"
    FONT_SCALE      = 0.7
    ALL_CAMERAS     = "<All Cameras>"
    
    LABEL_SCALE = 1.0
    LABEL_COLOR = [1.0, 1.0, 1.0]
    LABEL_ALPHA = [1.0, 1.0, 1.0]

    BORDER_SCALE = 1.0
    BORDER_COLOR = [0.0, 0.0, 0.0]
    BORDER_ALPHA = [0.5, 0.5, 0.5]
    
    COUNTER_POSITION = 6
    COUNTER_PADDING  = 4
    
    @classmethod
    def display(cls):
        cls.delete()
        
        main_window = cmds.window(cls.WINDOW_NAME,
                                  title    = "{0}".format(cls.APP_NAME),
                                  sizeable = True,
                                  menuBar  = True)
        
        #edit_menu = cmds.menu (label="Edit", parent=main_window)
        #cmds.menuItem (label="Reset Settings", command="kisPF_ZShotMaskUi.reset_settings()", parent=edit_menu)

        #help_menu = cmds.menu (label="Help", parent=main_window)
        #cmds.menuItem (label="About", command="kisPF_ZShotMaskUi.about()", parent=help_menu)
        
        main_layout = cmds.columnLayout(adjustableColumn=True, parent=main_window)

        cmds.separator (style="double", h=10, parent=main_layout)

        # Buttons
        button_layout = cmds.formLayout(parent=main_layout)
        resolve_btn = cmds.button(label = "Resolve",
                                 width = 80,
                                 bgc = [0.4, 0.5, 0.84],
                                 command = "kisPF_ZShotMaskUi.resolve()",
                                 parent = button_layout)
        create_btn = cmds.button(label = "Create",
                                 width = 80,
                                 bgc = [0.5, 0.85, 0.4],
                                 command = "kisPF_ZShotMask.create_mask()",
                                 parent = button_layout)
        delete_btn = cmds.button(label = "Delete",
                                 width = 80,
                                 bgc = [0.85, 0.5, 0.4],
                                 command = "kisPF_ZShotMask.delete_mask()",
                                 parent=button_layout)
        reset_btn = cmds.button(label = "Reset",
                                 width = 80,
                                 bgc = [0.85, 0.3, 0.1],
                                 command = 
                                 "kisPF_ZShotMask.reset_settings(),kisPF_ZShotMaskUi.update_ui_elements(),kisPF_ZShotMaskUi.update_mask()",
                                 parent=button_layout)
        cmds.formLayout(button_layout, e=True, af=(resolve_btn, "left", 10))
        cmds.formLayout(button_layout, e=True, ap=(resolve_btn, "right", 5, 25))
        cmds.formLayout(button_layout, e=True, ap=(create_btn, "left", 5, 25))
        cmds.formLayout(button_layout, e=True, ap=(create_btn, "right", 5, 50))
        cmds.formLayout(button_layout, e=True, ap=(delete_btn, "left", 5, 50))
        cmds.formLayout(button_layout, e=True, ap=(delete_btn, "right", 5, 75))
        cmds.formLayout(button_layout, e=True, ap=(reset_btn, "left", 5, 75))
        cmds.formLayout(button_layout, e=True, af=(reset_btn, "right", 5))

        cmds.separator (style="double", h=10, parent=main_layout)
        
        # Camera Section
        camera_layout       = cmds.frameLayout(label="Camera", parent=main_layout)
        camera_form_layout  = cmds.formLayout(parent=camera_layout)
        
        cls.camera_name = cmds.textFieldButtonGrp(label         ="Name  ",
                                                  buttonLabel   =" ... ",
                                                  columnWidth   =(1, 90),
                                                  changeCommand ="kisPF_ZShotMaskUi.update_mask()",
                                                  buttonCommand ="kisPF_ZShotMaskUi.display_camera_dialog()",
                                                  parent=camera_form_layout)
        
        cmds.formLayout(camera_form_layout, e=True, af=(cls.camera_name, "top", 3))
        cmds.formLayout(camera_form_layout, e=True, af=(cls.camera_name, "left", 0))
        
        # Labels Section
        label_layout = cmds.frameLayout(label="Labels", parent=main_layout)
        label_form_layout = cmds.formLayout(parent=label_layout)
        
        cls.label_text_ctrls                = []
        cls.label_settings_scale_ctrls      = []
        cls.label_settings_offset_x_ctrls   = []
        cls.label_settings_offset_y_ctrls   = []
        
        label_text = ["", "", "", "", "", ""]
        
        for i in range(0, len(label_text)):
            cls.create_label_fields(i, label_form_layout)
        
        """
        """
            
        cmds.formLayout(label_form_layout, e=True, af=(cls.label_text_ctrls[0], "top", 3))
        cmds.formLayout(label_form_layout, e=True, af=(cls.label_text_ctrls[0], "left", 0))

        label_text_count = len(cls.label_text_ctrls)
        for i in range(1, label_text_count):
            cmds.formLayout(label_form_layout, e=True, ac=(cls.label_text_ctrls[i], "top",   0, cls.label_text_ctrls[i - 1]))
            cmds.formLayout(label_form_layout, e=True, aoc=(cls.label_text_ctrls[i], "left", 0, cls.label_text_ctrls[i - 1]))

        artist_btn = cmds.button(label="Edit", parent=label_form_layout)
        cmds.button(artist_btn, e=True, c=("kisPF_ZShotMaskUi.toggle_artist_btn('{0}', '{1}')".format(artist_btn, cls.label_text_ctrls[4])))
        print (artist_btn)
        print ("kisPF_ZShotMaskUi.toggle_artist_btn({0}, {1})".format(artist_btn,cls.label_text_ctrls[4]))
        
        cmds.formLayout(label_form_layout, e=True, ac =(artist_btn, "top",  0, cls.label_text_ctrls[3]))
        cmds.formLayout(label_form_layout, e=True, ac =(artist_btn, "left", 0, cls.label_text_ctrls[4]))
        
        cmds.window(main_window, e=True, w=100, h=100)
        cmds.window(main_window, e=True, sizeable=False)
        cmds.window(main_window, e=True, rtf=True)
        
        cls.update_ui_elements()
        cmds.showWindow(main_window)
        
    @classmethod
    def delete(cls):
        if cmds.window(cls.WINDOW_NAME, exists=True):
            cmds.deleteUI(cls.WINDOW_NAME, window=True)


    @classmethod
    def create_label_fields(cls, text_index, parent):
        text = cmds.textFieldGrp(label=cls.LABELS[text_index],
                                 columnWidth=(1, 90),
                                 changeCommand="kisPF_ZShotMaskUi.update_mask()",
                                 enable=False,
                                 text=cls.LABELS_TEXT_INIT[text_index],
                                 parent=parent)
        
        cls.label_text_ctrls.append(text)
    
    @classmethod
    def toggle_artist_btn(cls, btn, field) :
        btn_label = cmds.button(btn, q=True, label=True)
        if btn_label == "Edit":
            cmds.button(btn, e=True, label="OK")
            cmds.textFieldGrp(field, e=True, enable=True)
        else :
            cmds.button(btn, e=True, label="Edit")
            cmds.textFieldGrp(field, e=True, enable=False)
            cls.update_mask()
    
    @classmethod
    def resolve (cls) :
        file = cmds.file(q=True, sn=True)
        fileSplit = file.split('/')
        fileSplit = fileSplit[-1].split('.')
        info = fileSplit[0].split('_')
        if(len(info)<4) :
            cmds.warning('The current file name can not be resolved.')
            return
        else :
            text_array = []
            for i in range(len(cls.LABELS)):
                text_array.append(cmds.textFieldGrp(cls.label_text_ctrls[i], q=True, text=True))
            text_array[0] = info[1]
            text_array[1] = '{0}_{1}'.format(info[2], info[3])
            if info[4] == 'lay':
                text_array[2] = ('Layout_{0}'.format(info[5]))
            elif info[4] == 'rou':
                text_array[2] = ('Rough_{0}'.format(info[5]))
            elif info[4] == 'det':
                text_array[2] = ('Detail_{0}'.format(info[5]))
            else :
                text_array[2] = ('{0}_{1}'.format(info[4], info[5]))
                
        kisPF_ZShotMask.set_label_text(text_array)
        kisPF_ZShotMaskUi.update_ui_elements()
        kisPF_ZShotMaskUi.update_mask()
        
    @classmethod
    def create (cls) :
        if cls.get_mask():
            cls.update_mask()
        else :
            kisPF_ZShotMask.create_mask()
    
    @classmethod
    def display_camera_dialog(cls):
        result = cmds.layoutDialog(ui="kisPF_ZShotMaskUi.camera_dialog_layout()",
                                   title="Select Camera",
                                   parent=cls.WINDOW_NAME)
        if result not in ["cancel", "dismiss"]:
            cmds.textFieldButtonGrp(cls.camera_name, e=True, text=result)
            cls.update_mask()

    @classmethod
    def camera_dialog_layout(cls):
        cameras = cmds.listCameras()
        cameras.insert(0, cls.ALL_CAMERAS)
        
        layout = cmds.setParent(q=True)
        cmds.formLayout(layout, e=True)
        
        cls.camera_tsl = cmds.textScrollList(numberOfRows = 8,
                                             parent = layout)
        for camera in cameras:
            cmds.textScrollList(cls.camera_tsl,
                                e = True,
                                append = camera,
                                doubleClickCommand = "kisPF_ZShotMaskUi.camera_dialog_ok()")
        
        current_camera = cmds.textFieldButtonGrp(cls.camera_name, q=True, text=True)
        if current_camera in camera:
            cmds.textScrollList(cls.camera_tsl, e=True, selectItem=current_camera)
            
        ok_button     = cmds.button(label="OK",     c="kisPF_ZShotMaskUi.camera_dialog_ok()")
        cancel_button = cmds.button(label="Cancel", c="kisPF_ZShotMaskUi.camera_dialog_cancel()")
        
        cmds.formLayout(layout, e=True, af=(cls.camera_tsl, "top", 0))
        cmds.formLayout(layout, e=True, af=(cls.camera_tsl, "left", 0))
        cmds.formLayout(layout, e=True, af=(cls.camera_tsl, "right", 0))
        
        cmds.formLayout(layout, e=True, ac=(cancel_button, "top", 4, cls.camera_tsl))
        cmds.formLayout(layout, e=True, af=(cancel_button, "right", 0))
        
        cmds.formLayout(layout, e=True, ac=(ok_button, "top", 4, cls.camera_tsl))
        cmds.formLayout(layout, e=True, ac=(ok_button, "right", 2, cancel_button))
        
    @classmethod
    def camera_dialog_ok(cls):
        selection = cmds.textScrollList(cls.camera_tsl, q=True, selectItem=True)
        if not selection:
            camera = ""
        else:
            camera = selection[0]
        
        split_path_name = camera.split('|')
        camera = split_path_name[-1]
        
        cmds.layoutDialog(dismiss=camera)
    
    @classmethod
    def camera_dialog_cancel(cls):
        cmds.layoutDialog(dismiss="cancel")

    @classmethod
    def update_ui_elements(cls):
        if not cmds.window(cls.WINDOW_NAME, exists=True):
            return
        
        camera_name = kisPF_ZShotMask.get_camera_name()
        if not camera_name:
            camera_name = cls.ALL_CAMERAS
        cmds.textFieldButtonGrp(cls.camera_name, e=True, text=camera_name)
        
        label_text = kisPF_ZShotMask.get_label_text()
        for i in range(len(cls.label_text_ctrls)):
            cmds.textFieldGrp(cls.label_text_ctrls[i], e=True, text=label_text[i])

        label_color = cls.LABEL_COLOR
        label_alpha = cls.LABEL_ALPHA
        border_color = cls.BORDER_COLOR
        border_alpha = cls.BORDER_ALPHA
        
    @classmethod
    def update_mask(cls):
        if not cmds.window(cls.WINDOW_NAME, exists=True):
            return

        kisPF_ZShotMask.set_camera_name(cmds.textFieldButtonGrp(cls.camera_name, q=True, text=True))

        text_array = []
        for i in range(len(cls.LABELS)):
            text_array.append(cmds.textFieldGrp(cls.label_text_ctrls[i], q=True, text=True))

        kisPF_ZShotMask.set_label_text(text_array)
        kisPF_ZShotMask.set_label_font(cls.FONT)
        kisPF_ZShotMask.set_label_color(cls.LABEL_COLOR[0],cls.LABEL_COLOR[1],cls.LABEL_COLOR[2], cls.LABEL_ALPHA[0])
        kisPF_ZShotMask.set_label_scale(cls.FONT_SCALE)

        kisPF_ZShotMask.set_border_visible(True,True)
        kisPF_ZShotMask.set_border_color(cls.BORDER_COLOR[0],cls.BORDER_COLOR[1],cls.BORDER_COLOR[2], cls.BORDER_ALPHA[0])
        kisPF_ZShotMask.set_border_scale(cls.BORDER_SCALE)

        kisPF_ZShotMask.set_counter_position(cls.COUNTER_POSITION)
        kisPF_ZShotMask.set_counter_padding(cls.COUNTER_PADDING)

        kisPF_ZShotMask.refresh_mask()

    @classmethod
    def about(cls):
        message = '<h3>Zurbrigg {0}</h3>'.format(cls.APP_NAME)
        message += '<p>Version: {0}<br>'.format(cls.VERSION)
        message += 'Author:  Chris Zurbrigg</p>'
        message += '<a style="color:white;" href="http://zurbrigg.com">http://zurbrigg.com</a><br>'
        message += '<p>Copyright &copy; 2017 Chris Zurbrigg</p>'

        cmds.confirmDialog(title="About", button="OK", message=message, messageAlign="left", parent=cls.WINDOW_NAME)

    @classmethod
    def reset_settings(cls):
        kisPF_ZShotMask.reset_settings()
        kisPF_ZShotMask.refresh_mask()

        cls.update_ui_elements()


if __name__ == "__main__":
    kisPF_ZShotMaskUi.display()
