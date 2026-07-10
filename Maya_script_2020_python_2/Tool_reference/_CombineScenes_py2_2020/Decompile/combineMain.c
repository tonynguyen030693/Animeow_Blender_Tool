
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void initCombineMain(void)

{
  undefined8 uVar1;
  int iVar2;
  longlong *plVar3;
  longlong *plVar4;
  longlong *plVar5;
  longlong *plVar6;
  longlong *plVar7;
  longlong *plVar8;
  longlong *plVar9;
  longlong *plVar10;
  longlong lVar11;
  code *pcVar12;
  code *pcVar13;
  code *pcVar14;
  longlong *plVar15;
  longlong *local_res8;
  longlong *local_res10;
  longlong *local_res18;
  longlong *local_res20;
  undefined8 in_stack_ffffffffffffff38;
  undefined4 uVar16;
  ulonglong uVar17;
  longlong *local_a8;
  code *local_a0;
  longlong *local_98;
  code *local_90;
  longlong *local_88;
  code *local_80;
  code *local_78;
  longlong *local_70;
  longlong *local_68;
  longlong *local_60;
  longlong *local_58;
  
                    /* 0x1aa80  1  initCombineMain */
  uVar16 = (undefined4)((ulonglong)in_stack_ffffffffffffff38 >> 0x20);
  local_res20 = (longlong *)0x0;
  pcVar12 = (code *)0x0;
  pcVar14 = (code *)0x0;
  local_res10 = (longlong *)0x0;
  local_res18 = (longlong *)0x0;
  plVar5 = (longlong *)0x0;
  local_90 = (code *)0x0;
  plVar6 = (longlong *)0x0;
  plVar7 = (longlong *)0x0;
  iVar2 = FUN_180003310();
  if (iVar2 < 0) {
    DAT_180029f08 = DAT_1800291f8;
    DAT_180029f00 = 1;
    DAT_18002958c = 0x30d8;
  }
  else {
    DAT_180029ee8 = PyTuple_New(0);
    if (DAT_180029ee8 == 0) {
      DAT_180029f08 = DAT_1800291f8;
      DAT_180029f00 = 1;
      DAT_18002958c = 0x30d9;
    }
    else {
      DAT_180029ef0 = PyString_FromStringAndSize(&DAT_180029568,0);
      if (DAT_180029ef0 == 0) {
        DAT_180029f08 = DAT_1800291f8;
        DAT_180029f00 = 1;
        DAT_18002958c = 0x30da;
      }
      else {
        _DAT_180029ef8 = PyUnicodeUCS2_FromStringAndSize(&DAT_180029569,0);
        if (_DAT_180029ef8 == 0) {
          DAT_180029f08 = DAT_1800291f8;
          DAT_180029f00 = 1;
          DAT_18002958c = 0x30db;
        }
        else {
          DAT_180029560 = FUN_180001ad0(&DAT_1800242f0);
          if (DAT_180029560 == 0) {
            DAT_180029f08 = DAT_1800291f8;
            DAT_180029f00 = 1;
            DAT_18002958c = 0x30dd;
          }
          else {
            plVar3 = (longlong *)
                     Py_InitModule4_64(s_CombineMain_1800247f8,&DAT_180029590,0,0,
                                       CONCAT44(uVar16,0x3f5));
            DAT_180029ec8 = plVar3;
            if (plVar3 == (longlong *)0x0) {
              DAT_180029f08 = DAT_1800291f8;
              DAT_180029f00 = 1;
              DAT_18002958c = 0x30f8;
              goto LAB_18001e22d;
            }
            *plVar3 = *plVar3 + 1;
            DAT_180029ed0 = (longlong *)PyModule_GetDict(plVar3);
            if (DAT_180029ed0 == (longlong *)0x0) {
              DAT_180029f08 = DAT_1800291f8;
              DAT_180029f00 = 1;
              DAT_18002958c = 0x30f9;
            }
            else {
              *DAT_180029ed0 = *DAT_180029ed0 + 1;
              DAT_180029ed8 = PyImport_AddModule(s___builtin___180024808);
              if (DAT_180029ed8 == 0) {
                DAT_180029f08 = DAT_1800291f8;
                DAT_180029f00 = 1;
                DAT_18002958c = 0x30fb;
              }
              else {
                DAT_180029ee0 = PyImport_AddModule(s_cython_runtime_180024830);
                if (DAT_180029ee0 == 0) {
                  DAT_180029f08 = DAT_1800291f8;
                  DAT_180029f00 = 1;
                  DAT_18002958c = 0x30fc;
                }
                else {
                  iVar2 = PyObject_SetAttrString
                                    (DAT_180029ec8,s___builtins___180024840,DAT_180029ed8);
                  if (iVar2 < 0) {
                    DAT_180029f08 = DAT_1800291f8;
                    DAT_180029f00 = 1;
                    DAT_18002958c = 0x3100;
                  }
                  else {
                    iVar2 = FUN_18001a950();
                    if (iVar2 < 0) {
                      DAT_180029f08 = DAT_1800291f8;
                      DAT_180029f00 = 1;
                      DAT_18002958c = 0x3102;
                    }
                    else if ((DAT_18002956c == 0) ||
                            (iVar2 = PyObject_SetAttrString
                                               (DAT_180029ec8,s___name___1800248a0,DAT_180029bf0),
                            -1 < iVar2)) {
                      iVar2 = FUN_180018b50();
                      if (iVar2 < 0) {
                        DAT_180029f08 = DAT_1800291f8;
                        DAT_180029f00 = 1;
                        DAT_18002958c = 0x3112;
                      }
                      else {
                        iVar2 = FUN_180018c30();
                        if (iVar2 < 0) {
                          DAT_180029f08 = DAT_1800291f8;
                          DAT_180029f00 = 1;
                          DAT_18002958c = 0x3114;
                        }
                        else {
                          iVar2 = PyType_Ready(&DAT_180024ee0);
                          if (iVar2 < 0) {
                            DAT_180029f08 = DAT_1800291f8;
                            DAT_180029f00 = 0x50;
                            DAT_18002958c = 0x3119;
                          }
                          else {
                            _DAT_180024f18 = 0;
                            DAT_180029580 = &DAT_180024ee0;
                            lVar11 = *(longlong *)_PyThreadState_Current_exref;
                            local_a0 = *(code **)(lVar11 + 0x60);
                            local_78 = *(code **)(lVar11 + 0x68);
                            plVar3 = *(longlong **)(lVar11 + 0x70);
                            if (local_a0 != (code *)0x0) {
                              *(longlong *)local_a0 = *(longlong *)local_a0 + 1;
                            }
                            if (local_78 != (code *)0x0) {
                              *(longlong *)local_78 = *(longlong *)local_78 + 1;
                            }
                            if (plVar3 != (longlong *)0x0) {
                              *plVar3 = *plVar3 + 1;
                            }
                            local_88 = plVar3;
                            plVar4 = (longlong *)FUN_1800014a0(DAT_180029d20);
                            if (plVar4 == (longlong *)0x0) {
                              DAT_180029f08 = DAT_1800291f8;
                              DAT_180029f00 = 3;
                              DAT_18002958c = 0x313a;
                              local_res8 = (longlong *)0x0;
                              local_68 = *(longlong **)_PyThreadState_Current_exref;
                              lVar11 = local_68[9];
                              if ((lVar11 == DAT_180029f10) ||
                                 ((plVar10 = (longlong *)0x0, plVar3 = (longlong *)0x0,
                                  plVar4 = (longlong *)0x0, lVar11 != 0 &&
                                  (iVar2 = PyErr_GivenExceptionMatches(lVar11,DAT_180029f10),
                                  iVar2 != 0)))) {
                                FUN_180002f70(s_tvTools__CombineScenes_CombineMa_1800248b0,
                                              DAT_18002958c,DAT_180029f00,DAT_180029f08);
                                iVar2 = FUN_180002500(local_68,&local_res8,&local_res20,&local_res10
                                                     );
                                if (iVar2 < 0) {
                                  DAT_180029f08 = DAT_1800291f8;
                                  DAT_180029f00 = 4;
                                  DAT_18002958c = 0x3157;
                                  plVar10 = local_res10;
                                  plVar3 = local_res8;
                                  plVar4 = local_res20;
                                }
                                else {
                                  lVar11 = *(longlong *)_PyThreadState_Current_exref;
                                  local_68 = *(longlong **)(lVar11 + 0x60);
                                  plVar3 = *(longlong **)(lVar11 + 0x68);
                                  plVar4 = *(longlong **)(lVar11 + 0x70);
                                  if (local_68 != (longlong *)0x0) {
                                    *local_68 = *local_68 + 1;
                                  }
                                  if (plVar3 != (longlong *)0x0) {
                                    *plVar3 = *plVar3 + 1;
                                  }
                                  if (plVar4 != (longlong *)0x0) {
                                    *plVar4 = *plVar4 + 1;
                                  }
                                  plVar5 = (longlong *)PyList_New(1);
                                  if (plVar5 != (longlong *)0x0) {
                                    *DAT_180029d20 = *DAT_180029d20 + 1;
                                    *(longlong **)plVar5[3] = DAT_180029d20;
                                    plVar10 = (longlong *)
                                              FUN_180002690(DAT_180029ad0,plVar5,0xffffffff);
                                    local_res18 = plVar10;
                                    if (plVar10 == (longlong *)0x0) {
                                      DAT_18002958c = 0x3178;
                                      goto LAB_18001b05c;
                                    }
                                    *plVar5 = *plVar5 + -1;
                                    if (*plVar5 == 0) {
                                      (**(code **)(plVar5[1] + 0x30))(plVar5);
                                    }
                                    plVar5 = (longlong *)FUN_1800027f0(plVar10,DAT_180029d20);
                                    if (plVar5 == (longlong *)0x0) {
                                      DAT_18002958c = 0x317b;
                                      goto LAB_18001b05c;
                                    }
                                    iVar2 = PyDict_SetItem(DAT_180029ed0,DAT_180029d20,plVar5);
                                    if (iVar2 < 0) {
                                      DAT_18002958c = 0x317d;
                                      goto LAB_18001b05c;
                                    }
                                    *plVar5 = *plVar5 + -1;
                                    if (*plVar5 == 0) {
                                      (**(code **)(plVar5[1] + 0x30))(plVar5);
                                    }
                                    *local_res18 = *local_res18 + -1;
                                    if (*local_res18 == 0) {
                                      (**(code **)(local_res18[1] + 0x30))();
                                    }
                                    local_res18 = (longlong *)0x0;
                                    if ((local_68 != (longlong *)0x0) &&
                                       (*local_68 = *local_68 + -1, *local_68 == 0)) {
                                      (**(code **)(local_68[1] + 0x30))();
                                    }
                                    if ((plVar3 != (longlong *)0x0) &&
                                       (*plVar3 = *plVar3 + -1, *plVar3 == 0)) {
                                      (**(code **)(plVar3[1] + 0x30))(plVar3);
                                    }
                                    if ((plVar4 != (longlong *)0x0) &&
                                       (*plVar4 = *plVar4 + -1, *plVar4 == 0)) {
                                      (**(code **)(plVar4[1] + 0x30))(plVar4);
                                    }
LAB_18001b340:
                                    *local_res8 = *local_res8 + -1;
                                    if (*local_res8 == 0) {
                                      (**(code **)(local_res8[1] + 0x30))();
                                    }
                                    *local_res20 = *local_res20 + -1;
                                    if (*local_res20 == 0) {
                                      (**(code **)(local_res20[1] + 0x30))();
                                    }
                                    *local_res10 = *local_res10 + -1;
                                    if (*local_res10 == 0) {
                                      (**(code **)(local_res10[1] + 0x30))();
                                    }
                                    FUN_180002450(*(undefined8 *)_PyThreadState_Current_exref,
                                                  local_a0,local_78,local_88);
                                    goto LAB_18001b3e0;
                                  }
                                  DAT_18002958c = 0x3173;
LAB_18001b05c:
                                  DAT_180029f08 = DAT_1800291f8;
                                  DAT_180029f00 = 6;
                                  local_60 = *(longlong **)_PyThreadState_Current_exref;
                                  if ((plVar5 != (longlong *)0x0) &&
                                     (*plVar5 = *plVar5 + -1, *plVar5 == 0)) {
                                    (**(code **)(plVar5[1] + 0x30))(plVar5);
                                  }
                                  local_a8 = (longlong *)0x0;
                                  if ((local_res18 != (longlong *)0x0) &&
                                     (*local_res18 = *local_res18 + -1, *local_res18 == 0)) {
                                    (**(code **)(local_res18[1] + 0x30))();
                                  }
                                  plVar10 = local_60;
                                  local_res18 = (longlong *)0x0;
                                  local_98 = (longlong *)0x0;
                                  if ((local_60[9] == DAT_180029f18) ||
                                     ((plVar5 = (longlong *)0x0, local_60[9] != 0 &&
                                      (iVar2 = PyErr_GivenExceptionMatches(), iVar2 != 0)))) {
                                    FUN_180002f70(s_tvTools__CombineScenes_CombineMa_1800249a8,
                                                  DAT_18002958c,DAT_180029f00,DAT_180029f08);
                                    iVar2 = FUN_180002500(plVar10,&local_98,&local_a8,&local_90);
                                    if (iVar2 < 0) {
                                      DAT_180029f00 = 7;
                                      DAT_18002958c = 0x319c;
                                    }
                                    else {
                                      plVar6 = (longlong *)PyList_New(1);
                                      if (plVar6 == (longlong *)0x0) {
                                        DAT_18002958c = 0x31a8;
                                      }
                                      else {
                                        *DAT_180029d20 = *DAT_180029d20 + 1;
                                        *(longlong **)plVar6[3] = DAT_180029d20;
                                        plVar7 = (longlong *)
                                                 FUN_180002690(DAT_180029ab0,plVar6,0xffffffff);
                                        if (plVar7 == (longlong *)0x0) {
                                          DAT_18002958c = 0x31ad;
                                        }
                                        else {
                                          *plVar6 = *plVar6 + -1;
                                          if (*plVar6 == 0) {
                                            (**(code **)(plVar6[1] + 0x30))(plVar6);
                                          }
                                          plVar6 = (longlong *)FUN_1800027f0(plVar7,DAT_180029d20);
                                          if (plVar6 == (longlong *)0x0) {
                                            DAT_18002958c = 0x31b0;
                                          }
                                          else {
                                            iVar2 = PyDict_SetItem(DAT_180029ed0,DAT_180029d20,
                                                                   plVar6);
                                            if (-1 < iVar2) {
                                              *plVar6 = *plVar6 + -1;
                                              if (*plVar6 == 0) {
                                                (**(code **)(plVar6[1] + 0x30))(plVar6);
                                              }
                                              *plVar7 = *plVar7 + -1;
                                              if (*plVar7 == 0) {
                                                (**(code **)(plVar7[1] + 0x30))(plVar7);
                                              }
                                              *local_98 = *local_98 + -1;
                                              if (*local_98 == 0) {
                                                (**(code **)(local_98[1] + 0x30))();
                                              }
                                              local_res18 = (longlong *)0x0;
                                              *local_a8 = *local_a8 + -1;
                                              if (*local_a8 == 0) {
                                                (**(code **)(local_a8[1] + 0x30))();
                                              }
                                              *(longlong *)local_90 = *(longlong *)local_90 + -1;
                                              if (*(longlong *)local_90 == 0) {
                                                (**(code **)(*(longlong *)(local_90 + 8) + 0x30))();
                                              }
                                              FUN_180002450(*(undefined8 *)
                                                             _PyThreadState_Current_exref,local_68,
                                                            plVar3,plVar4);
                                              goto LAB_18001b340;
                                            }
                                            DAT_18002958c = 0x31b2;
                                          }
                                        }
                                      }
                                      DAT_180029f00 = 8;
                                    }
                                    DAT_180029f08 = DAT_1800291f8;
                                    local_res18 = local_98;
                                    pcVar12 = local_90;
                                    plVar5 = local_a8;
                                  }
                                  FUN_180002450(*(undefined8 *)_PyThreadState_Current_exref,local_68
                                                ,plVar3,plVar4);
                                  plVar10 = local_res10;
                                  plVar3 = local_res8;
                                  plVar4 = local_res20;
                                }
                              }
                              pcVar14 = pcVar12;
                              FUN_180002450(*(undefined8 *)_PyThreadState_Current_exref,local_a0,
                                            local_78,local_88);
LAB_18001e0fa:
                              plVar8 = plVar10;
                              if ((plVar3 != (longlong *)0x0) &&
                                 (*plVar3 = *plVar3 + -1, *plVar3 == 0)) {
                                (**(code **)(plVar3[1] + 0x30))(plVar3);
                              }
                              goto LAB_18001e111;
                            }
                            *plVar4 = *plVar4 + -1;
                            if (*plVar4 == 0) {
                              (**(code **)(plVar4[1] + 0x30))(plVar4);
                            }
                            if ((local_a0 != (code *)0x0) &&
                               (*(longlong *)local_a0 = *(longlong *)local_a0 + -1,
                               *(longlong *)local_a0 == 0)) {
                              (**(code **)(*(longlong *)(local_a0 + 8) + 0x30))();
                            }
                            if ((local_78 != (code *)0x0) &&
                               (*(longlong *)local_78 = *(longlong *)local_78 + -1,
                               *(longlong *)local_78 == 0)) {
                              (**(code **)(*(longlong *)(local_78 + 8) + 0x30))();
                            }
                            if ((plVar3 != (longlong *)0x0) &&
                               (*plVar3 = *plVar3 + -1, *plVar3 == 0)) {
                              (**(code **)(plVar3[1] + 0x30))(plVar3);
                            }
LAB_18001b3e0:
                            plVar5 = (longlong *)0x0;
                            plVar8 = (longlong *)PyList_New(3);
                            if (plVar8 == (longlong *)0x0) {
                              DAT_180029f08 = DAT_1800291f8;
                              DAT_180029f00 = 9;
                              DAT_18002958c = 0x31f6;
                              goto LAB_18001e1a6;
                            }
                            *DAT_180029838 = *DAT_180029838 + 1;
                            *(longlong **)plVar8[3] = DAT_180029838;
                            *DAT_180029830 = *DAT_180029830 + 1;
                            *(longlong **)(plVar8[3] + 8) = DAT_180029830;
                            *DAT_180029828 = *DAT_180029828 + 1;
                            *(longlong **)(plVar8[3] + 0x10) = DAT_180029828;
                            plVar4 = (longlong *)FUN_180002690(DAT_1800297e8,plVar8,0xffffffff);
                            if (plVar4 == (longlong *)0x0) {
                              plVar7 = (longlong *)0x0;
                              DAT_180029f08 = DAT_1800291f8;
                              plVar6 = (longlong *)0x0;
                              DAT_180029f00 = 9;
                              DAT_18002958c = 0x3201;
                              pcVar14 = pcVar12;
                              goto LAB_18001e126;
                            }
                            *plVar8 = *plVar8 + -1;
                            if (*plVar8 == 0) {
                              (**(code **)(plVar8[1] + 0x30))(plVar8);
                            }
                            plVar8 = (longlong *)FUN_1800027f0(plVar4,DAT_180029838);
                            if (plVar8 == (longlong *)0x0) {
                              plVar7 = (longlong *)0x0;
                              DAT_180029f08 = DAT_1800291f8;
                              plVar6 = (longlong *)0x0;
                              DAT_180029f00 = 9;
                              DAT_18002958c = 0x3204;
                              pcVar14 = pcVar12;
LAB_18001e111:
                              if ((plVar4 != (longlong *)0x0) &&
                                 (*plVar4 = *plVar4 + -1, *plVar4 == 0)) {
                                (**(code **)(plVar4[1] + 0x30))(plVar4);
                              }
LAB_18001e126:
                              if ((plVar8 != (longlong *)0x0) &&
                                 (*plVar8 = *plVar8 + -1, *plVar8 == 0)) {
                                (**(code **)(plVar8[1] + 0x30))(plVar8);
                              }
LAB_18001e13b:
                              if ((plVar5 != (longlong *)0x0) &&
                                 (*plVar5 = *plVar5 + -1, *plVar5 == 0)) {
                                (**(code **)(plVar5[1] + 0x30))(plVar5);
                              }
                              if ((local_res18 != (longlong *)0x0) &&
                                 (*local_res18 = *local_res18 + -1, *local_res18 == 0)) {
                                (**(code **)(local_res18[1] + 0x30))();
                              }
                            }
                            else {
                              iVar2 = PyDict_SetItem(DAT_180029ed0,DAT_180029838,plVar8);
                              if (iVar2 < 0) {
                                plVar7 = (longlong *)0x0;
                                DAT_180029f08 = DAT_1800291f8;
                                plVar6 = (longlong *)0x0;
                                DAT_180029f00 = 9;
                                DAT_18002958c = 0x3206;
                                pcVar14 = pcVar12;
                                goto LAB_18001e111;
                              }
                              *plVar8 = *plVar8 + -1;
                              if (*plVar8 == 0) {
                                (**(code **)(plVar8[1] + 0x30))(plVar8);
                              }
                              plVar8 = (longlong *)FUN_1800027f0(plVar4,DAT_180029830);
                              if (plVar8 == (longlong *)0x0) {
                                plVar7 = (longlong *)0x0;
                                DAT_180029f08 = DAT_1800291f8;
                                plVar6 = (longlong *)0x0;
                                DAT_180029f00 = 9;
                                DAT_18002958c = 0x3208;
                                pcVar14 = pcVar12;
                                goto LAB_18001e111;
                              }
                              iVar2 = PyDict_SetItem(DAT_180029ed0,DAT_180029830,plVar8);
                              if (iVar2 < 0) {
                                plVar7 = (longlong *)0x0;
                                DAT_180029f08 = DAT_1800291f8;
                                plVar6 = (longlong *)0x0;
                                DAT_180029f00 = 9;
                                DAT_18002958c = 0x320a;
                                goto LAB_18001e111;
                              }
                              *plVar8 = *plVar8 + -1;
                              if (*plVar8 == 0) {
                                (**(code **)(plVar8[1] + 0x30))(plVar8);
                              }
                              plVar8 = (longlong *)FUN_1800027f0(plVar4,DAT_180029828);
                              if (plVar8 == (longlong *)0x0) {
                                plVar7 = (longlong *)0x0;
                                DAT_180029f08 = DAT_1800291f8;
                                plVar6 = (longlong *)0x0;
                                DAT_180029f00 = 9;
                                DAT_18002958c = 0x320c;
                                goto LAB_18001e111;
                              }
                              iVar2 = PyDict_SetItem(DAT_180029ed0,DAT_180029828,plVar8);
                              if (iVar2 < 0) {
                                plVar7 = (longlong *)0x0;
                                DAT_180029f08 = DAT_1800291f8;
                                plVar6 = (longlong *)0x0;
                                DAT_180029f00 = 9;
                                DAT_18002958c = 0x320e;
                                goto LAB_18001e111;
                              }
                              *plVar8 = *plVar8 + -1;
                              if (*plVar8 == 0) {
                                (**(code **)(plVar8[1] + 0x30))(plVar8);
                              }
                              *plVar4 = *plVar4 + -1;
                              if (*plVar4 == 0) {
                                (**(code **)(plVar4[1] + 0x30))(plVar4);
                              }
                              plVar4 = (longlong *)PyList_New(1);
                              if (plVar4 == (longlong *)0x0) {
                                DAT_180029f08 = DAT_1800291f8;
                                DAT_180029f00 = 0xb;
                                DAT_18002958c = 0x3219;
                                goto LAB_18001e1a6;
                              }
                              *DAT_1800298e8 = *DAT_1800298e8 + 1;
                              *(longlong **)plVar4[3] = DAT_1800298e8;
                              plVar8 = (longlong *)FUN_180002690(DAT_180029c28,plVar4,0xffffffff);
                              if (plVar8 == (longlong *)0x0) {
                                plVar7 = (longlong *)0x0;
                                DAT_180029f08 = DAT_1800291f8;
                                plVar6 = (longlong *)0x0;
                                DAT_180029f00 = 0xb;
                                DAT_18002958c = 0x321e;
                                goto LAB_18001e111;
                              }
                              *plVar4 = *plVar4 + -1;
                              if (*plVar4 == 0) {
                                (**(code **)(plVar4[1] + 0x30))(plVar4);
                              }
                              iVar2 = PyDict_SetItem(DAT_180029ed0,DAT_180029c48,plVar8);
                              if (iVar2 < 0) {
                                plVar7 = (longlong *)0x0;
                                DAT_180029f08 = DAT_1800291f8;
                                plVar6 = (longlong *)0x0;
                                DAT_180029f00 = 0xb;
                                DAT_18002958c = 0x3221;
                                pcVar14 = pcVar12;
                                goto LAB_18001e126;
                              }
                              *plVar8 = *plVar8 + -1;
                              if (*plVar8 == 0) {
                                (**(code **)(plVar8[1] + 0x30))(plVar8);
                              }
                              plVar8 = (longlong *)FUN_180002690(DAT_180029aa0,0,0xffffffff);
                              if (plVar8 == (longlong *)0x0) {
                                DAT_180029f08 = DAT_1800291f8;
                                DAT_180029f00 = 0xc;
                                DAT_18002958c = 0x322b;
                                goto LAB_18001e1a6;
                              }
                              iVar2 = PyDict_SetItem(DAT_180029ed0,DAT_180029aa0,plVar8);
                              if (iVar2 < 0) {
                                plVar7 = (longlong *)0x0;
                                DAT_180029f08 = DAT_1800291f8;
                                plVar6 = (longlong *)0x0;
                                DAT_180029f00 = 0xc;
                                DAT_18002958c = 0x322d;
                                pcVar14 = pcVar12;
                                goto LAB_18001e126;
                              }
                              *plVar8 = *plVar8 + -1;
                              if (*plVar8 == 0) {
                                (**(code **)(plVar8[1] + 0x30))(plVar8);
                              }
                              plVar8 = (longlong *)FUN_180002690(DAT_180029e18,0,0xffffffff);
                              if (plVar8 == (longlong *)0x0) {
                                DAT_180029f08 = DAT_1800291f8;
                                DAT_180029f00 = 0xd;
                                DAT_18002958c = 0x3237;
                                goto LAB_18001e1a6;
                              }
                              iVar2 = PyDict_SetItem(DAT_180029ed0,DAT_180029e18,plVar8);
                              if (iVar2 < 0) {
                                plVar7 = (longlong *)0x0;
                                DAT_180029f08 = DAT_1800291f8;
                                plVar6 = (longlong *)0x0;
                                DAT_180029f00 = 0xd;
                                DAT_18002958c = 0x3239;
                                goto LAB_18001e126;
                              }
                              *plVar8 = *plVar8 + -1;
                              if (*plVar8 == 0) {
                                (**(code **)(plVar8[1] + 0x30))(plVar8);
                              }
                              plVar8 = (longlong *)FUN_180002690(DAT_180029e28,0,0xffffffff);
                              if (plVar8 == (longlong *)0x0) {
                                DAT_180029f08 = DAT_1800291f8;
                                DAT_180029f00 = 0xe;
                                DAT_18002958c = 0x3243;
                                goto LAB_18001e1a6;
                              }
                              iVar2 = PyDict_SetItem(DAT_180029ed0,DAT_180029e28,plVar8);
                              if (iVar2 < 0) {
                                plVar7 = (longlong *)0x0;
                                DAT_180029f08 = DAT_1800291f8;
                                plVar6 = (longlong *)0x0;
                                DAT_180029f00 = 0xe;
                                DAT_18002958c = 0x3245;
                                goto LAB_18001e126;
                              }
                              *plVar8 = *plVar8 + -1;
                              if (*plVar8 == 0) {
                                (**(code **)(plVar8[1] + 0x30))(plVar8);
                              }
                              plVar8 = (longlong *)PyList_New(1);
                              if (plVar8 == (longlong *)0x0) {
                                DAT_180029f08 = DAT_1800291f8;
                                DAT_180029f00 = 0xf;
                                DAT_18002958c = 0x324f;
                                goto LAB_18001e1a6;
                              }
                              *DAT_180029ca0 = *DAT_180029ca0 + 1;
                              *(longlong **)plVar8[3] = DAT_180029ca0;
                              plVar4 = (longlong *)FUN_180002690(DAT_180029a68,plVar8,0xffffffff);
                              if (plVar4 == (longlong *)0x0) {
                                plVar7 = (longlong *)0x0;
                                DAT_180029f08 = DAT_1800291f8;
                                plVar6 = (longlong *)0x0;
                                DAT_180029f00 = 0xf;
                                DAT_18002958c = 0x3254;
                                goto LAB_18001e126;
                              }
                              *plVar8 = *plVar8 + -1;
                              if (*plVar8 == 0) {
                                (**(code **)(plVar8[1] + 0x30))(plVar8);
                              }
                              plVar8 = (longlong *)FUN_1800027f0(plVar4,DAT_180029ca0);
                              if (plVar8 == (longlong *)0x0) {
                                plVar7 = (longlong *)0x0;
                                DAT_180029f08 = DAT_1800291f8;
                                plVar6 = (longlong *)0x0;
                                DAT_180029f00 = 0xf;
                                DAT_18002958c = 0x3257;
                                goto LAB_18001e111;
                              }
                              iVar2 = PyDict_SetItem(DAT_180029ed0,DAT_180029ca0,plVar8);
                              if (iVar2 < 0) {
                                plVar7 = (longlong *)0x0;
                                DAT_180029f08 = DAT_1800291f8;
                                plVar6 = (longlong *)0x0;
                                DAT_180029f00 = 0xf;
                                DAT_18002958c = 0x3259;
                                goto LAB_18001e111;
                              }
                              *plVar8 = *plVar8 + -1;
                              if (*plVar8 == 0) {
                                (**(code **)(plVar8[1] + 0x30))(plVar8);
                              }
                              plVar6 = (longlong *)0x0;
                              *plVar4 = *plVar4 + -1;
                              if (*plVar4 == 0) {
                                (**(code **)(plVar4[1] + 0x30))(plVar4);
                              }
                              plVar4 = (longlong *)FUN_180002690(DAT_180029c88,0,0xffffffff);
                              if (plVar4 == (longlong *)0x0) {
                                DAT_180029f08 = DAT_1800291f8;
                                DAT_180029f00 = 0x11;
                                DAT_18002958c = 0x3264;
                                goto LAB_18001e1a6;
                              }
                              iVar2 = PyDict_SetItem(DAT_180029ed0,DAT_180029c88,plVar4);
                              if (iVar2 < 0) {
                                plVar7 = (longlong *)0x0;
                                DAT_180029f08 = DAT_1800291f8;
                                plVar6 = (longlong *)0x0;
                                DAT_180029f00 = 0x11;
                                DAT_18002958c = 0x3266;
                                plVar8 = (longlong *)0x0;
                                goto LAB_18001e111;
                              }
                              *plVar4 = *plVar4 + -1;
                              if (*plVar4 == 0) {
                                (**(code **)(plVar4[1] + 0x30))(plVar4);
                              }
                              lVar11 = *(longlong *)_PyThreadState_Current_exref;
                              pcVar12 = *(code **)(lVar11 + 0x60);
                              pcVar14 = *(code **)(lVar11 + 0x68);
                              plVar5 = *(longlong **)(lVar11 + 0x70);
                              if (pcVar12 != (code *)0x0) {
                                *(longlong *)pcVar12 = *(longlong *)pcVar12 + 1;
                              }
                              if (pcVar14 != (code *)0x0) {
                                *(longlong *)pcVar14 = *(longlong *)pcVar14 + 1;
                              }
                              if (plVar5 != (longlong *)0x0) {
                                *plVar5 = *plVar5 + 1;
                              }
                              local_a0 = pcVar12;
                              local_88 = plVar5;
                              local_78 = pcVar14;
                              plVar7 = (longlong *)PyList_New(1);
                              if (plVar7 == (longlong *)0x0) {
                                DAT_18002958c = 0x3280;
LAB_18001bc52:
                                DAT_180029f00 = 0x13;
                                pcVar14 = (code *)0x0;
                                local_60 = *(longlong **)_PyThreadState_Current_exref;
                                local_res18 = (longlong *)0x0;
                                local_res8 = (longlong *)0x0;
                                DAT_180029f08 = DAT_1800291f8;
                                if ((plVar7 != (longlong *)0x0) &&
                                   (*plVar7 = *plVar7 + -1, *plVar7 == 0)) {
                                  (**(code **)(plVar7[1] + 0x30))(plVar7);
                                }
                                local_res20 = (longlong *)0x0;
                                if ((plVar6 != (longlong *)0x0) &&
                                   (*plVar6 = *plVar6 + -1, *plVar6 == 0)) {
                                  (**(code **)(plVar6[1] + 0x30))(plVar6);
                                }
                                local_res10 = (longlong *)0x0;
                                FUN_180002f70(s_tvTools__CombineScenes_CombineMa_180024dc0,
                                              DAT_18002958c,DAT_180029f00,DAT_180029f08);
                                iVar2 = FUN_180002500(local_60,&local_res10,&local_res20,&local_res8
                                                     );
                                if (iVar2 < 0) {
                                  DAT_180029f00 = 0x14;
                                  DAT_18002958c = 0x32ae;
                                  pcVar13 = local_78;
                                  DAT_180029f08 = DAT_1800291f8;
                                }
                                else {
                                  pcVar14 = (code *)FUN_180002690(DAT_180029648,0,0xffffffff);
                                  if (pcVar14 == (code *)0x0) {
                                    DAT_180029f00 = 0x15;
                                    DAT_18002958c = 0x32ba;
                                    pcVar13 = local_78;
                                    DAT_180029f08 = DAT_1800291f8;
                                  }
                                  else {
                                    iVar2 = PyDict_SetItem(DAT_180029ed0,DAT_180029e78,pcVar14);
                                    if (-1 < iVar2) {
                                      *(longlong *)pcVar14 = *(longlong *)pcVar14 + -1;
                                      if (*(longlong *)pcVar14 == 0) {
                                        (**(code **)(*(longlong *)(pcVar14 + 8) + 0x30))(pcVar14);
                                      }
                                      *local_res10 = *local_res10 + -1;
                                      if (*local_res10 == 0) {
                                        (**(code **)(local_res10[1] + 0x30))();
                                      }
                                      *local_res20 = *local_res20 + -1;
                                      if (*local_res20 == 0) {
                                        (**(code **)(local_res20[1] + 0x30))();
                                      }
                                      *local_res8 = *local_res8 + -1;
                                      if (*local_res8 == 0) {
                                        (**(code **)(local_res8[1] + 0x30))();
                                      }
                                      FUN_180002450(*(undefined8 *)_PyThreadState_Current_exref,
                                                    local_a0,local_78,local_88);
                                      goto LAB_18001be73;
                                    }
                                    DAT_180029f00 = 0x15;
                                    DAT_18002958c = 0x32bc;
                                    pcVar13 = local_78;
                                    DAT_180029f08 = DAT_1800291f8;
                                  }
                                }
LAB_18001bd81:
                                plVar6 = (longlong *)0x0;
                                plVar7 = (longlong *)0x0;
                                DAT_1800291f8 = DAT_180029f08;
                                FUN_180002450(*(undefined8 *)_PyThreadState_Current_exref,pcVar12,
                                              pcVar13,local_88);
                                plVar10 = local_res10;
                                plVar3 = local_res8;
                                plVar4 = local_res20;
                                plVar5 = (longlong *)0x0;
                                goto LAB_18001e0fa;
                              }
                              *DAT_180029648 = *DAT_180029648 + 1;
                              *(longlong **)plVar7[3] = DAT_180029648;
                              plVar6 = (longlong *)FUN_180002690(DAT_180029940,plVar7,0xffffffff);
                              if (plVar6 == (longlong *)0x0) {
                                DAT_18002958c = 0x3285;
                                goto LAB_18001bc52;
                              }
                              *plVar7 = *plVar7 + -1;
                              if (*plVar7 == 0) {
                                (**(code **)(plVar7[1] + 0x30))(plVar7);
                              }
                              plVar7 = (longlong *)FUN_1800027f0(plVar6,DAT_180029648);
                              if (plVar7 == (longlong *)0x0) {
                                DAT_18002958c = 0x3288;
                                goto LAB_18001bc52;
                              }
                              iVar2 = PyDict_SetItem(DAT_180029ed0,DAT_180029e78,plVar7);
                              if (iVar2 < 0) {
                                DAT_18002958c = 0x328a;
                                goto LAB_18001bc52;
                              }
                              *plVar7 = *plVar7 + -1;
                              if (*plVar7 == 0) {
                                (**(code **)(plVar7[1] + 0x30))(plVar7);
                              }
                              *plVar6 = *plVar6 + -1;
                              if (*plVar6 == 0) {
                                (**(code **)(plVar6[1] + 0x30))(plVar6);
                              }
                              if ((local_a0 != (code *)0x0) &&
                                 (*(longlong *)local_a0 = *(longlong *)local_a0 + -1,
                                 *(longlong *)local_a0 == 0)) {
                                (**(code **)(*(longlong *)(local_a0 + 8) + 0x30))();
                              }
                              if ((pcVar14 != (code *)0x0) &&
                                 (*(longlong *)pcVar14 = *(longlong *)pcVar14 + -1,
                                 *(longlong *)pcVar14 == 0)) {
                                (**(code **)(*(longlong *)(pcVar14 + 8) + 0x30))(pcVar14);
                              }
                              if ((plVar5 != (longlong *)0x0) &&
                                 (*plVar5 = *plVar5 + -1, *plVar5 == 0)) {
                                (**(code **)(plVar5[1] + 0x30))(plVar5);
                              }
LAB_18001be73:
                              plVar6 = (longlong *)0x0;
                              lVar11 = *(longlong *)_PyThreadState_Current_exref;
                              local_78 = *(code **)(lVar11 + 0x60);
                              pcVar14 = *(code **)(lVar11 + 0x68);
                              plVar5 = *(longlong **)(lVar11 + 0x70);
                              if (local_78 != (code *)0x0) {
                                *(longlong *)local_78 = *(longlong *)local_78 + 1;
                              }
                              if (pcVar14 != (code *)0x0) {
                                *(longlong *)pcVar14 = *(longlong *)pcVar14 + 1;
                              }
                              if (plVar5 != (longlong *)0x0) {
                                *plVar5 = *plVar5 + 1;
                              }
                              local_a0 = pcVar14;
                              local_88 = plVar5;
                              plVar7 = (longlong *)PyList_New(1);
                              if (plVar7 == (longlong *)0x0) {
                                DAT_180029f08 = DAT_1800291f8;
                                DAT_18002958c = 0x32f2;
LAB_18001bf94:
                                DAT_180029f00 = 0x17;
                                pcVar14 = (code *)0x0;
                                uVar1 = *(undefined8 *)_PyThreadState_Current_exref;
                                local_res18 = (longlong *)0x0;
                                local_res10 = (longlong *)0x0;
                                DAT_1800291f8 = DAT_180029f08;
                                if ((plVar7 != (longlong *)0x0) &&
                                   (*plVar7 = *plVar7 + -1, *plVar7 == 0)) {
                                  (**(code **)(plVar7[1] + 0x30))(plVar7);
                                }
                                local_res8 = (longlong *)0x0;
                                if ((plVar6 != (longlong *)0x0) &&
                                   (*plVar6 = *plVar6 + -1, *plVar6 == 0)) {
                                  (**(code **)(plVar6[1] + 0x30))(plVar6);
                                }
                                local_res20 = (longlong *)0x0;
                                FUN_180002f70(s_tvTools__CombineScenes_CombineMa_180025068,
                                              DAT_18002958c,DAT_180029f00,DAT_180029f08);
                                iVar2 = FUN_180002500(uVar1,&local_res20,&local_res8,&local_res10);
                                if (iVar2 < 0) {
                                  DAT_180029f00 = 0x18;
                                  DAT_18002958c = 0x3320;
                                }
                                else {
                                  pcVar14 = (code *)FUN_180002690(DAT_180029798,0,0xffffffff);
                                  if (pcVar14 == (code *)0x0) {
                                    DAT_18002958c = 0x332c;
                                  }
                                  else {
                                    iVar2 = PyDict_SetItem(DAT_180029ed0,DAT_180029788,pcVar14);
                                    if (-1 < iVar2) {
                                      *(longlong *)pcVar14 = *(longlong *)pcVar14 + -1;
                                      if (*(longlong *)pcVar14 == 0) {
                                        (**(code **)(*(longlong *)(pcVar14 + 8) + 0x30))(pcVar14);
                                      }
                                      *local_res20 = *local_res20 + -1;
                                      if (*local_res20 == 0) {
                                        (**(code **)(local_res20[1] + 0x30))();
                                      }
                                      *local_res8 = *local_res8 + -1;
                                      if (*local_res8 == 0) {
                                        (**(code **)(local_res8[1] + 0x30))();
                                      }
                                      *local_res10 = *local_res10 + -1;
                                      if (*local_res10 == 0) {
                                        (**(code **)(local_res10[1] + 0x30))();
                                      }
                                      FUN_180002450(*(undefined8 *)_PyThreadState_Current_exref,
                                                    local_78,local_a0,local_88);
                                      goto LAB_18001c176;
                                    }
                                    DAT_18002958c = 0x332e;
                                  }
                                  DAT_180029f00 = 0x19;
                                }
                                DAT_180029f08 = DAT_1800291f8;
                                pcVar12 = local_78;
                                pcVar13 = local_a0;
                                goto LAB_18001bd81;
                              }
                              *DAT_180029798 = *DAT_180029798 + 1;
                              *(longlong **)plVar7[3] = DAT_180029798;
                              plVar6 = (longlong *)FUN_180002690(DAT_180029650,plVar7,0xffffffff);
                              if (plVar6 == (longlong *)0x0) {
                                DAT_180029f08 = DAT_1800291f8;
                                DAT_18002958c = 0x32f7;
                                goto LAB_18001bf94;
                              }
                              *plVar7 = *plVar7 + -1;
                              if (*plVar7 == 0) {
                                (**(code **)(plVar7[1] + 0x30))(plVar7);
                              }
                              plVar7 = (longlong *)FUN_1800027f0(plVar6,DAT_180029798);
                              if (plVar7 == (longlong *)0x0) {
                                DAT_18002958c = 0x32fa;
LAB_18001bf86:
                                DAT_180029f08 = DAT_1800291f8;
                                goto LAB_18001bf94;
                              }
                              iVar2 = PyDict_SetItem(DAT_180029ed0,DAT_180029788,plVar7);
                              if (iVar2 < 0) {
                                DAT_18002958c = 0x32fc;
                                goto LAB_18001bf86;
                              }
                              *plVar7 = *plVar7 + -1;
                              if (*plVar7 == 0) {
                                (**(code **)(plVar7[1] + 0x30))(plVar7);
                              }
                              *plVar6 = *plVar6 + -1;
                              if (*plVar6 == 0) {
                                (**(code **)(plVar6[1] + 0x30))(plVar6);
                              }
                              if ((local_78 != (code *)0x0) &&
                                 (*(longlong *)local_78 = *(longlong *)local_78 + -1,
                                 *(longlong *)local_78 == 0)) {
                                (**(code **)(*(longlong *)(local_78 + 8) + 0x30))();
                              }
                              if ((pcVar14 != (code *)0x0) &&
                                 (*(longlong *)pcVar14 = *(longlong *)pcVar14 + -1,
                                 *(longlong *)pcVar14 == 0)) {
                                (**(code **)(*(longlong *)(pcVar14 + 8) + 0x30))(pcVar14);
                              }
                              if ((plVar5 != (longlong *)0x0) &&
                                 (*plVar5 = *plVar5 + -1, *plVar5 == 0)) {
                                (**(code **)(plVar5[1] + 0x30))(plVar5);
                              }
LAB_18001c176:
                              plVar15 = (longlong *)0x0;
                              plVar10 = (longlong *)0x0;
                              plVar9 = (longlong *)FUN_1800014a0(DAT_180029d20);
                              if (plVar9 == (longlong *)0x0) {
                                DAT_180029f08 = DAT_1800291f8;
                                DAT_180029f00 = 0x1b;
                                DAT_18002958c = 0x3354;
                                goto LAB_18001e1a6;
                              }
                              plVar4 = (longlong *)FUN_1800014a0(DAT_180029788);
                              if (plVar4 == (longlong *)0x0) {
                                DAT_180029f00 = 0x1b;
                                DAT_18002958c = 0x3356;
                                pcVar14 = (code *)0x0;
LAB_18001e0ec:
                                plVar6 = (longlong *)0x0;
                                plVar7 = (longlong *)0x0;
                                DAT_180029f08 = DAT_1800291f8;
                                plVar3 = plVar9;
                                plVar5 = plVar15;
                                goto LAB_18001e0fa;
                              }
                              plVar5 = plVar9 + 1;
                              pcVar14 = (code *)0x0;
                              if (((code *)*plVar5 != PyMethod_Type_exref) ||
                                 (pcVar14 = (code *)plVar9[3], pcVar14 == (code *)0x0)) {
                                plVar6 = (longlong *)FUN_1800018a0(plVar9,plVar4);
                                plVar3 = plVar9;
                                if (plVar6 != (longlong *)0x0) {
LAB_18001c28f:
                                  *plVar4 = *plVar4 + -1;
                                  if (*plVar4 == 0) {
                                    lVar11 = plVar4[1];
                                    plVar15 = plVar4;
LAB_18001c29c:
                                    (**(code **)(lVar11 + 0x30))(plVar15);
                                  }
                                  goto LAB_18001c29f;
                                }
                                DAT_180029f00 = 0x1b;
                                DAT_18002958c = 0x3363;
                                plVar10 = (longlong *)0x0;
                                goto LAB_18001e0ec;
                              }
                              plVar3 = (longlong *)plVar9[2];
                              *(longlong *)pcVar14 = *(longlong *)pcVar14 + 1;
                              *plVar3 = *plVar3 + 1;
                              *plVar9 = *plVar9 + -1;
                              if (*plVar9 == 0) {
                                (**(code **)(plVar9[1] + 0x30))();
                              }
                              plVar5 = plVar3 + 1;
                              plVar9 = plVar3;
                              if ((code *)*plVar5 == PyFunction_Type_exref) {
                                local_78 = pcVar14;
                                local_70 = plVar4;
                                plVar6 = (longlong *)FUN_1800015b0(plVar3,&local_78,2);
                                if (plVar6 != (longlong *)0x0) {
                                  *(longlong *)pcVar14 = *(longlong *)pcVar14 + -1;
                                  if (*(longlong *)pcVar14 == 0) {
                                    (**(code **)(*(longlong *)(pcVar14 + 8) + 0x30))(pcVar14);
                                  }
                                  pcVar14 = (code *)0x0;
                                  goto LAB_18001c28f;
                                }
                                DAT_180029f00 = 0x1b;
                                DAT_18002958c = 0x336a;
                                plVar10 = (longlong *)0x0;
                                goto LAB_18001e0ec;
                              }
                              plVar15 = (longlong *)PyTuple_New(2);
                              if (plVar15 == (longlong *)0x0) {
                                plVar7 = (longlong *)0x0;
                                DAT_180029f08 = DAT_1800291f8;
                                plVar6 = (longlong *)0x0;
                                DAT_180029f00 = 0x1b;
                                DAT_18002958c = 0x337a;
                                plVar5 = plVar15;
                                goto LAB_18001e0fa;
                              }
                              plVar15[3] = (longlong)pcVar14;
                              plVar15[4] = (longlong)plVar4;
                              plVar4 = (longlong *)0x0;
                              pcVar14 = (code *)0x0;
                              plVar6 = (longlong *)FUN_1800014e0(plVar3,plVar15,0);
                              if (plVar6 == (longlong *)0x0) {
                                DAT_180029f00 = 0x1b;
                                DAT_18002958c = 0x3380;
                                plVar10 = (longlong *)0x0;
                                pcVar14 = (code *)0x0;
                                goto LAB_18001e0ec;
                              }
                              *plVar15 = *plVar15 + -1;
                              if (*plVar15 == 0) {
                                lVar11 = plVar15[1];
                                goto LAB_18001c29c;
                              }
LAB_18001c29f:
                              *plVar3 = *plVar3 + -1;
                              if (*plVar3 == 0) {
                                (**(code **)(*plVar5 + 0x30))(plVar3);
                              }
                              plVar5 = (longlong *)0x0;
                              *plVar6 = *plVar6 + -1;
                              if (*plVar6 == 0) {
                                (**(code **)(plVar6[1] + 0x30))(plVar6);
                              }
                              lVar11 = *(longlong *)_PyThreadState_Current_exref;
                              plVar6 = *(longlong **)(lVar11 + 0x60);
                              plVar7 = *(longlong **)(lVar11 + 0x68);
                              plVar3 = *(longlong **)(lVar11 + 0x70);
                              if (plVar6 != (longlong *)0x0) {
                                *plVar6 = *plVar6 + 1;
                              }
                              if (plVar7 != (longlong *)0x0) {
                                *plVar7 = *plVar7 + 1;
                              }
                              if (plVar3 != (longlong *)0x0) {
                                *plVar3 = *plVar3 + 1;
                              }
                              local_res20 = plVar7;
                              local_88 = plVar6;
                              plVar10 = (longlong *)PyList_New(1);
                              if (plVar10 == (longlong *)0x0) {
                                DAT_180029f08 = DAT_1800291f8;
                                DAT_18002958c = 0x339f;
LAB_18001c4ad:
                                DAT_180029f00 = 0x1d;
                                plVar6 = (longlong *)0x0;
                                plVar7 = (longlong *)0x0;
                                local_60 = *(longlong **)_PyThreadState_Current_exref;
                                local_res18 = (longlong *)0x0;
                                DAT_1800291f8 = DAT_180029f08;
                                if ((pcVar14 != (code *)0x0) &&
                                   (*(longlong *)pcVar14 = *(longlong *)pcVar14 + -1,
                                   *(longlong *)pcVar14 == 0)) {
                                  (**(code **)(*(longlong *)(pcVar14 + 8) + 0x30))(pcVar14);
                                }
                                pcVar14 = (code *)0x0;
                                local_a8 = (longlong *)0x0;
                                plVar4 = (longlong *)0x0;
                                if ((plVar10 != (longlong *)0x0) &&
                                   (*plVar10 = *plVar10 + -1, *plVar10 == 0)) {
                                  (**(code **)(plVar10[1] + 0x30))(plVar10);
                                }
                                local_res10 = (longlong *)0x0;
                                if ((plVar5 != (longlong *)0x0) &&
                                   (*plVar5 = *plVar5 + -1, *plVar5 == 0)) {
                                  (**(code **)(plVar5[1] + 0x30))(plVar5);
                                }
                                local_res8 = (longlong *)0x0;
                                FUN_180002f70(s_tvTools__CombineScenes_CombineMa_1800283b8,
                                              DAT_18002958c,DAT_180029f00,DAT_180029f08);
                                iVar2 = FUN_180002500(local_60,&local_res8,&local_res10,&local_a8);
                                if (iVar2 < 0) {
                                  DAT_180029f00 = 0x1e;
                                  DAT_18002958c = 0x33cd;
                                }
                                else {
                                  plVar4 = (longlong *)FUN_180002690(DAT_180029978,0,0xffffffff);
                                  if (plVar4 == (longlong *)0x0) {
                                    DAT_18002958c = 0x33d9;
                                  }
                                  else {
                                    iVar2 = PyDict_SetItem(DAT_180029ed0,DAT_180029970,plVar4);
                                    if (-1 < iVar2) {
                                      *plVar4 = *plVar4 + -1;
                                      if (*plVar4 == 0) {
                                        (**(code **)(plVar4[1] + 0x30))(plVar4);
                                      }
                                      *local_res8 = *local_res8 + -1;
                                      if (*local_res8 == 0) {
                                        (**(code **)(local_res8[1] + 0x30))();
                                      }
                                      *local_res10 = *local_res10 + -1;
                                      if (*local_res10 == 0) {
                                        (**(code **)(local_res10[1] + 0x30))();
                                      }
                                      *local_a8 = *local_a8 + -1;
                                      if (*local_a8 == 0) {
                                        (**(code **)(local_a8[1] + 0x30))();
                                      }
                                      FUN_180002450(*(undefined8 *)_PyThreadState_Current_exref,
                                                    local_88,local_res20,plVar3);
                                      goto LAB_18001c6be;
                                    }
                                    DAT_18002958c = 0x33db;
                                  }
                                  DAT_180029f00 = 0x1f;
                                }
                                DAT_180029f08 = DAT_1800291f8;
                                FUN_180002450(*(undefined8 *)_PyThreadState_Current_exref,local_88,
                                              local_res20,plVar3);
                                plVar10 = local_res10;
                                plVar3 = local_res8;
                                plVar5 = local_a8;
                                goto LAB_18001e0fa;
                              }
                              *DAT_180029978 = *DAT_180029978 + 1;
                              *(longlong **)plVar10[3] = DAT_180029978;
                              plVar5 = (longlong *)FUN_180002690(DAT_180029650,plVar10,0xffffffff);
                              if (plVar5 == (longlong *)0x0) {
                                DAT_180029f08 = DAT_1800291f8;
                                DAT_18002958c = 0x33a4;
                                goto LAB_18001c4ad;
                              }
                              *plVar10 = *plVar10 + -1;
                              if (*plVar10 == 0) {
                                (**(code **)(plVar10[1] + 0x30))(plVar10);
                              }
                              plVar10 = (longlong *)FUN_1800027f0(plVar5,DAT_180029978);
                              if (plVar10 == (longlong *)0x0) {
                                DAT_18002958c = 0x33a7;
LAB_18001c49f:
                                DAT_180029f08 = DAT_1800291f8;
                                goto LAB_18001c4ad;
                              }
                              iVar2 = PyDict_SetItem(DAT_180029ed0,DAT_180029970,plVar10);
                              if (iVar2 < 0) {
                                DAT_18002958c = 0x33a9;
                                goto LAB_18001c49f;
                              }
                              *plVar10 = *plVar10 + -1;
                              if (*plVar10 == 0) {
                                (**(code **)(plVar10[1] + 0x30))(plVar10);
                              }
                              *plVar5 = *plVar5 + -1;
                              if (*plVar5 == 0) {
                                (**(code **)(plVar5[1] + 0x30))(plVar5);
                              }
                              if ((plVar6 != (longlong *)0x0) &&
                                 (*plVar6 = *plVar6 + -1, *plVar6 == 0)) {
                                (**(code **)(plVar6[1] + 0x30))(plVar6);
                              }
                              if ((plVar7 != (longlong *)0x0) &&
                                 (*plVar7 = *plVar7 + -1, *plVar7 == 0)) {
                                (**(code **)(plVar7[1] + 0x30))(plVar7);
                              }
                              if ((plVar3 != (longlong *)0x0) &&
                                 (*plVar3 = *plVar3 + -1, *plVar3 == 0)) {
                                (**(code **)(plVar3[1] + 0x30))(plVar3);
                              }
LAB_18001c6be:
                              plVar5 = (longlong *)FUN_180002690(DAT_180029be0,0,0xffffffff);
                              if (plVar5 != (longlong *)0x0) {
                                iVar2 = PyDict_SetItem(DAT_180029ed0,DAT_180029be0,plVar5);
                                if (-1 < iVar2) {
                                  *plVar5 = *plVar5 + -1;
                                  if (*plVar5 == 0) {
                                    (**(code **)(plVar5[1] + 0x30))(plVar5);
                                  }
                                  plVar5 = (longlong *)0x0;
                                  plVar15 = (longlong *)0x0;
                                  plVar10 = (longlong *)FUN_1800014a0(DAT_180029d20);
                                  if (plVar10 == (longlong *)0x0) {
                                    plVar7 = (longlong *)0x0;
                                    DAT_180029f08 = DAT_1800291f8;
                                    plVar6 = (longlong *)0x0;
                                    DAT_180029f00 = 0x22;
                                    DAT_18002958c = 0x340d;
                                    goto LAB_18001e166;
                                  }
                                  plVar9 = (longlong *)FUN_1800014a0(DAT_180029970);
                                  if (plVar9 != (longlong *)0x0) {
                                    plVar5 = plVar10 + 1;
                                    plVar4 = (longlong *)0x0;
                                    if (((code *)*plVar5 == PyMethod_Type_exref) &&
                                       (plVar4 = (longlong *)plVar10[3], plVar4 != (longlong *)0x0))
                                    {
                                      plVar8 = (longlong *)plVar10[2];
                                      *plVar4 = *plVar4 + 1;
                                      *plVar8 = *plVar8 + 1;
                                      *plVar10 = *plVar10 + -1;
                                      if (*plVar10 == 0) {
                                        (**(code **)(plVar10[1] + 0x30))();
                                      }
                                      plVar5 = plVar8 + 1;
                                      plVar10 = plVar8;
                                      if ((code *)*plVar5 == PyFunction_Type_exref) {
                                        local_60 = plVar4;
                                        local_58 = plVar9;
                                        plVar6 = (longlong *)FUN_1800015b0(plVar8,&local_60,2);
                                        if (plVar6 != (longlong *)0x0) {
                                          *plVar4 = *plVar4 + -1;
                                          if (*plVar4 == 0) {
                                            (**(code **)(plVar4[1] + 0x30))(plVar4);
                                          }
                                          plVar4 = (longlong *)0x0;
                                          goto LAB_18001c882;
                                        }
                                        DAT_180029f00 = 0x22;
                                        DAT_18002958c = 0x3423;
                                        plVar15 = (longlong *)0x0;
                                      }
                                      else {
                                        pcVar14 = (code *)PyTuple_New(2);
                                        if (pcVar14 != (code *)0x0) {
                                          *(longlong **)(pcVar14 + 0x18) = plVar4;
                                          *(longlong **)(pcVar14 + 0x20) = plVar9;
                                          plVar4 = (longlong *)0x0;
                                          plVar6 = (longlong *)FUN_1800014e0(plVar8,pcVar14,0);
                                          if (plVar6 == (longlong *)0x0) {
                                            plVar7 = (longlong *)0x0;
                                            DAT_180029f08 = DAT_1800291f8;
                                            plVar6 = (longlong *)0x0;
                                            DAT_180029f00 = 0x22;
                                            DAT_18002958c = 0x3439;
                                            plVar5 = (longlong *)0x0;
                                            goto LAB_18001e126;
                                          }
                                          *(longlong *)pcVar14 = *(longlong *)pcVar14 + -1;
                                          if (*(longlong *)pcVar14 == 0) {
                                            (**(code **)(*(longlong *)(pcVar14 + 8) + 0x30))
                                                      (pcVar14);
                                          }
                                          pcVar14 = (code *)0x0;
                                          goto LAB_18001c894;
                                        }
                                        DAT_180029f00 = 0x22;
                                        DAT_18002958c = 0x3433;
                                      }
                                    }
                                    else {
                                      plVar6 = (longlong *)FUN_1800018a0(plVar10,plVar9);
                                      if (plVar6 != (longlong *)0x0) {
LAB_18001c882:
                                        *plVar9 = *plVar9 + -1;
                                        plVar8 = plVar10;
                                        if (*plVar9 == 0) {
                                          (**(code **)(plVar9[1] + 0x30))(plVar9);
                                        }
LAB_18001c894:
                                        *plVar8 = *plVar8 + -1;
                                        if (*plVar8 == 0) {
                                          (**(code **)(*plVar5 + 0x30))(plVar8);
                                        }
                                        *plVar6 = *plVar6 + -1;
                                        if (*plVar6 == 0) {
                                          (**(code **)(plVar6[1] + 0x30))(plVar6);
                                        }
                                        plVar5 = (longlong *)0x0;
                                        plVar15 = (longlong *)0x0;
                                        plVar10 = (longlong *)FUN_1800014a0(DAT_180029d20);
                                        plVar8 = plVar10;
                                        if (plVar10 == (longlong *)0x0) {
                                          plVar7 = (longlong *)0x0;
                                          DAT_180029f08 = DAT_1800291f8;
                                          plVar6 = (longlong *)0x0;
                                          DAT_180029f00 = 0x23;
                                          DAT_18002958c = 0x3448;
                                        }
                                        else {
                                          pcVar14 = (code *)FUN_1800014a0(DAT_180029e78);
                                          if (pcVar14 != (code *)0x0) {
                                            plVar5 = plVar10 + 1;
                                            plVar9 = (longlong *)0x0;
                                            if (((code *)*plVar5 == PyMethod_Type_exref) &&
                                               (plVar9 = (longlong *)plVar10[3],
                                               plVar9 != (longlong *)0x0)) {
                                              plVar8 = (longlong *)plVar10[2];
                                              *plVar9 = *plVar9 + 1;
                                              *plVar8 = *plVar8 + 1;
                                              *plVar10 = *plVar10 + -1;
                                              if (*plVar10 == 0) {
                                                (**(code **)(plVar10[1] + 0x30))();
                                              }
                                              plVar5 = plVar8 + 1;
                                              plVar10 = plVar8;
                                              if ((code *)*plVar5 == PyFunction_Type_exref) {
                                                local_88 = plVar9;
                                                local_80 = pcVar14;
                                                plVar6 = (longlong *)
                                                         FUN_1800015b0(plVar8,&local_88,2);
                                                if (plVar6 != (longlong *)0x0) {
                                                  *plVar9 = *plVar9 + -1;
                                                  if (*plVar9 == 0) {
                                                    (**(code **)(plVar9[1] + 0x30))(plVar9);
                                                  }
                                                  plVar9 = (longlong *)0x0;
                                                  goto LAB_18001caac;
                                                }
                                                DAT_180029f00 = 0x23;
                                                DAT_18002958c = 0x345e;
                                                plVar15 = (longlong *)0x0;
                                              }
                                              else {
                                                plVar4 = (longlong *)PyTuple_New(2);
                                                if (plVar4 != (longlong *)0x0) {
                                                  plVar4[3] = (longlong)plVar9;
                                                  plVar4[4] = (longlong)pcVar14;
                                                  pcVar14 = (code *)0x0;
                                                  plVar9 = (longlong *)0x0;
                                                  plVar6 = (longlong *)
                                                           FUN_1800014e0(plVar8,plVar4,0);
                                                  if (plVar6 == (longlong *)0x0) {
                                                    plVar7 = (longlong *)0x0;
                                                    DAT_180029f08 = DAT_1800291f8;
                                                    plVar6 = (longlong *)0x0;
                                                    DAT_180029f00 = 0x23;
                                                    DAT_18002958c = 0x3474;
                                                    plVar5 = (longlong *)0x0;
                                                    goto LAB_18001e111;
                                                  }
                                                  *plVar4 = *plVar4 + -1;
                                                  if (*plVar4 == 0) {
                                                    (**(code **)(plVar4[1] + 0x30))(plVar4);
                                                  }
                                                  plVar4 = (longlong *)0x0;
                                                  goto LAB_18001cac0;
                                                }
                                                DAT_180029f00 = 0x23;
                                                DAT_18002958c = 0x346e;
                                              }
                                            }
                                            else {
                                              plVar6 = (longlong *)FUN_1800018a0(plVar10,pcVar14);
                                              if (plVar6 == (longlong *)0x0) {
                                                DAT_180029f00 = 0x23;
                                                DAT_18002958c = 0x3457;
                                                plVar15 = (longlong *)0x0;
                                              }
                                              else {
LAB_18001caac:
                                                *(longlong *)pcVar14 = *(longlong *)pcVar14 + -1;
                                                if (*(longlong *)pcVar14 == 0) {
                                                  (**(code **)(*(longlong *)(pcVar14 + 8) + 0x30))
                                                            (pcVar14);
                                                }
LAB_18001cac0:
                                                pcVar14 = (code *)0x0;
                                                *plVar10 = *plVar10 + -1;
                                                if (*plVar10 == 0) {
                                                  (**(code **)(*plVar5 + 0x30))(plVar10);
                                                }
                                                *plVar6 = *plVar6 + -1;
                                                if (*plVar6 == 0) {
                                                  (**(code **)(plVar6[1] + 0x30))(plVar6);
                                                }
                                                plVar15 = (longlong *)FUN_1800014a0(DAT_180029e78);
                                                if (plVar15 == (longlong *)0x0) {
                                                  DAT_180029f00 = 0x26;
                                                  DAT_18002958c = 0x3483;
                                                  plVar10 = (longlong *)0x0;
                                                }
                                                else {
                                                  pcVar12 = *(code **)(plVar15[1] + 0x90);
                                                  if (pcVar12 == (code *)0x0) {
                                                    pcVar12 = *(code **)(plVar15[1] + 0x40);
                                                    if (pcVar12 == (code *)0x0) {
                                                      plVar10 = (longlong *)
                                                                PyObject_GetAttr(plVar15);
                                                    }
                                                    else {
                                                      plVar10 = (longlong *)
                                                                (*pcVar12)(plVar15,DAT_180029880 +
                                                                                   0x20);
                                                    }
                                                  }
                                                  else {
                                                    plVar10 = (longlong *)(*pcVar12)();
                                                  }
                                                  if (plVar10 == (longlong *)0x0) {
                                                    DAT_180029f00 = 0x26;
                                                    DAT_18002958c = 0x3485;
                                                  }
                                                  else {
                                                    *plVar15 = *plVar15 + -1;
                                                    if (*plVar15 == 0) {
                                                      (**(code **)(plVar15[1] + 0x30))(plVar15);
                                                    }
                                                    plVar15 = (longlong *)
                                                              FUN_1800014a0(DAT_180029838);
                                                    if (plVar15 == (longlong *)0x0) {
                                                      DAT_180029f00 = 0x26;
                                                      DAT_18002958c = 0x3488;
                                                    }
                                                    else {
                                                      pcVar12 = *(code **)(plVar15[1] + 0x90);
                                                      if (pcVar12 == (code *)0x0) {
                                                        pcVar12 = *(code **)(plVar15[1] + 0x40);
                                                        if (pcVar12 == (code *)0x0) {
                                                          plVar4 = (longlong *)
                                                                   PyObject_GetAttr(plVar15);
                                                        }
                                                        else {
                                                          plVar4 = (longlong *)
                                                                   (*pcVar12)(plVar15,DAT_180029810
                                                                                      + 0x20);
                                                        }
                                                      }
                                                      else {
                                                        plVar4 = (longlong *)(*pcVar12)();
                                                      }
                                                      if (plVar4 == (longlong *)0x0) {
                                                        DAT_180029f00 = 0x26;
                                                        DAT_18002958c = 0x348a;
                                                      }
                                                      else {
                                                        *plVar15 = *plVar15 + -1;
                                                        if (*plVar15 == 0) {
                                                          (**(code **)(plVar15[1] + 0x30))(plVar15);
                                                        }
                                                        plVar15 = (longlong *)
                                                                  FUN_1800014a0(DAT_180029970);
                                                        if (plVar15 == (longlong *)0x0) {
                                                          DAT_180029f00 = 0x26;
                                                          DAT_18002958c = 0x348d;
                                                        }
                                                        else {
                                                          pcVar14 = *(code **)(plVar15[1] + 0x90);
                                                          if (pcVar14 == (code *)0x0) {
                                                            pcVar14 = *(code **)(plVar15[1] + 0x40);
                                                            if (pcVar14 == (code *)0x0) {
                                                              pcVar14 = (code *)PyObject_GetAttr(
                                                  plVar15);
                                                  }
                                                  else {
                                                    pcVar14 = (code *)(*pcVar14)(plVar15,
                                                  DAT_180029730 + 0x20);
                                                  }
                                                  }
                                                  else {
                                                    pcVar14 = (code *)(*pcVar14)();
                                                  }
                                                  if (pcVar14 == (code *)0x0) {
                                                    DAT_180029f00 = 0x26;
                                                    DAT_18002958c = 0x348f;
                                                  }
                                                  else {
                                                    *plVar15 = *plVar15 + -1;
                                                    if (*plVar15 == 0) {
                                                      (**(code **)(plVar15[1] + 0x30))(plVar15);
                                                    }
                                                    plVar15 = (longlong *)PyTuple_New(3);
                                                    if (plVar15 == (longlong *)0x0) {
                                                      DAT_180029f00 = 0x26;
                                                      DAT_18002958c = 0x3492;
                                                    }
                                                    else {
                                                      plVar15[3] = (longlong)plVar10;
                                                      plVar5 = plVar15 + 3;
                                                      plVar15[4] = (longlong)plVar4;
                                                      plVar7 = (longlong *)0x0;
                                                      plVar10 = (longlong *)0x0;
                                                      plVar15[5] = (longlong)pcVar14;
                                                      plVar4 = (longlong *)0x0;
                                                      plVar6 = (longlong *)plVar15[2];
                                                      pcVar12 = (code *)0x0;
                                                      local_res10 = (longlong *)0x0;
                                                      local_res8 = plVar6;
                                                      if ((longlong)plVar6 < 1) {
LAB_18001ce4a:
                                                        pcVar14 = PyClass_Type_exref;
                                                      }
                                                      else {
                                                        do {
                                                          pcVar13 = *(code **)(*plVar5 + 8);
                                                          pcVar14 = pcVar12;
                                                          if ((((pcVar13 != PyClass_Type_exref) &&
                                                               (pcVar14 = pcVar13,
                                                               pcVar12 != (code *)0x0)) &&
                                                              (iVar2 = PyType_IsSubtype(pcVar12,
                                                  pcVar13), plVar6 = local_res8, pcVar14 = pcVar12,
                                                  iVar2 == 0)) &&
                                                  (iVar2 = PyType_IsSubtype(pcVar13,pcVar12),
                                                  plVar6 = local_res8, pcVar14 = pcVar13, iVar2 == 0
                                                  )) {
                                                    PyErr_SetString(*(undefined8 *)
                                                                     PyExc_TypeError_exref,
                                                                                                                                        
                                                  s_metaclass_conflict__the_metaclas_1800294a0);
                                                  DAT_180029f00 = 0x26;
                                                  DAT_18002958c = 0x349d;
                                                  pcVar14 = (code *)0x0;
                                                  goto LAB_18001e0ec;
                                                  }
                                                  plVar5 = plVar5 + 1;
                                                  local_res10 = (longlong *)
                                                                ((longlong)local_res10 + 1);
                                                  pcVar12 = pcVar14;
                                                  } while ((longlong)local_res10 < (longlong)plVar6)
                                                  ;
                                                  if (pcVar14 == (code *)0x0) goto LAB_18001ce4a;
                                                  }
                                                  *(longlong *)pcVar14 = *(longlong *)pcVar14 + 1;
                                                  plVar4 = (longlong *)
                                                           FUN_180002950(pcVar14,plVar15,
                                                                         DAT_180029658,DAT_180029658
                                                                         ,0,DAT_180029e68,0);
                                                  if (plVar4 == (longlong *)0x0) {
                                                    DAT_180029f00 = 0x26;
                                                    DAT_18002958c = 0x349f;
                                                    plVar10 = plVar7;
                                                  }
                                                  else {
                                                    iVar2 = PyObject_SetItem(plVar4,DAT_180029750,
                                                                             DAT_1800297a8);
                                                    if (iVar2 < 0) {
                                                      DAT_180029f00 = 0x2a;
                                                      DAT_18002958c = 0x34a9;
                                                      plVar10 = plVar7;
                                                    }
                                                    else {
                                                      iVar2 = PyObject_SetItem(plVar4,DAT_180029d60,
                                                                               DAT_1800297a0);
                                                      if (iVar2 < 0) {
                                                        DAT_180029f00 = 0x2b;
                                                        DAT_18002958c = 0x34b2;
                                                        plVar10 = plVar7;
                                                      }
                                                      else {
                                                        iVar2 = PyObject_SetItem(plVar4,
                                                  DAT_180029e00,DAT_180029898);
                                                  if (iVar2 < 0) {
                                                    DAT_180029f00 = 0x2c;
                                                    DAT_18002958c = 0x34bb;
                                                  }
                                                  else {
                                                    plVar10 = (longlong *)
                                                              FUN_180001be0(DAT_180029560,
                                                                            &
                                                  PTR_s___init___180024678,0,DAT_180029660,0,
                                                  DAT_180029e68,DAT_180029ed0,DAT_18002a130);
                                                  plVar5 = DAT_18002a068;
                                                  if (plVar10 == (longlong *)0x0) {
                                                    DAT_180029f00 = 0x2e;
                                                    DAT_18002958c = 0x34c4;
                                                  }
                                                  else {
                                                    plVar10[0x10] = (longlong)DAT_18002a068;
                                                    *plVar5 = *plVar5 + 1;
                                                    iVar2 = PyObject_SetItem(plVar4,DAT_180029af0,
                                                                             plVar10);
                                                    if (iVar2 < 0) {
                                                      DAT_180029f00 = 0x2e;
                                                      DAT_18002958c = 0x34c7;
                                                    }
                                                    else {
                                                      *plVar10 = *plVar10 + -1;
                                                      if (*plVar10 == 0) {
                                                        (**(code **)(plVar10[1] + 0x30))(plVar10);
                                                      }
                                                      plVar10 = (longlong *)
                                                                FUN_180001be0(DAT_180029560,
                                                                              &
                                                  PTR_s_initializeUI_180028be0,0,DAT_1800296c0,0,
                                                  DAT_180029e68,DAT_180029ed0,DAT_18002a138);
                                                  if (plVar10 == (longlong *)0x0) {
                                                    DAT_180029f00 = 0x38;
                                                    DAT_18002958c = 0x34d1;
                                                  }
                                                  else {
                                                    iVar2 = PyObject_SetItem(plVar4,DAT_180029af8,
                                                                             plVar10);
                                                    if (iVar2 < 0) {
                                                      DAT_180029f00 = 0x38;
                                                      DAT_18002958c = 0x34d3;
                                                    }
                                                    else {
                                                      *plVar10 = *plVar10 + -1;
                                                      if (*plVar10 == 0) {
                                                        (**(code **)(plVar10[1] + 0x30))(plVar10);
                                                      }
                                                      plVar10 = (longlong *)
                                                                FUN_180001be0(DAT_180029560,
                                                                              &
                                                  PTR_s_makeConnections_1800284a8,0,DAT_1800296d8,0,
                                                  DAT_180029e68,DAT_180029ed0,DAT_18002a140);
                                                  if (plVar10 == (longlong *)0x0) {
                                                    DAT_180029f00 = 0x50;
                                                    DAT_18002958c = 0x34dd;
                                                  }
                                                  else {
                                                    iVar2 = PyObject_SetItem(plVar4,DAT_180029c00,
                                                                             plVar10);
                                                    if (iVar2 < 0) {
                                                      DAT_180029f00 = 0x50;
                                                      DAT_18002958c = 0x34df;
                                                    }
                                                    else {
                                                      *plVar10 = *plVar10 + -1;
                                                      if (*plVar10 == 0) {
                                                        (**(code **)(plVar10[1] + 0x30))(plVar10);
                                                      }
                                                      plVar10 = (longlong *)
                                                                FUN_180001be0(DAT_180029560,
                                                                              &
                                                  PTR_s_hide_ui_1800250d8,0,DAT_1800296b8,0,
                                                  DAT_180029e68,DAT_180029ed0,DAT_18002a148);
                                                  if (plVar10 == (longlong *)0x0) {
                                                    DAT_180029f00 = 0x60;
                                                    DAT_18002958c = 0x34e9;
                                                  }
                                                  else {
                                                    iVar2 = PyObject_SetItem(plVar4,DAT_180029aa8,
                                                                             plVar10);
                                                    if (iVar2 < 0) {
                                                      DAT_180029f00 = 0x60;
                                                      DAT_18002958c = 0x34eb;
                                                    }
                                                    else {
                                                      *plVar10 = *plVar10 + -1;
                                                      if (*plVar10 == 0) {
                                                        (**(code **)(plVar10[1] + 0x30))(plVar10);
                                                      }
                                                      plVar10 = (longlong *)
                                                                FUN_180001be0(DAT_180029560,
                                                                              &
                                                  PTR_s_add_message_180028ac0,0,DAT_180029678,0,
                                                  DAT_180029e68,DAT_180029ed0,DAT_18002a150);
                                                  if (plVar10 == (longlong *)0x0) {
                                                    DAT_180029f00 = 0x68;
                                                    DAT_18002958c = 0x34f5;
                                                  }
                                                  else {
                                                    iVar2 = PyObject_SetItem(plVar4,DAT_180029910,
                                                                             plVar10);
                                                    if (iVar2 < 0) {
                                                      DAT_180029f00 = 0x68;
                                                      DAT_18002958c = 0x34f7;
                                                    }
                                                    else {
                                                      *plVar10 = *plVar10 + -1;
                                                      if (*plVar10 == 0) {
                                                        (**(code **)(plVar10[1] + 0x30))(plVar10);
                                                      }
                                                      plVar10 = (longlong *)
                                                                FUN_180001be0(DAT_180029560,
                                                                              &
                                                  PTR_s_test_funct_180028d78,0,DAT_180029720,0,
                                                  DAT_180029e68,DAT_180029ed0,DAT_18002a158);
                                                  if (plVar10 == (longlong *)0x0) {
                                                    DAT_180029f00 = 0x6b;
                                                    DAT_18002958c = 0x3501;
                                                  }
                                                  else {
                                                    iVar2 = PyObject_SetItem(plVar4,DAT_180029e48,
                                                                             plVar10);
                                                    if (iVar2 < 0) {
                                                      DAT_180029f00 = 0x6b;
                                                      DAT_18002958c = 0x3503;
                                                    }
                                                    else {
                                                      *plVar10 = *plVar10 + -1;
                                                      if (*plVar10 == 0) {
                                                        (**(code **)(plVar10[1] + 0x30))(plVar10);
                                                      }
                                                      plVar10 = (longlong *)
                                                                FUN_180001be0(DAT_180029560,
                                                                              &
                                                  PTR_s_set_rb_button_180028ec8,0,DAT_180029700,0,
                                                  DAT_180029e68,DAT_180029ed0,DAT_18002a160);
                                                  if (plVar10 == (longlong *)0x0) {
                                                    DAT_180029f00 = 0x73;
                                                    DAT_18002958c = 0x350d;
                                                  }
                                                  else {
                                                    iVar2 = PyObject_SetItem(plVar4,DAT_180029db8,
                                                                             plVar10);
                                                    if (iVar2 < 0) {
                                                      DAT_180029f00 = 0x73;
                                                      DAT_18002958c = 0x350f;
                                                    }
                                                    else {
                                                      *plVar10 = *plVar10 + -1;
                                                      if (*plVar10 == 0) {
                                                        (**(code **)(plVar10[1] + 0x30))(plVar10);
                                                      }
                                                      plVar10 = (longlong *)
                                                                FUN_180001be0(DAT_180029560,
                                                                              &
                                                  PTR_s_active_start_from_180024558,0,DAT_180029668,
                                                  0,DAT_180029e68,DAT_180029ed0,DAT_18002a168);
                                                  if (plVar10 == (longlong *)0x0) {
                                                    DAT_180029f00 = 0x7a;
                                                    DAT_18002958c = 0x3519;
                                                  }
                                                  else {
                                                    iVar2 = PyObject_SetItem(plVar4,DAT_1800298f8,
                                                                             plVar10);
                                                    if (iVar2 < 0) {
                                                      DAT_180029f00 = 0x7a;
                                                      DAT_18002958c = 0x351b;
                                                    }
                                                    else {
                                                      *plVar10 = *plVar10 + -1;
                                                      if (*plVar10 == 0) {
                                                        (**(code **)(plVar10[1] + 0x30))(plVar10);
                                                      }
                                                      plVar10 = (longlong *)
                                                                FUN_180001be0(DAT_180029560,
                                                                              &
                                                  PTR_s_active_start_from_Spin_180027fc0,0,
                                                  DAT_180029670,0,DAT_180029e68,DAT_180029ed0,
                                                  DAT_18002a170);
                                                  if (plVar10 == (longlong *)0x0) {
                                                    DAT_180029f00 = 0x83;
                                                    DAT_18002958c = 0x3525;
                                                  }
                                                  else {
                                                    iVar2 = PyObject_SetItem(plVar4,DAT_180029900,
                                                                             plVar10);
                                                    if (iVar2 < 0) {
                                                      DAT_180029f00 = 0x83;
                                                      DAT_18002958c = 0x3527;
                                                    }
                                                    else {
                                                      *plVar10 = *plVar10 + -1;
                                                      if (*plVar10 == 0) {
                                                        (**(code **)(plVar10[1] + 0x30))(plVar10);
                                                      }
                                                      plVar10 = (longlong *)
                                                                FUN_180001be0(DAT_180029560,
                                                                              &
                                                  PTR_s_proceedAll_func_1800289a8,0,DAT_1800296e0,0,
                                                  DAT_180029e68,DAT_180029ed0,DAT_18002a178);
                                                  if (plVar10 == (longlong *)0x0) {
                                                    DAT_180029f00 = 0x89;
                                                    DAT_18002958c = 0x3531;
                                                  }
                                                  else {
                                                    iVar2 = PyObject_SetItem(plVar4,DAT_180029cd0,
                                                                             plVar10);
                                                    if (iVar2 < 0) {
                                                      DAT_180029f00 = 0x89;
                                                      DAT_18002958c = 0x3533;
                                                    }
                                                    else {
                                                      *plVar10 = *plVar10 + -1;
                                                      if (*plVar10 == 0) {
                                                        (**(code **)(plVar10[1] + 0x30))(plVar10);
                                                      }
                                                      plVar10 = (longlong *)
                                                                FUN_180001be0(DAT_180029560,
                                                                              &
                                                  PTR_s_add_sources_to_widget_1800249d0,0,
                                                  DAT_180029680,0,DAT_180029e68,DAT_180029ed0,
                                                  DAT_18002a180);
                                                  if (plVar10 == (longlong *)0x0) {
                                                    DAT_180029f00 = 0x94;
                                                    DAT_18002958c = 0x353d;
                                                  }
                                                  else {
                                                    iVar2 = PyObject_SetItem(plVar4,DAT_180029918,
                                                                             plVar10);
                                                    if (iVar2 < 0) {
                                                      DAT_180029f00 = 0x94;
                                                      DAT_18002958c = 0x353f;
                                                    }
                                                    else {
                                                      *plVar10 = *plVar10 + -1;
                                                      if (*plVar10 == 0) {
                                                        (**(code **)(plVar10[1] + 0x30))(plVar10);
                                                      }
                                                      plVar10 = (longlong *)
                                                                FUN_180001be0(DAT_180029560,
                                                                              &
                                                  PTR_s_save_setting_funct_1800248d8,0,DAT_1800296e8
                                                  ,0,DAT_180029e68,DAT_180029ed0,DAT_18002a188);
                                                  if (plVar10 == (longlong *)0x0) {
                                                    DAT_180029f00 = 0xa0;
                                                    DAT_18002958c = 0x3549;
                                                  }
                                                  else {
                                                    iVar2 = PyObject_SetItem(plVar4,DAT_180029d48,
                                                                             plVar10);
                                                    if (iVar2 < 0) {
                                                      DAT_180029f00 = 0xa0;
                                                      DAT_18002958c = 0x354b;
                                                    }
                                                    else {
                                                      *plVar10 = *plVar10 + -1;
                                                      if (*plVar10 == 0) {
                                                        (**(code **)(plVar10[1] + 0x30))(plVar10);
                                                      }
                                                      plVar10 = (longlong *)
                                                                FUN_180001be0(DAT_180029560,
                                                                              &
                                                  PTR_s_list_file_in_path_180029418,0,DAT_1800296c8,
                                                  0,DAT_180029e68,DAT_180029ed0,DAT_18002a190);
                                                  if (plVar10 == (longlong *)0x0) {
                                                    DAT_180029f00 = 0xac;
                                                    DAT_18002958c = 0x3555;
                                                  }
                                                  else {
                                                    iVar2 = PyObject_SetItem(plVar4,DAT_180029bc0,
                                                                             plVar10);
                                                    if (iVar2 < 0) {
                                                      DAT_180029f00 = 0xac;
                                                      DAT_18002958c = 0x3557;
                                                    }
                                                    else {
                                                      *plVar10 = *plVar10 + -1;
                                                      if (*plVar10 == 0) {
                                                        (**(code **)(plVar10[1] + 0x30))(plVar10);
                                                      }
                                                      plVar10 = (longlong *)
                                                                FUN_180001be0(DAT_180029560,
                                                                              &
                                                  PTR_s_get_all_files_path_from_ui_180028960,0,
                                                  DAT_180029698,0,DAT_180029e68,DAT_180029ed0,
                                                  DAT_18002a198);
                                                  if (plVar10 == (longlong *)0x0) {
                                                    DAT_180029f00 = 0xb7;
                                                    DAT_18002958c = 0x3561;
                                                  }
                                                  else {
                                                    iVar2 = PyObject_SetItem(plVar4,DAT_180029a80,
                                                                             plVar10);
                                                    if (iVar2 < 0) {
                                                      DAT_180029f00 = 0xb7;
                                                      DAT_18002958c = 0x3563;
                                                    }
                                                    else {
                                                      *plVar10 = *plVar10 + -1;
                                                      if (*plVar10 == 0) {
                                                        (**(code **)(plVar10[1] + 0x30))(plVar10);
                                                      }
                                                      plVar10 = (longlong *)
                                                                FUN_180001be0(DAT_180029560,
                                                                              &
                                                  PTR_s_show_file_select_dialog_1800292a8,0,
                                                  DAT_180029718,0,DAT_180029e68,DAT_180029ed0,
                                                  DAT_18002a1a0);
                                                  if (plVar10 == (longlong *)0x0) {
                                                    DAT_180029f00 = 0xca;
                                                    DAT_18002958c = 0x356d;
                                                  }
                                                  else {
                                                    iVar2 = PyObject_SetItem(plVar4,DAT_180029de8,
                                                                             plVar10);
                                                    if (iVar2 < 0) {
                                                      DAT_180029f00 = 0xca;
                                                      DAT_18002958c = 0x356f;
                                                    }
                                                    else {
                                                      *plVar10 = *plVar10 + -1;
                                                      if (*plVar10 == 0) {
                                                        (**(code **)(plVar10[1] + 0x30))(plVar10);
                                                      }
                                                      plVar10 = (longlong *)
                                                                FUN_180001be0(DAT_180029560,
                                                                              &
                                                  PTR_s_show_Folder_select_dialog_180024ba8,0,
                                                  DAT_180029710,0,DAT_180029e68,DAT_180029ed0,
                                                  DAT_18002a1a8);
                                                  if (plVar10 == (longlong *)0x0) {
                                                    DAT_180029f00 = 0xd6;
                                                    DAT_18002958c = 0x3579;
                                                  }
                                                  else {
                                                    iVar2 = PyObject_SetItem(plVar4,DAT_180029de0,
                                                                             plVar10);
                                                    if (iVar2 < 0) {
                                                      DAT_180029f00 = 0xd6;
                                                      DAT_18002958c = 0x357b;
                                                    }
                                                    else {
                                                      *plVar10 = *plVar10 + -1;
                                                      if (*plVar10 == 0) {
                                                        (**(code **)(plVar10[1] + 0x30))(plVar10);
                                                      }
                                                      plVar10 = (longlong *)
                                                                FUN_180001be0(DAT_180029560,
                                                                              &
                                                  PTR_s_set_path_to_line_callby_180028628,0,
                                                  DAT_1800296f8,0,DAT_180029e68,DAT_180029ed0,
                                                  DAT_18002a1b0);
                                                  if (plVar10 == (longlong *)0x0) {
                                                    DAT_180029f00 = 0xe1;
                                                    DAT_18002958c = 0x3585;
                                                  }
                                                  else {
                                                    iVar2 = PyObject_SetItem(plVar4,DAT_180029db0,
                                                                             plVar10);
                                                    if (iVar2 < 0) {
                                                      DAT_180029f00 = 0xe1;
                                                      DAT_18002958c = 0x3587;
                                                    }
                                                    else {
                                                      *plVar10 = *plVar10 + -1;
                                                      if (*plVar10 == 0) {
                                                        (**(code **)(plVar10[1] + 0x30))(plVar10);
                                                      }
                                                      plVar10 = (longlong *)
                                                                FUN_180001be0(DAT_180029560,
                                                                              &
                                                  PTR_s_set_file_to_target_180029088,0,DAT_1800296f0
                                                  ,0,DAT_180029e68,DAT_180029ed0,DAT_18002a1b8);
                                                  if (plVar10 == (longlong *)0x0) {
                                                    DAT_180029f00 = 0xe8;
                                                    DAT_18002958c = 0x3591;
                                                  }
                                                  else {
                                                    iVar2 = PyObject_SetItem(plVar4,DAT_180029da8,
                                                                             plVar10);
                                                    if (iVar2 < 0) {
                                                      DAT_180029f00 = 0xe8;
                                                      DAT_18002958c = 0x3593;
                                                    }
                                                    else {
                                                      *plVar10 = *plVar10 + -1;
                                                      if (*plVar10 == 0) {
                                                        (**(code **)(plVar10[1] + 0x30))(plVar10);
                                                      }
                                                      plVar10 = (longlong *)
                                                                FUN_180001be0(DAT_180029560,
                                                                              &
                                                  PTR_s_set_sources_path_180024608,0,DAT_180029708,0
                                                  ,DAT_180029e68,DAT_180029ed0,DAT_18002a1c0);
                                                  if (plVar10 == (longlong *)0x0) {
                                                    DAT_180029f00 = 0xec;
                                                    DAT_18002958c = 0x359d;
                                                  }
                                                  else {
                                                    iVar2 = PyObject_SetItem(plVar4,DAT_180029dc0,
                                                                             plVar10);
                                                    if (iVar2 < 0) {
                                                      DAT_180029f00 = 0xec;
                                                      DAT_18002958c = 0x359f;
                                                    }
                                                    else {
                                                      *plVar10 = *plVar10 + -1;
                                                      if (*plVar10 == 0) {
                                                        (**(code **)(plVar10[1] + 0x30))(plVar10);
                                                      }
                                                      plVar10 = (longlong *)
                                                                FUN_180001be0(DAT_180029560,
                                                                              &
                                                  PTR_s_get_maya_file_path_180028ea8,0,DAT_1800296a8
                                                  ,0,DAT_180029e68,DAT_180029ed0,DAT_18002a1c8);
                                                  if (plVar10 == (longlong *)0x0) {
                                                    DAT_180029f00 = 0xf5;
                                                    DAT_18002958c = 0x35a9;
                                                  }
                                                  else {
                                                    iVar2 = PyObject_SetItem(plVar4,DAT_180029a90,
                                                                             plVar10);
                                                    if (iVar2 < 0) {
                                                      DAT_180029f00 = 0xf5;
                                                      DAT_18002958c = 0x35ab;
                                                    }
                                                    else {
                                                      *plVar10 = *plVar10 + -1;
                                                      if (*plVar10 == 0) {
                                                        (**(code **)(plVar10[1] + 0x30))(plVar10);
                                                      }
                                                      plVar10 = (longlong *)
                                                                FUN_180001be0(DAT_180029560,
                                                                              &
                                                  PTR_s_get_files_in_folder_1800244d8,0,
                                                  DAT_1800296a0,0,DAT_180029e68,DAT_180029ed0,
                                                  DAT_18002a1d0);
                                                  if (plVar10 == (longlong *)0x0) {
                                                    DAT_180029f00 = 0x105;
                                                    DAT_18002958c = 0x35b5;
                                                  }
                                                  else {
                                                    iVar2 = PyObject_SetItem(plVar4,DAT_180029a88,
                                                                             plVar10);
                                                    if (iVar2 < 0) {
                                                      DAT_180029f00 = 0x105;
                                                      DAT_18002958c = 0x35b7;
                                                    }
                                                    else {
                                                      *plVar10 = *plVar10 + -1;
                                                      if (*plVar10 == 0) {
                                                        (**(code **)(plVar10[1] + 0x30))(plVar10);
                                                      }
                                                      plVar10 = (longlong *)
                                                                FUN_180001be0(DAT_180029560,
                                                                              &
                                                  PTR_s_eventFilter_180028408,0,DAT_180029690,0,
                                                  DAT_180029e68,DAT_180029ed0,DAT_18002a1d8);
                                                  if (plVar10 == (longlong *)0x0) {
                                                    DAT_180029f00 = 0x124;
                                                    DAT_18002958c = 0x35c1;
                                                  }
                                                  else {
                                                    iVar2 = PyObject_SetItem(plVar4,DAT_1800299f0,
                                                                             plVar10);
                                                    if (iVar2 < 0) {
                                                      DAT_180029f00 = 0x124;
                                                      DAT_18002958c = 0x35c3;
                                                    }
                                                    else {
                                                      *plVar10 = *plVar10 + -1;
                                                      if (*plVar10 == 0) {
                                                        (**(code **)(plVar10[1] + 0x30))(plVar10);
                                                      }
                                                      plVar10 = (longlong *)
                                                                FUN_180001be0(DAT_180029560,
                                                                              &
                                                  PTR_s_get_maya_version_180029050,0,DAT_1800296b0,0
                                                  ,DAT_180029e68,DAT_180029ed0,DAT_18002a1e0);
                                                  if (plVar10 == (longlong *)0x0) {
                                                    DAT_180029f00 = 0x129;
                                                    DAT_18002958c = 0x35cd;
                                                  }
                                                  else {
                                                    iVar2 = PyObject_SetItem(plVar4,DAT_180029a98,
                                                                             plVar10);
                                                    if (iVar2 < 0) {
                                                      DAT_180029f00 = 0x129;
                                                      DAT_18002958c = 0x35cf;
                                                    }
                                                    else {
                                                      *plVar10 = *plVar10 + -1;
                                                      if (*plVar10 == 0) {
                                                        (**(code **)(plVar10[1] + 0x30))(plVar10);
                                                      }
                                                      uVar17 = DAT_180029e68;
                                                      plVar5 = DAT_180029ed0;
                                                      plVar10 = (longlong *)
                                                                FUN_180001be0(DAT_180029560,
                                                                              &
                                                  PTR_s_batch_mode_180024130,0,DAT_180029688,0,
                                                  DAT_180029e68,DAT_180029ed0,DAT_18002a1e8);
                                                  uVar16 = (undefined4)((ulonglong)plVar5 >> 0x20);
                                                  if (plVar10 == (longlong *)0x0) {
                                                    DAT_180029f00 = 0x130;
                                                    DAT_18002958c = 0x35d9;
                                                  }
                                                  else {
                                                    iVar2 = PyObject_SetItem(plVar4,DAT_180029938,
                                                                             plVar10);
                                                    if (iVar2 < 0) {
                                                      DAT_180029f00 = 0x130;
                                                      DAT_18002958c = 0x35db;
                                                    }
                                                    else {
                                                      *plVar10 = *plVar10 + -1;
                                                      if (*plVar10 == 0) {
                                                        (**(code **)(plVar10[1] + 0x30))(plVar10);
                                                      }
                                                      plVar10 = (longlong *)
                                                                FUN_180002ac0(pcVar14,DAT_180029658,
                                                                              plVar15,plVar4,0,
                                                                              uVar17 & 
                                                  0xffffffff00000000,CONCAT44(uVar16,1));
                                                  if (plVar10 == (longlong *)0x0) {
                                                    DAT_180029f00 = 0x26;
                                                    DAT_18002958c = 0x35e5;
                                                  }
                                                  else {
                                                    iVar2 = PyDict_SetItem(DAT_180029ed0,
                                                                           DAT_180029658,plVar10);
                                                    if (iVar2 < 0) {
                                                      DAT_180029f00 = 0x26;
                                                      DAT_18002958c = 0x35e7;
                                                    }
                                                    else {
                                                      *plVar10 = *plVar10 + -1;
                                                      if (*plVar10 == 0) {
                                                        (**(code **)(plVar10[1] + 0x30))(plVar10);
                                                      }
                                                      *plVar4 = *plVar4 + -1;
                                                      plVar10 = (longlong *)0x0;
                                                      if (*plVar4 == 0) {
                                                        (**(code **)(plVar4[1] + 0x30))(plVar4);
                                                      }
                                                      *(longlong *)pcVar14 =
                                                           *(longlong *)pcVar14 + -1;
                                                      plVar4 = (longlong *)0x0;
                                                      if (*(longlong *)pcVar14 == 0) {
                                                        (**(code **)(*(longlong *)(pcVar14 + 8) +
                                                                    0x30))(pcVar14);
                                                      }
                                                      *plVar15 = *plVar15 + -1;
                                                      pcVar14 = (code *)0x0;
                                                      if (*plVar15 == 0) {
                                                        (**(code **)(plVar15[1] + 0x30))(plVar15);
                                                      }
                                                      plVar15 = (longlong *)
                                                                FUN_180001be0(DAT_180029560,
                                                                              &
                                                  PTR_s_apply_dpi_scaling_180024740,0,DAT_180029930,
                                                  0,DAT_180029e68,DAT_180029ed0,DAT_18002a1f0);
                                                  if (plVar15 == (longlong *)0x0) {
                                                    DAT_180029f00 = 0x15c;
                                                    DAT_18002958c = 0x35f4;
                                                    pcVar14 = (code *)0x0;
                                                  }
                                                  else {
                                                    iVar2 = PyDict_SetItem(DAT_180029ed0,
                                                                           DAT_180029930,plVar15);
                                                    if (iVar2 < 0) {
                                                      DAT_180029f00 = 0x15c;
                                                      DAT_18002958c = 0x35f6;
                                                      pcVar14 = (code *)0x0;
                                                    }
                                                    else {
                                                      *plVar15 = *plVar15 + -1;
                                                      if (*plVar15 == 0) {
                                                        (**(code **)(plVar15[1] + 0x30))(plVar15);
                                                      }
                                                      plVar15 = (longlong *)PyDict_New();
                                                      if (plVar15 == (longlong *)0x0) {
                                                        DAT_18002958c = 0x35fe;
                                                      }
                                                      else {
                                                        iVar2 = PyDict_SetItem(DAT_180029ed0,
                                                                               DAT_180029e40,plVar15
                                                                              );
                                                        if (-1 < iVar2) {
                                                          *plVar15 = *plVar15 + -1;
                                                          if (*plVar15 != 0) {
                                                            return;
                                                          }
                                                          (**(code **)(plVar15[1] + 0x30))(plVar15);
                                                          return;
                                                        }
                                                        DAT_18002958c = 0x3600;
                                                      }
                                                      DAT_180029f00 = 1;
                                                    }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                  }
                                                }
                                              }
                                            }
                                            goto LAB_18001e0ec;
                                          }
                                          plVar7 = (longlong *)0x0;
                                          DAT_180029f08 = DAT_1800291f8;
                                          plVar6 = (longlong *)0x0;
                                          DAT_180029f00 = 0x23;
                                          DAT_18002958c = 0x344a;
                                        }
                                        goto LAB_18001e111;
                                      }
                                      DAT_180029f00 = 0x22;
                                      DAT_18002958c = 0x341c;
                                      plVar15 = (longlong *)0x0;
                                    }
                                    goto LAB_18001e0ec;
                                  }
                                  plVar7 = (longlong *)0x0;
                                  DAT_180029f08 = DAT_1800291f8;
                                  plVar6 = (longlong *)0x0;
                                  DAT_180029f00 = 0x22;
                                  DAT_18002958c = 0x340f;
                                  plVar8 = plVar10;
                                  goto LAB_18001e126;
                                }
                                plVar7 = (longlong *)0x0;
                                DAT_180029f08 = DAT_1800291f8;
                                plVar6 = (longlong *)0x0;
                                DAT_180029f00 = 0x20;
                                DAT_18002958c = 0x3403;
                                goto LAB_18001e13b;
                              }
                              plVar7 = (longlong *)0x0;
                              DAT_180029f08 = DAT_1800291f8;
                              plVar6 = (longlong *)0x0;
                              DAT_180029f00 = 0x20;
                              DAT_18002958c = 0x3401;
                            }
LAB_18001e166:
                            if ((pcVar14 != (code *)0x0) &&
                               (*(longlong *)pcVar14 = *(longlong *)pcVar14 + -1,
                               *(longlong *)pcVar14 == 0)) {
                              (**(code **)(*(longlong *)(pcVar14 + 8) + 0x30))(pcVar14);
                            }
                            if ((plVar6 != (longlong *)0x0) &&
                               (*plVar6 = *plVar6 + -1, *plVar6 == 0)) {
                              (**(code **)(plVar6[1] + 0x30))(plVar6);
                            }
                            if ((plVar7 != (longlong *)0x0) &&
                               (*plVar7 = *plVar7 + -1, *plVar7 == 0)) {
                              (**(code **)(plVar7[1] + 0x30))(plVar7);
                            }
                          }
                        }
                      }
                    }
                    else {
                      DAT_180029f08 = DAT_1800291f8;
                      DAT_180029f00 = 1;
                      DAT_18002958c = 0x3107;
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
LAB_18001e1a6:
  if (DAT_180029ec8 != (longlong *)0x0) {
    if (DAT_180029ed0 != (longlong *)0x0) {
      FUN_180002f70(s_init_tvTools__CombineScenes_Comb_180028c20,0,DAT_180029f00,DAT_180029f08);
    }
    plVar5 = DAT_180029ec8;
    *DAT_180029ec8 = *DAT_180029ec8 + -1;
    if (*plVar5 == 0) {
      (**(code **)(plVar5[1] + 0x30))();
    }
    DAT_180029ec8 = (longlong *)0x0;
    return;
  }
LAB_18001e22d:
  lVar11 = PyErr_Occurred();
  if (lVar11 == 0) {
    PyErr_SetString(*(undefined8 *)PyExc_ImportError_exref,
                    s_init_tvTools__CombineScenes_Comb_180028c58);
  }
  return;
}

