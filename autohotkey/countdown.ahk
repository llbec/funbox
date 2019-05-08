#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

Menu, Tray, Add, Show(&S), Tray_Count
Menu, Tray, Add, Reset(&R), Tray_Reload
Menu, Tray, Add, Exit(&X), Tray_Exit
Menu, Tray, NoStandard

FontSize := 14
;SysGet, ClockWidth, 78
;SysGet, ClockHeight, 79
ClockWidth := 200
ClockHeight := FontSize + (fontsize * 0.7)
global cd := new CountDown(0, 0, 0)
global tipCount := 0

Gui, -SysMenu -Caption +ToolWindow +AlwaysOnTop +E0x20
Gui, Color, Black
Gui, Font, cSilver s%FontSize% bold, Verdana
Gui, Add,Text,vDate yCenter x20, % cd.String()

Gosub WorkCD

Return

WorkCD:
SetTimer, UpdateClock, Off
Gui, Hide
cd.Reset(0, 45, 0)
SetTimer, StartRelax, 1000
Return

StartRelax:
cd.StepCount()
If cd.Overtime()
{
    MsgBox, , Relax, Rock your body,
    Gosub RelaxCD
}
Return

RelaxCD:
SetTimer, StartRelax, Off
cd.Reset(0, 10, 0)
Gui, Show, NoActivate xCenter y1 , Clock
WinSet, TransColor, 255, Clock
WinSet, Region, 10-0 W%ClockWidth% H%ClockHeight% R5-5, Clock
GuiControl,,Date, % cd.String()
SetTimer, UpdateClock, 1000
Return

UpdateClock:
cd.StepCount()
GuiControl,,Date, % cd.String()

If cd.Overtime()
    Gosub, WorkCD
Return

Tray_Count:
ToolTip, % cd.String()
tipCount := 0
SetTimer, RemoveToolTip, 1000
Return

RemoveToolTip:
tipCount++
If (tipCount >= 5)
{
    SetTimer, RemoveToolTip, Off
    ToolTip
}
Else
    ToolTip, % cd.String()
return

Tray_Show:
Menu, Tray, Show
Return
Tray_Reload:
Reload
Return
Tray_Exit:
ExitApp
Return

class CountDown
{
    __New(h, m, s)
    {
        this.h := h
        this.m := m
        this.s := s
    }

    Reset(h, m, s)
    {
        this.h := h
        this.m := m
        this.s := s
    }

    String()
    {
        Return Format("{1:02d}:{2:02d}:{3:02d}", this.h, this.m, this.s)
    }

    StepCount()
    {
        If this.s > 0
            this.s-=1
        Else
        {
            this.s := 59
            If this.m >0
                this.m-=1
            Else
            {
                this.m := 59
                If this.h > 0
                    this.h-=1
                Else
                {
                    this.h := 0
                    this.m := 0
                    this.s := 0
                }
            }
        }
        ;MsgBox, % this.h this.m this.s
        Return
    }

    Overtime()
    {
        If this.h = 0 And this.m = 0 And this.s = 0
            Return True
        Return False
    }
}