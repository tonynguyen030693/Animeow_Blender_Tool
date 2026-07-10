import maya.cmds as mc
import functools
from pprint import pprint


def CGAdddRibbonTool_NJR():
    setup_ui()


def setup_ui():
    if mc.window('CgCreateSimCorrectiveBlendShapeToolWindow', ex=True):
        mc.deleteUI('CgCreateSimCorrectiveBlendShapeToolWindow')

    mc.window('CgCreateSimCorrectiveBlendShapeToolWindow', title='Cg Create Sim Corrective BlendShape Tool')
    c = mc.columnLayout(adj=True)
    checkBox_grp = ['r_up_arm_checkBox', 'l_up_arm_checkBox', 'r_lo_arm_checkBox', 'l_lo_arm_checkBox',
                    'r_up_leg_checkBox', 'l_up_leg_checkBox', 'r_lo_leg_checkBox', 'l_lo_leg_checkBox']
    mc.text(label='select character', p=c)
    mc.checkBox('all_checkBox', label='all', p=c, v=True, onc=functools.partial(change_checkBox_value, checkBox_grp),
                ofc=functools.partial(change_checkBox_value, checkBox_grp))
    r0 = mc.rowLayout(numberOfColumns=2, adjustableColumn=1, p=c)
    mc.checkBox('r_up_arm_checkBox', label='r_up_arm', p=r0, v=True,
                ofc=functools.partial(off_all_checkBox_value, 'all_checkBox'))
    mc.checkBox('l_up_arm_checkBox', label='l_up_arm', p=r0, v=True,
                ofc=functools.partial(off_all_checkBox_value, 'all_checkBox'))
    r1 = mc.rowLayout(numberOfColumns=2, adjustableColumn=1, p=c)
    mc.checkBox('r_lo_arm_checkBox', label='r_lo_arm', p=r1, v=True,
                ofc=functools.partial(off_all_checkBox_value, 'all_checkBox'))
    mc.checkBox('l_lo_arm_checkBox', label='l_lo_arm', p=r1, v=True,
                ofc=functools.partial(off_all_checkBox_value, 'all_checkBox'))
    r2 = mc.rowLayout(numberOfColumns=2, adjustableColumn=1, p=c)
    mc.checkBox('r_up_leg_checkBox', label='r_up_leg', p=r2, v=True,
                ofc=functools.partial(off_all_checkBox_value, 'all_checkBox'))
    mc.checkBox('l_up_leg_checkBox', label='l_up_leg', p=r2, v=True,
                ofc=functools.partial(off_all_checkBox_value, 'all_checkBox'))
    r3 = mc.rowLayout(numberOfColumns=2, adjustableColumn=1, p=c)
    mc.checkBox('r_lo_leg_checkBox', label='r_lo_leg', p=r3, v=True,
                ofc=functools.partial(off_all_checkBox_value, 'all_checkBox'))
    mc.checkBox('l_lo_leg_checkBox', label='l_lo_leg', p=r3, v=True,
                ofc=functools.partial(off_all_checkBox_value, 'all_checkBox'))
    mc.button('do_it_button', label='add ribbon', en=True, c=functools.partial(do_it, checkBox_grp), p=c)
    mc.button('do_remove_button', label='remove ribbon', en=True, c=functools.partial(do_remove, checkBox_grp), p=c)
    mc.showWindow('CgCreateSimCorrectiveBlendShapeToolWindow')


