#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

#include "simplefs.h"

#define WRITE 1
#define READ 0
#define MAX_NAMELEN 16

int allocation_block_count(int offset, int len, int block_size)
{
    int start_blk = offset / block_size + 1;

    if (len < block_size) {
        return 1;
    } else {
        return (len/block_size + 1);
    }
}


int allocate_block(struct fs_meta_t *fs, int offset, int len)
{
    pthread_rwlock_wrlock(&fs->sb->lock);
    int needed_block;
    //needed_block = allocation_block_count(len);
    pthread_rwlock_unlock(&fs->sb->lock); 
}


void populate_superblock(struct fs_meta_t *fs, 
        int num_blocks,
        int num_inodes,
        int block_size)
{
    struct superblock_t *sb = fs->sb;

    // Starting 1 block is reserved for super blocks
    //
    sb->lock = PTHREAD_RWLOCK_INITIALIZER;
    sb->num_blocks = num_blocks;
    sb->num_inodes = num_inodes;
    sb->block_size = block_size;
    sb->num_used_inode = 0;
    sb->data_block_start = 1;
}

void init_file_table(struct fs_meta_t *fs, int num_entries)
{
    struct file_table_t *file_table = fs->file_table;

    file_table = (struct file_table_t*) malloc(sizeof(struct file_table_t));
    file_table->entries = (struct file_table_entry_t *) malloc(sizeof(struct file_table_entry_t) * num_entries);
    file_table->lock = PTHREAD_RWLOCK_INITIALIZER;
    file_table->num_entries = 0;
}

void init_fd_table(struct fs_meta_t *fs, int num_entries)
{
    struct fd_table_t *fd_table = fs->fd_table;
    fd_table = (struct fd_table_t*) malloc(sizeof(struct fd_table_t));
    fd_table->entries = (struct fd_info_t*) malloc(sizeof(struct fd_info_t) * (10*num_entries));
    fd_table->lock = PTHREAD_RWLOCK_INITIALIZER;
    fd_table->num_entries = 0;
}

void init_inode_table(struct fs_meta_t *fs, int num_entries)
{
    struct inode_table_t *inode_table = fs->inode_table;
    inode_table = (struct inode_table_t*) malloc(sizeof(struct inode_table_t));
    inode_table->inodes = (struct inode_t*)malloc(sizeof(struct inode_t) * num_entries);
}

struct fs_meta_t *fs;

int update_ondisk(struct fs_meta_t *fs, void *src, int offset, int len)
{
    int ret = -1;
    ret = pwrite(fs->fd, (char*)src, offset, len);
    fsync(fs->fd);

    return ret;
}

int create_fs(char *filename, int size, int block_size, int inodes)
{
    int ret = -1;
    int fd;

    fd = open(filename, O_CREAT| O_RDWR|O_TRUNC); 
    if (fd < 0)
        return fd;
   
    fs = (struct fs_meta_t*) malloc(sizeof(struct fs_meta_t));
    fs->fd = fd;

    int num_blocks = size / block_size;

    populate_superblock(fs, num_blocks, inodes, block_size);
    init_inode_table(fs, inodes);
    init_file_table(fs, inodes);
    init_fd_table(fs, inodes);

    ret = write(fd, fs->sb, sizeof(struct superblock_t));
    fs->abs_offset[0] = ret;
    ret = write(fd, fs->inode_table, sizeof(struct inode_table_t));
    fs->abs_offset[1] = fs->abs_offset[0] + ret;
    ret = write(fd, fs->file_table, sizeof(struct file_table_t));
    fs->abs_offset[2] = fs->abs_offset[1] + ret;

    fsync(fd);
}

int get_next_free_inode(fs_meta_t *fs)
{
    return fs->sb->num_used_inode++;
}

int inode_table_add_entry(fs_meta_t *fs)
{
    // superblock is already write locked
    int ino;
    ino = get_next_free_inode(fs);
    if (ino < 0) {
        return -1;
    }

    // create an entry in inode table
    struct inode_t *inode_info = &(fs->inode_table->inodes[ino]);
    pthread_rwlock_wrlock(&inode_info->lock);
    inode_info->size = 0;
    inode_info->owner = 0;
    pthread_rwlock_unlock(&inode_info->lock);

    fsync(fs->fd);
    return ino;
}


