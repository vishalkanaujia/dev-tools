#FIO=/home/ems/kanaujia/fio/fioa
FIO=fio
#MOUNT_NAME=/mnt/cephfs_perf/
MOUNT_NAME=/home/ems/kanaujia/dev-tools/logger/test_dir
FILESIZE=1mb
FILENAME=$MOUNT_NAME/$FILESIZE.blob

if [ "$#" -ne 6 ]; then
    echo "Illegal number of parameters"
    echo "./fio_runner.sh <LOAD=randread> <Block SZ=4k> <Time=120> <# FIO=8> <LOG PATH> ><INDEX>"
    exit -1
fi

LOAD=$1
BLKSZ=$2
TIME=$3
FIO_COUNT=$4
INDEX=$6
OUTPUT=$5/$INDEX.fio.log

echo "Staring FIO number $INDEX"
sudo $FIO --filename=$FILENAME.$INDEX --name=benchmark.fio.$INDEX \
--output=$OUTPUT --status-interval=5 --direct=1 --rw=$1 \
--bs=$2 --numjobs=$FIO_COUNT --iodepth=8 --runtime=$3 \
--size=$FILESIZE --randrepeat=0 --invalidate=1 \
--time_based --ioengine=libaio \
--group_reporting --thread --filesize=$FILESIZE --verify=0

echo "fio runs completed"
