
code * FUN_180002b80(void)

{
  code *pcVar1;
  longlong *plVar2;
  undefined8 uVar3;
  int iVar4;
  code *pcVar5;
  code *pcVar6;
  code *pcVar7;
  longlong *plVar8;
  longlong *plVar9;
  longlong *plVar10;
  longlong lVar11;
  code *pcVar12;
  code *pcVar13;
  code *pcVar14;
  longlong *plVar15;
  code *pcVar16;
  code *pcVar17;
  code *pcVar18;
  longlong *plVar19;
  code *local_48 [2];
  
  uVar3 = DAT_18000cb68;
  pcVar16 = (code *)0x0;
  pcVar13 = (code *)0x0;
  pcVar12 = (code *)0x0;
  pcVar17 = (code *)0x0;
  pcVar18 = (code *)0x0;
  pcVar5 = (code *)PyDict_GetItem(DAT_18000cc20,DAT_18000cb68);
  if (pcVar5 == (code *)0x0) {
    pcVar5 = (code *)FUN_180001070(uVar3);
  }
  else {
    *(longlong *)pcVar5 = *(longlong *)pcVar5 + 1;
  }
  if (pcVar5 == (code *)0x0) {
    DAT_18000cc50 = DAT_18000c6c8;
    DAT_18000cc14 = 0x1d;
    DAT_18000cc10 = 0x498;
    pcVar13 = pcVar16;
  }
  else {
    pcVar6 = *(code **)(*(longlong *)(pcVar5 + 8) + 0x90);
    if (pcVar6 == (code *)0x0) {
      pcVar6 = *(code **)(*(longlong *)(pcVar5 + 8) + 0x40);
      if (pcVar6 == (code *)0x0) {
        pcVar6 = (code *)PyObject_GetAttr(pcVar5);
      }
      else {
        pcVar6 = (code *)(*pcVar6)(pcVar5,DAT_18000cb20 + 0x20);
      }
    }
    else {
      pcVar6 = (code *)(*pcVar6)();
    }
    if (pcVar6 == (code *)0x0) {
      DAT_18000cc50 = DAT_18000c6c8;
      DAT_18000cc14 = 0x1d;
      DAT_18000cc10 = 0x49a;
      pcVar12 = pcVar16;
      pcVar13 = pcVar16;
      pcVar17 = pcVar16;
      pcVar18 = pcVar16;
    }
    else {
      *(longlong *)pcVar5 = *(longlong *)pcVar5 + -1;
      if (*(longlong *)pcVar5 == 0) {
        (**(code **)(*(longlong *)(pcVar5 + 8) + 0x30))(pcVar5);
      }
      pcVar5 = pcVar16;
      if ((*(code **)(pcVar6 + 8) == PyMethod_Type_exref) &&
         (pcVar1 = *(code **)(pcVar6 + 0x18), pcVar5 = pcVar1, pcVar1 != (code *)0x0)) {
        pcVar14 = *(code **)(pcVar6 + 0x10);
        *(longlong *)pcVar1 = *(longlong *)pcVar1 + 1;
        *(longlong *)pcVar14 = *(longlong *)pcVar14 + 1;
        *(longlong *)pcVar6 = *(longlong *)pcVar6 + -1;
        if (*(longlong *)pcVar6 == 0) {
          (**(code **)(*(longlong *)(pcVar6 + 8) + 0x30))();
        }
        pcVar7 = (code *)FUN_1800014f0(pcVar14,pcVar1);
        if (pcVar7 == (code *)0x0) {
          DAT_18000cc50 = DAT_18000c6c8;
          DAT_18000cc14 = 0x1d;
          DAT_18000cc10 = 0x4a8;
          pcVar6 = pcVar14;
        }
        else {
          *(longlong *)pcVar1 = *(longlong *)pcVar1 + -1;
          pcVar5 = pcVar16;
          if (*(longlong *)pcVar1 == 0) {
            (**(code **)(*(longlong *)(pcVar1 + 8) + 0x30))(pcVar1);
          }
LAB_180002d0f:
          pcVar13 = pcVar7;
          *(longlong *)pcVar14 = *(longlong *)pcVar14 + -1;
          if (*(longlong *)pcVar14 == 0) {
            (**(code **)(*(longlong *)(pcVar14 + 8) + 0x30))(pcVar14);
          }
          uVar3 = DAT_18000cbe8;
          plVar8 = (longlong *)PyDict_GetItem(DAT_18000cc20,DAT_18000cbe8);
          if (plVar8 == (longlong *)0x0) {
            plVar8 = (longlong *)FUN_180001070(uVar3);
          }
          else {
            *plVar8 = *plVar8 + 1;
          }
          if (plVar8 == (longlong *)0x0) {
            DAT_18000cc14 = 0x1e;
            DAT_18000cc10 = 0x4b9;
            pcVar12 = pcVar16;
            pcVar6 = pcVar16;
            pcVar17 = pcVar16;
            pcVar18 = pcVar16;
LAB_18000319c:
            DAT_18000cc50 = DAT_18000c6c8;
          }
          else {
            pcVar6 = *(code **)(plVar8[1] + 0x90);
            if (pcVar6 == (code *)0x0) {
              pcVar6 = *(code **)(plVar8[1] + 0x40);
              if (pcVar6 == (code *)0x0) {
                pcVar6 = (code *)PyObject_GetAttr(plVar8);
              }
              else {
                pcVar6 = (code *)(*pcVar6)(plVar8,DAT_18000cc00 + 0x20);
              }
            }
            else {
              pcVar6 = (code *)(*pcVar6)();
            }
            if (pcVar6 == (code *)0x0) {
              DAT_18000cc14 = 0x1e;
              DAT_18000cc10 = 0x4bb;
              goto LAB_18000319c;
            }
            *plVar8 = *plVar8 + -1;
            if (*plVar8 == 0) {
              (**(code **)(plVar8[1] + 0x30))(plVar8);
            }
            pcVar1 = *(code **)(*(longlong *)(pcVar6 + 8) + 0x90);
            if (pcVar1 == (code *)0x0) {
              pcVar1 = *(code **)(*(longlong *)(pcVar6 + 8) + 0x40);
              if (pcVar1 == (code *)0x0) {
                plVar8 = (longlong *)PyObject_GetAttr(pcVar6);
              }
              else {
                plVar8 = (longlong *)(*pcVar1)(pcVar6,DAT_18000cb30 + 0x20);
              }
            }
            else {
              plVar8 = (longlong *)(*pcVar1)();
            }
            if (plVar8 == (longlong *)0x0) {
              DAT_18000cc50 = DAT_18000c6c8;
              DAT_18000cc14 = 0x1e;
              DAT_18000cc10 = 0x4be;
              goto LAB_1800031c7;
            }
            *(longlong *)pcVar6 = *(longlong *)pcVar6 + -1;
            if (*(longlong *)pcVar6 == 0) {
              (**(code **)(*(longlong *)(pcVar6 + 8) + 0x30))(pcVar6);
            }
            pcVar6 = (code *)PyObject_RichCompare(plVar8,DAT_18000cc70,5);
            if (pcVar6 == (code *)0x0) {
              DAT_18000cc14 = 0x1e;
              DAT_18000cc10 = 0x4c1;
              goto LAB_18000319c;
            }
            *plVar8 = *plVar8 + -1;
            if (*plVar8 == 0) {
              (**(code **)(plVar8[1] + 0x30))(plVar8);
            }
            iVar4 = FUN_180001000(pcVar6);
            if (iVar4 < 0) {
              DAT_18000cc50 = DAT_18000c6c8;
              DAT_18000cc14 = 0x1e;
              DAT_18000cc10 = 0x4c3;
              goto LAB_1800031c7;
            }
            *(longlong *)pcVar6 = *(longlong *)pcVar6 + -1;
            if (*(longlong *)pcVar6 == 0) {
              (**(code **)(*(longlong *)(pcVar6 + 8) + 0x30))(pcVar6);
            }
            pcVar6 = (code *)0x0;
            if (iVar4 == 0) {
              lVar11 = *(longlong *)_PyThreadState_Current_exref;
              plVar8 = *(longlong **)(lVar11 + 0x60);
              plVar9 = *(longlong **)(lVar11 + 0x68);
              plVar2 = *(longlong **)(lVar11 + 0x70);
              if (plVar8 != (longlong *)0x0) {
                *plVar8 = *plVar8 + 1;
              }
              if (plVar9 != (longlong *)0x0) {
                *plVar9 = *plVar9 + 1;
              }
              if (plVar2 != (longlong *)0x0) {
                *plVar2 = *plVar2 + 1;
              }
              plVar19 = plVar9;
              plVar10 = (longlong *)FUN_1800010f0(DAT_18000cc08);
              plVar15 = plVar10;
              pcVar18 = pcVar16;
              if (plVar10 == (longlong *)0x0) {
                DAT_18000cc10 = 0x52f;
                pcVar12 = pcVar16;
              }
              else {
                if (*(code **)(pcVar13 + 8) == PyInt_Type_exref) {
                  *(longlong *)pcVar13 = *(longlong *)pcVar13 + 1;
                  pcVar17 = pcVar13;
                }
                else {
                  pcVar17 = (code *)PyNumber_Int(pcVar13);
                }
                if (pcVar17 == (code *)0x0) {
                  DAT_18000cc10 = 0x531;
                  pcVar12 = pcVar16;
                  pcVar16 = pcVar17;
                }
                else {
                  pcVar18 = (code *)FUN_1800010f0(DAT_18000caa8);
                  if (pcVar18 == (code *)0x0) {
                    DAT_18000cc10 = 0x533;
                    pcVar16 = pcVar17;
                  }
                  else {
                    pcVar5 = *(code **)(*(longlong *)(pcVar18 + 8) + 0x90);
                    if (pcVar5 == (code *)0x0) {
                      pcVar5 = *(code **)(*(longlong *)(pcVar18 + 8) + 0x40);
                      if (pcVar5 == (code *)0x0) {
                        pcVar5 = (code *)PyObject_GetAttr(pcVar18);
                      }
                      else {
                        pcVar5 = (code *)(*pcVar5)(pcVar18,DAT_18000ca68 + 0x20);
                      }
                    }
                    else {
                      pcVar5 = (code *)(*pcVar5)();
                    }
                    if (pcVar5 == (code *)0x0) {
                      DAT_18000cc10 = 0x535;
                      pcVar16 = pcVar17;
                    }
                    else {
                      *(longlong *)pcVar18 = *(longlong *)pcVar18 + -1;
                      if (*(longlong *)pcVar18 == 0) {
                        (**(code **)(*(longlong *)(pcVar18 + 8) + 0x30))(pcVar18);
                      }
                      pcVar6 = pcVar16;
                      pcVar18 = pcVar16;
                      if (((code *)plVar10[1] == PyMethod_Type_exref) &&
                         (pcVar18 = (code *)plVar10[3], pcVar6 = (code *)0x0, pcVar18 != (code *)0x0
                         )) {
                        plVar15 = (longlong *)plVar10[2];
                        *(longlong *)pcVar18 = *(longlong *)pcVar18 + 1;
                        *plVar15 = *plVar15 + 1;
                        *plVar10 = *plVar10 + -1;
                        if (*plVar10 == 0) {
                          (**(code **)(plVar10[1] + 0x30))();
                        }
                        pcVar6 = (code *)0x1;
                      }
                      iVar4 = (int)pcVar6;
                      if ((code *)plVar15[1] == PyFunction_Type_exref) {
                        local_48[0] = pcVar17;
                        local_48[1] = pcVar5;
                        pcVar6 = (code *)FUN_180001130(plVar15,local_48 + -(longlong)pcVar6,
                                                       iVar4 + 2,0,plVar19,pcVar18);
                        if (pcVar6 != (code *)0x0) {
                          if ((pcVar18 != (code *)0x0) &&
                             (*(longlong *)pcVar18 = *(longlong *)pcVar18 + -1,
                             *(longlong *)pcVar18 == 0)) {
                            (**(code **)(*(longlong *)(pcVar18 + 8) + 0x30))(pcVar18);
                          }
                          *(longlong *)pcVar17 = *(longlong *)pcVar17 + -1;
                          if (*(longlong *)pcVar17 == 0) {
                            (**(code **)(*(longlong *)(pcVar17 + 8) + 0x30))(pcVar17);
                          }
                          *(longlong *)pcVar5 = *(longlong *)pcVar5 + -1;
                          if (*(longlong *)pcVar5 == 0) {
                            lVar11 = *(longlong *)(pcVar5 + 8);
                            pcVar12 = pcVar5;
LAB_1800035b4:
                            (**(code **)(lVar11 + 0x30))(pcVar12);
                          }
LAB_1800035b7:
                          *plVar15 = *plVar15 + -1;
                          if (*plVar15 == 0) {
                            (**(code **)(plVar15[1] + 0x30))(plVar15);
                          }
                          FUN_180001700(*(undefined8 *)_PyThreadState_Current_exref,plVar8,plVar9,
                                        plVar2);
                          goto LAB_1800035f1;
                        }
                        DAT_18000cc10 = 0x547;
                        pcVar16 = pcVar17;
                      }
                      else {
                        pcVar12 = (code *)PyTuple_New(iVar4 + 2);
                        if (pcVar12 == (code *)0x0) {
                          DAT_18000cc10 = 0x559;
                          pcVar16 = pcVar17;
                        }
                        else {
                          if (pcVar18 != (code *)0x0) {
                            *(code **)(pcVar12 + 0x18) = pcVar18;
                            pcVar18 = pcVar16;
                          }
                          *(code **)(pcVar12 + (longlong)pcVar6 * 8 + 0x18) = pcVar17;
                          *(code **)(pcVar12 + (ulonglong)(iVar4 + 1) * 8 + 0x18) = pcVar5;
                          pcVar5 = (code *)0x0;
                          pcVar6 = (code *)FUN_180001360(plVar15,pcVar12,0);
                          if (pcVar6 != (code *)0x0) {
                            *(longlong *)pcVar12 = *(longlong *)pcVar12 + -1;
                            if (*(longlong *)pcVar12 == 0) {
                              lVar11 = *(longlong *)(pcVar12 + 8);
                              goto LAB_1800035b4;
                            }
                            goto LAB_1800035b7;
                          }
                          DAT_18000cc10 = 0x564;
                        }
                      }
                    }
                  }
                }
              }
              DAT_18000cc14 = 0x22;
              uVar3 = *(undefined8 *)_PyThreadState_Current_exref;
              DAT_18000cc50 = DAT_18000c6c8;
              if ((pcVar18 != (code *)0x0) &&
                 (*(longlong *)pcVar18 = *(longlong *)pcVar18 + -1, *(longlong *)pcVar18 == 0)) {
                (**(code **)(*(longlong *)(pcVar18 + 8) + 0x30))(pcVar18);
              }
              if ((pcVar16 != (code *)0x0) &&
                 (*(longlong *)pcVar16 = *(longlong *)pcVar16 + -1, *(longlong *)pcVar16 == 0)) {
                (**(code **)(*(longlong *)(pcVar16 + 8) + 0x30))(pcVar16);
              }
              if ((pcVar5 != (code *)0x0) &&
                 (*(longlong *)pcVar5 = *(longlong *)pcVar5 + -1, *(longlong *)pcVar5 == 0)) {
                (**(code **)(*(longlong *)(pcVar5 + 8) + 0x30))(pcVar5);
              }
              if ((pcVar12 != (code *)0x0) &&
                 (*(longlong *)pcVar12 = *(longlong *)pcVar12 + -1, *(longlong *)pcVar12 == 0)) {
                (**(code **)(*(longlong *)(pcVar12 + 8) + 0x30))(pcVar12);
              }
              if ((plVar15 != (longlong *)0x0) && (*plVar15 = *plVar15 + -1, *plVar15 == 0)) {
                (**(code **)(plVar15[1] + 0x30))(plVar15);
              }
              FUN_180001780(uVar3,0,0,0);
              FUN_180001700(*(undefined8 *)_PyThreadState_Current_exref,plVar8,plVar19,plVar2);
              pcVar6 = _Py_NoneStruct_exref;
              *(longlong *)_Py_NoneStruct_exref = *(longlong *)_Py_NoneStruct_exref + 1;
              goto LAB_1800035f1;
            }
            plVar9 = (longlong *)FUN_1800010f0(DAT_18000cc08);
            if (plVar9 == (longlong *)0x0) {
              DAT_18000cc50 = DAT_18000c6c8;
              DAT_18000cc14 = 0x1f;
              DAT_18000cc10 = 0x4cf;
              goto LAB_1800031c7;
            }
            if (*(code **)(pcVar13 + 8) == PyInt_Type_exref) {
              *(longlong *)pcVar13 = *(longlong *)pcVar13 + 1;
              pcVar5 = pcVar13;
            }
            else {
              pcVar5 = (code *)PyNumber_Int(pcVar13);
            }
            plVar8 = plVar9;
            if (pcVar5 == (code *)0x0) {
              DAT_18000cc10 = 0x4d1;
              pcVar12 = pcVar16;
              pcVar17 = pcVar16;
              pcVar18 = pcVar16;
LAB_180003192:
              pcVar6 = (code *)0x0;
              DAT_18000cc14 = 0x1f;
              goto LAB_18000319c;
            }
            pcVar12 = (code *)FUN_1800010f0(DAT_18000caa8);
            if (pcVar12 != (code *)0x0) {
              pcVar17 = *(code **)(*(longlong *)(pcVar12 + 8) + 0x90);
              if (pcVar17 == (code *)0x0) {
                pcVar17 = *(code **)(*(longlong *)(pcVar12 + 8) + 0x40);
                if (pcVar17 == (code *)0x0) {
                  pcVar17 = (code *)PyObject_GetAttr(pcVar12);
                }
                else {
                  pcVar17 = (code *)(*pcVar17)(pcVar12,DAT_18000ca68 + 0x20);
                }
              }
              else {
                pcVar17 = (code *)(*pcVar17)();
              }
              if (pcVar17 == (code *)0x0) {
                DAT_18000cc10 = 0x4d5;
              }
              else {
                *(longlong *)pcVar12 = *(longlong *)pcVar12 + -1;
                if (*(longlong *)pcVar12 == 0) {
                  (**(code **)(*(longlong *)(pcVar12 + 8) + 0x30))(pcVar12);
                }
                pcVar12 = pcVar16;
                pcVar6 = pcVar16;
                if (((code *)plVar9[1] == PyMethod_Type_exref) &&
                   (pcVar12 = (code *)plVar9[3], pcVar6 = (code *)0x0, pcVar12 != (code *)0x0)) {
                  plVar8 = (longlong *)plVar9[2];
                  *(longlong *)pcVar12 = *(longlong *)pcVar12 + 1;
                  *plVar8 = *plVar8 + 1;
                  *plVar9 = *plVar9 + -1;
                  if (*plVar9 == 0) {
                    (**(code **)(plVar9[1] + 0x30))();
                  }
                  pcVar6 = (code *)0x1;
                }
                iVar4 = (int)pcVar6;
                if ((code *)plVar8[1] == PyFunction_Type_exref) {
                  local_48[0] = pcVar5;
                  local_48[1] = pcVar17;
                  pcVar6 = (code *)FUN_180001130(plVar8,local_48 + -(longlong)pcVar6,iVar4 + 2,0);
                  if (pcVar6 != (code *)0x0) {
                    if ((pcVar12 != (code *)0x0) &&
                       (*(longlong *)pcVar12 = *(longlong *)pcVar12 + -1, *(longlong *)pcVar12 == 0)
                       ) {
                      (**(code **)(*(longlong *)(pcVar12 + 8) + 0x30))(pcVar12);
                    }
                    *(longlong *)pcVar5 = *(longlong *)pcVar5 + -1;
                    if (*(longlong *)pcVar5 == 0) {
                      (**(code **)(*(longlong *)(pcVar5 + 8) + 0x30))(pcVar5);
                    }
                    *(longlong *)pcVar17 = *(longlong *)pcVar17 + -1;
                    if (*(longlong *)pcVar17 == 0) {
                      lVar11 = *(longlong *)(pcVar17 + 8);
                      pcVar18 = pcVar17;
LAB_180003263:
                      (**(code **)(lVar11 + 0x30))(pcVar18);
                    }
LAB_180003266:
                    *plVar8 = *plVar8 + -1;
                    if (*plVar8 == 0) {
                      (**(code **)(plVar8[1] + 0x30))(plVar8);
                    }
                    goto LAB_1800035f1;
                  }
                  DAT_18000cc10 = 0x4e7;
                }
                else {
                  pcVar18 = (code *)PyTuple_New(iVar4 + 2);
                  if (pcVar18 == (code *)0x0) {
                    DAT_18000cc50 = DAT_18000c6c8;
                    DAT_18000cc14 = 0x1f;
                    DAT_18000cc10 = 0x4f9;
                    pcVar6 = pcVar16;
                    goto LAB_1800031aa;
                  }
                  if (pcVar12 != (code *)0x0) {
                    *(code **)(pcVar18 + 0x18) = pcVar12;
                    pcVar12 = pcVar16;
                  }
                  *(code **)(pcVar18 + (longlong)pcVar6 * 8 + 0x18) = pcVar5;
                  *(code **)(pcVar18 + (ulonglong)(iVar4 + 1) * 8 + 0x18) = pcVar17;
                  pcVar17 = (code *)0x0;
                  pcVar6 = (code *)FUN_180001360(plVar8,pcVar18,0);
                  if (pcVar6 != (code *)0x0) {
                    *(longlong *)pcVar18 = *(longlong *)pcVar18 + -1;
                    if (*(longlong *)pcVar18 == 0) {
                      lVar11 = *(longlong *)(pcVar18 + 8);
                      goto LAB_180003263;
                    }
                    goto LAB_180003266;
                  }
                  DAT_18000cc10 = 0x504;
                  pcVar5 = pcVar16;
                }
              }
              goto LAB_180003192;
            }
            DAT_18000cc50 = DAT_18000c6c8;
            DAT_18000cc14 = 0x1f;
            DAT_18000cc10 = 0x4d3;
            pcVar6 = pcVar16;
            pcVar17 = pcVar16;
            pcVar18 = pcVar16;
          }
LAB_1800031aa:
          DAT_18000c6c8 = DAT_18000cc50;
          if ((plVar8 != (longlong *)0x0) && (*plVar8 = *plVar8 + -1, *plVar8 == 0)) {
            (**(code **)(plVar8[1] + 0x30))(plVar8);
          }
        }
      }
      else {
        pcVar7 = (code *)FUN_180001640(pcVar6);
        pcVar14 = pcVar6;
        if (pcVar7 != (code *)0x0) goto LAB_180002d0f;
        DAT_18000cc50 = DAT_18000c6c8;
        DAT_18000cc14 = 0x1d;
        DAT_18000cc10 = 0x4ab;
      }
    }
LAB_1800031c7:
    if ((pcVar5 != (code *)0x0) &&
       (*(longlong *)pcVar5 = *(longlong *)pcVar5 + -1, *(longlong *)pcVar5 == 0)) {
      (**(code **)(*(longlong *)(pcVar5 + 8) + 0x30))(pcVar5);
    }
    if ((pcVar6 != (code *)0x0) &&
       (*(longlong *)pcVar6 = *(longlong *)pcVar6 + -1, *(longlong *)pcVar6 == 0)) {
      (**(code **)(*(longlong *)(pcVar6 + 8) + 0x30))(pcVar6);
    }
    if ((pcVar12 != (code *)0x0) &&
       (*(longlong *)pcVar12 = *(longlong *)pcVar12 + -1, *(longlong *)pcVar12 == 0)) {
      (**(code **)(*(longlong *)(pcVar12 + 8) + 0x30))(pcVar12);
    }
    if ((pcVar17 != (code *)0x0) &&
       (*(longlong *)pcVar17 = *(longlong *)pcVar17 + -1, *(longlong *)pcVar17 == 0)) {
      (**(code **)(*(longlong *)(pcVar17 + 8) + 0x30))(pcVar17);
    }
    if ((pcVar18 != (code *)0x0) &&
       (*(longlong *)pcVar18 = *(longlong *)pcVar18 + -1, *(longlong *)pcVar18 == 0)) {
      (**(code **)(*(longlong *)(pcVar18 + 8) + 0x30))(pcVar18);
    }
  }
  FUN_1800028e0(s_tvTools__CombineScenes_cbSingleT_18000c770,DAT_18000cc10,DAT_18000cc14,
                DAT_18000cc50);
  pcVar6 = pcVar16;
LAB_1800035f1:
  if ((pcVar13 != (code *)0x0) &&
     (*(longlong *)pcVar13 = *(longlong *)pcVar13 + -1, *(longlong *)pcVar13 == 0)) {
    (**(code **)(*(longlong *)(pcVar13 + 8) + 0x30))(pcVar13);
  }
  return pcVar6;
}

