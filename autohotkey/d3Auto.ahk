#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

;启动标志框
Gui,  1:Add, GroupBox, x10 y10 w70 h80 Center, 启动
Gui,  1:Font
Gui,  1:Add, Radio, x20 y30 w50 h25 vradiostart, Start
Gui,  1:Add, Radio, x20 y60 w50 h25 vradiostop checked, Stop
Gui,  1:Font

;控制方式框
Gui,  1:Add, GroupBox, x90 y10 w70 h80 Center, 控制方式
Gui,  1:Font
Gui,  1:Add, Radio, x100 y30 w50 h25 vradiomouse checked, 鼠标
Gui,  1:Add, Radio, x100 y60 w50 h25 vradiokeyboard, 键盘
Gui,  1:Font

;技能设置框1,2,3,4
Gui,  1:Add, GroupBox, x170 y10 w70 h80 Center, 按键 1:
Gui,  1:Add, DropDownList, x180 y30 w50 h25 r2 vddl1 Choose1 AltSubmit, 启用|关闭
Gui,  1:Add, Edit, x180 y60 w35 h20 vedit1 Center, 600
Gui,  1:Add, Text, x220 y64 w15 h20 vtext1 Center, MS

Gui,  1:Add, GroupBox, x250 y10 w70 h80 Center, 按键 2:
Gui,  1:Add, DropDownList, x260 y30 w50 h25 r2 vddl2 Choose1 AltSubmit, 启用|关闭
Gui,  1:Add, Edit, x260 y60 w35 h20 vedit2 Center, 600
Gui,  1:Add, Text, x300 y64 w15 h20 vtext2 Center, MS

Gui,  1:Add, GroupBox, x330 y10 w70 h80 Center, 按键 3:
Gui,  1:Add, DropDownList, x340 y30 w50 h25 r2 vddl3 Choose1 AltSubmit, 启用|关闭
Gui,  1:Add, Edit, x340 y60 w35 h20 vedit3 Center, 600
Gui,  1:Add, Text, x380 y64 w15 h20 vtext3 Center, MS

Gui,  1:Add, GroupBox, x410 y10 w70 h80 Center, 按键 4:
Gui,  1:Add, DropDownList, x420 y30 w50 h25 r2 vddl4 Choose1 AltSubmit, 启用|关闭
Gui,  1:Add, Edit, x420 y60 w35 h20 vedit4 Center, 600
Gui,  1:Add, Text, x460 y64 w15 h20 vtext4 Center, MS

/*
;技能设置框1,2,3,4
Gui,  1:Add, GroupBox, x90 y10 w70 h80 Center, 按键 1:
Gui,  1:Add, DropDownList, x100 y30 w50 h25 r2 vddl4 Choose1 AltSubmit, 启用|关闭
Gui,  1:Add, Edit, x100 y60 w35 h20 vedit4 Center, 600
Gui,  1:Add, Text, x140 y64 w15 h20 vtext4 Center, MS

Gui,  1:Add, GroupBox, x170 y10 w70 h80 Center, 按键 2:
Gui,  1:Add, DropDownList, x180 y30 w50 h25 r2 vddl1 Choose1 AltSubmit, 启用|关闭
Gui,  1:Add, Edit, x180 y60 w35 h20 vedit1 Center, 600
Gui,  1:Add, Text, x220 y64 w15 h20 vtext1 Center, MS

Gui,  1:Add, GroupBox, x250 y10 w70 h80 Center, 按键 3:
Gui,  1:Add, DropDownList, x260 y30 w50 h25 r2 vddl2 Choose1 AltSubmit, 启用|关闭
Gui,  1:Add, Edit, x260 y60 w35 h20 vedit2 Center, 600
Gui,  1:Add, Text, x300 y64 w15 h20 vtext2 Center, MS

Gui,  1:Add, GroupBox, x330 y10 w70 h80 Center, 按键 4:
Gui,  1:Add, DropDownList, x340 y30 w50 h25 r2 vddl3 Choose1 AltSubmit, 启用|关闭
Gui,  1:Add, Edit, x340 y60 w35 h20 vedit3 Center, 600
Gui,  1:Add, Text, x380 y64 w15 h20 vtext3 Center, MS
*/

;显示窗口
Gui,  1:-MaximizeBox -MinimizeBox 
Gui,  1:Show, CEnter w490 h100, D3 Auto