def do_it(*args):
    part_jt_dict = {'lf_up_arm': {1: 'L_Arm_Upper_Bind_01_Bn', 2: 'L_Arm_Upper_Bind_02_Bn', 3: 'L_Arm_Upper_Bind_03_Bn',
                                  4: 'L_Arm_Upper_Bind_04_Bn', 5: 'L_Arm_Upper_Bind_05_Bn'},
                    'rt_up_arm': {1: 'R_Arm_Upper_Bind_01_Bn', 2: 'R_Arm_Upper_Bind_02_Bn', 3: 'R_Arm_Upper_Bind_03_Bn',
                                  4: 'R_Arm_Upper_Bind_04_Bn', 5: 'R_Arm_Upper_Bind_05_Bn'},
                    'lf_lo_arm': {1: 'L_Arm_Lower_Bind_01_Bn', 2: 'L_Arm_Lower_Bind_02_Bn', 3: 'L_Arm_Lower_Bind_03_Bn',
                                  4: 'L_Arm_Lower_Bind_04_Bn', 5: 'L_Arm_Lower_Bind_05_Bn'},
                    'rt_lo_arm': {1: 'R_Arm_Lower_Bind_01_Bn', 2: 'R_Arm_Lower_Bind_02_Bn', 3: 'R_Arm_Lower_Bind_03_Bn',
                                  4: 'R_Arm_Lower_Bind_04_Bn', 5: 'R_Arm_Lower_Bind_05_Bn'},
                    'lf_up_leg': {1: 'L_Leg_Upper_Bind_01_Bn', 2: 'L_Leg_Upper_Bind_02_Bn', 3: 'L_Leg_Upper_Bind_03_Bn',
                                  4: 'L_Leg_Upper_Bind_04_Bn', 5: 'L_Leg_Upper_Bind_05_Bn'},
                    'rt_up_leg': {1: 'R_Leg_Upper_Bind_01_Bn', 2: 'R_Leg_Upper_Bind_02_Bn', 3: 'R_Leg_Upper_Bind_03_Bn',
                                  4: 'R_Leg_Upper_Bind_04_Bn', 5: 'R_Leg_Upper_Bind_05_Bn'},
                    'lf_lo_leg': {1: 'L_Leg_Lower_Bind_01_Bn', 2: 'L_Leg_Lower_Bind_02_Bn', 3: 'L_Leg_Lower_Bind_03_Bn',
                                  4: 'L_Leg_Lower_Bind_04_Bn', 5: 'L_Leg_Lower_Bind_05_Bn'},
                    'rt_lo_leg': {1: 'R_Leg_Lower_Bind_01_Bn', 2: 'R_Leg_Lower_Bind_02_Bn', 3: 'R_Leg_Lower_Bind_03_Bn',
                                  4: 'R_Leg_Lower_Bind_04_Bn', 5: 'R_Leg_Lower_Bind_05_Bn'}}
    part_compar_dict = {'lf_up_arm': 'L_Arm_01_Bn', 'lf_lo_arm': 'L_Arm_03_Bn', 'rt_up_arm': 'R_Arm_01_Bn',
                        'rt_lo_arm': 'R_Arm_03_Bn', 'lf_up_leg': 'L_Leg_01_Bn', 'lf_lo_leg': 'L_Leg_03_Bn',
                        'rt_up_leg': 'R_Leg_01_Bn', 'rt_lo_leg': 'R_Leg_03_Bn'}

    checkBox_compar_dict = {'r_up_arm_checkBox': 'rt_up_arm', 'l_up_arm_checkBox': 'lf_up_arm',
                            'r_lo_arm_checkBox': 'rt_lo_arm', 'l_lo_arm_checkBox': 'lf_lo_arm',
                            'r_up_leg_checkBox': 'rt_up_leg', 'l_up_leg_checkBox': 'lf_up_leg',
                            'r_lo_leg_checkBox': 'rt_lo_leg', 'l_lo_leg_checkBox': 'lf_lo_leg'}
    ns = get_namespace()
    if ns:
        rs, rc, ro = create_ribbon_hierarchy()
        do_part = []
        for cb in args[0]:
            if mc.checkBox(cb, q=True, v=True):
                do_part.append(checkBox_compar_dict[cb])

        for part_name in do_part:
            ribbon_jt_dict, ribbon_grp_dict = duplicate_ribbon_joint(ns, part_name, part_jt_dict, rs)
            curve_obj_a = create_nurbs_curve(ns, part_name, ribbon_jt_dict, 1)
            curve_obj_b = create_nurbs_curve(ns, part_name, ribbon_jt_dict, -1)
            loft_plane = create_nurbs_plane(ns, curve_obj_a, curve_obj_b, '%s_loft_plane' % part_name, ro)
            rebuild_surface(loft_plane)
            follicle_dict = create_follicle(ns, loft_plane, 5, part_name, ro)
            connect_attr(follicle_dict, ribbon_jt_dict, True)
            ctrl_jt_dict = create_plane_rig(ns, loft_plane, ribbon_jt_dict, part_name, rs)
            ctrl_dict = create_ribbon_ctrl(ns, ctrl_jt_dict, part_name, rc, part_compar_dict)
            create_ctrl_shape(ctrl_dict)
            connect_attr(ctrl_dict, ctrl_jt_dict, False)
            combine_ribbon_to_rig(ns, ribbon_jt_dict, part_name, part_jt_dict)


