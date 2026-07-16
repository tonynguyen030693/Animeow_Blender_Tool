
code * FUN_180002cb0(longlong param_1,code *param_2,longlong *param_3,longlong *param_4,
                    code *param_5)

{
  longlong lVar1;
  size_t sVar2;
  longlong *plVar3;
  undefined8 uVar4;
  uint uVar5;
  int iVar6;
  longlong *plVar7;
  code *pcVar8;
  code *pcVar9;
  longlong *plVar10;
  code *pcVar11;
  code *pcVar12;
  longlong *plVar13;
  code *pcVar14;
  code *pcVar15;
  code *pcVar16;
  code *pcVar17;
  code *pcVar18;
  code *local_res8;
  code *local_res10;
  longlong *local_res18;
  longlong *local_res20;
  longlong *local_e8;
  code *local_e0;
  code *local_d8;
  longlong *local_d0;
  longlong *local_c8;
  longlong *local_c0;
  longlong *local_b8;
  longlong *local_b0;
  code *local_a8;
  code *local_a0;
  code *local_98;
  longlong local_90;
  code *local_88;
  code *local_80;
  code *local_78;
  code *local_70;
  code *local_68;
  longlong *local_60;
  code *local_58;
  
  pcVar17 = (code *)0x0;
  pcVar16 = (code *)0x0;
  local_e8 = *(longlong **)(param_1 + 0x60);
  pcVar14 = (code *)0x0;
  pcVar18 = (code *)0x0;
  local_d0 = (longlong *)0x0;
  local_b0 = (longlong *)0x0;
  local_a8 = (code *)0x0;
  local_e0 = (code *)0x0;
  local_res10 = param_2;
  local_res18 = param_3;
  local_res20 = param_4;
  plVar7 = (longlong *)FUN_1800014a0(DAT_18000dbb8,0,0xffffffff);
  if (plVar7 == (longlong *)0x0) {
    DAT_18000dca8 = DAT_18000d978;
    DAT_18000dca0 = 0x11;
    DAT_18000dc44 = 0x520;
  }
  else {
    lVar1 = *(longlong *)_PyThreadState_Current_exref;
    local_b8 = *(longlong **)(lVar1 + 0x60);
    local_c0 = *(longlong **)(lVar1 + 0x68);
    local_c8 = *(longlong **)(lVar1 + 0x70);
    if (local_b8 != (longlong *)0x0) {
      *local_b8 = *local_b8 + 1;
    }
    if (local_c0 != (longlong *)0x0) {
      *local_c0 = *local_c0 + 1;
    }
    if (local_c8 != (longlong *)0x0) {
      *local_c8 = *local_c8 + 1;
    }
    uVar5 = (uint)(param_2 == _Py_TrueStruct_exref);
    local_d0 = plVar7;
    if ((param_2 != _Py_ZeroStruct_exref && param_2 != _Py_NoneStruct_exref) &&
        param_2 != _Py_TrueStruct_exref) {
      uVar5 = PyObject_IsTrue(param_2);
    }
    pcVar8 = pcVar17;
    if ((int)uVar5 < 0) {
      DAT_18000dca0 = 0x13;
      DAT_18000dc44 = 0x53c;
      pcVar12 = pcVar17;
      pcVar14 = pcVar17;
      pcVar16 = pcVar17;
      pcVar18 = pcVar17;
LAB_180003f3c:
      DAT_18000dca8 = DAT_18000d978;
      pcVar9 = pcVar8;
    }
    else {
      pcVar12 = pcVar17;
      pcVar9 = pcVar17;
      if (uVar5 == 0) {
LAB_1800037d0:
        pcVar18 = pcVar9;
        pcVar14 = pcVar12;
        plVar7 = local_e8;
        lVar1 = local_e8[5];
        if (lVar1 == 0) {
          PyErr_Format(*(undefined8 *)PyExc_NameError_exref,
                       s_free_variable___s__referenced_be_18000d6c0,&DAT_18000d11c);
          DAT_18000dca0 = 0x21;
          DAT_18000dc44 = 0x622;
          pcVar16 = pcVar17;
          goto LAB_180003f39;
        }
        pcVar16 = *(code **)(*(longlong *)(lVar1 + 8) + 0x90);
        if (pcVar16 == (code *)0x0) {
          pcVar16 = *(code **)(*(longlong *)(lVar1 + 8) + 0x40);
          if (pcVar16 == (code *)0x0) {
            pcVar12 = (code *)PyObject_GetAttr();
          }
          else {
            pcVar12 = (code *)(*pcVar16)(lVar1,DAT_18000dc48 + 0x20);
          }
        }
        else {
          pcVar12 = (code *)(*pcVar16)();
        }
        if (pcVar12 == (code *)0x0) {
          DAT_18000dca0 = 0x21;
          DAT_18000dc44 = 0x623;
          pcVar16 = (code *)0x0;
        }
        else {
          pcVar8 = pcVar17;
          if ((*(code **)(pcVar12 + 8) == PyMethod_Type_exref) &&
             (pcVar8 = *(code **)(pcVar12 + 0x18), pcVar8 != (code *)0x0)) {
            pcVar16 = *(code **)(pcVar12 + 0x10);
            *(longlong *)pcVar8 = *(longlong *)pcVar8 + 1;
            *(longlong *)pcVar16 = *(longlong *)pcVar16 + 1;
            *(longlong *)pcVar12 = *(longlong *)pcVar12 + -1;
            if (*(longlong *)pcVar12 == 0) {
              (**(code **)(*(longlong *)(pcVar12 + 8) + 0x30))();
            }
            plVar10 = (longlong *)FUN_180001b30(pcVar16,pcVar8);
            if (plVar10 == (longlong *)0x0) {
              DAT_18000dca0 = 0x21;
              DAT_18000dc44 = 0x630;
              pcVar12 = pcVar16;
              pcVar16 = (code *)0x0;
            }
            else {
              *(longlong *)pcVar8 = *(longlong *)pcVar8 + -1;
              pcVar9 = pcVar17;
              if (*(longlong *)pcVar8 == 0) {
                (**(code **)(*(longlong *)(pcVar8 + 8) + 0x30))(pcVar8);
              }
LAB_180003913:
              *(longlong *)pcVar16 = *(longlong *)pcVar16 + -1;
              if (*(longlong *)pcVar16 == 0) {
                (**(code **)(*(longlong *)(pcVar16 + 8) + 0x30))(pcVar16);
              }
              pcVar16 = (code *)0x0;
              pcVar8 = *(code **)(*(longlong *)(DAT_18000dad0 + 8) + 0x90);
              local_b0 = plVar10;
              if (pcVar8 == (code *)0x0) {
                pcVar8 = *(code **)(*(longlong *)(DAT_18000dad0 + 8) + 0x40);
                if (pcVar8 == (code *)0x0) {
                  pcVar12 = (code *)PyObject_GetAttr();
                }
                else {
                  pcVar12 = (code *)(*pcVar8)(DAT_18000dad0,DAT_18000db78 + 0x20);
                }
              }
              else {
                pcVar12 = (code *)(*pcVar8)();
              }
              pcVar8 = pcVar9;
              if (pcVar12 == (code *)0x0) {
                DAT_18000dca0 = 0x22;
                DAT_18000dc44 = 0x641;
              }
              else {
                lVar1 = plVar7[5];
                if (lVar1 == 0) {
                  PyErr_Format(*(undefined8 *)PyExc_NameError_exref,
                               s_free_variable___s__referenced_be_18000d6c0,&DAT_18000d134);
                  DAT_18000dca0 = 0x22;
                  DAT_18000dc44 = 0x643;
                }
                else {
                  pcVar18 = *(code **)(*(longlong *)(lVar1 + 8) + 0x90);
                  if (pcVar18 == (code *)0x0) {
                    pcVar18 = *(code **)(*(longlong *)(lVar1 + 8) + 0x40);
                    if (pcVar18 == (code *)0x0) {
                      pcVar18 = (code *)PyObject_GetAttr();
                    }
                    else {
                      pcVar18 = (code *)(*pcVar18)(lVar1,DAT_18000dc48 + 0x20);
                    }
                  }
                  else {
                    pcVar18 = (code *)(*pcVar18)();
                  }
                  if (pcVar18 == (code *)0x0) {
                    DAT_18000dca0 = 0x22;
                    DAT_18000dc44 = 0x644;
                  }
                  else {
                    pcVar14 = pcVar17;
                    if ((*(code **)(pcVar18 + 8) == PyMethod_Type_exref) &&
                       (pcVar9 = *(code **)(pcVar18 + 0x18), pcVar14 = pcVar9, pcVar9 != (code *)0x0
                       )) {
                      pcVar15 = *(code **)(pcVar18 + 0x10);
                      *(longlong *)pcVar9 = *(longlong *)pcVar9 + 1;
                      *(longlong *)pcVar15 = *(longlong *)pcVar15 + 1;
                      *(longlong *)pcVar18 = *(longlong *)pcVar18 + -1;
                      if (*(longlong *)pcVar18 == 0) {
                        (**(code **)(*(longlong *)(pcVar18 + 8) + 0x30))();
                      }
                      pcVar8 = (code *)FUN_180001b30(pcVar15,pcVar9);
                      if (pcVar8 == (code *)0x0) {
                        DAT_18000dca0 = 0x22;
                        DAT_18000dc44 = 0x651;
                        pcVar18 = pcVar15;
                      }
                      else {
                        *(longlong *)pcVar9 = *(longlong *)pcVar9 + -1;
                        pcVar14 = pcVar17;
                        plVar7 = local_e8;
                        if (*(longlong *)pcVar9 == 0) {
                          (**(code **)(*(longlong *)(pcVar9 + 8) + 0x30))(pcVar9);
                          plVar7 = local_e8;
                        }
LAB_180003ac8:
                        *(longlong *)pcVar15 = *(longlong *)pcVar15 + -1;
                        if (*(longlong *)pcVar15 == 0) {
                          (**(code **)(*(longlong *)(pcVar15 + 8) + 0x30))(pcVar15);
                        }
                        pcVar18 = (code *)0x0;
                        if (plVar7[4] == 0) {
                          PyErr_Format(*(undefined8 *)PyExc_NameError_exref,
                                       s_free_variable___s__referenced_be_18000d6c0,
                                       s_start_time_18000d140);
                          DAT_18000dca0 = 0x22;
                          DAT_18000dc44 = 0x658;
                        }
                        else {
                          pcVar18 = (code *)PyNumber_Subtract(pcVar8);
                          if (pcVar18 == (code *)0x0) {
                            DAT_18000dca0 = 0x22;
                            DAT_18000dc44 = 0x659;
                          }
                          else {
                            *(longlong *)pcVar8 = *(longlong *)pcVar8 + -1;
                            if (*(longlong *)pcVar8 == 0) {
                              (**(code **)(*(longlong *)(pcVar8 + 8) + 0x30))(pcVar8);
                            }
                            pcVar9 = pcVar12 + 8;
                            pcVar8 = pcVar17;
                            pcVar15 = pcVar14;
                            if ((*(code **)pcVar9 == PyMethod_Type_exref) &&
                               (pcVar8 = *(code **)(pcVar12 + 0x18), pcVar8 != (code *)0x0)) {
                              pcVar11 = *(code **)(pcVar12 + 0x10);
                              *(longlong *)pcVar8 = *(longlong *)pcVar8 + 1;
                              *(longlong *)pcVar11 = *(longlong *)pcVar11 + 1;
                              *(longlong *)pcVar12 = *(longlong *)pcVar12 + -1;
                              if (*(longlong *)pcVar12 == 0) {
                                (**(code **)(*(longlong *)(pcVar12 + 8) + 0x30))();
                              }
                              local_res8 = pcVar11 + 8;
                              pcVar12 = pcVar11;
                              if (*(code **)local_res8 == PyFunction_Type_exref) {
                                local_78 = pcVar8;
                                local_70 = pcVar18;
                                pcVar16 = (code *)FUN_180001840(pcVar11,&local_78,2);
                                if (pcVar16 != (code *)0x0) {
                                  *(longlong *)pcVar8 = *(longlong *)pcVar8 + -1;
                                  if (*(longlong *)pcVar8 == 0) {
                                    (**(code **)(*(longlong *)(pcVar8 + 8) + 0x30))(pcVar8);
                                  }
                                  *(longlong *)pcVar18 = *(longlong *)pcVar18 + -1;
                                  pcVar9 = local_res8;
                                  pcVar8 = pcVar17;
                                  if (*(longlong *)pcVar18 == 0) {
                                    (**(code **)(*(longlong *)(pcVar18 + 8) + 0x30))(pcVar18);
                                    pcVar9 = local_res8;
                                  }
                                  goto LAB_180003c41;
                                }
                                DAT_18000dca0 = 0x22;
                                DAT_18000dc44 = 0x66e;
                              }
                              else {
                                pcVar14 = (code *)PyTuple_New(2);
                                if (pcVar14 == (code *)0x0) {
                                  DAT_18000dca0 = 0x22;
                                  DAT_18000dc44 = 0x67e;
                                }
                                else {
                                  *(code **)(pcVar14 + 0x18) = pcVar8;
                                  *(code **)(pcVar14 + 0x20) = pcVar18;
                                  pcVar18 = (code *)0x0;
                                  pcVar16 = (code *)FUN_180001600(pcVar11,pcVar14,0);
                                  if (pcVar16 != (code *)0x0) {
                                    *(longlong *)pcVar14 = *(longlong *)pcVar14 + -1;
                                    pcVar15 = pcVar17;
                                    pcVar9 = local_res8;
                                    pcVar8 = pcVar17;
                                    if (*(longlong *)pcVar14 == 0) {
                                      (**(code **)(*(longlong *)(pcVar14 + 8) + 0x30))(pcVar14);
                                      pcVar9 = local_res8;
                                    }
                                    goto LAB_180003c41;
                                  }
                                  DAT_18000dca0 = 0x22;
                                  DAT_18000dc44 = 0x684;
                                  pcVar8 = (code *)0x0;
                                }
                              }
                            }
                            else {
                              pcVar16 = (code *)FUN_180001b30(pcVar12,pcVar18);
                              if (pcVar16 == (code *)0x0) {
                                DAT_18000dca0 = 0x22;
                                DAT_18000dc44 = 0x667;
                              }
                              else {
                                *(longlong *)pcVar18 = *(longlong *)pcVar18 + -1;
                                pcVar11 = pcVar12;
                                if (*(longlong *)pcVar18 == 0) {
                                  (**(code **)(*(longlong *)(pcVar18 + 8) + 0x30))(pcVar18);
                                }
LAB_180003c41:
                                *(longlong *)pcVar11 = *(longlong *)pcVar11 + -1;
                                if (*(longlong *)pcVar11 == 0) {
                                  (**(code **)(*(longlong *)pcVar9 + 0x30))(pcVar11);
                                }
                                iVar6 = FUN_180002a60(0,pcVar16);
                                pcVar14 = pcVar15;
                                if (-1 < iVar6) {
                                  *(longlong *)pcVar16 = *(longlong *)pcVar16 + -1;
                                  if (*(longlong *)pcVar16 == 0) {
                                    (**(code **)(*(longlong *)(pcVar16 + 8) + 0x30))(pcVar16);
                                  }
                                  plVar7 = local_e8;
                                  lVar1 = local_e8[5];
                                  while (lVar1 != 0) {
                                    pcVar18 = *(code **)(*(longlong *)(lVar1 + 8) + 0x90);
                                    if (pcVar18 == (code *)0x0) {
                                      pcVar18 = *(code **)(*(longlong *)(lVar1 + 8) + 0x40);
                                      if (pcVar18 == (code *)0x0) {
                                        pcVar12 = (code *)PyObject_GetAttr(lVar1);
                                      }
                                      else {
                                        pcVar12 = (code *)(*pcVar18)(lVar1,DAT_18000dc48 + 0x20);
                                      }
                                    }
                                    else {
                                      pcVar12 = (code *)(*pcVar18)(lVar1);
                                    }
                                    if (pcVar12 == (code *)0x0) {
                                      DAT_18000dca0 = 0x25;
                                      pcVar18 = (code *)0x0;
                                      DAT_18000dc44 = 0x6a7;
                                      pcVar16 = pcVar17;
                                      goto LAB_180003f3c;
                                    }
                                    pcVar14 = pcVar17;
                                    if ((*(code **)(pcVar12 + 8) == PyMethod_Type_exref) &&
                                       (pcVar14 = *(code **)(pcVar12 + 0x18), pcVar14 != (code *)0x0
                                       )) {
                                      pcVar9 = *(code **)(pcVar12 + 0x10);
                                      *(longlong *)pcVar14 = *(longlong *)pcVar14 + 1;
                                      *(longlong *)pcVar9 = *(longlong *)pcVar9 + 1;
                                      *(longlong *)pcVar12 = *(longlong *)pcVar12 + -1;
                                      if (*(longlong *)pcVar12 == 0) {
                                        (**(code **)(*(longlong *)(pcVar12 + 8) + 0x30))();
                                      }
                                      pcVar16 = (code *)FUN_180001b30(pcVar9,pcVar14);
                                      if (pcVar16 == (code *)0x0) {
                                        DAT_18000dca0 = 0x25;
                                        pcVar18 = (code *)0x0;
                                        DAT_18000dc44 = 0x6b4;
                                        pcVar12 = pcVar9;
                                        goto LAB_180003f3c;
                                      }
                                      *(longlong *)pcVar14 = *(longlong *)pcVar14 + -1;
                                      pcVar18 = pcVar17;
                                      if (*(longlong *)pcVar14 == 0) {
                                        (**(code **)(*(longlong *)(pcVar14 + 8) + 0x30))(pcVar14);
                                      }
                                    }
                                    else {
                                      pcVar16 = (code *)FUN_180001c80(pcVar12);
                                      pcVar9 = pcVar12;
                                      pcVar18 = pcVar14;
                                      if (pcVar16 == (code *)0x0) {
                                        DAT_18000dca0 = 0x25;
                                        pcVar18 = (code *)0x0;
                                        DAT_18000dc44 = 0x6b7;
                                        goto LAB_180003f3c;
                                      }
                                    }
                                    pcVar14 = pcVar18;
                                    *(longlong *)pcVar9 = *(longlong *)pcVar9 + -1;
                                    if (*(longlong *)pcVar9 == 0) {
                                      (**(code **)(*(longlong *)(pcVar9 + 8) + 0x30))(pcVar9);
                                    }
                                    pcVar12 = (code *)PyNumber_Subtract(pcVar16,local_b0);
                                    if (pcVar12 == (code *)0x0) {
                                      DAT_18000dca0 = 0x25;
                                      pcVar18 = (code *)0x0;
                                      DAT_18000dc44 = 0x6bb;
                                      goto LAB_180003f3c;
                                    }
                                    *(longlong *)pcVar16 = *(longlong *)pcVar16 + -1;
                                    if (*(longlong *)pcVar16 == 0) {
                                      (**(code **)(*(longlong *)(pcVar16 + 8) + 0x30))(pcVar16);
                                    }
                                    local_res8 = (code *)CONCAT44(local_res8._4_4_,2);
                                    pcVar16 = (code *)PyInt_FromLong(2);
                                    if (pcVar16 == (code *)0x0) {
                                      DAT_18000dca0 = 0x25;
                                      pcVar18 = (code *)0x0;
                                      DAT_18000dc44 = 0x6be;
                                      goto LAB_180003f3c;
                                    }
                                    pcVar14 = (code *)PyObject_RichCompare(pcVar12,pcVar16,5);
                                    if (pcVar14 == (code *)0x0) {
                                      DAT_18000dca0 = 0x25;
                                      pcVar18 = (code *)0x0;
                                      DAT_18000dc44 = 0x6c0;
                                      goto LAB_180003f3c;
                                    }
                                    *(longlong *)pcVar12 = *(longlong *)pcVar12 + -1;
                                    if (*(longlong *)pcVar12 == 0) {
                                      (**(code **)(*(longlong *)(pcVar12 + 8) + 0x30))(pcVar12);
                                    }
                                    *(longlong *)pcVar16 = *(longlong *)pcVar16 + -1;
                                    pcVar12 = (code *)0x0;
                                    if (*(longlong *)pcVar16 == 0) {
                                      (**(code **)(*(longlong *)(pcVar16 + 8) + 0x30))(pcVar16);
                                    }
                                    pcVar16 = (code *)0x0;
                                    iVar6 = FUN_180001000(pcVar14);
                                    if (iVar6 < 0) {
                                      DAT_18000dca0 = 0x25;
                                      pcVar18 = (code *)0x0;
                                      DAT_18000dc44 = 0x6c3;
                                      goto LAB_180003f3c;
                                    }
                                    *(longlong *)pcVar14 = *(longlong *)pcVar14 + -1;
                                    if (*(longlong *)pcVar14 == 0) {
                                      (**(code **)(*(longlong *)(pcVar14 + 8) + 0x30))(pcVar14);
                                    }
                                    if (iVar6 != 0) {
                                      lVar1 = plVar7[3];
                                      if (lVar1 == 0) {
                                        PyErr_Format(*(undefined8 *)PyExc_NameError_exref,
                                                     s_free_variable___s__referenced_be_18000d6c0,
                                                     &DAT_18000cd94);
                                        DAT_18000dca0 = 0x26;
                                        pcVar18 = (code *)0x0;
                                        DAT_18000dc44 = 0x6ce;
                                        pcVar14 = (code *)0x0;
                                        goto LAB_180003f3c;
                                      }
                                      pcVar14 = *(code **)(*(longlong *)(lVar1 + 8) + 0x90);
                                      if (pcVar14 == (code *)0x0) {
                                        pcVar14 = *(code **)(*(longlong *)(lVar1 + 8) + 0x40);
                                        if (pcVar14 == (code *)0x0) {
                                          pcVar14 = (code *)PyObject_GetAttr();
                                        }
                                        else {
                                          pcVar14 = (code *)(*pcVar14)(lVar1,DAT_18000db20 + 0x20);
                                        }
                                      }
                                      else {
                                        pcVar14 = (code *)(*pcVar14)();
                                      }
                                      if (pcVar14 == (code *)0x0) {
                                        DAT_18000dca0 = 0x26;
                                        pcVar18 = (code *)0x0;
                                        DAT_18000dc44 = 0x6cf;
                                        goto LAB_180003f3c;
                                      }
                                      plVar7 = (longlong *)FUN_180001600(pcVar14,DAT_18000dcc0,0);
                                      if (plVar7 == (longlong *)0x0) {
                                        DAT_18000dca0 = 0x26;
                                        pcVar18 = (code *)0x0;
                                        DAT_18000dc44 = 0x6d1;
                                        pcVar16 = (code *)0x0;
                                        goto LAB_180003f3c;
                                      }
                                      *(longlong *)pcVar14 = *(longlong *)pcVar14 + -1;
                                      if (*(longlong *)pcVar14 == 0) {
                                        (**(code **)(*(longlong *)(pcVar14 + 8) + 0x30))(pcVar14);
                                      }
                                      *plVar7 = *plVar7 + -1;
                                      if (*plVar7 == 0) {
                                        (**(code **)(plVar7[1] + 0x30))(plVar7);
                                      }
                                      pcVar16 = (code *)0x0;
                                      pcVar14 = *(code **)(*(longlong *)(DAT_18000dbf8 + 8) + 0x90);
                                      if (pcVar14 == (code *)0x0) {
                                        pcVar14 = *(code **)(*(longlong *)(DAT_18000dbf8 + 8) + 0x40
                                                            );
                                        if (pcVar14 == (code *)0x0) {
                                          pcVar14 = (code *)PyObject_GetAttr();
                                        }
                                        else {
                                          pcVar14 = (code *)(*pcVar14)(DAT_18000dbf8,
                                                                       DAT_18000db78 + 0x20);
                                        }
                                      }
                                      else {
                                        pcVar14 = (code *)(*pcVar14)();
                                      }
                                      if (pcVar14 == (code *)0x0) {
                                        DAT_18000dca0 = 0x27;
                                        pcVar18 = (code *)0x0;
                                        DAT_18000dc44 = 0x6dd;
                                        goto LAB_180003f3c;
                                      }
                                      local_res8 = (code *)CONCAT44(local_res8._4_4_,2);
                                      pcVar12 = (code *)PyInt_FromLong(2);
                                      pcVar18 = (code *)0x0;
                                      if (pcVar12 == (code *)0x0) {
                                        DAT_18000dca0 = 0x27;
                                        DAT_18000dc44 = 0x6df;
                                        goto LAB_180003f3c;
                                      }
                                      local_d8 = pcVar14 + 8;
                                      pcVar18 = pcVar17;
                                      if ((*(code **)local_d8 == PyMethod_Type_exref) &&
                                         (pcVar18 = *(code **)(pcVar14 + 0x18),
                                         pcVar18 != (code *)0x0)) {
                                        pcVar15 = *(code **)(pcVar14 + 0x10);
                                        *(longlong *)pcVar18 = *(longlong *)pcVar18 + 1;
                                        *(longlong *)pcVar15 = *(longlong *)pcVar15 + 1;
                                        *(longlong *)pcVar14 = *(longlong *)pcVar14 + -1;
                                        if (*(longlong *)pcVar14 == 0) {
                                          (**(code **)(*(longlong *)local_d8 + 0x30))(pcVar14);
                                        }
                                        pcVar9 = pcVar15 + 8;
                                        pcVar14 = pcVar15;
                                        if (*(code **)pcVar9 == PyFunction_Type_exref) {
                                          local_a0 = pcVar18;
                                          local_98 = pcVar12;
                                          pcVar16 = (code *)FUN_180001840(pcVar15,&local_a0,2);
                                          if (pcVar16 == (code *)0x0) {
                                            DAT_18000dca0 = 0x27;
                                            DAT_18000dc44 = 0x6f3;
                                            goto LAB_180003f3c;
                                          }
                                          *(longlong *)pcVar18 = *(longlong *)pcVar18 + -1;
                                          if (*(longlong *)pcVar18 == 0) {
                                            (**(code **)(*(longlong *)(pcVar18 + 8) + 0x30))
                                                      (pcVar18);
                                          }
                                          *(longlong *)pcVar12 = *(longlong *)pcVar12 + -1;
                                          pcVar18 = pcVar17;
                                          if (*(longlong *)pcVar12 == 0) {
                                            (**(code **)(*(longlong *)(pcVar12 + 8) + 0x30))
                                                      (pcVar12);
                                          }
                                        }
                                        else {
                                          pcVar11 = (code *)PyTuple_New(2);
                                          pcVar8 = pcVar11;
                                          if (pcVar11 == (code *)0x0) {
                                            DAT_18000dca0 = 0x27;
                                            DAT_18000dc44 = 0x703;
                                            goto LAB_180003f3c;
                                          }
                                          *(code **)(pcVar11 + 0x18) = pcVar18;
                                          *(code **)(pcVar11 + 0x20) = pcVar12;
                                          pcVar18 = (code *)0x0;
                                          pcVar16 = (code *)FUN_180001600(pcVar15,pcVar11,0);
                                          if (pcVar16 == (code *)0x0) {
                                            DAT_18000dca0 = 0x27;
                                            DAT_18000dc44 = 0x709;
                                            pcVar12 = (code *)0x0;
                                            goto LAB_180003f3c;
                                          }
                                          *(longlong *)pcVar11 = *(longlong *)pcVar11 + -1;
                                          pcVar8 = pcVar17;
                                          if (*(longlong *)pcVar11 == 0) {
                                            (**(code **)(*(longlong *)(pcVar11 + 8) + 0x30))
                                                      (pcVar11);
                                          }
                                        }
                                      }
                                      else {
                                        pcVar16 = (code *)FUN_180001b30(pcVar14,pcVar12);
                                        if (pcVar16 == (code *)0x0) {
                                          DAT_18000dca0 = 0x27;
                                          DAT_18000dc44 = 0x6ec;
                                          goto LAB_180003f3c;
                                        }
                                        *(longlong *)pcVar12 = *(longlong *)pcVar12 + -1;
                                        pcVar15 = pcVar14;
                                        pcVar9 = local_d8;
                                        if (*(longlong *)pcVar12 == 0) {
                                          (**(code **)(*(longlong *)(pcVar12 + 8) + 0x30))(pcVar12);
                                          pcVar9 = local_d8;
                                        }
                                      }
                                      *(longlong *)pcVar15 = *(longlong *)pcVar15 + -1;
                                      if (*(longlong *)pcVar15 == 0) {
                                        (**(code **)(*(longlong *)pcVar9 + 0x30))(pcVar15);
                                      }
                                      iVar6 = FUN_180002a60(0,pcVar16);
                                      if (iVar6 < 0) {
                                        DAT_18000dca0 = 0x27;
                                        DAT_18000dc44 = 0x70f;
                                        pcVar14 = pcVar17;
                                        goto LAB_180003f39;
                                      }
                                      *(longlong *)pcVar16 = *(longlong *)pcVar16 + -1;
                                      if (*(longlong *)pcVar16 == 0) {
                                        (**(code **)(*(longlong *)(pcVar16 + 8) + 0x30))(pcVar16);
                                      }
                                      if ((local_b8 != (longlong *)0x0) &&
                                         (*local_b8 = *local_b8 + -1, *local_b8 == 0)) {
                                        (**(code **)(local_b8[1] + 0x30))();
                                      }
                                      if ((local_c0 != (longlong *)0x0) &&
                                         (*local_c0 = *local_c0 + -1, *local_c0 == 0)) {
                                        (**(code **)(local_c0[1] + 0x30))();
                                      }
                                      if ((local_c8 != (longlong *)0x0) &&
                                         (*local_c8 = *local_c8 + -1, *local_c8 == 0)) {
                                        (**(code **)(local_c8[1] + 0x30))(local_c8);
                                      }
                                      goto LAB_18000493a;
                                    }
                                    pcVar14 = pcVar17;
                                    lVar1 = plVar7[5];
                                  }
                                  PyErr_Format(*(undefined8 *)PyExc_NameError_exref,
                                               s_free_variable___s__referenced_be_18000d6c0,
                                               &DAT_18000d1fc);
                                  DAT_18000dca0 = 0x25;
                                  DAT_18000dc44 = 0x6a6;
                                  goto LAB_180003f36;
                                }
                                DAT_18000dca0 = 0x22;
                                pcVar18 = (code *)0x0;
                                DAT_18000dc44 = 0x68a;
                                pcVar12 = (code *)0x0;
                              }
                            }
                          }
                        }
                      }
                    }
                    else {
                      pcVar8 = (code *)FUN_180001c80(pcVar18);
                      pcVar15 = pcVar18;
                      if (pcVar8 != (code *)0x0) goto LAB_180003ac8;
                      DAT_18000dca0 = 0x22;
                      DAT_18000dc44 = 0x654;
                    }
                  }
                }
              }
            }
          }
          else {
            plVar10 = (longlong *)FUN_180001c80(pcVar12);
            pcVar16 = pcVar12;
            pcVar9 = pcVar8;
            if (plVar10 != (longlong *)0x0) goto LAB_180003913;
            DAT_18000dca0 = 0x21;
            DAT_18000dc44 = 0x633;
            pcVar16 = (code *)0x0;
          }
        }
        goto LAB_180003f3c;
      }
      pcVar8 = *(code **)(local_d0[1] + 0x90);
      if (pcVar8 == (code *)0x0) {
        pcVar8 = *(code **)(local_d0[1] + 0x40);
        if (pcVar8 == (code *)0x0) {
          pcVar8 = (code *)PyObject_GetAttr(local_d0);
        }
        else {
          pcVar8 = (code *)(*pcVar8)(local_d0,DAT_18000dc08 + 0x20);
        }
      }
      else {
        pcVar8 = (code *)(*pcVar8)();
      }
      if (pcVar8 == (code *)0x0) {
        DAT_18000dca0 = 0x15;
        DAT_18000dc44 = 0x546;
        pcVar12 = (code *)0x0;
        goto LAB_180003f3c;
      }
      pcVar12 = *(code **)(*(longlong *)(pcVar8 + 8) + 0x90);
      if (pcVar12 == (code *)0x0) {
        pcVar12 = *(code **)(*(longlong *)(pcVar8 + 8) + 0x40);
        if (pcVar12 == (code *)0x0) {
          pcVar12 = (code *)PyObject_GetAttr(pcVar8);
        }
        else {
          pcVar12 = (code *)(*pcVar12)(pcVar8,DAT_18000db98 + 0x20);
        }
      }
      else {
        pcVar12 = (code *)(*pcVar12)();
      }
      if (pcVar12 == (code *)0x0) {
        DAT_18000dca0 = 0x15;
        DAT_18000dc44 = 0x548;
        goto LAB_180003f3c;
      }
      *(longlong *)pcVar8 = *(longlong *)pcVar8 + -1;
      if (*(longlong *)pcVar8 == 0) {
        (**(code **)(*(longlong *)(pcVar8 + 8) + 0x30))(pcVar8);
      }
      pcVar9 = (code *)PyDict_New();
      if (pcVar9 != (code *)0x0) {
        iVar6 = PyDict_SetItem(pcVar9,DAT_18000dbc0,DAT_18000dbd8);
        if (iVar6 < 0) {
          DAT_18000dca0 = 0x15;
          DAT_18000dc44 = 0x54d;
          pcVar8 = pcVar9;
        }
        else {
          plVar7 = (longlong *)FUN_180001600(pcVar12,DAT_18000dc88,pcVar9);
          if (plVar7 == (longlong *)0x0) {
            DAT_18000dca8 = DAT_18000d978;
            DAT_18000dca0 = 0x15;
            DAT_18000dc44 = 0x54e;
            pcVar16 = (code *)0x0;
            goto LAB_180003f4a;
          }
          *(longlong *)pcVar12 = *(longlong *)pcVar12 + -1;
          if (*(longlong *)pcVar12 == 0) {
            (**(code **)(*(longlong *)(pcVar12 + 8) + 0x30))(pcVar12);
          }
          *(longlong *)pcVar9 = *(longlong *)pcVar9 + -1;
          pcVar12 = (code *)0x0;
          if (*(longlong *)pcVar9 == 0) {
            (**(code **)(*(longlong *)(pcVar9 + 8) + 0x30))(pcVar9);
          }
          *plVar7 = *plVar7 + -1;
          pcVar8 = (code *)0x0;
          if (*plVar7 == 0) {
            (**(code **)(plVar7[1] + 0x30))(plVar7);
          }
          pcVar9 = PyString_Type_exref;
          pcVar16 = (code *)0x0;
          if (param_5 == DAT_18000db28) {
LAB_180003099:
            lVar1 = local_e8[2];
            if (lVar1 == 0) {
              PyErr_Format(*(undefined8 *)PyExc_NameError_exref,
                           s_free_variable___s__referenced_be_18000d6c0,&DAT_18000d04c);
              DAT_18000dca0 = 0x1a;
              DAT_18000dc44 = 0x565;
            }
            else {
              pcVar8 = *(code **)(*(longlong *)(lVar1 + 8) + 0x90);
              if (pcVar8 == (code *)0x0) {
                pcVar8 = *(code **)(*(longlong *)(lVar1 + 8) + 0x40);
                if (pcVar8 == (code *)0x0) {
                  pcVar8 = (code *)PyObject_GetAttr();
                }
                else {
                  pcVar8 = (code *)(*pcVar8)(lVar1,DAT_18000db30 + 0x20);
                }
              }
              else {
                pcVar8 = (code *)(*pcVar8)();
              }
              if (pcVar8 == (code *)0x0) {
                DAT_18000dca0 = 0x1a;
                DAT_18000dc44 = 0x566;
              }
              else {
                pcVar12 = (code *)PyList_New(1);
                if (pcVar12 == (code *)0x0) {
                  DAT_18000dca0 = 0x1a;
                  DAT_18000dc44 = 0x568;
                }
                else {
                  *local_res18 = *local_res18 + 1;
                  **(undefined8 **)(pcVar12 + 0x18) = local_res18;
                  local_res8 = pcVar8 + 8;
                  pcVar14 = pcVar17;
                  if ((*(code **)local_res8 == PyMethod_Type_exref) &&
                     (pcVar14 = *(code **)(pcVar8 + 0x18), pcVar14 != (code *)0x0)) {
                    pcVar9 = *(code **)(pcVar8 + 0x10);
                    *(longlong *)pcVar14 = *(longlong *)pcVar14 + 1;
                    *(longlong *)pcVar9 = *(longlong *)pcVar9 + 1;
                    *(longlong *)pcVar8 = *(longlong *)pcVar8 + -1;
                    if (*(longlong *)pcVar8 == 0) {
                      (**(code **)(*(longlong *)local_res8 + 0x30))(pcVar8);
                    }
                    pcVar15 = pcVar9 + 8;
                    pcVar8 = pcVar9;
                    if (*(code **)pcVar15 == PyFunction_Type_exref) {
                      local_88 = pcVar14;
                      local_80 = pcVar12;
                      plVar7 = (longlong *)FUN_180001840(pcVar9,&local_88,2);
                      if (plVar7 != (longlong *)0x0) {
                        *(longlong *)pcVar14 = *(longlong *)pcVar14 + -1;
                        if (*(longlong *)pcVar14 == 0) {
                          (**(code **)(*(longlong *)(pcVar14 + 8) + 0x30))(pcVar14);
                        }
                        *(longlong *)pcVar12 = *(longlong *)pcVar12 + -1;
                        pcVar14 = pcVar17;
                        if (*(longlong *)pcVar12 == 0) {
                          (**(code **)(*(longlong *)(pcVar12 + 8) + 0x30))(pcVar12);
                        }
                        goto LAB_18000330e;
                      }
                      DAT_18000dca0 = 0x1a;
                      DAT_18000dc44 = 0x57f;
                      pcVar16 = (code *)0x0;
                    }
                    else {
                      pcVar18 = (code *)PyTuple_New(2);
                      if (pcVar18 == (code *)0x0) {
                        DAT_18000dca8 = DAT_18000d978;
                        DAT_18000dca0 = 0x1a;
                        DAT_18000dc44 = 0x58f;
                        goto LAB_180003f4a;
                      }
                      *(code **)(pcVar18 + 0x18) = pcVar14;
                      *(code **)(pcVar18 + 0x20) = pcVar12;
                      pcVar14 = (code *)0x0;
                      pcVar12 = (code *)0x0;
                      plVar7 = (longlong *)FUN_180001600(pcVar9,pcVar18,0);
                      if (plVar7 != (longlong *)0x0) {
                        *(longlong *)pcVar18 = *(longlong *)pcVar18 + -1;
                        if (*(longlong *)pcVar18 == 0) {
                          (**(code **)(*(longlong *)(pcVar18 + 8) + 0x30))(pcVar18);
                        }
                        goto LAB_18000330e;
                      }
                      DAT_18000dca0 = 0x1a;
                      DAT_18000dc44 = 0x595;
                      pcVar16 = (code *)0x0;
                    }
                  }
                  else {
                    plVar7 = (longlong *)FUN_180001b30(pcVar8,pcVar12);
                    if (plVar7 != (longlong *)0x0) {
                      *(longlong *)pcVar12 = *(longlong *)pcVar12 + -1;
                      pcVar15 = local_res8;
                      if (*(longlong *)pcVar12 == 0) {
                        (**(code **)(*(longlong *)(pcVar12 + 8) + 0x30))(pcVar12);
                        pcVar15 = local_res8;
                      }
LAB_18000330e:
                      *(longlong *)pcVar8 = *(longlong *)pcVar8 + -1;
                      if (*(longlong *)pcVar8 == 0) {
                        (**(code **)(*(longlong *)pcVar15 + 0x30))(pcVar8);
                      }
                      *plVar7 = *plVar7 + -1;
                      pcVar15 = pcVar14;
                      pcVar9 = PyString_Type_exref;
                      if (*plVar7 == 0) {
                        (**(code **)(plVar7[1] + 0x30))(plVar7);
                        pcVar9 = PyString_Type_exref;
                      }
                      goto LAB_180003343;
                    }
                    DAT_18000dca0 = 0x1a;
                    DAT_18000dc44 = 0x578;
                    pcVar16 = (code *)0x0;
                  }
                }
              }
            }
            goto LAB_180003f3c;
          }
          pcVar15 = pcVar17;
          if (*(code **)(DAT_18000db28 + 8) != PyString_Type_exref ||
              *(code **)(param_5 + 8) != PyString_Type_exref) {
            if ((*(code **)(DAT_18000db28 + 8) != PyString_Type_exref ||
                 param_5 != _Py_NoneStruct_exref) &&
               (pcVar15 = pcVar14,
               *(code **)(param_5 + 8) != PyString_Type_exref ||
               DAT_18000db28 != _Py_NoneStruct_exref)) {
              plVar7 = (longlong *)PyObject_RichCompare(param_5,DAT_18000db28,2);
              if (plVar7 != (longlong *)0x0) {
                uVar5 = FUN_180001000(plVar7);
                *plVar7 = *plVar7 + -1;
                local_res8 = (code *)CONCAT44(local_res8._4_4_,uVar5);
                pcVar9 = PyString_Type_exref;
                if (*plVar7 == 0) {
                  (**(code **)(plVar7[1] + 0x30))(plVar7);
                  pcVar9 = PyString_Type_exref;
                  uVar5 = (uint)local_res8;
                }
LAB_18000308f:
                if (-1 < (int)uVar5) {
                  pcVar15 = pcVar14;
                  if (uVar5 != 0) goto LAB_180003099;
                  goto LAB_180003343;
                }
              }
              DAT_18000dca0 = 0x18;
              DAT_18000dc44 = 0x55b;
              goto LAB_180003f3c;
            }
          }
          else {
            sVar2 = *(size_t *)(param_5 + 0x10);
            if ((sVar2 == *(size_t *)(DAT_18000db28 + 0x10)) &&
               (pcVar15 = pcVar14, param_5[0x20] == DAT_18000db28[0x20])) {
              if (sVar2 == 1) goto LAB_180003099;
              if (((*(int *)(param_5 + 0x18) == *(int *)(DAT_18000db28 + 0x18)) ||
                  (*(int *)(param_5 + 0x18) == -1)) || (*(int *)(DAT_18000db28 + 0x18) == -1)) {
                iVar6 = memcmp(param_5 + 0x20,DAT_18000db28 + 0x20,sVar2);
                uVar5 = (uint)(iVar6 == 0);
                goto LAB_18000308f;
              }
            }
          }
LAB_180003343:
          pcVar14 = pcVar15;
          pcVar16 = (code *)0x0;
          if (param_5 == DAT_18000db88) {
LAB_180003441:
            lVar1 = local_e8[2];
            if (lVar1 != 0) {
              pcVar18 = *(code **)(*(longlong *)(lVar1 + 8) + 0x90);
              if (pcVar18 == (code *)0x0) {
                pcVar18 = *(code **)(*(longlong *)(lVar1 + 8) + 0x40);
                if (pcVar18 == (code *)0x0) {
                  pcVar8 = (code *)PyObject_GetAttr();
                }
                else {
                  pcVar8 = (code *)(*pcVar18)(lVar1,DAT_18000db90 + 0x20);
                }
              }
              else {
                pcVar8 = (code *)(*pcVar18)();
              }
              if (pcVar8 == (code *)0x0) {
                DAT_18000dca0 = 0x1c;
                DAT_18000dc44 = 0x5b8;
                pcVar18 = pcVar17;
              }
              else {
                pcVar9 = pcVar17;
                pcVar18 = pcVar17;
                if ((*(code **)(pcVar8 + 8) == PyMethod_Type_exref) &&
                   (pcVar18 = *(code **)(pcVar8 + 0x18), pcVar9 = (code *)0x0,
                   pcVar18 != (code *)0x0)) {
                  pcVar12 = *(code **)(pcVar8 + 0x10);
                  *(longlong *)pcVar18 = *(longlong *)pcVar18 + 1;
                  *(longlong *)pcVar12 = *(longlong *)pcVar12 + 1;
                  *(longlong *)pcVar8 = *(longlong *)pcVar8 + -1;
                  if (*(longlong *)pcVar8 == 0) {
                    (**(code **)(*(longlong *)(pcVar8 + 8) + 0x30))();
                  }
                  pcVar9 = (code *)0x1;
                  pcVar8 = pcVar12;
                }
                iVar6 = (int)pcVar9;
                if (*(code **)(pcVar8 + 8) != PyFunction_Type_exref) {
                  pcVar12 = (code *)PyTuple_New(iVar6 + 2);
                  if (pcVar12 == (code *)0x0) {
                    DAT_18000dca0 = 0x1c;
                    DAT_18000dc44 = 0x5d7;
                  }
                  else {
                    if (pcVar18 != (code *)0x0) {
                      *(code **)(pcVar12 + 0x18) = pcVar18;
                      pcVar18 = pcVar17;
                    }
                    *local_res20 = *local_res20 + 1;
                    *(longlong **)(pcVar12 + (longlong)pcVar9 * 8 + 0x18) = local_res20;
                    *(longlong *)local_res10 = *(longlong *)local_res10 + 1;
                    *(code **)(pcVar12 + (ulonglong)(iVar6 + 1) * 8 + 0x18) = local_res10;
                    plVar7 = (longlong *)FUN_180001600(pcVar8,pcVar12,0);
                    if (plVar7 != (longlong *)0x0) {
                      *(longlong *)pcVar12 = *(longlong *)pcVar12 + -1;
                      pcVar16 = pcVar18;
                      if (*(longlong *)pcVar12 == 0) {
                        (**(code **)(*(longlong *)(pcVar12 + 8) + 0x30))(pcVar12);
                      }
                      goto LAB_180003645;
                    }
                    DAT_18000dca0 = 0x1c;
                    DAT_18000dc44 = 0x5e2;
                    pcVar16 = (code *)0x0;
                  }
                  goto LAB_180003f3c;
                }
                local_60 = local_res20;
                local_58 = local_res10;
                local_68 = pcVar18;
                plVar7 = (longlong *)FUN_180001840(pcVar8,&local_60 + -(longlong)pcVar9,iVar6 + 2,0)
                ;
                if (plVar7 != (longlong *)0x0) {
                  pcVar16 = pcVar17;
                  if ((pcVar18 != (code *)0x0) &&
                     (*(longlong *)pcVar18 = *(longlong *)pcVar18 + -1, *(longlong *)pcVar18 == 0))
                  {
                    (**(code **)(*(longlong *)(pcVar18 + 8) + 0x30))(pcVar18);
                  }
LAB_180003645:
                  *(longlong *)pcVar8 = *(longlong *)pcVar8 + -1;
                  if (*(longlong *)pcVar8 == 0) {
                    (**(code **)(*(longlong *)(pcVar8 + 8) + 0x30))(pcVar8);
                  }
                  *plVar7 = *plVar7 + -1;
                  pcVar18 = pcVar16;
                  if (*plVar7 == 0) {
                    (**(code **)(plVar7[1] + 0x30))(plVar7);
                  }
                  goto LAB_180003669;
                }
                DAT_18000dca0 = 0x1c;
                DAT_18000dc44 = 0x5c9;
                pcVar16 = (code *)0x0;
              }
              goto LAB_180003f39;
            }
            PyErr_Format(*(undefined8 *)PyExc_NameError_exref,
                         s_free_variable___s__referenced_be_18000d6c0,&DAT_18000d0e8);
            DAT_18000dca0 = 0x1c;
            DAT_18000dc44 = 0x5b7;
            pcVar8 = pcVar17;
LAB_180003f36:
            pcVar16 = (code *)0x0;
            pcVar18 = pcVar17;
          }
          else {
            if (*(code **)(param_5 + 8) != pcVar9 || *(code **)(DAT_18000db88 + 8) != pcVar9) {
              if (*(code **)(DAT_18000db88 + 8) != pcVar9 || param_5 != _Py_NoneStruct_exref) {
                if (*(code **)(param_5 + 8) != pcVar9 || DAT_18000db88 != _Py_NoneStruct_exref) {
                  plVar7 = (longlong *)PyObject_RichCompare(param_5,DAT_18000db88,2);
                  if (plVar7 != (longlong *)0x0) {
                    uVar5 = FUN_180001000(plVar7);
                    *plVar7 = *plVar7 + -1;
                    if (*plVar7 == 0) {
                      (**(code **)(plVar7[1] + 0x30))(plVar7);
                    }
                    goto LAB_180003433;
                  }
LAB_180003486:
                  DAT_18000dca0 = 0x1b;
                  DAT_18000dc44 = 0x5ad;
                  pcVar8 = pcVar17;
                  goto LAB_180003f36;
                }
                pcVar18 = (code *)0x0;
              }
              else {
                pcVar18 = (code *)0x0;
              }
            }
            else {
              sVar2 = *(size_t *)(param_5 + 0x10);
              pcVar18 = pcVar17;
              if ((sVar2 == *(size_t *)(DAT_18000db88 + 0x10)) &&
                 (param_5[0x20] == DAT_18000db88[0x20])) {
                if (sVar2 == 1) goto LAB_180003441;
                if (((*(int *)(param_5 + 0x18) == *(int *)(DAT_18000db88 + 0x18)) ||
                    (*(int *)(param_5 + 0x18) == -1)) || (*(int *)(DAT_18000db88 + 0x18) == -1)) {
                  iVar6 = memcmp(param_5 + 0x20,DAT_18000db88 + 0x20,sVar2);
                  uVar5 = (uint)(iVar6 == 0);
LAB_180003433:
                  if ((int)uVar5 < 0) goto LAB_180003486;
                  pcVar18 = (code *)0x0;
                  if (uVar5 != 0) goto LAB_180003441;
                }
                else {
                  pcVar18 = (code *)0x0;
                }
              }
            }
LAB_180003669:
            pcVar16 = *(code **)(local_d0[1] + 0x90);
            if (pcVar16 == (code *)0x0) {
              pcVar16 = *(code **)(local_d0[1] + 0x40);
              if (pcVar16 == (code *)0x0) {
                pcVar8 = (code *)PyObject_GetAttr(local_d0);
              }
              else {
                pcVar8 = (code *)(*pcVar16)(local_d0,DAT_18000dc08 + 0x20);
              }
            }
            else {
              pcVar8 = (code *)(*pcVar16)();
            }
            if (pcVar8 != (code *)0x0) {
              pcVar16 = *(code **)(*(longlong *)(pcVar8 + 8) + 0x90);
              if (pcVar16 == (code *)0x0) {
                pcVar16 = *(code **)(*(longlong *)(pcVar8 + 8) + 0x40);
                if (pcVar16 == (code *)0x0) {
                  pcVar12 = (code *)PyObject_GetAttr(pcVar8);
                }
                else {
                  pcVar12 = (code *)(*pcVar16)(pcVar8,DAT_18000dc58 + 0x20);
                }
              }
              else {
                pcVar12 = (code *)(*pcVar16)();
              }
              if (pcVar12 == (code *)0x0) {
                DAT_18000dca0 = 0x20;
                DAT_18000dc44 = 0x5fb;
                pcVar16 = (code *)0x0;
              }
              else {
                *(longlong *)pcVar8 = *(longlong *)pcVar8 + -1;
                if (*(longlong *)pcVar8 == 0) {
                  (**(code **)(*(longlong *)(pcVar8 + 8) + 0x30))(pcVar8);
                }
                pcVar9 = pcVar17;
                if ((*(code **)(pcVar12 + 8) == PyMethod_Type_exref) &&
                   (pcVar9 = *(code **)(pcVar12 + 0x18), pcVar9 != (code *)0x0)) {
                  pcVar16 = *(code **)(pcVar12 + 0x10);
                  *(longlong *)pcVar9 = *(longlong *)pcVar9 + 1;
                  *(longlong *)pcVar16 = *(longlong *)pcVar16 + 1;
                  *(longlong *)pcVar12 = *(longlong *)pcVar12 + -1;
                  if (*(longlong *)pcVar12 == 0) {
                    (**(code **)(*(longlong *)(pcVar12 + 8) + 0x30))();
                  }
                  plVar7 = (longlong *)FUN_180001b30(pcVar16,pcVar9);
                  if (plVar7 != (longlong *)0x0) {
                    *(longlong *)pcVar9 = *(longlong *)pcVar9 + -1;
                    pcVar8 = pcVar17;
                    if (*(longlong *)pcVar9 == 0) {
                      (**(code **)(*(longlong *)(pcVar9 + 8) + 0x30))(pcVar9);
                    }
LAB_1800037ad:
                    *(longlong *)pcVar16 = *(longlong *)pcVar16 + -1;
                    if (*(longlong *)pcVar16 == 0) {
                      (**(code **)(*(longlong *)(pcVar16 + 8) + 0x30))(pcVar16);
                    }
                    *plVar7 = *plVar7 + -1;
                    pcVar12 = pcVar14;
                    pcVar9 = pcVar18;
                    if (*plVar7 == 0) {
                      (**(code **)(plVar7[1] + 0x30))(plVar7);
                    }
                    goto LAB_1800037d0;
                  }
                  DAT_18000dca0 = 0x20;
                  DAT_18000dc44 = 0x609;
                  pcVar12 = pcVar16;
                  pcVar16 = (code *)0x0;
                  pcVar8 = pcVar9;
                }
                else {
                  plVar7 = (longlong *)FUN_180001c80(pcVar12);
                  pcVar16 = pcVar12;
                  pcVar8 = pcVar9;
                  if (plVar7 != (longlong *)0x0) goto LAB_1800037ad;
                  DAT_18000dca0 = 0x20;
                  DAT_18000dc44 = 0x60c;
                  pcVar16 = (code *)0x0;
                }
              }
              goto LAB_180003f3c;
            }
            DAT_18000dca0 = 0x20;
            DAT_18000dc44 = 0x5f9;
            pcVar16 = pcVar17;
          }
LAB_180003f39:
          pcVar12 = (code *)0x0;
        }
        goto LAB_180003f3c;
      }
      DAT_18000dca8 = DAT_18000d978;
      DAT_18000dca0 = 0x15;
      DAT_18000dc44 = 0x54b;
      pcVar14 = pcVar17;
      pcVar16 = pcVar17;
      pcVar18 = pcVar17;
    }
LAB_180003f4a:
    local_90 = *(longlong *)_PyThreadState_Current_exref;
    DAT_18000d978 = DAT_18000dca8;
    if ((pcVar18 != (code *)0x0) &&
       (*(longlong *)pcVar18 = *(longlong *)pcVar18 + -1, *(longlong *)pcVar18 == 0)) {
      (**(code **)(*(longlong *)(pcVar18 + 8) + 0x30))(pcVar18);
    }
    if ((pcVar12 != (code *)0x0) &&
       (*(longlong *)pcVar12 = *(longlong *)pcVar12 + -1, *(longlong *)pcVar12 == 0)) {
      (**(code **)(*(longlong *)(pcVar12 + 8) + 0x30))(pcVar12);
    }
    if ((pcVar9 != (code *)0x0) &&
       (*(longlong *)pcVar9 = *(longlong *)pcVar9 + -1, *(longlong *)pcVar9 == 0)) {
      (**(code **)(*(longlong *)(pcVar9 + 8) + 0x30))(pcVar9);
    }
    local_d8 = (code *)0x0;
    if ((pcVar14 != (code *)0x0) &&
       (*(longlong *)pcVar14 = *(longlong *)pcVar14 + -1, *(longlong *)pcVar14 == 0)) {
      (**(code **)(*(longlong *)(pcVar14 + 8) + 0x30))(pcVar14);
    }
    local_res8 = (code *)0x0;
    if ((pcVar16 != (code *)0x0) &&
       (*(longlong *)pcVar16 = *(longlong *)pcVar16 + -1, *(longlong *)pcVar16 == 0)) {
      (**(code **)(*(longlong *)(pcVar16 + 8) + 0x30))(pcVar16);
    }
    lVar1 = local_90;
    local_e8 = (longlong *)0x0;
    pcVar18 = pcVar17;
    pcVar16 = pcVar17;
    pcVar14 = pcVar17;
    if ((*(longlong *)(local_90 + 0x48) != *(longlong *)PyExc_Exception_exref) &&
       ((pcVar8 = pcVar17, *(longlong *)(local_90 + 0x48) == 0 ||
        (iVar6 = PyErr_GivenExceptionMatches(), iVar6 == 0)))) goto LAB_1800046fa;
    FUN_180002780(s_tvTools__CombineScenes_batchMode_18000d278,DAT_18000dc44,DAT_18000dca0,
                  DAT_18000dca8);
    iVar6 = FUN_180001df0(lVar1,&local_e8,&local_res8,&local_d8);
    pcVar8 = local_res8;
    if (iVar6 < 0) {
      DAT_18000dca0 = 0x2a;
      DAT_18000dc44 = 0x744;
LAB_1800046e9:
      DAT_18000dca8 = DAT_18000d978;
    }
    else {
      *(longlong *)local_res8 = *(longlong *)local_res8 + 1;
      local_a8 = local_res8;
      pcVar14 = *(code **)(*(longlong *)(DAT_18000dac0 + 8) + 0x90);
      if (pcVar14 == (code *)0x0) {
        pcVar14 = *(code **)(*(longlong *)(DAT_18000dac0 + 8) + 0x40);
        if (pcVar14 == (code *)0x0) {
          pcVar12 = (code *)PyObject_GetAttr();
        }
        else {
          pcVar12 = (code *)(*pcVar14)(DAT_18000dac0,DAT_18000db78 + 0x20);
        }
      }
      else {
        pcVar12 = (code *)(*pcVar14)();
      }
      if (pcVar12 == (code *)0x0) {
        DAT_18000dc44 = 0x752;
LAB_1800046df:
        DAT_18000dca0 = 0x2b;
        pcVar14 = pcVar12;
        goto LAB_1800046e9;
      }
      pcVar9 = pcVar12 + 8;
      local_e0 = (code *)0x0;
      if ((*(code **)pcVar9 != PyMethod_Type_exref) ||
         (pcVar15 = *(code **)(pcVar12 + 0x18), local_e0 = pcVar15, pcVar15 == (code *)0x0)) {
        pcVar16 = (code *)FUN_180001b30(pcVar12,pcVar8);
        pcVar11 = local_e0;
        if (pcVar16 == (code *)0x0) {
          DAT_18000dc44 = 0x75f;
        }
        else {
LAB_1800046b1:
          *(longlong *)pcVar12 = *(longlong *)pcVar12 + -1;
          if (*(longlong *)pcVar12 == 0) {
            (**(code **)(*(longlong *)pcVar9 + 0x30))(pcVar12);
          }
          iVar6 = FUN_180002a60(0,pcVar16);
          if (-1 < iVar6) {
            *(longlong *)pcVar16 = *(longlong *)pcVar16 + -1;
            if (*(longlong *)pcVar16 == 0) {
              (**(code **)(*(longlong *)(pcVar16 + 8) + 0x30))(pcVar16);
            }
            lVar1 = *(longlong *)_PyThreadState_Current_exref;
            plVar7 = *(longlong **)(lVar1 + 0x60);
            plVar10 = *(longlong **)(lVar1 + 0x68);
            plVar3 = *(longlong **)(lVar1 + 0x70);
            if (plVar7 != (longlong *)0x0) {
              *plVar7 = *plVar7 + 1;
            }
            if (plVar10 != (longlong *)0x0) {
              *plVar10 = *plVar10 + 1;
            }
            if (plVar3 != (longlong *)0x0) {
              *plVar3 = *plVar3 + 1;
            }
            plVar13 = (longlong *)FUN_180001600(DAT_18000dcb0,DAT_18000dcc8,0);
            if (plVar13 == (longlong *)0x0) {
              DAT_18000dca8 = DAT_18000d978;
              DAT_18000dca0 = 0x2d;
              DAT_18000dc44 = 0x799;
              uVar4 = *(undefined8 *)_PyThreadState_Current_exref;
              if ((pcVar11 != (code *)0x0) &&
                 (*(longlong *)pcVar11 = *(longlong *)pcVar11 + -1, *(longlong *)pcVar11 == 0)) {
                (**(code **)(*(longlong *)(pcVar11 + 8) + 0x30))(pcVar11);
              }
              FUN_180001f80(uVar4,0,0,0);
              FUN_180001d40(*(undefined8 *)_PyThreadState_Current_exref,plVar7,plVar10,plVar3);
            }
            else {
              *plVar13 = *plVar13 + -1;
              if (*plVar13 == 0) {
                (**(code **)(plVar13[1] + 0x30))(plVar13);
              }
              if ((plVar7 != (longlong *)0x0) && (*plVar7 = *plVar7 + -1, *plVar7 == 0)) {
                (**(code **)(plVar7[1] + 0x30))(plVar7);
              }
              if ((plVar10 != (longlong *)0x0) && (*plVar10 = *plVar10 + -1, *plVar10 == 0)) {
                (**(code **)(plVar10[1] + 0x30))(plVar10);
              }
              if ((plVar3 != (longlong *)0x0) && (*plVar3 = *plVar3 + -1, *plVar3 == 0)) {
                (**(code **)(plVar3[1] + 0x30))(plVar3);
              }
            }
            *local_e8 = *local_e8 + -1;
            if (*local_e8 == 0) {
              (**(code **)(local_e8[1] + 0x30))();
            }
            *(longlong *)pcVar8 = *(longlong *)pcVar8 + -1;
            if (*(longlong *)pcVar8 == 0) {
              (**(code **)(*(longlong *)(pcVar8 + 8) + 0x30))(pcVar8);
            }
            *(longlong *)local_d8 = *(longlong *)local_d8 + -1;
            if (*(longlong *)local_d8 == 0) {
              (**(code **)(*(longlong *)(local_d8 + 8) + 0x30))();
            }
            FUN_180001d40(*(undefined8 *)_PyThreadState_Current_exref,local_b8,local_c0,local_c8);
LAB_18000493a:
            pcVar17 = _Py_NoneStruct_exref;
            *(longlong *)_Py_NoneStruct_exref = *(longlong *)_Py_NoneStruct_exref + 1;
            goto LAB_180004944;
          }
          DAT_18000dc44 = 0x77f;
          pcVar12 = pcVar17;
        }
        goto LAB_1800046df;
      }
      pcVar14 = *(code **)(pcVar12 + 0x10);
      *(longlong *)pcVar15 = *(longlong *)pcVar15 + 1;
      *(longlong *)pcVar14 = *(longlong *)pcVar14 + 1;
      *(longlong *)pcVar12 = *(longlong *)pcVar12 + -1;
      if (*(longlong *)pcVar12 == 0) {
        (**(code **)(*(longlong *)(pcVar12 + 8) + 0x30))();
      }
      pcVar9 = pcVar14 + 8;
      pcVar11 = pcVar17;
      pcVar12 = pcVar14;
      if (*(code **)pcVar9 == PyFunction_Type_exref) {
        local_98 = pcVar8;
        local_a0 = pcVar15;
        pcVar16 = (code *)FUN_180001840(pcVar14,&local_a0,2);
        if (pcVar16 != (code *)0x0) {
          *(longlong *)pcVar15 = *(longlong *)pcVar15 + -1;
          if (*(longlong *)pcVar15 == 0) {
            (**(code **)(*(longlong *)(pcVar15 + 8) + 0x30))(pcVar15);
          }
          local_e0 = (code *)0x0;
          goto LAB_1800046b1;
        }
        DAT_18000dca8 = DAT_18000d978;
        DAT_18000dca0 = 0x2b;
        DAT_18000dc44 = 0x765;
      }
      else {
        local_res8 = (code *)PyTuple_New(2);
        if (local_res8 == (code *)0x0) {
          DAT_18000dca8 = DAT_18000d978;
          DAT_18000dca0 = 0x2b;
          DAT_18000dc44 = 0x773;
          pcVar18 = local_res8;
        }
        else {
          *(code **)(local_res8 + 0x18) = pcVar15;
          *(longlong *)pcVar8 = *(longlong *)pcVar8 + 1;
          *(code **)(local_res8 + 0x20) = pcVar8;
          local_e0 = (code *)0x0;
          pcVar16 = (code *)FUN_180001600(pcVar14,local_res8,0);
          if (pcVar16 != (code *)0x0) {
            *(longlong *)local_res8 = *(longlong *)local_res8 + -1;
            if (*(longlong *)local_res8 == 0) {
              (**(code **)(*(longlong *)(local_res8 + 8) + 0x30))(local_res8);
              pcVar11 = (code *)0x0;
            }
            goto LAB_1800046b1;
          }
          DAT_18000dca8 = DAT_18000d978;
          DAT_18000dca0 = 0x2b;
          DAT_18000dc44 = 0x779;
          pcVar18 = local_res8;
        }
      }
    }
LAB_1800046fa:
    FUN_180001d40(*(undefined8 *)_PyThreadState_Current_exref,local_b8,local_c0,local_c8);
    if ((local_d8 != (code *)0x0) &&
       (*(longlong *)local_d8 = *(longlong *)local_d8 + -1, *(longlong *)local_d8 == 0)) {
      (**(code **)(*(longlong *)(local_d8 + 8) + 0x30))();
    }
    if ((pcVar16 != (code *)0x0) &&
       (*(longlong *)pcVar16 = *(longlong *)pcVar16 + -1, *(longlong *)pcVar16 == 0)) {
      (**(code **)(*(longlong *)(pcVar16 + 8) + 0x30))(pcVar16);
    }
    if ((local_e8 != (longlong *)0x0) && (*local_e8 = *local_e8 + -1, *local_e8 == 0)) {
      (**(code **)(local_e8[1] + 0x30))();
    }
    if ((pcVar8 != (code *)0x0) &&
       (*(longlong *)pcVar8 = *(longlong *)pcVar8 + -1, *(longlong *)pcVar8 == 0)) {
      (**(code **)(*(longlong *)(pcVar8 + 8) + 0x30))(pcVar8);
    }
    if ((pcVar14 != (code *)0x0) &&
       (*(longlong *)pcVar14 = *(longlong *)pcVar14 + -1, *(longlong *)pcVar14 == 0)) {
      (**(code **)(*(longlong *)(pcVar14 + 8) + 0x30))(pcVar14);
    }
    if ((local_e0 != (code *)0x0) &&
       (*(longlong *)local_e0 = *(longlong *)local_e0 + -1, *(longlong *)local_e0 == 0)) {
      (**(code **)(*(longlong *)(local_e0 + 8) + 0x30))();
    }
    if ((pcVar18 != (code *)0x0) &&
       (*(longlong *)pcVar18 = *(longlong *)pcVar18 + -1, *(longlong *)pcVar18 == 0)) {
      (**(code **)(*(longlong *)(pcVar18 + 8) + 0x30))(pcVar18);
    }
  }
  FUN_180002780(s_tvTools__CombineScenes_batchMode_18000d708,DAT_18000dc44,DAT_18000dca0,
                DAT_18000dca8);
LAB_180004944:
  if ((local_d0 != (longlong *)0x0) && (*local_d0 = *local_d0 + -1, *local_d0 == 0)) {
    (**(code **)(local_d0[1] + 0x30))();
  }
  if ((local_b0 != (longlong *)0x0) && (*local_b0 = *local_b0 + -1, *local_b0 == 0)) {
    (**(code **)(local_b0[1] + 0x30))();
  }
  if ((local_a8 != (code *)0x0) &&
     (*(longlong *)local_a8 = *(longlong *)local_a8 + -1, *(longlong *)local_a8 == 0)) {
    (**(code **)(*(longlong *)(local_a8 + 8) + 0x30))(local_a8);
  }
  return pcVar17;
}

