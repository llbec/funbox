#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

hour := 0
minute := 0
second := 10
FontSize := 100
SysGet, ClockWidth, 78
SysGet, ClockHeight, 79
;ClockWidth := A_ScreenWidth
;ClockHeight := FontSize + (fontsize * 0.7)
cd := new CountDown(hour, minute, second)
Clocktext := cd.String()

Gui, -SysMenu -Caption +ToolWindow +AlwaysOnTop +E0x20
Gui, Color, Black
Gui, Font, cSilver s%FontSize% bold, Verdana
Gui, Add,Text,vDate yCenter xCenter, %ClockText%
Gui, Show, NoActivate xCenter yCenter , Clock
;WinSet, TransColor, 255, Clock
;WinSet, Region, 10-0 W%ClockWidth% H%ClockHeight% R5-5, Clock
SetTimer, UpdateClock, 1000
Return

UpdateClock:
cd.Setpcount()
ClockText := cd.String()
GuiControl,,Date, %ClockText%

If cd.Overtime()
    Gosub, Tray_Exit
Return

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

    String()
    {
        Return Format("{1:02d}:{2:02d}:{3:02d}", this.h, this.m, this.s)
    }

    Setpcount()
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