def do_remove(*args):
    part_jt_dict = {'lf_up_arm': {1: 'L_Arm_Upper_Bind_01_Bn', 2: 'L_Arm_Upper_Bind_02_Bn', 3: 'L_Arm_Upper_Bind_03_Bn',
                                  4: 'L_Arm_Upper_Bind_04_Bn', 5: 'L_Arm_Upper_Bind_05_Bn'},
                    'rt_up_arm': {1: 'R_Arm_Upper_Bind_01_Bn', 2: 'R_Arm_Upper_Bind_02_Bn', 3: 'R_Arm_Upper_Bind_03_Bn',
                                  4: 'R_Arm_Upper_Bind_04_Bn', 5: 'R_Arm_Upper_Bind_05_Bn'},
                    'lf_lo_arm': {1: 'L_Arm_Lower_Bind_01_Bn', 2: 'L_Arm_Lower_Bind_02_Bn', 3: 'L_Arm_Lower_Bind_03_Bn',
                                  4: 'L_Arm_Lower_Bind_04_Bn', 5: 'L_Arm_Lower_Bind_05_Bn'},
                    'rt_lo_arm': {1: 'R_Arm_Lower_Bind_01_Bn', 2: 'R_Arm_Lower_Bind_02_Bn', 3: 'R_Arm_Lower_Bind_03_Bn',
                                  4: 'R_Arm_Lower_Bind_04_Bn', 5: 'R_Arm_Lower_Bind_05_Bn'},
                    'lf_up_leg': {1: 'L_Leg_Upper_Bind_01_Bn', 2: 'L_Leg_Upper_Bind_02_Bn', 3: 'L_Leg_Upper_Bind_03_Bn',
                                  4: 'L_Leg_Upper_Bind_04_Bn', 5: 'L_Leg_Upper_Bind_05_Bn'},
                    'rt_up_leg': {1: 'R_Leg_Upper_Bind_01_Bn', 2: 'R_Leg_Upper_Bind_02_Bn', 3: 'R_Leg_Upper_Bind_03_Bn',
                                  4: 'R_Leg_Upper_Bind_04_Bn', 5: 'R_Leg_Upper_Bind_05_Bn'},
                    'lf_lo_leg': {1: 'L_Leg_Lower_Bind_01_Bn', 2: 'L_Leg_Lower_Bind_02_Bn', 3: 'L_Leg_Lower_Bind_03_Bn',
                                  4: 'L_Leg_Lower_Bind_04_Bn', 5: 'L_Leg_Lower_Bind_05_Bn'},
                    'rt_lo_leg': {1: 'R_Leg_Lower_Bind_01_Bn', 2: 'R_Leg_Lower_Bind_02_Bn', 3: 'R_Leg_Lower_Bind_03_Bn',
                                  4: 'R_Leg_Lower_Bind_04_Bn', 5: 'R_Leg_Lower_Bind_05_Bn'}}
    checkBox_compar_dict = {'r_up_arm_checkBox': 'rt_up_arm', 'l_up_arm_checkBox': 'lf_up_arm',
                            'r_lo_arm_checkBox': 'rt_lo_arm', 'l_lo_arm_checkBox': 'lf_lo_arm',
                            'r_up_leg_checkBox': 'rt_up_leg', 'l_up_leg_checkBox': 'lf_up_leg',
                            'r_lo_leg_checkBox': 'rt_lo_leg', 'l_lo_leg_checkBox': 'lf_lo_leg'}
    ns = get_namespace()
    if ns:
        do_part = []
        for cb in args[0]:
            if mc.checkBox(cb, q=True, v=True):
                do_part.append(checkBox_compar_dict[cb])
        for part_name in do_part:
            ribbon_grp, ribbon_jt = find_ribbon_skeleton(ns, part_name, part_jt_dict)
            follicle_grp, plane = find_ribbon_noTransform(ns, part_name, 'loft_plane')
            ctrl_grp, ctrl_jt_grp = find_ribbon_ctrl(ns, part_name)
            ribbon_nodes = find_ribbon_nodes(ribbon_jt)
            reconnect_attr(ribbon_jt)
            mc.delete(ribbon_grp, follicle_grp, plane, ctrl_grp, ctrl_jt_grp)
            for rn in ribbon_nodes:
                mc.delete(rn)


