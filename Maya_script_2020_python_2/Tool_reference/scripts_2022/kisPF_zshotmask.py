###############################################################################
# Name:
#   kisPF_zshotmask.py
#
# Author:
#   Chris Zurbrigg (http://zurbrigg.com)
#
# Modified by:
#
#   Gorae (Choi Sangho / cucumber128@naver.com)
#
# Usage:
#   Visit http://zurbrigg.com for details
#
# Copyright (C) 2017 Chris Zurbrigg. All rights reserved.
###############################################################################

import maya.api.OpenMaya as om
import maya.api.OpenMayaRender as omr
import maya.api.OpenMayaUI as omui

import maya.cmds as cmds


def maya_useNewAPI():
    """
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass


class kisPF_ZShotMaskLocator(omui.MPxLocatorNode):
    """
    """

    NAME = "kisPF_zshotmask"
    TYPE_ID = om.MTypeId(0x0011A895)
    #TYPE_ID = om.MTypeId(0x0011A885)
    DRAW_DB_CLASSIFICATION = "drawdb/geometry/kisPF_zshotmask"
    DRAW_REGISTRANT_ID = "kisPF_ZShotMaskNode"

    TEXT_ATTRS = ["topLeftText",      "tlt", 
                  "topCenterText",    "tct", 
                  "topRightText",     "trt",
                  "bottomLeftText",   "blt", 
                  "bottomCenterText", "bct", 
                  "bottomRightText",  "brt"]

    def __init__(self):
        """
        """
        super(kisPF_ZShotMaskLocator, self).__init__()

    @classmethod
    def creator(cls):
        """
        """
        return kisPF_ZShotMaskLocator()

    @classmethod
    def initialize(cls):
        """
        """

        t_attr = om.MFnTypedAttribute()
        stringData = om.MFnStringData()
        obj = stringData.create("")
        camera_name = t_attr.create("camera", "cam", om.MFnData.kString, obj)
        t_attr.writable = True
        t_attr.storable = True
        t_attr.keyable = False
        kisPF_ZShotMaskLocator.addAttribute(camera_name)

        attr = om.MFnNumericAttribute()
        counter_position = attr.create("counterPosition", "cp", om.MFnNumericData.kShort, 6)
        attr.writable = True
        attr.storable = True
        attr.keyable = True
        attr.setMin(0)
        attr.setMax(6)
        kisPF_ZShotMaskLocator.addAttribute(counter_position)

        attr = om.MFnNumericAttribute()
        counter_padding = attr.create("counterPadding", "cpd", om.MFnNumericData.kShort, 4)
        attr.writable = True
        attr.storable = True
        attr.keyable = True
        attr.setMin(1)
        attr.setMax(6)
        kisPF_ZShotMaskLocator.addAttribute(counter_padding)

        for i in range(0, len(cls.TEXT_ATTRS), 2):
            t_attr = om.MFnTypedAttribute()
            stringData = om.MFnStringData()
            obj = stringData.create("Position {0}".format(str(i / 2 + 1).zfill(2)))
            position = t_attr.create(cls.TEXT_ATTRS[i], cls.TEXT_ATTRS[i + 1], om.MFnData.kString, obj)
            t_attr.writable = True
            t_attr.storable = True
            t_attr.keyable = True
            kisPF_ZShotMaskLocator.addAttribute(position)

        attr = om.MFnNumericAttribute()
        counter_position = attr.create("textPadding", "tp", om.MFnNumericData.kShort, 10)
        attr.writable = True
        attr.storable = True
        attr.keyable = True
        attr.setMin(0)
        attr.setMax(50)
        kisPF_ZShotMaskLocator.addAttribute(counter_position)

        t_attr = om.MFnTypedAttribute()
        stringData = om.MFnStringData()
        obj = stringData.create("Consolas")
        font_name = t_attr.create("fontName", "fn", om.MFnData.kString, obj)
        t_attr.writable = True
        t_attr.storable = True
        t_attr.keyable = True
        kisPF_ZShotMaskLocator.addAttribute(font_name)

        attr = om.MFnNumericAttribute()
        font_color = attr.createColor("fontColor", "fc")
        attr.default = (1.0, 1.0, 1.0)
        attr.writable = True
        attr.storable = True
        attr.keyable = True
        kisPF_ZShotMaskLocator.addAttribute(font_color)

        attr = om.MFnNumericAttribute()
        font_alpha = attr.create("fontAlpha", "fa", om.MFnNumericData.kFloat, 1.0)
        attr.writable = True
        attr.storable = True
        attr.keyable = True
        attr.setMin(0.0)
        attr.setMax(1.0)
        kisPF_ZShotMaskLocator.addAttribute(font_alpha)

        attr = om.MFnNumericAttribute()
        font_scale = attr.create("fontScale", "fs", om.MFnNumericData.kFloat, 1.0)
        attr.writable = True
        attr.storable = True
        attr.keyable = True
        attr.setMin(0.1)
        attr.setMax(2.0)
        kisPF_ZShotMaskLocator.addAttribute(font_scale)

        attr = om.MFnNumericAttribute()
        top_border = attr.create("topBorder", "tbd", om.MFnNumericData.kBoolean, True)
        attr.writable = True
        attr.storable = True
        attr.keyable = True
        kisPF_ZShotMaskLocator.addAttribute(top_border)

        attr = om.MFnNumericAttribute()
        bottom_border = attr.create("bottomBorder", "bbd", om.MFnNumericData.kBoolean, True)
        attr.writable = True
        attr.storable = True
        attr.keyable = True
        kisPF_ZShotMaskLocator.addAttribute(bottom_border)

        attr = om.MFnNumericAttribute()
        border_color = attr.createColor("borderColor", "bc")
        attr.default = (0.0, 0.0, 0.0)
        attr.writable = True
        attr.storable = True
        attr.keyable = True
        kisPF_ZShotMaskLocator.addAttribute(border_color)

        attr = om.MFnNumericAttribute()
        border_alpha = attr.create("borderAlpha", "ba", om.MFnNumericData.kFloat, 1.0)
        attr.writable = True
        attr.storable = True
        attr.keyable = True
        attr.setMin(0.0)
        attr.setMax(1.0)
        kisPF_ZShotMaskLocator.addAttribute(border_alpha)

        attr = om.MFnNumericAttribute()
        border_scale = attr.create("borderScale", "bs", om.MFnNumericData.kFloat, 1.0)
        attr.writable = True
        attr.storable = True
        attr.keyable = True
        attr.setMin(0.5)
        attr.setMax(2.0)
        kisPF_ZShotMaskLocator.addAttribute(border_scale)


class kisPF_ZShotMaskData(om.MUserData):
    """
    """

    def __init__(self):
        """
        """
        super(kisPF_ZShotMaskData, self).__init__(False)  # don't delete after draw


class kisPF_ZShotMaskDrawOverride(omr.MPxDrawOverride):
    """
    """

    NAME = "kisPF_zshotmask_draw_override"

    def __init__(self, obj):
        """
        """
        super(kisPF_ZShotMaskDrawOverride, self).__init__(obj, kisPF_ZShotMaskDrawOverride.draw)

    def supportedDrawAPIs(self):
        """
        """
        return (omr.MRenderer.kAllDevices)

    def isBounded(self, obj_path, camera_path):
        """
        """
        return False

    def boundingBox(self, obj_path, camera_path):
        """
        """
        return om.MBoundingBox()

    def prepareForDraw(self, obj_path, camera_path, frame_context, old_data):
        """
        """
        data = old_data
        if not isinstance(data, kisPF_ZShotMaskData):
            data = kisPF_ZShotMaskData()

        fnDagNode = om.MFnDagNode(obj_path)

        data.camera_name = fnDagNode.findPlug("camera", False).asString()

        data.text_fields = []
        for i in range(0, len(kisPF_ZShotMaskLocator.TEXT_ATTRS), 2):
            data.text_fields.append(fnDagNode.findPlug(kisPF_ZShotMaskLocator.TEXT_ATTRS[i], False).asString())

        counter_padding = fnDagNode.findPlug("counterPadding", False).asInt()
        if counter_padding < 1:
            counter_padding = 1
        elif counter_padding > 6:
            counter_padding = 6

        current_time = int(cmds.currentTime(q=True))
        counter_position = fnDagNode.findPlug("counterPosition", False).asInt()
        if counter_position > 0 and counter_position <= len(kisPF_ZShotMaskLocator.TEXT_ATTRS) / 2:
            data.text_fields[counter_position - 1] = "{0}".format(str(current_time).zfill(counter_padding))

        data.text_padding = fnDagNode.findPlug("textPadding", False).asInt()

        camera_path = frame_context.getCurrentCameraPath()
        camera = om.MFnCamera(camera_path)
        focal_length = camera.focalLength
        data.text_fields[3] = "{0} {1}".format(str(round(focal_length, 1)), "mm")
        
        data.font_name = fnDagNode.findPlug("fontName", False).asString()

        r = fnDagNode.findPlug("fontColorR", False).asFloat()
        g = fnDagNode.findPlug("fontColorG", False).asFloat()
        b = fnDagNode.findPlug("fontColorB", False).asFloat()
        a = fnDagNode.findPlug("fontAlpha", False).asFloat()
        data.font_color = om.MColor((r, g, b, a))

        data.font_scale = fnDagNode.findPlug("fontScale", False).asFloat()

        r = fnDagNode.findPlug("borderColorR", False).asFloat()
        g = fnDagNode.findPlug("borderColorG", False).asFloat()
        b = fnDagNode.findPlug("borderColorB", False).asFloat()
        a = fnDagNode.findPlug("borderAlpha", False).asFloat()
        data.border_color = om.MColor((r, g, b, a))

        data.border_scale = fnDagNode.findPlug("borderScale", False).asFloat()

        data.top_border = fnDagNode.findPlug("topBorder", False).asBool()
        data.bottom_border = fnDagNode.findPlug("bottomBorder", False).asBool()

        return data

    def hasUIDrawables(self):
        """
        """
        return True

    def addUIDrawables(self, obj_path, draw_manager, frame_context, data):
        """
        """
        if not isinstance(data, kisPF_ZShotMaskData):
            return

        camera_path = frame_context.getCurrentCameraPath()
        camera = om.MFnCamera(camera_path)

        if data.camera_name and self.camera_exists(data.camera_name) and not self.is_camera_match(camera_path, data.camera_name):
            return

        camera_aspect_ratio = camera.aspectRatio()
        device_aspect_ratio = cmds.getAttr("defaultResolution.deviceAspectRatio")

        vp_x, vp_y, vp_width, vp_height = frame_context.getViewportDimensions()
        vp_half_width = 0.5 * vp_width
        vp_half_height = 0.5 * vp_height
        vp_aspect_ratio = vp_width / float(vp_height)

        scale = 1.0

        if camera.filmFit == om.MFnCamera.kHorizontalFilmFit:
            mask_width = vp_width / camera.overscan
            mask_height = mask_width / device_aspect_ratio
        elif camera.filmFit == om.MFnCamera.kVerticalFilmFit:
            mask_height = vp_height / camera.overscan
            mask_width = mask_height * device_aspect_ratio
        elif camera.filmFit == om.MFnCamera.kFillFilmFit:
            if vp_aspect_ratio < camera_aspect_ratio:
                if camera_aspect_ratio < device_aspect_ratio:
                    scale = camera_aspect_ratio / vp_aspect_ratio
                else:
                    scale = device_aspect_ratio / vp_aspect_ratio
            elif camera_aspect_ratio > device_aspect_ratio:
                scale = device_aspect_ratio / camera_aspect_ratio

            mask_width = vp_width / camera.overscan * scale
            mask_height = mask_width / device_aspect_ratio

        elif camera.filmFit == om.MFnCamera.kOverscanFilmFit:
            if vp_aspect_ratio < camera_aspect_ratio:
                if camera_aspect_ratio < device_aspect_ratio:
                    scale = camera_aspect_ratio / vp_aspect_ratio
                else:
                    scale = device_aspect_ratio / vp_aspect_ratio
            elif camera_aspect_ratio > device_aspect_ratio:
                scale = device_aspect_ratio / camera_aspect_ratio

            mask_height = vp_height / camera.overscan / scale
            mask_width = mask_height * device_aspect_ratio
        else:
            om.MGlobal.displayError("[kisPF_ZShotMask] Unknown Film Fit value")
            return

        mask_half_width = 0.5 * mask_width
        mask_x = vp_half_width - mask_half_width

        mask_half_height = 0.5 * mask_height
        mask_bottom_y = vp_half_height - mask_half_height
        mask_top_y = vp_half_height + mask_half_height

        border_height = int(0.05 * mask_height * data.border_scale)
        background_size = (int(mask_width), border_height)

        draw_manager.beginDrawable()
        draw_manager.setFontName(data.font_name)
        draw_manager.setFontSize(int((border_height - border_height * 0.15) * data.font_scale))
        draw_manager.setColor(data.font_color)

        if data.top_border:
            self.draw_border(draw_manager, om.MPoint(mask_x, mask_top_y - border_height), background_size, data.border_color)
        if data.bottom_border:
            self.draw_border(draw_manager, om.MPoint(mask_x, mask_bottom_y), background_size, data.border_color)

        self.draw_text(draw_manager, om.MPoint(mask_x + data.text_padding, mask_top_y - border_height), data.text_fields[0], omr.MUIDrawManager.kLeft, background_size)
        self.draw_text(draw_manager, om.MPoint(vp_half_width, mask_top_y - border_height), data.text_fields[1], omr.MUIDrawManager.kCenter, background_size)
        self.draw_text(draw_manager, om.MPoint(mask_x + mask_width - data.text_padding, mask_top_y - border_height), data.text_fields[2], omr.MUIDrawManager.kRight, background_size)
        self.draw_text(draw_manager, om.MPoint(mask_x + data.text_padding, mask_bottom_y), data.text_fields[3], omr.MUIDrawManager.kLeft, background_size)
        self.draw_text(draw_manager, om.MPoint(vp_half_width, mask_bottom_y), data.text_fields[4], omr.MUIDrawManager.kCenter, background_size)
        self.draw_text(draw_manager, om.MPoint(mask_x + mask_width - data.text_padding, mask_bottom_y), data.text_fields[5], omr.MUIDrawManager.kRight, background_size)

        draw_manager.endDrawable()

    def draw_border(self, draw_manager, position, background_size, color):
        """
        """
        draw_manager.text2d(position, " ", alignment=omr.MUIDrawManager.kLeft, backgroundSize=background_size, backgroundColor=color)

    def draw_text(self, draw_manager, position, text, alignment, background_size):
        """
        """
        if(len(text) > 0):
            draw_manager.text2d(position, text, alignment=alignment, backgroundSize=background_size, backgroundColor=om.MColor((0.0, 0.0, 0.0, 0.0)))

    def camera_exists(self, name):
        """
        """
        # ---------------------------------------------------------------------
        # om.MItDependencyNodes is only supported in Maya 2016.5 and newer
        # ---------------------------------------------------------------------
        # dg_iter = om.MItDependencyNodes(om.MFn.kCamera)
        # while not dg_iter.isDone():
        #     if dg_iter.thisNode().hasFn(om.MFn.kDagNode):
        #         camera_path = om.MDagPath.getAPathTo(dg_iter.thisNode())
        #         if self.is_camera_match(camera_path, name):
        #             return True
        #     dg_iter.next()
        # return False

        return name in cmds.listCameras()

    def is_camera_match(self, camera_path, name):
        """
        """
        path_name = camera_path.fullPathName()
        split_path_name = path_name.split('|')
        if len(split_path_name) >= 1:
            if split_path_name[-1] == name:
                return True
        if len(split_path_name) >= 2:
            if split_path_name[-2] == name:
                return True

        return False

    @staticmethod
    def creator(obj):
        """
        """
        return kisPF_ZShotMaskDrawOverride(obj)

    @staticmethod
    def draw(context, data):
        """
        """
        return


def initializePlugin(obj):
    """
    """
    pluginFn = om.MFnPlugin(obj, "Chris Zurbrigg", "1.0.1", "Any")

    try:
        pluginFn.registerNode(kisPF_ZShotMaskLocator.NAME,
                              kisPF_ZShotMaskLocator.TYPE_ID,
                              kisPF_ZShotMaskLocator.creator,
                              kisPF_ZShotMaskLocator.initialize,
                              om.MPxNode.kLocatorNode,
                              kisPF_ZShotMaskLocator.DRAW_DB_CLASSIFICATION)
    except:
        om.MGlobal.displayError("Failed to register node: {0}".format(kisPF_ZShotMaskLocator.NAME))

    try:
        omr.MDrawRegistry.registerDrawOverrideCreator(kisPF_ZShotMaskLocator.DRAW_DB_CLASSIFICATION,
                                                      kisPF_ZShotMaskLocator.DRAW_REGISTRANT_ID,
                                                      kisPF_ZShotMaskDrawOverride.creator)
    except:
        om.MGlobal.displayError("Failed to register draw override: {0}".format(kisPF_ZShotMaskDrawOverride.NAME))


def uninitializePlugin(obj):
    """
    """
    pluginFn = om.MFnPlugin(obj)

    try:
        omr.MDrawRegistry.deregisterDrawOverrideCreator(kisPF_ZShotMaskLocator.DRAW_DB_CLASSIFICATION, kisPF_ZShotMaskLocator.DRAW_REGISTRANT_ID)
    except:
        om.MGlobal.displayError("Failed to deregister draw override: {0}".format(kisPF_ZShotMaskDrawOverride.NAME))

    try:
        pluginFn.deregisterNode(kisPF_ZShotMaskLocator.TYPE_ID)
    except:
        om.MGlobal.displayError("Failed to unregister node: {0}".format(kisPF_ZShotMaskLocator.NAME))


if __name__ == "__main__":

    cmds.file(f=True, new=True)

    plugin_name = "kisPF_zshotmask.py"
    cmds.evalDeferred('if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(plugin_name))
    cmds.evalDeferred('if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(plugin_name))

    cmds.evalDeferred('cmds.createNode("kisPF_zshotmask")')
