/*
 * Simple FS
 */
#ifndef __SIMPLE_FS
#define SIMPLEFS
#endif

#include <pthread.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <assert.h>

#define MAX_FILE_BLOCKS 4096
#define MAX_FD 1024

#define WRITE 1
#define READ 0
#define MAX_NAMELEN 16

struct superblock_t {
    pthread_rwlock_t lock;
    int num_blocks;
    int inode_allocated;
    int num_inodes;
    int num_used_inode;
    int inode_table_offset;
    int block_size;
    int allocated_blocks;
    int cur_block;
};

struct file_table_entry_t {
    char file_name[MAX_NAMELEN];
    int inode;
};

struct file_table_t {
    pthread_rwlock_t lock;
    struct file_table_entry_t *entries;
    int num_entries;
};

struct inode_t {
    int size;
    int owner;
    int data_blocks[MAX_FILE_BLOCKS];
    int num_blocks;
    pthread_rwlock_t lock;
};

struct inode_table_t {
    struct inode_t *inodes;
};

struct fd_table_t {
    struct fd_info_t *entries;
    int num_entries;
    pthread_rwlock_t lock;
};

struct fd_info_t {
    int inode;
    int mode;
    int offset;
    int valid;
};

struct fs_meta_t {
    int fd;
    struct superblock_t *sb;
    struct inode_table_t *inode_table;
    struct file_table_t *file_table;
    struct fd_table_t *fd_table;
    pthread_rwlock_t lock;
};

int create_fs(struct fs_meta_t **fs,
        const char *filename,
        int size,
        int block_size,
        int inodes);


// file ops
int open_file(struct fs_meta_t *fs, char *filename, int mode);
int close_file (struct fs_meta_t *fs, int fd);
int write_file(struct fs_meta_t *fs, int fd, char *buf, int blen);
int read_file(struct fs_meta_t *fs, int fd, char *buf, int blen);
int seek_file(struct fs_meta_t *fs, int fd, int offset);
