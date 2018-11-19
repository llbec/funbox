#!/bin/bash
#ScriptName: ulord

screen_name="ulord"
screen -dmS $screen_name
screen -x -S $screen_name -p 0 -X stuff $'/home/abc/gdb.sh\n'