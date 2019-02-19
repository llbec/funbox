#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

Interval:=600

~LButton::
While GetKeyState("LButton", "P")
{
    send, 1
    send, 2
    send, 3
    send, 4
    Sleep, %Interval%
}

$1::
{
    SetTimer, LabelCast, %Interval%
    send, 1
}
Return

$2::
{
    SetTimer, LabelCast, %Interval%
    send, 2
}
Return

$3::
{
    SetTimer, LabelCast, %Interval%
    send, 3
}
Return

$4::
{
    SetTimer, LabelCast, %Interval%
    send, 4
}
Return

$t::
{
    SetTimer, LabelCast, off
    send, t
}
Return

$m::
{
    SetTimer, LabelCast, off
    send, m
}
Return

LabelCast:
Send, 1
Send, 2
Send, 3
Send, 4
Return

LabelAttack:
Send, {Space Down}
Click
Send, {Space Up}
Return

LabelMove:
Send, {Space Down}
Send, a
Send, {Space Up}
Return