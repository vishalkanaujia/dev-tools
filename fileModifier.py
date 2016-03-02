import os
import sys
from os import walk
import fnmatch
import re

files_list = []

# If you want to skipp _first_ N lines from an existing file
#
lines_to_skip = 8

# Collect all valid files to process
#
def get_file_list(mypath):
    print "Source path= " + mypath

    # We will process *.c and *.h files
    #
    cfile = re.compile("^.*?\.[ch]$")

    for root, directory, filename in walk(mypath):
        for f in filename:
            if cfile.match(f):
                fname = os.path.join(root, f)
                files_list.append(fname)
                print "adding file= " + fname
    return files_list            

# Removes N lines from files
#
def modifier(mypath="."):
    print "In modifier: mypath= " + path
    for f in files_list:
        print "modifier: Processing file= " + str(f)
        fpath = f.rstrip('\n')

        try:
            sfile = open(fpath, "rw+")
            d = sfile.readlines()
            sfile.seek(0);

            for l in d:
                if count <= lines_to_skip:
                    if count == lines_to_skip:
                        print "Found a match!" + str(l)
                else:
                    sfile.write(l)
        except:
            print "File open error=" + fpath
            print "modifier:Unexpected error:", sys.exc_info()[0]
        else:
            print "Closing file: " + fpath
            sfile.truncate()
            sfile.close()


# Add contents of a file to files
#
def appendLicense(mypath, license_file):
    print "license_file= " + license_file

    try:
        lfile = open(license_file, "rw+")
        lic = lfile.readlines()
    except:
        print "appendLicense:License has unexpected error:", sys.exc_info()[0]
        return

    for line in files_list:
        print "append: Processing file=" + str(line)
        fpath = str(line).rstrip('\n')

        try:
            sfile = open(fpath, "rw+")
            d = sfile.readlines()
            sfile.seek(0);

            # Add the license
            for l in lic:
                sfile.write(l)

            for l in d:    
                sfile.write(l)
        except:
            print "File open error=" + fpath
            print "appendLicense: source file Unexpected error:", sys.exc_info()[0]
        else:
            sfile.truncate()
            sfile.close()
    lfile.close()


# Check for a pattern in all lines in a file for all files
#
def checkPattern(fpath, pattern):
    #count = 0
    found = False
    try:
        sfile = open(fpath, "rw+")
        all_lines = sfile.readlines()
        sfile.seek(0);

        for line in all_lines:
            #if count >= 100:
            #    break

            #print "searching for " + pattern + "in " + line 
            if pattern.lower() in line.lower():
                    #print "Found a match!" + str(l)
                    print "Found a match!"
                    found = True
                    break
            #count += 1
        sfile.close()
    except:
        print "File open error=" + fpath
        print "modifier:Unexpected error:", sys.exc_info()[0]
    return found


# Add content only if a pattern does not exist in a given file
#
def appendLicense2(mypath, license_file, pattern):
    print "license_file= " + license_file

    try:
        lfile = open(license_file, "rw+")
        lic = lfile.readlines()
    except:
        print "appendLicense:License has unexpected error:", sys.exc_info()[0]
        return

    for line in files_list:
        print "append: Processing file=" + str(line)
        fpath = str(line).rstrip('\n')

        try:
            # check if a copyright already exist!, if no, add one
            check_pattern = checkPattern(fpath, pattern)

            sfile = open(fpath, "rw+")
            d = sfile.readlines()
            sfile.seek(0);

            # Add the license
            if check_pattern is False:
                for l in lic:
                    sfile.write(l)

            for l in d:
                sfile.write(l)
        except:
            print "File open error=" + fpath
            print "appendLicense: source file Unexpected error:", sys.exc_info()[0]
        else:
            sfile.truncate()
            sfile.close()
    lfile.close()
 
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "Failure: run as following"
        print "$runner.py <directory> <pattern> <file contents to add>"
        exit(0)

    print "Source directory= " + str(sys.argv[1])
    
    path = str(sys.argv[1])
    files_list = get_file_list(path)
    print files_list
    pattern = str(sys.argv[2])
    file_to_add = str(sys.argv[3])
   
    # Add the 'file_to_add' contents to all files only if pattern is not present in the file
    #appendLicense2(path, license_old, pattern)

    # Remove N line(s)
    #modifier(path)

    # Just add the 'file_to_add' contents to all files
    #appendLicense(path, license_new)
