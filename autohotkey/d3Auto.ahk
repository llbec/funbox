#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

;启动标志框
Gui,  1:Add, GroupBox, x10 y10 w310 h30 Center, 启停
Gui,  1:Font
Gui,  1:Add, Radio, x20 y15 w50 h25 gLabelStart vradiostart, 启动
Gui,  1:Add, Radio, x80 y15 w50 h25 gLabelStop vradiostop checked, 停止
Gui,  1:Font

;控制方式框
Gui,  1:Add, GroupBox, x10 y45 w310 h30 Center, 控制方式
Gui,  1:Font
Gui,  1:Add, Radio, x20 y50 w50 h25 gLabelLBCtrl vctrlLb checked, 左键
Gui,  1:Add, Radio, x80 y50 w50 h25 gLabelSpaceCtrl vctrlSpace, 空格
Gui,  1:Add, Radio, x140 y50 w50 h25 gLabelKeyboardCtrl vctrlkeyboard, CtrlR
Gui,  1:Font

;技能设置框1,2,3,4
Gui,  1:Add, GroupBox, x10 y10 w70 h80 Center, 按键 1:
Gui,  1:Add, DropDownList, x180 y30 w50 h25 r2 vselected1 Choose1 AltSubmit, 启用|关闭
Gui,  1:Add, Edit, x180 y60 w35 h20 vedit1 Center, 600
Gui,  1:Add, Text, x220 y64 w15 h20 vcd1 Center, MS

Gui,  1:Add, GroupBox, x90 y10 w70 h80 Center, 按键 2:
Gui,  1:Add, DropDownList, x260 y30 w50 h25 r2 vselected2 Choose1 AltSubmit, 启用|关闭
Gui,  1:Add, Edit, x260 y60 w35 h20 vedit2 Center, 600
Gui,  1:Add, Text, x300 y64 w15 h20 vcd2 Center, MS

Gui,  1:Add, GroupBox, x170 y10 w70 h80 Center, 按键 3:
Gui,  1:Add, DropDownList, x340 y30 w50 h25 r2 vselected3 Choose1 AltSubmit, 启用|关闭
Gui,  1:Add, Edit, x340 y60 w35 h20 vedit3 Center, 600
Gui,  1:Add, Text, x380 y64 w15 h20 vcd3 Center, MS

Gui,  1:Add, GroupBox, x250 y10 w70 h80 Center, 按键 4:
Gui,  1:Add, DropDownList, x420 y30 w50 h25 r2 vselected4 Choose1 AltSubmit, 启用|关闭
Gui,  1:Add, Edit, x420 y60 w35 h20 vedit4 Center, 600
Gui,  1:Add, Text, x460 y64 w15 h20 vcd4 Center, MS

;显示窗口
Gui,  1:-MaximizeBox -MinimizeBox 
Gui,  1:Show, CEnter w330 h100, D3 Auto

;全局变量
bRunning := False
nCount := 0
bKey := False

GuiClose:
	ExitApp
Return

LabelCasting1:
    Send, 1
Return

LabelCasting2:
    Send, 2
Return

LabelCasting3:
    Send, 3
Return

LabelCasting4:
    Send, 4
Return

LabelTimer1:
    If selected1 = 1
        SetTimer, LabelCasting1, %cd1%
Return

LabelTimer2:
    If selected2 = 1
        SetTimer, LabelCasting2, %cd2%
Return

LabelTimer3:
    If selected3 = 1
        SetTimer, LabelCasting3, %cd3%
Return

LabelTimer4:
    If selected4 = 1
    {
        SetTimer, LabelCasting4, %cd4%
        ;MsgBox, , Result, selected4=%selected4% cd4=%cd4%,
    }
Return

LabelCastingStart:
    Gosub, LabelTimer1
    Gosub, LabelTimer2
    Gosub, LabelTimer3
    Gosub, LabelTimer4
Return

LabelCastingStop:
    SetTimer, LabelCasting1, off
    SetTimer, LabelCasting2, off
    SetTimer, LabelCasting3, off
    SetTimer, LabelCasting4, off
Return

LabelCheckState:
    bState := False
    If CtrlLB = 1
    {
        GetKeyState, bLButtonState, LButton, P
        If bLButtonState = U
            bState := False
        Else
            bState := True
    }
    Else If CtrlSpace = 1
    {
        GetKeyState, bSpaceState, Space, P
        If bSpaceState = U
            bState := False
        Else
            bState := True
    }
    Else
        bState := bKey
    
    If bState
    {
        If !bRunning
        {
            nCount++
            If nCount >= 3
            {
                bRunning := True
                Gosub LabelCastingStart
            }
        }
    }
    Else
    {
        If bRunning
        {
            bRunning := False
            Gosub LabelCastingStop
        }
    }
Return

LabelKeyStart
    nCount := 3
    bKey := True
Return

LabelKeyStop
    nCount := 0
    bKey := False
Return

LabelStart
    Gui,  1:Submit, NoHide
    SetTimer, LabelCheckState, 100
Return

LabelStop
    Gui,  1:Submit, NoHide
    SetTimer, LabelCheckState, off
Return

LabelLBCtrl
    Gui,  1:Submit, NoHide
    bRunning := False
    nCount : = 0
Return

LabelSpaceCtrl
    Gui,  1:Submit, NoHide
    bRunning := False
    nCount : = 0
Return

LabelKeyboardCtrl
    Gui,  1:Submit, NoHide
    bRunning := False
    nCount : = 3
Return

^r::
{
    If (ctrlkeyboard = 1)
    {
        nCount := 3
        bKey := True
    }
}
Return

$t::
{
    If (ctrlkeyboard = 1)
    {
        nCount := 0
        bKey := False
    }
    Send, t
}
Return

$m::
{
    If (ctrlkeyboard = 1)
    {
        nCount := 0
        bKey := False
    }
    Send, m
}
Return

$Enter::
{
    If (ctrlkeyboard = 1)
    {
        nCount := 0
        bKey := False
    }
    Send, Enter
}
Return