def find_ribbon_skeleton(ns, part_name, part_jt_dict):
    top_grp = '%s%s_ribbon_grp' % (ns, part_name)
    rtd = {}
    for id in part_jt_dict[part_name].keys():
        jt = '%s%s' % (ns, part_jt_dict[part_name][id].replace('Bind', 'Ribbon'))
        rtd.setdefault(id, jt)
    return top_grp, rtd


def find_ribbon_noTransform(ns, part_name, plane_name):
    loft_plane = '%s%s_%s' % (ns, part_name, plane_name)
    follicle_top_grp = '%s%s_Follicle_Grp' % (ns, part_name)
    return follicle_top_grp, loft_plane


def find_ribbon_ctrl(ns, part_name):
    ctrl_grp = '%s%s_ribbon_ctrl_jt_grp' % (ns, part_name)
    ctrl_jt_grp = '%s%s_ctrl_grp' % (ns, part_name)
    return ctrl_grp, ctrl_jt_grp


def find_ribbon_nodes(ribbon_jt):
    all_nodes = []
    for id in ribbon_jt.keys():
        nodes_str = mc.getAttr('%s.nodes' % ribbon_jt[id])
        for n in nodes_str.split(', '):
            all_nodes.append(n)
    return all_nodes


def reconnect_attr(ribbon_jt):
    for id in ribbon_jt.keys():
        twist_jt = ribbon_jt[id].replace('Ribbon', 'Bind').replace('Bn', 'Jnt')
        bn_jt = ribbon_jt[id].replace('Ribbon', 'Bind')
        print(twist_jt)
        print(bn_jt)
        for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
            mc.connectAttr('%s.%s' % (twist_jt, attr), '%s.%s' % (bn_jt, attr), f=True)


def get_namespace():
    sel = mc.ls(sl=True)
    ns = None
    if sel:
        if ':' in sel[0]:
            ns = '%s:' % mc.ls(sl=True)[0].split(':')[0]
    return ns


def create_ctrl_shape(ctrl_dict):
    sel = mc.ls(sl=True)
    for id in ctrl_dict.keys():
        ctrl = ctrl_dict[id]
        new_curve = mc.curve(d=1, p=(
            [-2, 0, 0], [-2.292893, 0, -0.707107], [-3, 0, -1], [-3.707107, 0, -0.707107], [-4, 0, 0],
            [-3.707107, 0, 0.707107], [-3, 0, 1], [-2.292893, 0, 0.707107], [-2, 0, 0], [-2.292893, 0, 0.707107],
            [-3.707107, 0, -0.707107], [-4, 0, 0], [-3.707107, 0, 0.707107], [-2.292893, 0, -0.707107], [-2, 0, 0],
            [0, 0, 0], [2, 0, 0], [2.292893, 0, 0.707107], [3, 0, 1], [3.707107, 0, 0.707107], [4, 0, 0],
            [3.707107, 0, -0.707107], [3, 0, -1], [2.292893, 0, -0.707107], [2, 0, 0], [2.292893, 0, 0.707107],
            [3.707107, 0, -0.707107], [4, 0, 0], [3.707107, 0, 0.707107], [2.292893, 0, -0.707107], [2, 0, 0],
            [0, 0, 0],
            [0, 0, 2], [-0.707107, 0, 2.292893], [-1, 0, 3], [-0.707107, 0, 3.707107], [0, 0, 4],
            [0.707107, 0, 3.707107],
            [1, 0, 3], [0.707107, 0, 2.292893], [0, 0, 2], [0.707107, 0, 2.292893], [-0.707107, 0, 3.707107], [0, 0, 4],
            [0.707107, 0, 3.707107], [-0.707107, 0, 2.292893], [0, 0, 2], [0, 0, -2], [-0.707107, 0, -2.292893],
            [-1, 0, -3], [-0.707107, 0, -3.707107], [0, 0, -4], [0.707107, 0, -3.707107], [1, 0, -3],
            [0.707107, 0, -2.292893], [0, 0, -2], [0.707107, 0, -2.292893], [-0.707107, 0, -3.707107], [0, 0, -4],
            [0.707107, 0, -3.707107], [-0.707107, 0, -2.292893]),
                             k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23,
                                24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45,
                                46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60])
        mc.setAttr('%s.rz' % new_curve, 90)
        mc.setAttr('%s.sx' % new_curve, 3)
        mc.setAttr('%s.sy' % new_curve, 3)
        mc.setAttr('%s.sz' % new_curve, 3)
        mc.makeIdentity(new_curve, apply=True, r=True, s=True)
        curve_shape = mc.listRelatives(new_curve, c=True, type='nurbsCurve')
        mc.parent(curve_shape[0], ctrl, s=True, r=True)
        mc.delete(new_curve)
        if sel:
            mc.select(sel, r=True)
        else:
            mc.select(cl=True)


