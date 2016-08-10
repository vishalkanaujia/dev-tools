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

echo "Logs are fetched from ${OUTPUT_DIR}"

heading "Stopping commands and collecting logs"
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "Log directory does not exist"
    exit
fi

cd $OUTPUT_DIR
if [ $? != 0 ] ; then
    echo "Error: Failed to reach ouput directory $OUTPUT_DIR" >&2
    exit 1
else
    echo "Got $OUTPUT_DIR successfully"
fi

####################################################################

system_recur_stats_cmds=(
    "sudo killall top"
    "sudo killall iostat"
)

for ((i=0; i <${#system_recur_stats_cmds[*]}; i++));
do
    cmd=${system_recur_stats_cmds[i]}
    echo $cmd
    eval $cmd
done

#################### CREATE THE FINAL TAR FILE
heading "Creating tarfile ${LOG_FILENAME}"
# Moving to parent directory
cd ../../../
echo $PWD
sudo tar zcvf $LOG_FILENAME $OUTPUT_DIR

#heading "Removing interim output directory ${HOSTNAME}/"
#sudo rm -fr "./osd"
