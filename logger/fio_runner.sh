for i in {1..$4}
do
    sudo fio --filename=/mnt/cephfs/1tb.blob --name=$1.fio --output=$2_$1.log --status-interval=5 --direct=1 --rw=$1 --bs=$2 --numjobs=8 --iodepth=8 --runtime=$3 --norandommap --time_based --ioengine=libaio --group_reporting --thread --filesize=1tb
done
