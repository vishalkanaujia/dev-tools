#!/usr/bin/python

from threading import Thread
import time
import paramiko
import datetime
import os
import sys
import subprocess

class SMFWorker(Thread):
    def __init__(self, args, index):
        Thread.__init__(self)
        self.args = args
        self.index = index

    def run(self):
        n = self.args["node"]
        f_sz = self.args["f_sz"]
        index = self.index
        mount_name = self.args["mount"]
        files = self.args["files"]

        op = self.args["op"]
        test_sfx = self.args["test_sfx"]
        smf_threads = self.args["smf_threads"]

        execute_smf(n, op, f_sz, files, smf_threads, mount_name, test_sfx, self.index)

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

def execute_smf_worker(nodes, op, files, f_sz, smf_threads, mount_name, test_sfx):
    i = 1
    threads = []
    for n in nodes:
        args = {}
        args["node"] = n
        args["op"] = op
        args["f_sz"] = str(f_sz)
        args["files"] = str(files)
        args["smf_threads"] = str(smf_threads)
        args["mount"] = mount_name
        args["test_sfx"] = test_sfx
        args["index"] = str(i)

        worker = SMFWorker(args, str(i))
        threads += [worker]
        i = i + 1

    print "total threads=%s" %(str(threads))
 
    for worker in threads:
        worker.start()

    for t in threads:
        print "Start SMF waiting for thread %s" %(str(t))
        t.join()
        print "End SMF waiting for thread %s" %(str(t))

def clean_up_mount_point(n):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()

    ssh.connect(hostname=n, port=22, username='ems', password='ems123')

    fio_script_path = "smf_cleaner.sh"

    new_script_path = "/tmp/" + fio_script_path
    sub_cmd = "chmod +x " + new_script_path + ";"

    cmd = sub_cmd + "bash -x  "
    cmd = cmd + new_script_path
    print "Running smf cleaner = " + cmd

    stdin, stdout, stderr = ssh.exec_command(cmd)

    print "Execute cleanup stdout from node:%s" %(n)
    print_lines(stderr.readlines())
    print "cleanup stdout: ", stdout.readlines()
    print_lines(stdout.readlines())

    ssh.close()

def clean_up_logs(n):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()

    ssh.connect(hostname=n, port=22, username='ems', password='ems123')

    fio_script_path = "smf_log_cleaner.sh"

    new_script_path = "/tmp/" + fio_script_path
    sub_cmd = "chmod +x " + new_script_path + ";"

    cmd = sub_cmd + "bash -x  "
    cmd = cmd + new_script_path
    print "Running smf cleaner = " + cmd

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

def execute_smf(n, op, f_sz, files, smf_threads, mount_name, test_sfx, index):
    script_path = "smf_runner.sh"
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()
    ssh.connect(hostname=n, port=22, username='ems', password='ems123')

    mount_name = mount_name + "/" + str(n)
    mkdir_cmd = "sudo mkdir -p " + mount_name + "; sudo chmod -R 777 " + mount_name + ";"

    new_script_path = "/tmp/" + script_path
    sub_cmd = mkdir_cmd + "chmod +x " + new_script_path + ";"
    cmd = sub_cmd + "bash -x  "
    cmd = cmd + new_script_path + " " + op + " " + n + " " + files + " " + \
            f_sz + " " + smf_threads + " " + mount_name + " " + index + " " + test_sfx

    print "Running smf cmd = " + cmd

    stdin, stdout, stderr = ssh.exec_command(cmd)

    print "Execute SMF stdout from node:%s" %(n)

    print "SMF stderr: "
    print_lines(stderr.readlines())
    print "SMF stdout: ", stdout.readlines()

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

    #print "fio stdout: ", stdout.readlines()
    #print_lines(stdout.readlines())

    ssh.close()

def remote_collect_start(nodes, args=None):
    for n in nodes:
        print "Starting collection on node:" + n
        execute_push_on_a_node(n, 'remote_commands.sh', args)

def create_log_path(args):
    now = datetime.datetime.now()
    sfx = [str(now.year), str(now.month), str(now.day), str(now.hour), str(now.minute)]
    unique_str = ".".join(sfx)
    log_dir_name = os.getcwd() + "/smf/" + str(unique_str)
    #os.system("mkdir -p " + log_dir_name)
    return log_dir_name

