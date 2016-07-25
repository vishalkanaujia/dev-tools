#!/usr/bin/python

import threading
import time
import paramiko
import datetime
import os

def print_lines(lines):
    for l in lines:
        print l

def ssh_remote_run(client, script):
    # Setup sftp connection and transmit this script
    destination = "/tmp/" + script
    print "Copy: src=%s dest=%s" %(script, destination)

    sftp = client.open_sftp()
    sftp.put(script, destination)
    sftp.close()

def execute_fio(n, load, block_sz, time, num_fio, log_path):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
    ssh.load_system_host_keys()

    ssh.connect(hostname=n, port=22, username='ems', password='ems123')

    fio_script_path = "fio_runner.sh"
    ssh_remote_run(ssh, fio_script_path)

    new_script_path = "/tmp/" + fio_script_path
    sub_cmd = "chmod +x " + new_script_path + ";"
 
    cmd = sub_cmd + "bash -x "
    cmd = cmd + new_script_path + " " + load + " " + block_sz + " " + \
            time + " " + num_fio + " " + log_path
    print "Running fio cmd = " + cmd

    stdin, stdout, stderr = ssh.exec_command(cmd)

    print "Execute FIO stdout from node:%s" %(n)
    print "fio stderr: "
    print_lines(stderr.readlines())
    print "fio stdout: ", stdout.readlines()
    print_lines(stdout.readlines())

    ssh.close()

def execute_push_on_a_node(n, remote_script_path, args=None):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
    ssh.load_system_host_keys()

    ssh.connect(hostname=n, port=22, username='ems', password='ems123')

    ssh_remote_run(ssh, remote_script_path)
    new_remote_script_path = "/tmp/" + remote_script_path
    sub_cmd = "chmod +x " + new_remote_script_path + ";"

    if args is not None:
        cmd = new_remote_script_path + " " + args
    else:
        cmd = new_remote_script_path

    cmd = sub_cmd + "bash -x " + cmd
    print "Runing command:" + cmd

    stdin, stdout, stderr = ssh.exec_command(cmd)

    print "Push: %s arg= %s stdout on node:%s" %(new_remote_script_path, args, n)
    print "Execute PUSH stdout from node:%s" %(n)
    print "fio stderr: "
    print_lines(stderr.readlines())
    print "fio stdout: ", stdout.readlines()
    print_lines(stdout.readlines())

    ssh.close()

def remote_collect_start(nodes, args=None):
    for n in nodes:
        print "Starting collection on node:" + n
        execute_push_on_a_node(n, 'remote_commands.sh', args)

def create_log_path(args):
    now = datetime.datetime.now()
    unique_str = str(now.year)+ str(now.month)+ str(now.day)+ str(now.hour) + str(now.minute)
    log_dir_name = os.getcwd() + "/" + args + "_" + str(unique_str)
    os.system("mkdir -p " + log_dir_name)
    os.system("mkdir -p " + log_dir_name + "/fio_logs")
    return log_dir_name

def remote_collect_stop(nodes, args=None):
    for n in nodes:
        execute_push_on_a_node(n, "finisher.sh", args)

def collect_all_stats(nodes, load, args):
    local_loc_dir = args[1]
    test_suffix = args[0]

    print "collect_all_stats: Copying all stats to %s" %(local_loc_dir)
    print args

    for n in nodes:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.load_system_host_keys()
        ssh.connect(hostname=n, port=22, username='ems', password='ems123')

        file_name = "ifos_logs." + n + "." + test_suffix + ".tar.gz"
        remote_loc = "/home/ems/vishalk/" + file_name
        local_loc = local_loc_dir + "/" + file_name

        sftp = ssh.open_sftp()
        print "SFTP from %s to %s" %(remote_loc, local_loc)
        sftp.get(remote_loc, local_loc)
        sftp.close()

        ssh.close()

if __name__ == "__main__":
    nodes = ["iflab1", "iflab2"]
    client_node = "iflab10"
    #load_profile = ["read", "write", "randrw"]
    #block_sz = ["4k", "16k", "64k", "256k", "1024k", "4m", "16m"]
    load_profile = ["read"]
    block_sz = ["4k", "1m"]
    time = "5"
    num_fio = "1"

    for load in load_profile:
        for blk_sz in block_sz:
            test_suffix_name = load + "_" + blk_sz
            log_path = create_log_path(test_suffix_name)
            args = []
            args.append(str(test_suffix_name))
            args.append(str(log_path))
            print "Prepared list" + str(args)
            remote_collect_start(nodes, args[0])

            #
            execute_fio(client_node, load, blk_sz, time, num_fio, args[1])

            #
            remote_collect_stop(nodes, args[0])
            collect_all_stats(nodes, load, args)
    print "Exiting Main Thread"