int file_table_add_entry(fs_meta_t *fs, char *filename, int inode)
{
    pthread_rwlock_wrlock(&fs->file_table->lock);
    int index = fs->file_table->num_entries;

    strncpy(fs->file_table->entries[index].file_name, filename, MAX_NAMELEN);
    fs->file_table->entries[index].inode = inode;
    pthread_rwlock_unlock(&fs->file_table->lock);
}

int fd_table_lookup(struct fs_meta_t *fs, int fd)
{
    struct fd_info_t *fd_entry;
    int inode = -1;

    pthread_rwlock_rdlock(&fs->fd_table->lock);

    fd_entry = &(fs->fd_table->entries[fd]);

    if (fd_entry->valid == 1 &&
        fd < fs->fd_table->num_entries) {
        inode = fd_entry->inode;
    }
    pthread_rwlock_unlock(&fs->fd_table->lock);
    return inode;
}


struct fd_info_t* fd_table_get_entry(struct fs_meta_t *fs, int fd)
{
    struct fd_info_t *fd_entry;

    pthread_rwlock_rdlock(&fs->fd_table->lock);

    fd_entry = &(fs->fd_table->entries[fd]);

    if (fd_entry->valid == 1 &&
        fd < fs->fd_table->num_entries) {
        return fd_entry;
    }
    return NULL;
}


int fd_table_add_entry(struct fs_meta_t *fs, int inode, int mode)
{
    struct fd_info_t *fd_entry;
    int fd = -1;

    pthread_rwlock_rdlock(&fs->fd_table->lock);
    fd = fs->fd_table->num_entries++;
    fd_entry = &(fs->fd_table->entries[fd]);
    fd_entry->inode = inode;
    fd_entry->offset = 0;
    fd_entry->mode = mode;

    pthread_rwlock_unlock(&fs->fd_table->lock);
    return inode;
}

int is_exiting_block(struct inode_t *ino, int offset, int *block_start, int *block_end)
{

}

int read_modify_write_block(struct inode_t *ino, int block_start,
        int block_end, char *buf, int len)
{

}

int write_data(struct inode_t *ino, int block_start,
        int block_end, char *buf, int len)
{

}

int write(struct fs_meta_t *fs, int fd, char *buf, int len)
{
    int inode;
    struct inode_table_t *inotable;
    struct inode_t *ino;
    int exiting_data = 0;
    int block_start, block_end;
    int offset;
    int ret;

    inode = fd_table_lookup(fs, fd);
    ino = &(fs->inode_table->inodes[inode]);

    // lock inode
    pthread_rwlock_wrlock(&ino->lock);

    // offset = 
   // we don't need any lock on blocks as we already have write lock on
    // inode entry.
    if (is_exiting_block(ino, offset, &block_start, &block_end)) {
        ret = read_modify_write_block(ino, block_start, block_end, buf, len);
    } else {
        // XXX: handle multiple blocks write
        // Lock super block to get write protected data blocks
        ret = write_data(ino, block_start, block_end, buf, len);
    }

    ino->data_blocks[ino->num_blocks++] = block_start;
    ino->size += len;
    pthread_rwlock_unlock(&ino->lock);

    return ret;
}

int get_data(struct inode_t *ino, char *buf, int offset,
        int len, int start_blk, int end_blk)
{

}

int offset_to_block(struct inode_t *ino, int offset, int len,
      int *block_start, int *block_end)
{
}

int read(struct fs_meta_t *fs, int fd, char *buf, int len)
{
  int inode;
  struct inode_table_t *inotable;
  struct inode_t *ino;
  int block_start, block_end;
  int offset;
  struct fd_info_t *fd_entry;
  int ret = -1;

  fd_entry = fd_table_get_entry(fs, fd);
  if (fd_entry == NULL) {
      pthread_rwlock_unlock(&fs->fd_table->lock);
      return -1;
  }
  ino = &(fs->inode_table->inodes[inode]);

  // lock inode
  pthread_rwlock_rdlock(&ino->lock);
  offset = fd_entry->offset;
  int block = offset_to_block(ino, offset, len, &block_start, &block_end);
  ret = get_data(ino, buf, offset, len, block_start, block_end);
  offset += len;

  pthread_rwlock_unlock(&fs->fd_table->lock);
  pthread_rwlock_unlock(&ino->lock);
}

