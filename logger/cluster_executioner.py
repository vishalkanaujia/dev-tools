#!/usr/bin/python

from threading import Thread
import time
import paramiko
import datetime
import os
import sys

class FIOWorker(Thread):
    def __init__(self, args, index):
        Thread.__init__(self)
        self.args = args
        self.index = index

    def run(self):
        n = self.args["node"]
        block_sz = self.args["block_sz"]
        index = self.index
        mount_name = self.args["mount_name"]
        size = self.args["size"]

        if self.args["type"] =="prepare":
            prepare_fio(n, block_sz, index, mount_name, size)
            return

        if self.args["type"] =="execute":
            load = self.args["load"]
            time = self.args["time"]
            log_path = self.args["log_path"]
            fio_threads = self.args["fio_threads"]

            execute_fio(n, load, block_sz, time, \
                     log_path, index, mount_name, size, fio_threads)
        else:
            print "Illegal type %s passed" %(self.args["type"])
            sys.exit(-1)
        
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

def prepare_fio_worker(n, block_sz, mount_name, size):
    threads = []
    index = 1
    for node in n:
        worker = prepare_fio_worker_internal(node, block_sz, index,
                                 mount_name, size)
        threads += [worker]
        index = index + 1

    for worker in threads:
        print "Starting: prepare: node=%s thread = %s" %(node, str(worker))
        worker.start()

    for t in threads:
        print "Node=%s: Start waiting for thread %s" %(node, str(t))
        t.join()
        print "End waiting for thread %s" %(str(t))

def prepare_fio_worker_internal(n, block_sz, index, mount_name, size):
    args = {}
    args["type"] = "prepare"
    args["node"] = n
    args["block_sz"] = block_sz
    args["mount_name"] = mount_name
    args["size"] = size

    args["index"] = str(index)
    worker = FIOWorker(args, str(index))

    return worker

def execute_fio_worker(n, load, block_sz, time, num_fio,
                       log_path, mount_name, size, fio_threads):
    threads = []
    index = 1
    for node in n:
        worker = execute_fio_worker_internal(node, load, block_sz, time, index,
                      log_path, mount_name, size, fio_threads)
        threads += [worker]
        index = index + 1

    for worker in threads:
        worker.start()

    for t in threads:
        print "Start waiting for thread %s" %(str(t))
        t.join()
        print "End waiting for thread %s" %(str(t))

    #print('Took {}'.format(time() - ts))

def execute_fio_worker_internal(n, load, block_sz, time, index,
                       log_path, mount_name, size, fio_threads):
    args = {}
    args["type"] = "execute"
    args["node"] = n
    args["load"] = load
    args["block_sz"] = block_sz
    args["time"] = time
    args["log_path"] = log_path
    args["mount_name"] = mount_name
    args["size"] = size
    args["fio_threads"] = fio_threads
    args["index"] = str(index)

    worker = FIOWorker(args, str(index))

    return worker

def clean_up_mount_point(n):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
    ssh.load_system_host_keys()

    ssh.connect(hostname=n, port=22, username='ems', password='ems123')

    fio_script_path = "fio_cleaner.sh"

    new_script_path = "/tmp/" + fio_script_path
    sub_cmd = "chmod +x " + new_script_path + ";"
 
    #cmd = sub_cmd + "bash -x  -x "
    cmd = sub_cmd + "bash -x  "
    cmd = cmd + new_script_path
    print "Running fio cmd = " + cmd

    stdin, stdout, stderr = ssh.exec_command(cmd)

    print "Execute cleanup stdout from node:%s" %(n)
    print_lines(stderr.readlines())
    print "cleanup stdout: ", stdout.readlines()
    print_lines(stdout.readlines())

    ssh.close()

def copy_script(node, script_path):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
    ssh.load_system_host_keys()

    ssh.connect(hostname=node, port=22, username='ems', password='ems123')

    ssh_remote_run(ssh, script_path)
    ssh.close()

def execute_fio(n, load, block_sz, time, log_path,
                index, mount_name, size, fio_threads):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
    ssh.load_system_host_keys()

    ssh.connect(hostname=n, port=22, username='ems', password='ems123')

    fio_script_path = "fio_runner.sh"

    new_script_path = "/tmp/" + fio_script_path
    sub_cmd = "chmod +x " + new_script_path + ";"
 
    cmd = sub_cmd + "bash -x  "
    cmd = cmd + new_script_path + " " + load + " " + block_sz + " " + \
            time + " " + fio_threads + " " + log_path + " " + index \
          + " "  + mount_name + " " + size

    print "Running fio cmd = " + cmd

    stdin, stdout, stderr = ssh.exec_command(cmd)

    print "Execute FIO stdout from node:%s" %(n)
    print "fio stderr: "
    print_lines(stderr.readlines())
    print "fio stdout: ", stdout.readlines()
    print_lines(stdout.readlines())

    ssh.close()

