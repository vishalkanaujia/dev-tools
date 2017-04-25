#include "simplefs.h"

int main()
{
    struct fs_meta_t *fs;

    int ret;
    ret = create_fs(&fs, "myfs.fs", 4096*4, 1024, 16);
    if (ret != 0) {
        printf("Failed to create the file system err=%d\n", ret);
        exit(0);
    }

    char buf[1024];
    char buf_read[1024];

    // Test 1
    // checks file descriptors
    int fd1 = open_file(fs, "abc.txt", WRITE);
    int fd2 = open_file(fs, "abc.txt", READ);
    int fd3 = open_file(fs, "abc.txt", READ);
    
    assert(fd2 = fd1 + 1);
    assert(fd3 = fd2 + 1);

    int fd4 = open_file(fs, "xyz.txt", READ);
    assert(fd4 < 0);

    // Test 2 
    // Read and writes, data correctness
    memset(buf, 'A', 1024);
    ret = write_file(fs, fd1, buf, 1024);
    if (ret != 1024) {
        printf("Write failed for fd %d\n", fd1);
    }

    ret = read_file(fs, fd2, buf_read, 1024);
    assert(ret == 1024);
    assert(buf_read[0] == 'A');
    
    // Test 2.a. Seek test
    memset(buf, 'B', 1024);
    ret = write_file(fs, fd1, buf, 1024);
 
    ret = seek_file(fs, fd2, 0);
    ret = read_file(fs, fd2, buf_read, 1024);
    assert(buf_read[0] == 'A');

    ret = close_file(fs, fd1);
    ret = close_file(fs, fd2);
    ret = close_file(fs, fd3);
    ret = close_file(fs, fd4);
    assert(ret == -1);

    // Test 3
    // File system boundary tests
    char filename[32];
    int i, fd;

    for (i = 0; i < 15; i++)
    {
        sprintf(filename, "test.%d", i);
        fd = open_file(fs, filename, WRITE);
        printf("fd[%d]= %d\n", i, fd);
        assert(fd >= 0);
    }

    fd = open_file(fs, "boundary.file", WRITE);
    assert(fd == -1);

    for (i = 1; i < 1; i++)
    {
        sprintf(filename, "test.%d", i);
        printf("closing fd[%d]= %d\n", i, fd);
        ret = close_file(fs, fd);
        assert(ret >= 0);
    }
   
    // Test 4
    // Creating a very large file that does not
    // fit in the file system
    fd = open_file(fs, "large_file", WRITE);
    char data[32*1024];
    int len = sizeof(data)/sizeof(char);
    ret = write_file(fs, fd, data, len);
    assert(ret == -1);

    // Test 5
    // Multi threading test case
    // To DO

    return 0;
}