int update_fd_table(struct fs_meta_t *fs, int fd)
{
}

int seek(struct fs_meta_t *fs, int fd, int offset)
{
  int inode;
  struct inode_table_t *inotable;
  struct inode_t *ino;
  int valid_offset;
  struct fd_info_t *fd_entry;

  fd_entry = fd_table_get_entry(fs, fd);
  inode = fd_entry->inode;

  ino = &(fs->inode_table->inodes[inode]);

  // lock inode
  pthread_rwlock_rdlock(&ino->lock);
  if (ino->size < offset)
    valid_offset = ino->size;
  pthread_rwlock_unlock(&ino->lock);

  update_fd_table(fs, offset);
}

int get_next_ino(struct fs_meta_t *fs)
{
    if(fs->sb->num_used_inode <= fs->sb->num_inodes)
        return fs->sb->num_used_inode++;
    return -1;    
}

int create(struct fs_meta_t *fs, char *filename, int mode)
{
    int ret = 0;
    int fd = -1;
    int inode = 0;

    pthread_rwlock_wrlock(&fs->sb->lock);

    ret = inode_table_add_entry(fs);
    if (ret < 0)
        goto err;

    inode = ret;
    ret = file_table_add_entry(fs, filename, inode);
    if (ret < 0)
        goto err;

    // get fd for new file
    fd = fd_table_add_entry(fs, inode, mode);
    if (fd < 0)
        goto err;
err:
    pthread_rwlock_unlock(&fs->sb->lock);
    return fd;
}

int search_for_free_slot(struct fd_table_t *fdt)
{
    // traverse all fd entries and find an invalid entry
}

#define MAX_FDS 1024
int create_new_fd(struct fs_meta_t *fs, int inode, int mode)
{
    struct fd_table_t *fdt = fs->fd_table;
    int fd = -1;

    pthread_rwlock_wrlock(&fdt->lock);
    if (fdt->num_entries == MAX_FDS) {
        pthread_rwlock_unlock(&fdt->lock);
        return fd;
    }

    fd = search_for_free_slot(fdt);
    if (fd < 0)
        fd = fdt->num_entries++;
    struct fd_info_t *fd_entry = &(fdt->entries[fd]);
    fd_entry->offset = 0;
    fd_entry->valid = 1;
    fd_entry->inode = inode;
    pthread_rwlock_unlock(&fdt->lock);
    return fd;
}

int lookup_file_table(struct fs_meta_t *fs, char *filename)
{


}

int open(struct fs_meta_t *fs, char *filename, int mode)
{
    int inode;
    int fd = -1;

    if (mode == READ) {
        pthread_rwlock_rdlock(&fs->file_table->lock);
        inode = lookup_file_table(fs, filename);
        if (inode > 0) { // file exists
            fd = create_new_fd(fs, inode, mode);
                return fd;
        }
    }

    if (mode == WRITE) {
        pthread_rwlock_rdlock(&fs->file_table->lock);
        inode = lookup_file_table(fs, filename);
        if (inode > 0) { // file exists
            fd = create_new_fd(fs, inode, mode);
            pthread_rwlock_unlock(&fs->file_table->lock);
            return fd;
        } else { // create file
            pthread_rwlock_unlock(&fs->file_table->lock);
            fd = create(fs, filename, mode);
        }
        return fd;
    }
}

int close (struct fs_meta_t *fs, int fd)
{
    struct fd_table_t *fdt;
    int ret = -1;
    int inode = 0;

    pthread_rwlock_rdlock(&fs->file_table->lock);
    fdt = fs->fd_table;
    pthread_rwlock_wrlock(&fdt->lock);

    struct fd_info_t *fd_entry = &(fdt->entries[fd]);
    if (fd_entry->valid) {
        fd_entry->offset = 0;
        fd_entry->valid = 0;
        fd_entry->inode = 0;
        ret = 0;
    }
    pthread_rwlock_unlock(&fdt->lock);
    pthread_rwlock_unlock(&fs->file_table->lock);
    return ret;
}

int main()
{
    int ret;
    ret = create_fs("/tmp/myfs", 4096*16, 1024, 16);
    if (ret != 0)
        printf("Failed to create the file system err=%d\n", ret);
    return ret;    
}
