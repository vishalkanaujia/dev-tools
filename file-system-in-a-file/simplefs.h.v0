/*
 * Simple FS
 */

#include <pthread.h>

#define MAX_FILE_BLOCKS 4096
#define MAX_SIZE 16

struct superblock_t {
    pthread_rwlock_t lock;
    int num_blocks;
    int inode_allocated;
    int num_inodes;
    int num_used_inode;
    int inode_table_offset;
    int block_size;
    int allocated_blocks;
    int data_block_start;
};

struct file_table_entry_t {
    char file_name[16];
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
    int data_blocks[MAX_SIZE];
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
    int abs_offset[4];
    pthread_rwlock_t lock;
};
// file ops
int open(struct file_meta_t*, char *filename, int mode);
int close(struct file_meta_t*, int fd);
int read(struct file_meta_t*, int fd, char *buffer, int len);
int write(struct file_meta_t*, int fd, char *buffer, int len);
int seek(struct file_meta_t*, int fd, int offset);
