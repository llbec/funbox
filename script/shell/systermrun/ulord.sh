#!/bin/bash
#ScriptName: ulord

### BEGIN INIT INFO
# Provides:          ulord
# Required-Start:    $local_fs $network
# Required-Stop:     $local_fs
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: ulord gdb screen
# Description:       ulord gdb screen
### END INIT INFO

screen_name="ulord"
screen -dmS $screen_name
screen -x -S $screen_name -p 0 -X stuff $"gdb -ex run /home/abc/utchain/src/ulordd\n"
