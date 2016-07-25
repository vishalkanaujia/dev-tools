FIO=/home/ems/kanaujia/fio/fio
MOUNT_NAME=/mnt/cephfs_perf/

for i in {1..$4}
do
    sudo $FIO --filename=$MOUNT_NAME/1tb.blob --name=$1.fio --output=$5/$2_$1.log --status-interval=5 --direct=1 --rw=$1 --bs=$2 --numjobs=8 --iodepth=8 --runtime=$3 --norandommap --time_based --ioengine=libaio --group_reporting --thread --filesize=1tb
done
