OUTPUT_ROOT="$HOME/ems/vishalk/SMF"
HOSTNAME=`hostname -s`
CURRENT_DATETIME_STR=`date +%Y%m%d_%H%M%S`

# if an argument is provided, use that in place of CURRENT_DATETIME_STR
if [[ "$#" -ge 1 ]]; then
    CURRENT_DATETIME_STR=$1
fi

OUTPUT_DIR="${OUTPUT_ROOT}/osd/${HOSTNAME}/${CURRENT_DATETIME_STR}/"
LOG_FILENAME="osd.${HOSTNAME}.${CURRENT_DATETIME_STR}.tar.gz"

heading() {
    echo -e "\n$1" | tr [a-z] [A-Z]
    echo "----------------------------------------------------------------------"
}

echo "Logs will be collected in ${OUTPUT_DIR}"

heading "Creating an interim directory for collecting logs"
mkdir -p $OUTPUT_DIR && cd $OUTPUT_DIR
if [ $? != 0 ] ; then
    echo "Error: Failed to create ouput directory $OUTPUT_DIR" >&2
    exit 1
else
    echo "Created $OUTPUT_DIR successfully"
fi

####################################################################

SYSTEM_STATS_CMD_OUTPUT_FILE="system_stats_output.txt"
CEPH_STATS_CMD_OUTPUT_FILE="ceph_osd_mon_output.txt"
IOSTAT_CMD_OUTPUT_FILE="iostat_output.txt"
TOP_CMD_OUTPUT_FILE="top_output.txt"

system_stats_cmds=(
    "date"
    "sudo df -h"
    "sudo uname -a"
    "sudo lsb_release -a"
    "sudo dmesg"
    "mount"
    "cat /proc/mounts"
    "ps -ef"
    "cat /proc/cpuinfo"
    "cat /proc/meminfo"
    "vmstat  1 3"
    "uptime"
    "pstree"
    "free"
    "ifconfig -a"
)

system_recur_stats_cmds=(
    "top -b -d 5"
    "iostat -x 5"
    "ifstat -t -w 5"
)

ceph_stats_cmds=(
    "sudo ceph df"
    "sudo ceph report"
)

recur_stats_output=(
    "top.txt"
    "iostat.txt"
    "collectl.txt"
)

for cmd in "${system_stats_cmds[@]}" ; do
    echo "# $cmd >> $SYSTEM_STATS_CMD_OUTPUT_FILE"
    echo -e "\n# $cmd" >> $SYSTEM_STATS_CMD_OUTPUT_FILE
    eval $cmd >> $SYSTEM_STATS_CMD_OUTPUT_FILE
done

for cmd in "${ceph_stats_cmds[@]}" ; do
    echo "# $cmd >> $CEPH_STATS_CMD_OUTPUT_FILE"
    echo -e "\n# $cmd" >> $CEPH_STATS_CMD_OUTPUT_FILE
    eval $cmd >> $CEPH_STATS_CMD_OUTPUT_FILE
done

for ((i=0; i <${#system_recur_stats_cmds[*]}; i++));
do
    cmd=${system_recur_stats_cmds[i]}
    out=${recur_stats_output[i]}
    echo $cmd
    echo $out
    #echo "# cmd >> out
    #echo -e "\n# cmd" >> $SYSTEM_STATS_CMD_OUTPUT_FILE
    eval $cmd > $out&
done
