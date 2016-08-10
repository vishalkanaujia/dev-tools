SMF="$HOME/ems/kanaujia/smallfile/smallfile_cli.py "
OUTPUT_ROOT="$HOME/ems/vishalk/SMF"
HOSTNAME=`hostname -s`
CURRENT_DATETIME_STR=`date +%Y%m%d_%H%M%S`

if [ "$#" -ne 8 ]; then
    echo "Illegal number of parameters"
    echo "./smf_runner.sh <op> <hosts> <files#> <record_sz> <threads> <mount> <INDEX> <sfx>"
    exit -1
fi

# if an argument is provided, use that in place of CURRENT_DATETIME_STR
if [[ "$#" -ge 1 ]]; then
    CURRENT_DATETIME_STR=$8
fi

OUTPUT_DIR="${OUTPUT_ROOT}/client/${HOSTNAME}/${CURRENT_DATETIME_STR}/"
LOG_FILENAME="client.${HOSTNAME}.${CURRENT_DATETIME_STR}.tar.gz"

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


echo "Staring FIO runner number $INDEX"

sudo echo 3 | sudo tee /proc/sys/vm/drop_caches && sudo sync

smf_out=$INDEX.smf.log
op=$1
hosts=$2
files=$3
file_size_kib=$4
t=$5
topdir=$6
index=$7
suffx=$8

cmd=$SMF
cmd="$cmd --host-set $hosts"
cmd="$cmd --files $files --file-size $file_size_kib --threads $t" 
cmd="$cmd --response-times Y --top $topdir --operation "

#$cmd cleanup
rm -rf $topdir
mkdir -v $topdir
drop_cache
$cmd $op > $smf_out

echo "SMF run completed"
