#!/bin/bash
#ScriptName: ProcessKeeper

### BEGIN INIT INFO
# Provides:          Bec
# Required-Start:    $local_fs $network
# Required-Stop:     $local_fs
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: process keeper
# Description:       scan and keeper process running
### END INIT INFO

function StartProcess()
{
    screen_name="keeper"
    scr_count=$(screen -ls | grep $screen_name | wc -l)
    if [ $scr_count -ne 0 ]; then
	screen -S $screen_name -X quit
    fi
    screen -dmS $screen_name
    screen -x -S $screen_name -p 0 -X stuff $"gdb -ex run /root/utchain/src/ulordd\n"
}

echo "Process Keeper started!"
while ((1)) ; do
count=$(ps -aux | grep ulordd | grep -v grep | grep -v SCREEN | grep -v screen | grep -v gdb | wc -l)
#echo "$count"
if [ $count -eq 0 ]; then
    echo "count==0, restart process"
    StartProcess;
else
    echo "count==$count"
fi
sleep 1
done