def change_checkBox_value(*args):
    checkBox_grp = args[0]
    if args[1]:
        for cb in checkBox_grp:
            mc.checkBox(cb, e=True, v=True)
    else:
        for cb in checkBox_grp:
            mc.checkBox(cb, e=True, v=False)


def off_all_checkBox_value(*args):
    mc.checkBox(args[0], e=True, v=False)


def create_ribbon_hierarchy():
    dont_kill = 'Dont_kill'
    ribbon_skeleton = 'ribbon_skeleton'
    ribbon_controller = 'ribbon_controller'
    ribbon_noTransform = 'ribbon_noTransform'
    if not mc.objExists(dont_kill):
        mc.group(n=dont_kill, em=True)
    if not mc.objExists(ribbon_skeleton):
        mc.group(n=ribbon_skeleton, em=True)
        mc.setAttr('%s.v' % ribbon_skeleton, 0)
        mc.parent(ribbon_skeleton, dont_kill)
    if not mc.objExists(ribbon_controller):
        mc.group(n=ribbon_controller, em=True)
        mc.parent(ribbon_controller, dont_kill)
    if not mc.objExists(ribbon_noTransform):
        mc.group(n=ribbon_noTransform, em=True)
        mc.setAttr('%s.v' % ribbon_noTransform, 0)
        mc.parent(ribbon_noTransform, dont_kill)

    return ribbon_skeleton, ribbon_controller, ribbon_noTransform


def duplicate_ribbon_joint(ns, part, part_jt_dict, ribbon_skeleton):
    top_grp = mc.group(em=True, n='%s%s_ribbon_grp' % (ns, part))
    rtd = {}
    rgd = {}
    for id in part_jt_dict[part].keys():
        mc.select(cl=True)
        jt = '%s%s' % (ns, part_jt_dict[part][id])
        ribbon = mc.joint(n='%s%s' % (ns, part_jt_dict[part][id].replace('Bind', 'Ribbon')))
        grp = mc.group(em=True, n='%s%s' % (ns, part_jt_dict[part][id].replace('Bind', 'Con')))
        mc.parent(ribbon, grp)
        p = mc.parentConstraint(jt, grp, mo=False)
        s = mc.scaleConstraint(jt, grp, mo=False)
        mc.delete(p, s)
        rtd.setdefault(id, ribbon)
        # mc.makeIdentity(ribbon, apply=True, r=True)
        rgd.setdefault(id, grp)
        mc.parent(grp, top_grp)
    mc.parent(top_grp, ribbon_skeleton)
    return rtd, rgd


def get_skin_object(ns, part, part_jt_dict):
    jt = '%s%s' % (ns, part_jt_dict[part][1])
    skin_clusters = mc.listConnections(jt, d=True, s=False, type='skinCluster')
    sk_shapes = []
    for sc in skin_clusters:
        shape = mc.listConnections(sc, d=True, s=False, type='mesh')
        if shape:
            sk_shapes.append(shape[0])
    return list(set(sk_shapes))


def get_sk_shape_blendShape(sk_shapes):
    bs_dict = {}
    for ss in sk_shapes:
        all_shape = mc.listRelatives(ss, c=True, ad=True, type='mesh')
        for s in all_shape:
            bs = mc.listConnections(s, d=True, s=False, type='blendShape')
            if bs:
                bs_dict.setdefault(ss, bs[0])
    return bs_dict


def create_nurbs_curve(ns, part, ribbon_jt_dict, offset=1):
    curve_point = []
    for id in ribbon_jt_dict.keys():
        # jt = '%s%s' % (ns, part_jt_dict[part][id])
        ribbon_jt = ribbon_jt_dict[id]
        t = mc.xform(ribbon_jt, q=True, ws=True, t=True)
        if 'arm' in part:
            curve_point.append([t[0], t[1] + offset, t[2]])
        else:
            curve_point.append([t[0] + offset, t[1], t[2]])
    curve_obj = mc.curve(p=curve_point, d=1)
    mc.xform(curve_obj, cpc=True)
    # mc.setAttr('%s.tz' % curve_obj, offset)
    return curve_obj


