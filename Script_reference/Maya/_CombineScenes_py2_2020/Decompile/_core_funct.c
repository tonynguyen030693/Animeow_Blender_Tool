
code * FUN_180007f30(undefined8 param_1,undefined8 param_2,longlong *param_3,undefined8 param_4,
                    undefined8 param_5,undefined8 param_6)

{
  code *pcVar1;
  int iVar2;
  longlong *plVar3;
  code *pcVar4;
  code *pcVar5;
  longlong *plVar6;
  code *pcVar7;
  code *pcVar8;
  longlong lVar9;
  code *pcVar10;
  code *pcVar11;
  code *pcVar12;
  code *local_58;
  code *local_50;
  longlong *local_48;
  code *local_40;
  longlong *local_38;
  
  pcVar12 = (code *)0x0;
  pcVar11 = (code *)0x0;
  pcVar10 = (code *)0x0;
  local_48 = (longlong *)0x0;
  local_50 = (code *)0x0;
  local_58 = (code *)0x0;
  plVar3 = (longlong *)FUN_180001f30(DAT_180044978,param_6,1,0);
  if (plVar3 == (longlong *)0x0) {
    DAT_180044938 = DAT_1800433d8;
    DAT_180044930 = 0x87;
    DAT_180044538 = 0x1360;
    pcVar11 = pcVar12;
  }
  else {
    pcVar4 = *(code **)(*(longlong *)(DAT_180044060 + 8) + 0x90);
    if (pcVar4 == (code *)0x0) {
      pcVar4 = *(code **)(*(longlong *)(DAT_180044060 + 8) + 0x40);
      if (pcVar4 == (code *)0x0) {
        pcVar4 = (code *)PyObject_GetAttr();
      }
      else {
        pcVar4 = (code *)(*pcVar4)(DAT_180044060,DAT_180044830 + 0x20);
      }
    }
    else {
      pcVar4 = (code *)(*pcVar4)();
    }
    local_48 = plVar3;
    if (pcVar4 == (code *)0x0) {
      DAT_180044938 = DAT_1800433d8;
      DAT_180044930 = 0x88;
      DAT_180044538 = 0x136c;
    }
    else {
      pcVar11 = pcVar4 + 8;
      pcVar8 = pcVar12;
      if ((*(code **)pcVar11 == PyMethod_Type_exref) &&
         (pcVar8 = *(code **)(pcVar4 + 0x18), pcVar8 != (code *)0x0)) {
        pcVar5 = *(code **)(pcVar4 + 0x10);
        *(longlong *)pcVar8 = *(longlong *)pcVar8 + 1;
        *(longlong *)pcVar5 = *(longlong *)pcVar5 + 1;
        *(longlong *)pcVar4 = *(longlong *)pcVar4 + -1;
        if (*(longlong *)pcVar4 == 0) {
          (**(code **)(*(longlong *)(pcVar4 + 8) + 0x30))();
        }
        pcVar11 = pcVar5 + 8;
        pcVar7 = pcVar12;
        pcVar4 = pcVar5;
        if (*(code **)pcVar11 == PyFunction_Type_exref) {
          local_40 = pcVar8;
          local_38 = plVar3;
          plVar3 = (longlong *)FUN_180001640(pcVar5,&local_40,2);
          if (plVar3 != (longlong *)0x0) {
            *(longlong *)pcVar8 = *(longlong *)pcVar8 + -1;
            if (*(longlong *)pcVar8 == 0) {
              (**(code **)(*(longlong *)(pcVar8 + 8) + 0x30))(pcVar8);
            }
            goto LAB_1800080e0;
          }
          DAT_180044938 = DAT_1800433d8;
          DAT_180044930 = 0x88;
          DAT_180044538 = 0x137f;
          pcVar10 = pcVar12;
        }
        else {
          pcVar10 = (code *)PyTuple_New(2);
          if (pcVar10 == (code *)0x0) {
            DAT_180044938 = DAT_1800433d8;
            DAT_180044930 = 0x88;
            DAT_180044538 = 0x138d;
          }
          else {
            *(code **)(pcVar10 + 0x18) = pcVar8;
            *plVar3 = *plVar3 + 1;
            *(longlong **)(pcVar10 + 0x20) = plVar3;
            pcVar8 = (code *)0x0;
            plVar3 = (longlong *)FUN_1800014a0(pcVar5,pcVar10,0);
            if (plVar3 != (longlong *)0x0) {
              *(longlong *)pcVar10 = *(longlong *)pcVar10 + -1;
              if (*(longlong *)pcVar10 == 0) {
                (**(code **)(*(longlong *)(pcVar10 + 8) + 0x30))(pcVar10);
              }
              goto LAB_1800080e0;
            }
            DAT_180044938 = DAT_1800433d8;
            DAT_180044930 = 0x88;
            DAT_180044538 = 0x1393;
          }
        }
LAB_18000935c:
        if ((pcVar4 != (code *)0x0) &&
           (*(longlong *)pcVar4 = *(longlong *)pcVar4 + -1, *(longlong *)pcVar4 == 0)) {
          (**(code **)(*(longlong *)(pcVar4 + 8) + 0x30))(pcVar4);
        }
LAB_180009376:
        pcVar11 = local_58;
        if ((pcVar8 != (code *)0x0) &&
           (*(longlong *)pcVar8 = *(longlong *)pcVar8 + -1, *(longlong *)pcVar8 == 0)) {
          (**(code **)(*(longlong *)(pcVar8 + 8) + 0x30))(pcVar8);
        }
      }
      else {
        plVar3 = (longlong *)FUN_180001930(pcVar4,plVar3);
        pcVar7 = pcVar8;
        pcVar5 = pcVar4;
        if (plVar3 == (longlong *)0x0) {
          DAT_180044938 = DAT_1800433d8;
          DAT_180044930 = 0x88;
          DAT_180044538 = 0x1379;
          goto LAB_18000935c;
        }
LAB_1800080e0:
        pcVar8 = pcVar7;
        *(longlong *)pcVar5 = *(longlong *)pcVar5 + -1;
        if (*(longlong *)pcVar5 == 0) {
          (**(code **)(*(longlong *)pcVar11 + 0x30))(pcVar5);
        }
        iVar2 = FUN_180003650(0,plVar3);
        if (iVar2 < 0) {
          DAT_180044930 = 0x88;
          DAT_180044538 = 0x1399;
          pcVar4 = pcVar12;
          pcVar10 = pcVar12;
          goto LAB_18000933e;
        }
        *plVar3 = *plVar3 + -1;
        if (*plVar3 == 0) {
          (**(code **)(plVar3[1] + 0x30))(plVar3);
        }
        plVar3 = (longlong *)FUN_180001b00(DAT_180043cf0);
        if (plVar3 == (longlong *)0x0) {
          DAT_180044938 = DAT_1800433d8;
          DAT_180044930 = 0x89;
          DAT_180044538 = 0x13a3;
          pcVar10 = pcVar12;
          local_58 = pcVar12;
          goto LAB_180009376;
        }
        pcVar10 = *(code **)(plVar3[1] + 0x90);
        if (pcVar10 == (code *)0x0) {
          pcVar10 = *(code **)(plVar3[1] + 0x40);
          if (pcVar10 == (code *)0x0) {
            pcVar4 = (code *)PyObject_GetAttr(plVar3);
          }
          else {
            pcVar4 = (code *)(*pcVar10)(plVar3,DAT_180043ec8 + 0x20);
          }
        }
        else {
          pcVar4 = (code *)(*pcVar10)();
        }
        if (pcVar4 == (code *)0x0) {
          DAT_180044930 = 0x89;
          DAT_180044538 = 0x13a5;
          pcVar10 = pcVar12;
          goto LAB_18000933e;
        }
        *plVar3 = *plVar3 + -1;
        if (*plVar3 == 0) {
          (**(code **)(plVar3[1] + 0x30))(plVar3);
        }
        plVar3 = (longlong *)PyDict_New();
        if (plVar3 == (longlong *)0x0) {
          pcVar10 = (code *)0x0;
          DAT_180044938 = DAT_1800433d8;
          DAT_180044930 = 0x89;
          DAT_180044538 = 0x13a8;
          goto LAB_18000935c;
        }
        iVar2 = PyDict_SetItem(plVar3,DAT_180043f08,DAT_180044978);
        if (iVar2 < 0) {
          DAT_180044930 = 0x89;
          pcVar10 = (code *)0x0;
          DAT_180044538 = 0x13aa;
LAB_18000933e:
          DAT_180044938 = DAT_1800433d8;
          *plVar3 = *plVar3 + -1;
          if (*plVar3 == 0) {
            (**(code **)(plVar3[1] + 0x30))(plVar3);
          }
          goto LAB_18000935c;
        }
        iVar2 = PyDict_SetItem(plVar3,DAT_180043d30,DAT_180044978);
        if (iVar2 < 0) {
          DAT_180044930 = 0x89;
          pcVar10 = (code *)0x0;
          DAT_180044538 = 0x13ab;
          goto LAB_18000933e;
        }
        pcVar10 = (code *)FUN_1800014a0(pcVar4,DAT_180044918,plVar3);
        if (pcVar10 == (code *)0x0) {
          DAT_180044930 = 0x89;
          DAT_180044538 = 0x13ac;
          goto LAB_18000933e;
        }
        *(longlong *)pcVar4 = *(longlong *)pcVar4 + -1;
        if (*(longlong *)pcVar4 == 0) {
          (**(code **)(*(longlong *)(pcVar4 + 8) + 0x30))(pcVar4);
        }
        *plVar3 = *plVar3 + -1;
        pcVar4 = (code *)0x0;
        if (*plVar3 == 0) {
          (**(code **)(plVar3[1] + 0x30))(plVar3);
        }
        if (*(code **)(pcVar10 + 8) == PyInt_Type_exref) {
          *(longlong *)pcVar10 = *(longlong *)pcVar10 + 1;
          pcVar5 = pcVar10;
        }
        else {
          pcVar5 = (code *)PyNumber_Int(pcVar10);
        }
        if (pcVar5 == (code *)0x0) {
          DAT_180044938 = DAT_1800433d8;
          DAT_180044930 = 0x89;
          DAT_180044538 = 0x13b0;
          local_58 = (code *)0x0;
          goto LAB_180009376;
        }
        *(longlong *)pcVar10 = *(longlong *)pcVar10 + -1;
        if (*(longlong *)pcVar10 == 0) {
          (**(code **)(*(longlong *)(pcVar10 + 8) + 0x30))(pcVar10);
        }
        plVar3 = (longlong *)FUN_180001b00(DAT_180043cf0);
        local_50 = pcVar5;
        if (plVar3 == (longlong *)0x0) {
          DAT_180044938 = DAT_1800433d8;
          DAT_180044930 = 0x8a;
          DAT_180044538 = 0x13bd;
          pcVar10 = (code *)0x0;
          local_58 = (code *)0x0;
          goto LAB_180009376;
        }
        pcVar10 = *(code **)(plVar3[1] + 0x90);
        if (pcVar10 == (code *)0x0) {
          pcVar10 = *(code **)(plVar3[1] + 0x40);
          if (pcVar10 == (code *)0x0) {
            pcVar10 = (code *)PyObject_GetAttr(plVar3);
          }
          else {
            pcVar10 = (code *)(*pcVar10)(plVar3,DAT_180043ec8 + 0x20);
          }
        }
        else {
          pcVar10 = (code *)(*pcVar10)();
        }
        if (pcVar10 == (code *)0x0) {
          DAT_180044930 = 0x8a;
          DAT_180044538 = 0x13bf;
          goto LAB_18000933e;
        }
        *plVar3 = *plVar3 + -1;
        if (*plVar3 == 0) {
          (**(code **)(plVar3[1] + 0x30))(plVar3);
        }
        plVar3 = (longlong *)PyDict_New();
        if (plVar3 == (longlong *)0x0) {
          DAT_180044938 = DAT_1800433d8;
          DAT_180044930 = 0x8a;
          DAT_180044538 = 0x13c2;
          local_58 = (code *)0x0;
          goto LAB_180009376;
        }
        iVar2 = PyDict_SetItem(plVar3,DAT_180043f08,DAT_180044978);
        if (iVar2 < 0) {
          DAT_180044930 = 0x8a;
          DAT_180044538 = 0x13c4;
          goto LAB_18000933e;
        }
        iVar2 = PyDict_SetItem(plVar3,DAT_180043cb0,DAT_180044978);
        if (iVar2 < 0) {
          DAT_180044930 = 0x8a;
          DAT_180044538 = 0x13c5;
          goto LAB_18000933e;
        }
        pcVar4 = (code *)FUN_1800014a0(pcVar10,DAT_180044918,plVar3);
        if (pcVar4 == (code *)0x0) {
          DAT_180044930 = 0x8a;
          DAT_180044538 = 0x13c6;
          goto LAB_18000933e;
        }
        *(longlong *)pcVar10 = *(longlong *)pcVar10 + -1;
        if (*(longlong *)pcVar10 == 0) {
          (**(code **)(*(longlong *)(pcVar10 + 8) + 0x30))(pcVar10);
        }
        *plVar3 = *plVar3 + -1;
        pcVar10 = (code *)0x0;
        if (*plVar3 == 0) {
          (**(code **)(plVar3[1] + 0x30))(plVar3);
        }
        if (*(code **)(pcVar4 + 8) == PyInt_Type_exref) {
          *(longlong *)pcVar4 = *(longlong *)pcVar4 + 1;
          pcVar11 = pcVar4;
        }
        else {
          pcVar11 = (code *)PyNumber_Int(pcVar4);
        }
        if (pcVar11 == (code *)0x0) {
          DAT_180044938 = DAT_1800433d8;
          DAT_180044930 = 0x8a;
          DAT_180044538 = 0x13ca;
          goto LAB_18000935c;
        }
        *(longlong *)pcVar4 = *(longlong *)pcVar4 + -1;
        if (*(longlong *)pcVar4 == 0) {
          (**(code **)(*(longlong *)(pcVar4 + 8) + 0x30))(pcVar4);
        }
        plVar3 = (longlong *)FUN_180001b00(DAT_180043cf0);
        local_58 = pcVar11;
        if (plVar3 == (longlong *)0x0) {
          DAT_180044938 = DAT_1800433d8;
          DAT_180044930 = 0x8b;
          DAT_180044538 = 0x13d7;
          goto LAB_180009376;
        }
        pcVar4 = *(code **)(plVar3[1] + 0x90);
        if (pcVar4 == (code *)0x0) {
          pcVar4 = *(code **)(plVar3[1] + 0x40);
          if (pcVar4 == (code *)0x0) {
            pcVar4 = (code *)PyObject_GetAttr(plVar3);
          }
          else {
            pcVar4 = (code *)(*pcVar4)(plVar3,DAT_180043f60 + 0x20);
          }
        }
        else {
          pcVar4 = (code *)(*pcVar4)();
        }
        if (pcVar4 == (code *)0x0) {
          DAT_180044930 = 0x8b;
          DAT_180044538 = 0x13d9;
          goto LAB_18000933e;
        }
        *plVar3 = *plVar3 + -1;
        if (*plVar3 == 0) {
          (**(code **)(plVar3[1] + 0x30))(plVar3);
        }
        plVar3 = (longlong *)PyDict_New();
        if (plVar3 == (longlong *)0x0) {
          DAT_180044938 = DAT_1800433d8;
          DAT_180044930 = 0x8b;
          DAT_180044538 = 0x13dc;
          goto LAB_18000935c;
        }
        iVar2 = PyDict_SetItem(plVar3,DAT_180044100,DAT_180044978);
        if (iVar2 < 0) {
          DAT_180044930 = 0x8b;
          DAT_180044538 = 0x13de;
          goto LAB_18000933e;
        }
        plVar6 = (longlong *)FUN_1800014a0(pcVar4,DAT_180044918,plVar3);
        if (plVar6 == (longlong *)0x0) {
          DAT_180044930 = 0x8b;
          DAT_180044538 = 0x13df;
          pcVar10 = (code *)0x0;
          goto LAB_18000933e;
        }
        *(longlong *)pcVar4 = *(longlong *)pcVar4 + -1;
        if (*(longlong *)pcVar4 == 0) {
          (**(code **)(*(longlong *)(pcVar4 + 8) + 0x30))(pcVar4);
        }
        *plVar3 = *plVar3 + -1;
        pcVar4 = (code *)0x0;
        if (*plVar3 == 0) {
          (**(code **)(plVar3[1] + 0x30))(plVar3);
        }
        *plVar6 = *plVar6 + -1;
        if (*plVar6 == 0) {
          (**(code **)(plVar6[1] + 0x30))(plVar6);
        }
        pcVar10 = (code *)FUN_1800020a0(param_6,DAT_180044978,1);
        if (pcVar10 == (code *)0x0) {
          DAT_180044938 = DAT_1800433d8;
          DAT_180044930 = 0x8c;
          DAT_180044538 = 0x13ec;
          goto LAB_180009376;
        }
        iVar2 = FUN_180001000(pcVar10);
        if (iVar2 < 0) {
          DAT_180044938 = DAT_1800433d8;
          DAT_180044930 = 0x8c;
          DAT_180044538 = 0x13ee;
          goto LAB_180009376;
        }
        *(longlong *)pcVar10 = *(longlong *)pcVar10 + -1;
        if (*(longlong *)pcVar10 == 0) {
          (**(code **)(*(longlong *)(pcVar10 + 8) + 0x30))(pcVar10);
        }
        pcVar10 = (code *)0x0;
        pcVar7 = (code *)FUN_180001b00(DAT_180043cf0);
        if (iVar2 != 0) {
          pcVar10 = pcVar7;
          if (pcVar7 == (code *)0x0) {
            DAT_180044938 = DAT_1800433d8;
            DAT_180044930 = 0x8d;
            DAT_180044538 = 0x13f9;
          }
          else {
            pcVar1 = *(code **)(*(longlong *)(pcVar7 + 8) + 0x90);
            if (pcVar1 == (code *)0x0) {
              pcVar1 = *(code **)(*(longlong *)(pcVar7 + 8) + 0x40);
              if (pcVar1 == (code *)0x0) {
                plVar3 = (longlong *)PyObject_GetAttr(pcVar7);
              }
              else {
                plVar3 = (longlong *)(*pcVar1)(pcVar7,DAT_180044548 + 0x20);
              }
            }
            else {
              plVar3 = (longlong *)(*pcVar1)();
            }
            if (plVar3 != (longlong *)0x0) {
              *(longlong *)pcVar7 = *(longlong *)pcVar7 + -1;
              if (*(longlong *)pcVar7 == 0) {
                (**(code **)(*(longlong *)(pcVar7 + 8) + 0x30))(pcVar7);
              }
              pcVar10 = (code *)PyTuple_New(1);
              if (pcVar10 == (code *)0x0) {
                DAT_180044930 = 0x8d;
                DAT_180044538 = 0x13fe;
              }
              else {
                *param_3 = *param_3 + 1;
                *(longlong **)(pcVar10 + 0x18) = param_3;
                pcVar4 = (code *)PyDict_New();
                if (pcVar4 == (code *)0x0) {
                  DAT_180044930 = 0x8d;
                  DAT_180044538 = 0x1403;
                }
                else {
                  iVar2 = PyDict_SetItem(pcVar4,DAT_1800440b0,_Py_ZeroStruct_exref);
                  if (iVar2 < 0) {
                    DAT_180044930 = 0x8d;
                    DAT_180044538 = 0x1405;
                  }
                  else {
                    iVar2 = PyDict_SetItem(pcVar4,DAT_180043d38,_Py_TrueStruct_exref);
                    if (iVar2 < 0) {
                      DAT_180044930 = 0x8d;
                      DAT_180044538 = 0x1406;
                    }
                    else {
                      iVar2 = PyDict_SetItem(pcVar4,DAT_180043f80,_Py_ZeroStruct_exref);
                      if (iVar2 < 0) {
                        DAT_180044930 = 0x8d;
                        DAT_180044538 = 0x140f;
                      }
                      else {
                        iVar2 = PyDict_SetItem(pcVar4,DAT_180043f78,_Py_ZeroStruct_exref);
                        if (iVar2 < 0) {
                          DAT_180044930 = 0x8d;
                          DAT_180044538 = 0x1410;
                        }
                        else {
                          iVar2 = PyDict_SetItem(pcVar4,DAT_180043e48,DAT_180044978);
                          if (iVar2 < 0) {
                            DAT_180044930 = 0x8d;
                            DAT_180044538 = 0x1411;
                          }
                          else {
                            iVar2 = PyDict_SetItem(pcVar4,DAT_180044540,_Py_ZeroStruct_exref);
                            if (iVar2 < 0) {
                              DAT_180044930 = 0x8d;
                              DAT_180044538 = 0x141a;
                            }
                            else {
                              iVar2 = PyDict_SetItem(pcVar4,DAT_180043ee8,_Py_TrueStruct_exref);
                              if (iVar2 < 0) {
                                DAT_180044930 = 0x8d;
                                DAT_180044538 = 0x141b;
                              }
                              else {
                                iVar2 = PyDict_SetItem(pcVar4,DAT_180044068,DAT_180044978);
                                if (iVar2 < 0) {
                                  DAT_180044930 = 0x8d;
                                  DAT_180044538 = 0x141c;
                                }
                                else {
                                  iVar2 = PyDict_SetItem(pcVar4,DAT_180044078,DAT_180044978);
                                  if (iVar2 < 0) {
                                    DAT_180044930 = 0x8d;
                                    DAT_180044538 = 0x141d;
                                  }
                                  else {
                                    iVar2 = PyDict_SetItem(pcVar4,DAT_180043ff8,DAT_180044978);
                                    if (iVar2 < 0) {
                                      DAT_180044930 = 0x8d;
                                      DAT_180044538 = 0x141e;
                                    }
                                    else {
                                      iVar2 = PyDict_SetItem(pcVar4,DAT_180044058,
                                                             _Py_TrueStruct_exref);
                                      if (iVar2 < 0) {
                                        DAT_180044930 = 0x8d;
                                        DAT_180044538 = 0x1427;
                                      }
                                      else {
                                        pcVar8 = (code *)PyTuple_New(2);
                                        if (pcVar8 == (code *)0x0) {
                                          DAT_180044930 = 0x90;
                                          DAT_180044538 = 0x1428;
                                        }
                                        else {
                                          *(longlong *)pcVar5 = *(longlong *)pcVar5 + 1;
                                          *(code **)(pcVar8 + 0x18) = pcVar5;
                                          *(longlong *)pcVar11 = *(longlong *)pcVar11 + 1;
                                          *(code **)(pcVar8 + 0x20) = pcVar11;
                                          iVar2 = PyDict_SetItem(pcVar4,DAT_180044108,pcVar8);
                                          if (iVar2 < 0) {
                                            DAT_180044930 = 0x8d;
                                            DAT_180044538 = 0x1430;
                                          }
                                          else {
                                            *(longlong *)pcVar8 = *(longlong *)pcVar8 + -1;
                                            if (*(longlong *)pcVar8 == 0) {
                                              (**(code **)(*(longlong *)(pcVar8 + 8) + 0x30))
                                                        (pcVar8);
                                            }
                                            pcVar8 = (code *)0x0;
                                            iVar2 = PyDict_SetItem(pcVar4,DAT_1800446c8,
                                                                   _Py_TrueStruct_exref);
                                            if (iVar2 < 0) {
                                              DAT_180044930 = 0x8d;
                                              DAT_180044538 = 0x1432;
                                            }
                                            else {
                                              iVar2 = PyDict_SetItem(pcVar4,DAT_1800445f0,
                                                                     _Py_ZeroStruct_exref);
                                              if (iVar2 < 0) {
                                                DAT_180044930 = 0x8d;
                                                DAT_180044538 = 0x143b;
                                              }
                                              else {
                                                plVar6 = (longlong *)
                                                         FUN_1800014a0(plVar3,pcVar10,pcVar4);
                                                if (plVar6 != (longlong *)0x0) {
                                                  *plVar3 = *plVar3 + -1;
                                                  if (*plVar3 == 0) {
                                                    (**(code **)(plVar3[1] + 0x30))(plVar3);
                                                  }
                                                  *(longlong *)pcVar10 = *(longlong *)pcVar10 + -1;
                                                  if (*(longlong *)pcVar10 == 0) {
                                                    (**(code **)(*(longlong *)(pcVar10 + 8) + 0x30))
                                                              (pcVar10);
                                                  }
                                                  *(longlong *)pcVar4 = *(longlong *)pcVar4 + -1;
                                                  if (*(longlong *)pcVar4 == 0) {
                                                    (**(code **)(*(longlong *)(pcVar4 + 8) + 0x30))
                                                              (pcVar4);
                                                  }
                                                  *plVar6 = *plVar6 + -1;
                                                  if (*plVar6 == 0) {
                                                    lVar9 = plVar6[1];
                                                    goto LAB_18000920b;
                                                  }
                                                  goto LAB_18000920e;
                                                }
                                                DAT_180044930 = 0x8d;
                                                DAT_180044538 = 0x1444;
                                                pcVar8 = (code *)0x0;
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
              goto LAB_18000933e;
            }
            DAT_180044938 = DAT_1800433d8;
            DAT_180044930 = 0x8d;
            DAT_180044538 = 0x13fb;
          }
          goto LAB_180009376;
        }
        if (pcVar7 == (code *)0x0) {
          DAT_180044938 = DAT_1800433d8;
          DAT_180044930 = 0x93;
          DAT_180044538 = 0x145d;
          goto LAB_1800093a1;
        }
        pcVar4 = *(code **)(*(longlong *)(pcVar7 + 8) + 0x90);
        if (pcVar4 == (code *)0x0) {
          pcVar4 = *(code **)(*(longlong *)(pcVar7 + 8) + 0x40);
          if (pcVar4 == (code *)0x0) {
            pcVar4 = (code *)PyObject_GetAttr(pcVar7);
          }
          else {
            pcVar4 = (code *)(*pcVar4)(pcVar7,DAT_180044548 + 0x20);
          }
        }
        else {
          pcVar4 = (code *)(*pcVar4)();
        }
        if (pcVar4 == (code *)0x0) {
          DAT_180044938 = DAT_1800433d8;
          DAT_180044930 = 0x93;
          DAT_180044538 = 0x145f;
          pcVar8 = pcVar7;
          goto LAB_180009376;
        }
        *(longlong *)pcVar7 = *(longlong *)pcVar7 + -1;
        if (*(longlong *)pcVar7 == 0) {
          (**(code **)(*(longlong *)(pcVar7 + 8) + 0x30))(pcVar7);
        }
        pcVar8 = (code *)PyTuple_New(1);
        if (pcVar8 == (code *)0x0) {
          DAT_180044938 = DAT_1800433d8;
          DAT_180044930 = 0x93;
          DAT_180044538 = 0x1462;
          goto LAB_18000935c;
        }
        *param_3 = *param_3 + 1;
        *(longlong **)(pcVar8 + 0x18) = param_3;
        pcVar10 = (code *)PyDict_New();
        if (pcVar10 == (code *)0x0) {
          DAT_180044938 = DAT_1800433d8;
          DAT_180044930 = 0x93;
          DAT_180044538 = 0x1467;
          goto LAB_18000935c;
        }
        iVar2 = PyDict_SetItem(pcVar10,DAT_1800440b0,_Py_ZeroStruct_exref);
        if (iVar2 < 0) {
          DAT_180044938 = DAT_1800433d8;
          DAT_180044930 = 0x93;
          DAT_180044538 = 0x1469;
          goto LAB_18000935c;
        }
        iVar2 = PyDict_SetItem(pcVar10,DAT_180043d38,_Py_TrueStruct_exref);
        if (iVar2 < 0) {
          DAT_180044938 = DAT_1800433d8;
          DAT_180044930 = 0x93;
          DAT_180044538 = 0x146a;
          goto LAB_18000935c;
        }
        iVar2 = PyDict_SetItem(pcVar10,DAT_180043f80,_Py_ZeroStruct_exref);
        if (iVar2 < 0) {
          DAT_180044938 = DAT_1800433d8;
          DAT_180044930 = 0x93;
          DAT_180044538 = 0x1473;
          goto LAB_18000935c;
        }
        iVar2 = PyDict_SetItem(pcVar10,DAT_180043f78,_Py_ZeroStruct_exref);
        if (iVar2 < 0) {
          DAT_180044938 = DAT_1800433d8;
          DAT_180044930 = 0x93;
          DAT_180044538 = 0x1474;
          goto LAB_18000935c;
        }
        iVar2 = PyDict_SetItem(pcVar10,DAT_180043e48,DAT_180044978);
        if (iVar2 < 0) {
          DAT_180044938 = DAT_1800433d8;
          DAT_180044930 = 0x93;
          DAT_180044538 = 0x1475;
          goto LAB_18000935c;
        }
        iVar2 = PyDict_SetItem(pcVar10,DAT_180044540,_Py_ZeroStruct_exref);
        if (iVar2 < 0) {
          DAT_180044938 = DAT_1800433d8;
          DAT_180044930 = 0x93;
          DAT_180044538 = 0x147e;
          goto LAB_18000935c;
        }
        iVar2 = PyDict_SetItem(pcVar10,DAT_180043ee8,_Py_TrueStruct_exref);
        if (iVar2 < 0) {
          DAT_180044938 = DAT_1800433d8;
          DAT_180044930 = 0x93;
          DAT_180044538 = 0x147f;
          goto LAB_18000935c;
        }
        iVar2 = PyDict_SetItem(pcVar10,DAT_180044068,DAT_180044978);
        if (iVar2 < 0) {
          DAT_180044938 = DAT_1800433d8;
          DAT_180044930 = 0x93;
          DAT_180044538 = 0x1480;
          goto LAB_18000935c;
        }
        iVar2 = PyDict_SetItem(pcVar10,DAT_180043ff8,DAT_180044978);
        if (iVar2 < 0) {
          DAT_180044938 = DAT_1800433d8;
          DAT_180044930 = 0x93;
          DAT_180044538 = 0x1481;
          goto LAB_18000935c;
        }
        iVar2 = PyDict_SetItem(pcVar10,DAT_180044058,_Py_TrueStruct_exref);
        if (iVar2 < 0) {
          DAT_180044938 = DAT_1800433d8;
          DAT_180044930 = 0x93;
          DAT_180044538 = 0x148a;
          goto LAB_18000935c;
        }
        plVar3 = (longlong *)PyTuple_New(2);
        if (plVar3 == (longlong *)0x0) {
          DAT_180044938 = DAT_1800433d8;
          DAT_180044930 = 0x96;
          DAT_180044538 = 0x148b;
          goto LAB_18000935c;
        }
        *(longlong *)pcVar5 = *(longlong *)pcVar5 + 1;
        plVar3[3] = (longlong)pcVar5;
        *(longlong *)pcVar11 = *(longlong *)pcVar11 + 1;
        plVar3[4] = (longlong)pcVar11;
        iVar2 = PyDict_SetItem(pcVar10,DAT_180044108,plVar3);
        if (iVar2 < 0) {
          DAT_180044930 = 0x93;
          DAT_180044538 = 0x1493;
          goto LAB_18000933e;
        }
        *plVar3 = *plVar3 + -1;
        if (*plVar3 == 0) {
          (**(code **)(plVar3[1] + 0x30))(plVar3);
        }
        iVar2 = PyDict_SetItem(pcVar10,DAT_1800446c8,_Py_TrueStruct_exref);
        if (iVar2 < 0) {
          DAT_180044938 = DAT_1800433d8;
          DAT_180044930 = 0x93;
          DAT_180044538 = 0x1495;
          goto LAB_18000935c;
        }
        iVar2 = PyDict_SetItem(pcVar10,DAT_1800445f0,_Py_ZeroStruct_exref);
        if (iVar2 < 0) {
          DAT_180044938 = DAT_1800433d8;
          DAT_180044930 = 0x93;
          DAT_180044538 = 0x149e;
          goto LAB_18000935c;
        }
        plVar6 = (longlong *)FUN_1800014a0(pcVar4,pcVar8,pcVar10);
        if (plVar6 == (longlong *)0x0) {
          DAT_180044938 = DAT_1800433d8;
          DAT_180044930 = 0x93;
          DAT_180044538 = 0x14a7;
          goto LAB_18000935c;
        }
        *(longlong *)pcVar4 = *(longlong *)pcVar4 + -1;
        if (*(longlong *)pcVar4 == 0) {
          (**(code **)(*(longlong *)(pcVar4 + 8) + 0x30))(pcVar4);
        }
        *(longlong *)pcVar8 = *(longlong *)pcVar8 + -1;
        if (*(longlong *)pcVar8 == 0) {
          (**(code **)(*(longlong *)(pcVar8 + 8) + 0x30))(pcVar8);
        }
        *(longlong *)pcVar10 = *(longlong *)pcVar10 + -1;
        if (*(longlong *)pcVar10 == 0) {
          (**(code **)(*(longlong *)(pcVar10 + 8) + 0x30))(pcVar10);
        }
        *plVar6 = *plVar6 + -1;
        if (*plVar6 == 0) {
          lVar9 = plVar6[1];
LAB_18000920b:
          (**(code **)(lVar9 + 0x30))(plVar6);
        }
LAB_18000920e:
        plVar3 = (longlong *)FUN_180001b00(DAT_180043cf0);
        if (plVar3 == (longlong *)0x0) {
          DAT_180044938 = DAT_1800433d8;
          DAT_180044930 = 0x99;
          DAT_180044538 = 0x14b7;
          goto LAB_1800093a1;
        }
        pcVar10 = *(code **)(plVar3[1] + 0x90);
        if (pcVar10 == (code *)0x0) {
          pcVar10 = *(code **)(plVar3[1] + 0x40);
          if (pcVar10 == (code *)0x0) {
            pcVar10 = (code *)PyObject_GetAttr(plVar3);
          }
          else {
            pcVar10 = (code *)(*pcVar10)(plVar3,DAT_180043f60 + 0x20);
          }
        }
        else {
          pcVar10 = (code *)(*pcVar10)();
        }
        if (pcVar10 == (code *)0x0) {
          DAT_180044538 = 0x14b9;
LAB_180009331:
          pcVar8 = (code *)0x0;
          DAT_180044930 = 0x99;
          pcVar4 = (code *)0x0;
          goto LAB_18000933e;
        }
        *plVar3 = *plVar3 + -1;
        if (*plVar3 == 0) {
          (**(code **)(plVar3[1] + 0x30))(plVar3);
        }
        plVar3 = (longlong *)PyDict_New();
        if (plVar3 != (longlong *)0x0) {
          iVar2 = PyDict_SetItem(plVar3,DAT_180044100,DAT_180044970);
          if (iVar2 < 0) {
            DAT_180044538 = 0x14be;
          }
          else {
            plVar6 = (longlong *)FUN_1800014a0(pcVar10,DAT_180044918,plVar3);
            if (plVar6 != (longlong *)0x0) {
              *(longlong *)pcVar10 = *(longlong *)pcVar10 + -1;
              if (*(longlong *)pcVar10 == 0) {
                (**(code **)(*(longlong *)(pcVar10 + 8) + 0x30))(pcVar10);
              }
              *plVar3 = *plVar3 + -1;
              if (*plVar3 == 0) {
                (**(code **)(plVar3[1] + 0x30))(plVar3);
              }
              *plVar6 = *plVar6 + -1;
              if (*plVar6 == 0) {
                (**(code **)(plVar6[1] + 0x30))(plVar6);
              }
              pcVar12 = _Py_NoneStruct_exref;
              *(longlong *)_Py_NoneStruct_exref = *(longlong *)_Py_NoneStruct_exref + 1;
              goto LAB_180009403;
            }
            DAT_180044538 = 0x14bf;
          }
          goto LAB_180009331;
        }
        DAT_180044938 = DAT_1800433d8;
        DAT_180044930 = 0x99;
        DAT_180044538 = 0x14bc;
      }
      if ((pcVar10 != (code *)0x0) &&
         (*(longlong *)pcVar10 = *(longlong *)pcVar10 + -1, *(longlong *)pcVar10 == 0)) {
        (**(code **)(*(longlong *)(pcVar10 + 8) + 0x30))(pcVar10);
      }
    }
  }
LAB_1800093a1:
  FUN_180003390(s_tvTools__CombineScenes__core_fun_18003c9a8,DAT_180044538,DAT_180044930,
                DAT_180044938);
  pcVar5 = local_50;
LAB_180009403:
  if ((local_48 != (longlong *)0x0) && (*local_48 = *local_48 + -1, *local_48 == 0)) {
    (**(code **)(local_48[1] + 0x30))();
  }
  if ((pcVar5 != (code *)0x0) &&
     (*(longlong *)pcVar5 = *(longlong *)pcVar5 + -1, *(longlong *)pcVar5 == 0)) {
    (**(code **)(*(longlong *)(pcVar5 + 8) + 0x30))(pcVar5);
  }
  if ((pcVar11 != (code *)0x0) &&
     (*(longlong *)pcVar11 = *(longlong *)pcVar11 + -1, *(longlong *)pcVar11 == 0)) {
    (**(code **)(*(longlong *)(pcVar11 + 8) + 0x30))(pcVar11);
  }
  return pcVar12;
}

