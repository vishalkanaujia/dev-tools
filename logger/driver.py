import os

nodes=["iflab1"]
load = ["WR", "RD", "50_50", "70_30"]

# fio_runner.sh randwrite 4k 30 2
main_cmd = "./fio_runner.sh"

for node in nodes:
    i = 0
    cmd = node + " \'bash -s\'" + " < ./remote_commands.sh " + load[i]
    #cmd = node + " \'bash -s\'"
    ssh_cmd = "ssh ems@" + cmd
    print ssh_cmd
    os.system(ssh_cmd)
    # Run fio
    
    cmd = node + " \'bash -s\'" + " < ./finisher.sh " + load[i]
    ssh_cmd = "ssh ems@" + cmd
    os.system(ssh_cmd)
