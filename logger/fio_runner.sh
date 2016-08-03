FIO=fio
OUTPUT_ROOT="/home/ems/vishalk"
HOSTNAME=`hostname -s`
CURRENT_DATETIME_STR=`date +%Y%m%d_%H%M%S`


if [ "$#" -ne 8 ]; then
    echo "Illegal number of parameters"
    echo "./fio_runner.sh <LOAD=randread> <Block SZ=4k> <Time=120> <# FIO=8> <LOG PATH> ><INDEX> <MOUNT><SZ>"
    exit -1
fi

# if an argument is provided, use that in place of CURRENT_DATETIME_STR
if [[ "$#" -ge 1 ]]; then
    CURRENT_DATETIME_STR=$5
fi

OUTPUT_DIR="${OUTPUT_ROOT}/${HOSTNAME}/client_logs/${CURRENT_DATETIME_STR}/"
LOG_FILENAME="client_logs.fio.${HOSTNAME}.${CURRENT_DATETIME_STR}.tar.gz"

heading() {
    echo -e "\n$1" | tr [a-z] [A-Z]
    echo "----------------------------------------------------------------------"
}

echo "Logs will be collected in ${OUTPUT_DIR}/${LOG_FILENAME}"

heading "Creating an interim directory for collecting logs"
mkdir -p $OUTPUT_DIR && cd $OUTPUT_DIR
if [ $? != 0 ] ; then
    echo "Error: Failed to create ouput directory $OUTPUT_DIR" >&2
    exit 1
else
    echo "Created $OUTPUT_DIR successfully"
fi

LOAD=$1
BLKSZ=$2
TIME=$3
FIO_COUNT=$4
INDEX=$6
OUTPUT=$INDEX.fio.log
MOUNT_NAME=$7
FILESIZE=$8
FILENAME=$MOUNT_NAME/$FILESIZE.blob.$INDEX

echo "Staring FIO runner number $INDEX"

sudo echo 3 | sudo tee /proc/sys/vm/drop_caches && sudo sync

sudo $FIO --filename=$FILENAME --name=benchmark.fio.$INDEX \
--output=$OUTPUT --direct=1 --rw=$1 \
--bs=$2 --numjobs=$FIO_COUNT --iodepth=16 --runtime=$3 \
--size=$FILESIZE --randrepeat=0 --invalidate=1 \
--time_based --ioengine=libaio \
--group_reporting --thread --filesize=$FILESIZE --verify=0

echo "fio runs completed"
