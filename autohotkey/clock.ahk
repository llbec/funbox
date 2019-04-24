#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

#SingleInstance Force

SplitPath, A_AhkPath, ,Dir,
;Menu Tray, Icon, %Dir%\Scripts\Resource\Clock.ico,,1

Menu, Tray, Click, 1
Menu, Tray, Tip, 时钟
Menu, Tray, Add, 时钟, Tray_Show
Menu, Tray, ToggleEnable, 时钟
Menu, Tray, Default, 时钟
Menu, Tray, Add
Menu, Tray, Add, 重启(&R), Tray_Reload
Menu, Tray, Add, 退出(&X), Tray_Exit
Menu, Tray, NoStandard

FontSize := 14
ClockWidth := 75
ClockHeight := FontSize + (fontsize * 0.7)
FormatTime, Clocktext ,, HH:mm

Gui, -SysMenu -Caption +ToolWindow +AlwaysOnTop +E0x20
Gui, Color, Black
Gui, Font, cSilver s%FontSize% bold, Verdana
Gui, Add,Text,vDate y-1 x15, %ClockText%
Gui, Show, NoActivate xCenter y1 , Clock
WinSet, TransColor, 255, Clock
WinSet, Region, 10-0 W%ClockWidth% H%ClockHeight% R5-5, Clock
SetTimer, UpdateClock, 60000
Return

UpdateClock:
FormatTime, ClockText ,, HH:mm
GuiControl,,Date, %ClockText%
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