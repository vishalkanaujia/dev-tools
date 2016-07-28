#FIO=/home/ems/kanaujia/fio/fioa
FIO=fio
#MOUNT_NAME=/home/ems/kanaujia/dev-tools/logger/test_dir

if [ "$#" -ne 3 ]; then
    echo "Illegal number of parameters"
    echo "./fio_prepare.sh <Block SZ=4k> <INDEX> <MOUNT>" 
    exit -1
fi

MOUNT_NAME=$3
FILESIZE=1gb
FILENAME=$MOUNT_NAME/$FILESIZE.blob

BLKSZ=$1
INDEX=$2

sudo $FIO --filename=$FILENAME.$INDEX --name=prepare.phase.$INDEX \
--status-interval=5 --direct=1 --rw=write --bs=$1 --numjobs=8 \
--iodepth=8 --norandommap --size=$FILESIZE \
--ioengine=libaio --group_reporting --thread --filesize=$FILESIZE \
--nrfile=1 --randrepeat=0
