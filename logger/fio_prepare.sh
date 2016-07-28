#FIO=/home/ems/kanaujia/fio/fioa
FIO=fio
#MOUNT_NAME=/home/ems/kanaujia/dev-tools/logger/test_dir

if [ "$#" -ne 4 ]; then
    echo "Illegal number of parameters"
    echo "./fio_prepare.sh <Block SZ=4k> <INDEX> <MOUNT><SIZE>" 
    exit -1
fi

MOUNT_NAME=$3
FILESIZE=$4
FILENAME=$MOUNT_NAME/$FILESIZE.blob

BLKSZ=$1
INDEX=$2

sudo $FIO --filename=$FILENAME.$INDEX --name=prepare.phase.$INDEX \
--direct=1 --rw=write --bs=$1 \
--iodepth=8 --size=$FILESIZE --sync=0 \
--ioengine=libaio --filesize=$FILESIZE \
--nrfile=1 --randrepeat=0 --refill_buffers