def prepare_fio(n, block_sz, index, mount_name, size):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy()) 
    ssh.load_system_host_keys()

    ssh.connect(hostname=n, port=22, username='ems', password='ems123')

    fio_script_path = "fio_prepare.sh"

    new_script_path = "/tmp/" + fio_script_path
    sub_cmd = "chmod +x " + new_script_path + ";"
 
    cmd = sub_cmd + "bash -x  "
    cmd = cmd + new_script_path + " " + block_sz + " " + index \
          + " " + mount_name + " " + size

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

log_cwd = ""
def create_log_path(args):
    now = datetime.datetime.now()
    unique_str = str(now.year)+ str(now.month)+ str(now.day)+ str(now.hour) + str(now.minute)
    #log_dir_name = os.getcwd() + "/" + args + "/" + args + "_" + str(unique_str)
    log_dir_name = args + "_" + str(unique_str)
    log_cwd = os.getcwd() + "/" + args + "/" + log_dir_name
    os.system("mkdir -p " + log_cwd)
    return log_dir_name

def remote_collect_stop(nodes, args=None):
    for n in nodes:
        execute_push_on_a_node(n, "finisher.sh", args)

def remote_collect_stop_client(nodes, args=None):
    for n in nodes:
        execute_push_on_a_node(n, "client_finisher.sh", args)

def collect_all_stats(nodes, load, args):
    local_loc_dir = args[1]
    test_suffix = args[0]
    log_cwd = os.getcwd() + "/" + args[0] + "/" + args[1]
    print "collect_all_stats: Copying all stats to %s" %(local_loc_dir)
    print args

    for n in nodes:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.load_system_host_keys()
        ssh.connect(hostname=n, port=22, username='ems', password='ems123')

        file_name = "ifos_logs." + n + "." + test_suffix + ".tar.gz"
        remote_loc = "/home/ems/vishalk/" + file_name
        local_loc = log_cwd + "/" + file_name

        sftp = ssh.open_sftp()
        print "SFTP from %s to %s" %(remote_loc, local_loc)
        sftp.get(remote_loc, local_loc)
        sftp.close()

        ssh.close()

def collect_all_stats_client(nodes, load, args):
    local_loc_dir = args[1]
    test_suffix = args[0]
    log_cwd = os.getcwd() + "/" + args[0] + "/" + args[1]

    print "collect_all_stats: Copying all stats to %s" %(local_loc_dir)
    print args

    for n in nodes:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.load_system_host_keys()
        ssh.connect(hostname=n, port=22, username='ems', password='ems123')

        file_name = "client_logs.fio." + n + "." + local_loc_dir + ".tar.gz"
        remote_loc = "/home/ems/vishalk/" + file_name
        local_loc = log_cwd + "/" + file_name

        sftp = ssh.open_sftp()
        print "SFTP from %s to %s" %(remote_loc, local_loc)
        sftp.get(remote_loc, local_loc)
        sftp.close()

        ssh.close()

if __name__ == "__main__":
    if len(sys.argv) < 6:
        print "python executioner.py <runtype=prepare/run> <fio thread> <time> <mount> <size=1g>"
        sys.exit(-1)

    #fio_jobs = sys.argv[1]
    runtype = sys.argv[1]
    fio_threads = sys.argv[2]
    time = sys.argv[3]
    mount_name = sys.argv[4]
    size = sys.argv[5]

    #nodes = ["iflab1", "iflab2", "iflab3", "iflab4", "iflab12"]
    #client_node = ["iflab12", "iflab10", "iflab1", "iflab2", "iflab3", "iflab4"]
    client_node = ["iflab12", "iflab10"]
    nodes = ["iflab1"]# "iflab2", "iflab3", "iflab4"]

    load_profile = ["randread"]
    fio_jobs = len(client_node)

    #block_sz = ["4k", "64k", "4m"]
    #load_profile = ["read"]
    block_sz = ["4k"]
    prepare_blk_sz = "4mb"

    scripts = ["fio_prepare.sh", "fio_runner.sh", "fio_cleaner.sh", "client_finisher.sh"]

    for node in client_node:
        for script in scripts:
            copy_script(node, script)

    if runtype == "prepare":
        clean_up_mount_point(client_node[0])

        #prepare_client_set = ["iflab12", "iflab10", "iflab1", "iflab2"]

        prepare_fio_worker(client_node, prepare_blk_sz, mount_name, size)
        print "Prepare is done"
        exit(0)

    for blk_sz in block_sz:
        for load in load_profile:
            test_suffix_name = load + "_" + blk_sz
            log_path = create_log_path(test_suffix_name)
            args = []
            args.append(str(test_suffix_name))
            args.append(str(log_path))
            print "Prepared list" + str(args)

            #
            remote_collect_start(nodes, args[1])
            execute_fio_worker(client_node, load, blk_sz, time,
                           fio_jobs, args[1], mount_name, size, fio_threads)
            #
            remote_collect_stop(nodes, args[1])
            remote_collect_stop_client(client_node, args[1])
            collect_all_stats(nodes, load, args)
            collect_all_stats_client(client_node, load, args)
    print "Exiting Main Thread"