def remote_collect_stop_client(nodes, args=None):
    for n in nodes:
        execute_push_on_a_node(n, "smf_finisher.sh", args)

def remote_collect_stop(nodes, args=None):
    for n in nodes:
        execute_push_on_a_node(n, "osd_finisher.sh", args)

def collect_all_stats(nodes, local_dir):
    print "collect_all_stats: Copying all stats to %s" %(local_dir)
    print args

    for n in nodes:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.load_system_host_keys()
        ssh.connect(hostname=n, port=22, username='ems', password='ems123')

        file_name = "ifos_logs." + n + "." + test_suffix + ".tar.gz"
        remote_loc = "/home/ems/vishalk/SMF" + file_name
        local_loc = local_loc_dir + "/" + file_name

        sftp = ssh.open_sftp()
        print "SFTP from %s to %s" %(remote_loc, local_loc)
        sftp.get(remote_loc, local_loc)
        sftp.close()

        ssh.close()

def collect_mds_logs(n):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()

    ssh.connect(hostname=n, port=22, username='ems', password='ems123')

    fio_script_path = "mds-logger.sh"

    new_script_path = "/tmp/" + fio_script_path
    sub_cmd = "chmod +x " + new_script_path + ";"

    cmd = sub_cmd + "bash -x  "
    cmd = cmd + new_script_path
    print "Running MDS logger " + cmd

    stdin, stdout, stderr = ssh.exec_command(cmd)

    print "Execute cleanup stdout from node:%s" %(n)
    print_lines(stderr.readlines())
    print "cleanup stdout: ", stdout.readlines()
    print_lines(stdout.readlines())

    ssh.close()

if __name__ == "__main__":
    if len(sys.argv) < 1:
        print "python executioner.py <mount>"
        sys.exit(-1)

    mount_name = sys.argv[1]

    #nodes = ["iflab1", "iflab2", "iflab3", "iflab4", "iflab12"]
    nodes = ["iflab1", "iflab2", "iflab3", "iflab12"]
    #client_node = ["iflab10", "iflab12"]
    client_node = ["iflab10"] #, "iflab12"]
    mds_node = ["iflab12"]
    ops = ["create", "delete"]
    file_sz = ["1"]
    total_sz_gb = ["2"]
    thread_count = ["32"]
    scripts = ["smf_runner.sh", "smf_finisher.sh", "smf_cleaner.sh", "smf_log_cleaner.sh"]
    '''

    nodes = ["iflab1", "iflab2"]
    client_node = ["iflab12"]

    ops = ["create", "read"]
    file_sz = ["4096"]
    total_sz_gb = ["4"]
    thread_count = ["4"]
    scripts = ["smf_runner.sh", "smf_finisher.sh", "smf_cleaner.sh", "smf_log_cleaner.sh", "mds-logger.sh"]
    '''

    log_path = create_log_path("")
    for script in scripts:
        for n in nodes:
            copy_script(n, script)
        for n in client_node:
            copy_script(n, script)

    clean_up_mount_point(client_node[0])

    for n in nodes:
        clean_up_logs(n)

    for n in client_node:
        clean_up_logs(n)

    collect_mds_logs(mds_node[0]) 
    ii = 0
    for sz in total_sz_gb:
        set_sz = total_sz_gb[ii]
        print "Total size =%s" %(sz)
        for t in thread_count:
            print "Total threads =%s" %(t)
            for f_sz in file_sz:
                files = (int(sz) * 1024 * 1024) / int(f_sz)
                files = files / int(t)
                print "Creating total %s files per thread" %(files)
                for op in ops:
                    test_sfx = set_sz + "g." + op + "." + f_sz + "." + t + "." + sz

                    print "Running test: %s.%s" %(log_path, test_sfx)
                    #
                    remote_collect_start(nodes, test_sfx)

                    execute_smf_worker(client_node, op, files, f_sz, t, mount_name, test_sfx)
                    collect_mds_logs(mds_node[0]) 

                    #
                    remote_collect_stop(nodes, test_sfx)
                    remote_collect_stop_client(client_node, test_sfx)
        ii = ii + 1
    #
    # collect_all_stats(nodes)
    print "Exiting Main Thread"
