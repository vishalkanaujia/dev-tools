#FIO=/home/ems/kanaujia/fio/fioa
FIO=fio
#MOUNT_NAME=/mnt/cephfs_perf/
MOUNT_NAME=/home/ems/kanaujia/dev-tools/logger/test_dir
FILESIZE=1mb
FILENAME=$MOUNT_NAME/$FILESIZE.blob

if [ "$#" -ne 2 ]; then
    echo "Illegal number of parameters"
    echo "./fio_prepare.sh <Block SZ=4k> <INDEX>" 
    exit -1
fi

BLKSZ=$1
INDEX=$2

sudo $FIO --filename=$FILENAME.$INDEX --name=prepare.phase.$INDEX \
--status-interval=5 --direct=1 --rw=write --bs=$1 --numjobs=4 \
--iodepth=8 --norandommap --size=$FILESIZE \
--ioengine=libaio --group_reporting --thread --filesize=$FILESIZE \
--nrfile=1 --sync=0 --randrepeat=0
