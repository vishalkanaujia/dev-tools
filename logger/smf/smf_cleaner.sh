#FIO=/home/ems/kanaujia/fio/fioa
MOUNT_NAME=/mnt/cephfs_perf/SMF
echo "Deleting mount point $MOUNT_NAME"
sudo rm -rf $MOUNT_NAME/*