bState = False
nCount = 0

;SetTimer, LabelLog, 100
Return

GuiClose:
	ExitApp
Return

;r:
;    MsgBox started!
;    Control, Check, ,%radiostart%
;Return

LabelCast1:
Send, 1
Return

LabelCast2:
Send, 2
Return

LabelCast3:
Send, 3
Return

LabelCast4:
Send, 4
Return

LabelTimer1:
    If ddl1 = 1
        SetTimer, LabelCast1, %edit1%
Return

LabelTimer2:
    If ddl2 = 1
        SetTimer, LabelCast2, %edit2%
Return

LabelTimer3:
    If ddl3 = 1
        SetTimer, LabelCast3, %edit3%
Return

LabelTimer4:
    If ddl4 = 1
    {
        SetTimer, LabelCast4, %edit4%
        ;MsgBox, , Result, ddl4=%ddl4% edit4=%edit4%,
    }
Return

LabelActionStart:
    Gosub LabelTimer1
    Gosub LabelTimer2
    Gosub LabelTimer3
    Gosub LabelTimer4
    bState = True
Return

LabelActionStop:
    SetTimer, LabelCast1, off
    SetTimer, LabelCast2, off
    SetTimer, LabelCast3, off
    SetTimer, LabelCast4, off
    bState = False
Return

LabelRunner:
    Gui,  1:Submit, NoHide
    If radiomouse = 0
    {
        SetTimer, LabelRunner, off
    }
    GetKeyState, bLButtonState, LButton, P
    ToolTip, %bLButtonState%`n%nCount%`n%bState%, 0, 0, 2
    If bLButtonState = U
    {
        nCount = 0
        If bState = True
        {
            Gosub LabelActionStop
        }
    }
    Else
    {
        If nCount < 3 
        {
            nCount += 1
        }
        Else
        {
            If bState = False
            {
                ;MsgBox, , log, action start, 1
                Gosub LabelActionStart
            }
        }
    }
Return

LabelKeyBoardStart:
    Gui,  1:Submit, NoHide
    If radiostart = 1
    {
        If radiomouse = 0
        {
            Gosub LabelActionStart
        }
    }
Return

LabelKeyBoardStop:
    Gui,  1:Submit, NoHide
    If radiostart = 1
    {
        If radiomouse = 0
        {
            Gosub LabelActionStop
        }
    }
Return

LabelMouseStart:
    Gui,  1:Submit, NoHide
    If radiostart = 1
    {
        If radiomouse = 1
        {
            SetTimer, LabelRunner, 100
        }
    }
Return

LabelMouseStop:
    Gui,  1:Submit, NoHide
    If radiostart = 1
    {
        If radiomouse = 1
        {
            SetTimer, LabelRunner, off
            nCount = 0
            Gosub LabelActionStop
        }
    }
Return

LabelLog:
    ToolTip, log:%nCount%`n%bState%, 400, 0,
Return

/*
LabelMouseStart:
    Gui,  1:Submit, NoHide
    If radiostart = 1
    {
        If radiomouse = 1 
        {
            SetTimer, LabelCheckLBTN, 100
        }
    }
Return

LabelCheckLBTN:
    GetKeyState, EWD_LButtonState, LButton, P
    if EWD_LButtonState = U
    {
        SetTimer, LabelCheckLBTN, off
        SetTimer, LabelCast1, off
        SetTimer, LabelCast2, off
        SetTimer, LabelCast3, off
        SetTimer, LabelCast4, off
        ncount = 0
        return
    }
    If ncount < 10
        ncount += 1
    If ncount = 3
    {
        Gosub LabelTimer1
        Gosub LabelTimer2
        Gosub LabelTimer3
        Gosub LabelTimer4
    }
Return
*/

$1::
{
    Gosub LabelKeyBoardStart
    Send, 1
}
Return

$2::
{
    Gosub LabelKeyBoardStart
    Send, 2
}
Return

$3::
{
    Gosub LabelKeyBoardStart
    Send, 3
}
Return

$4::
{
    Gosub LabelKeyBoardStart
    Send, 4
}
Return

$t::
{
    Gosub LabelKeyBoardStop
    Send, t
}
Return

$m::
{
    Gosub LabelKeyBoardStop
    Send, m
}
Return

^r::
{
    Gosub LabelMouseStart
}
Return