def create_nurbs_plane(ns, curve_a='curve1', curve_b='curve2', name='loft_plane',
                       ribbon_noTransform='ribbon_noTransform'):
    mc.loft(curve_a, curve_b, n='%s%s' % (ns, name), ch=1, u=1, c=0, ar=1, d=1, ss=1, rn=0, po=0, rsn=True)
    mc.delete(curve_a, curve_b)
    mc.parent('%s%s' % (ns, name), ribbon_noTransform)
    return '%s%s' % (ns, name)


def rebuild_surface(loft_plane):
    mc.rebuildSurface(loft_plane, ch=1, rpo=1, rt=0, end=1, kr=0, kcp=0, kc=0, su=2, du=3, sv=1, dv=3, tol=0.01, fr=0,
                      dir=2)


def create_follicle(ns, loft_plane, ribbon_value, follicle_prefix_name, ribbon_noTransform):
    follicle_top_grp = mc.group(n='%s%s_Follicle_Grp' % (ns, follicle_prefix_name), em=True)
    # mc.setAttr('%s.v' % follicle_top_grp, 0)
    distance_offset = 1.0 / (float(ribbon_value) - 1.0)
    pu = 0
    follicle_dict = {}
    follicle_name = None
    for i in range(ribbon_value):
        follicle_name = '%s%s_%03d_Follicle' % (ns, follicle_prefix_name, i + 1)
        follicle_shape = '%s%s_%03d_FollicleShape' % (ns, follicle_prefix_name, i + 1)
        mc.shadingNode('follicle', asUtility=True, n=follicle_shape)
        mc.setAttr('%s.simulationMethod' % follicle_shape, 0)
        follicle_transform = mc.listRelatives(follicle_shape, p=True)
        mc.rename(follicle_transform, follicle_name)
        surface_shape = mc.listRelatives(loft_plane, c=True, type='nurbsSurface')
        mc.connectAttr('%s.local' % surface_shape[0], '%s.inputSurface' % follicle_shape)
        mc.connectAttr('%s.worldMatrix' % surface_shape[0], '%s.inputWorldMatrix' % follicle_shape)
        mc.connectAttr('%s.outTranslateX' % follicle_shape, '%s.tx' % follicle_name)
        mc.connectAttr('%s.outTranslateY' % follicle_shape, '%s.ty' % follicle_name)
        mc.connectAttr('%s.outTranslateZ' % follicle_shape, '%s.tz' % follicle_name)
        mc.connectAttr('%s.outRotateX' % follicle_shape, '%s.rx' % follicle_name)
        mc.connectAttr('%s.outRotateY' % follicle_shape, '%s.ry' % follicle_name)
        mc.connectAttr('%s.outRotateZ' % follicle_shape, '%s.rz' % follicle_name)
        mc.setAttr('%s.parameterU' % follicle_shape, pu)
        mc.setAttr('%s.parameterV' % follicle_shape, 0.5)
        pu += distance_offset
        mc.parent(follicle_name, follicle_top_grp)
        follicle_dict.setdefault(i + 1, follicle_name)
    mc.select(cl=True)
    mc.parent(follicle_top_grp, ribbon_noTransform)
    jt = mc.joint()
    if follicle_name:
        mc.orientConstraint(follicle_name, jt, offset=[0, 0, -90])
    mc.delete(jt)
    return follicle_dict


def connect_attr(follicle_dict, ribbon_jt_dict, constraint):
    for id in follicle_dict.keys():
        if not constraint:
            for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']:
                mc.connectAttr('%s.%s' % (follicle_dict[id], attr), '%s.%s' % (ribbon_jt_dict[id], attr))
        else:
            mc.parentConstraint(follicle_dict[id], ribbon_jt_dict[id], mo=True)
            mc.scaleConstraint(follicle_dict[id], ribbon_jt_dict[id], mo=True)


