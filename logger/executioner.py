#!/usr/bin/python

import threading
import time
import paramiko

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

def execute_fio(n, load, block_sz, time, num_fio):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
    ssh.load_system_host_keys()

    ssh.connect(hostname=n, port=22, username='ems', password='ems123')

    fio_script_path = "fio_runner.sh"
    ssh_remote_run(ssh, fio_script_path)

    new_script_path = "/tmp/" + fio_script_path
    sub_cmd = "chmod +x " + new_script_path + ";"
 
    cmd = sub_cmd + new_script_path + " " + load + " " + block_sz + " " + time + " " + num_fio
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
        cmd = new_remote_script_path + " " +args
    else:
        cmd = new_remote_script_path

    cmd = sub_cmd + "bash " + cmd
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

def remote_collect_stop(nodes, args=None):
    for n in nodes:
        execute_push_on_a_node(n, "finisher.sh")
    
if __name__ == "__main__":
    nodes = ["iflab1", "iflab2"]
    client_node = "iflab10"
    #load_profile = ["read", "write", "randrw"]
    #block_sz = ["4k", "16k", "64k", "256k", "1024k", "4m", "16m"]
    load_profile = ["read" ]
    block_sz = ["4k", "16k"]
    time = "3"
    num_fio = "1"

    for load in load_profile:
        for blk_sz in block_sz:
            test_suffix_name = load + "_" + blk_sz
            remote_collect_start(nodes, test_suffix_name)
            execute_fio(client_node, load, blk_sz, time, num_fio)
            remote_collect_stop(nodes, None)
    print "Exiting Main Thread"