def create_plane_rig(ns, loft_plane, ribbon_jt_dict, name, ribbon_skeleton):
    jt_dict = {}
    grp = mc.group(em=True, n='%s%s_ribbon_ctrl_jt_grp' % (ns, name))
    jt_a = ribbon_jt_dict[1].replace('_Bn', '').replace('01', 'A')
    jt_b = ribbon_jt_dict[3].replace('_Bn', '').replace('03', 'B')
    jt_c = ribbon_jt_dict[5].replace('_Bn', '').replace('05', 'C')
    mc.select(cl=True)
    mc.joint(n=jt_a)
    jt_dict.setdefault(1, jt_a)
    grp_a = mc.group(jt_a, n=ribbon_jt_dict[1].replace('_Bn', '_Grp').replace('01', 'A'))
    mc.select(cl=True)
    mc.joint(n=jt_b)
    jt_dict.setdefault(2, jt_b)
    grp_b = mc.group(jt_b, n=ribbon_jt_dict[3].replace('_Bn', '_Grp').replace('03', 'B'))
    mc.select(cl=True)
    mc.joint(n=jt_c)
    jt_dict.setdefault(3, jt_c)
    grp_c = mc.group(jt_c, n=ribbon_jt_dict[5].replace('_Bn', '_Grp').replace('05', 'C'))
    p_a = mc.parentConstraint(ribbon_jt_dict[1], grp_a, mo=False)
    p_b = mc.parentConstraint(ribbon_jt_dict[3], grp_b, mo=False)
    p_c = mc.parentConstraint(ribbon_jt_dict[5], grp_c, mo=False)
    mc.delete(p_a, p_b, p_c)
    mc.skinCluster(jt_a, jt_b, jt_c, loft_plane, dr=2)
    mc.parent(grp_a, grp_b, grp_c, grp)
    mc.parent(grp, ribbon_skeleton)
    return jt_dict


def create_ribbon_ctrl(ns, ctrl_jt_dict, name, ribbon_controller, part_compar_dict):
    ctrl_dict = {}
    ctrl_grp = mc.group(em=True, n='%s%s_ctrl_grp' % (ns, name))
    mc.parent(ctrl_grp, ribbon_controller)
    mc.parentConstraint('%s%s' % (ns, part_compar_dict[name]), ctrl_grp, mo=True)
    for id in ctrl_jt_dict.keys():
        ctrl = mc.group(em=True, n='%s_Ctrl' % ctrl_jt_dict[id])
        con = mc.group(em=True, n='%s_Con' % ctrl_jt_dict[id])
        grp = mc.group(em=True, n='%s_Grp' % ctrl_jt_dict[id])
        mc.parent(ctrl, con)
        mc.parent(con, grp)
        p = mc.parentConstraint(ctrl_jt_dict[id], grp, mo=False)
        mc.delete(p)
        mc.parent(grp, ctrl_grp)
        ctrl_dict.setdefault(id, ctrl)
    return ctrl_dict


def combine_ribbon_to_rig(ns, ribbon_jt_dict, part, part_jt_dict):
    for id in part_jt_dict[part].keys():
        ribbon_jt = ribbon_jt_dict[id]
        twist_jt = '%s%s' % (ns, part_jt_dict[part][id])
        main_jt = twist_jt.replace('Bn', 'Jnt')
        pma_t = mc.shadingNode('plusMinusAverage', asUtility=True)
        pma_r = mc.shadingNode('plusMinusAverage', asUtility=True)
        md_s = mc.shadingNode('multiplyDivide', asUtility=True)
        nodes = '%s, %s, %s' % (pma_t, pma_r, md_s)
        mc.connectAttr('%s.t' % main_jt, '%s.input3D[0]' % pma_t)
        mc.connectAttr('%s.r' % main_jt, '%s.input3D[0]' % pma_r)
        mc.connectAttr('%s.s' % main_jt, '%s.input1' % md_s)
        mc.connectAttr('%s.t' % ribbon_jt, '%s.input3D[1]' % pma_t)
        mc.connectAttr('%s.r' % ribbon_jt, '%s.input3D[1]' % pma_r)
        mc.connectAttr('%s.s' % ribbon_jt, '%s.input2' % md_s)
        mc.connectAttr('%s.output3D' % pma_t, '%s.t' % twist_jt, f=True)
        mc.connectAttr('%s.output3D' % pma_r, '%s.r' % twist_jt, f=True)
        mc.connectAttr('%s.output' % md_s, '%s.s' % twist_jt, f=True)
        mc.addAttr(ribbon_jt, ln='nodes', dt='string')
        mc.setAttr('%s.nodes' % ribbon_jt, nodes, type='string')
