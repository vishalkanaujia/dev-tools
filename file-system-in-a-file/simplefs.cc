#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

#include "simplefs.h"

static int allocate_block(struct fs_meta_t *fs)
{
    if (fs->sb->cur_block > fs->sb->num_blocks) {
        return -1;
    }
    return (++(fs->sb->cur_block));
}


static int init_blocks(struct fs_meta_t **fs)
{
    (*fs)->sb->cur_block = 2;    
    // Available blocks are from 2...num_blocks
}


static void populate_superblock(struct fs_meta_t **fs, 
        int num_blocks,
        int num_inodes,
        int block_size)
{
    struct superblock_t *sb = (*fs)->sb;

    // Starting 1 block is reserved for super blocks
    //
    sb->lock = PTHREAD_RWLOCK_INITIALIZER;
    sb->num_blocks = num_blocks;
    sb->num_inodes = num_inodes;
    sb->block_size = block_size;
    sb->num_used_inode = 0;
}

static void init_file_table(struct fs_meta_t **fs, int num_entries)
{
    struct file_table_t *file_table = (*fs)->file_table;

    file_table->entries = (struct file_table_entry_t *) malloc(sizeof(struct file_table_entry_t) * num_entries);
    file_table->lock = PTHREAD_RWLOCK_INITIALIZER;
    file_table->num_entries = 0;
}

static void init_fd_table(struct fs_meta_t **fs, int num_entries)
{
    struct fd_table_t *fd_table = (*fs)->fd_table;
    fd_table->entries = (struct fd_info_t*) malloc(sizeof(struct fd_info_t) * MAX_FD);
    fd_table->lock = PTHREAD_RWLOCK_INITIALIZER;
    fd_table->num_entries = MAX_FD;
}

void init_inode_table(struct fs_meta_t **fs, int num_entries)
{
    (*fs)->inode_table->inodes = (struct inode_t*) malloc(sizeof(struct inode_t) * num_entries);
}

struct fs_meta_t *fs;

static int update_ondisk(struct fs_meta_t *fs, void *src, int offset, int len)
{
    int ret = -1;
    ret = pwrite(fs->fd, (char*)src, offset, len);
    fsync(fs->fd);

    return ret;
}

int create_fs(struct fs_meta_t **fs, const char *filename, int size, int block_size, int inodes)
{
    int ret = -1;
    int fd;


    fd = open(filename, O_CREAT|O_RDWR|O_TRUNC); 
    if (fd < 0)
        return fd;

    *fs = (struct fs_meta_t*) malloc(sizeof(struct fs_meta_t));

    (*fs)->fd = fd;
    (*fs)->sb = (struct superblock_t*) malloc(sizeof(struct superblock_t));

    int num_blocks = size / block_size;

    populate_superblock(fs, num_blocks, inodes, block_size);
    init_blocks(fs);

    (*fs)->file_table = (struct file_table_t*) malloc(sizeof(struct file_table_t));
    (*fs)->inode_table = (struct inode_table_t*) malloc(sizeof(struct file_table_t));
    (*fs)->fd_table = (struct fd_table_t*) malloc(sizeof(struct fd_table_t));
    init_inode_table(fs, inodes);
    init_file_table(fs, inodes);
    init_fd_table(fs, inodes);

    ret = write(fd, (*fs)->sb, sizeof(struct superblock_t));
    fsync(fd);
}

static int get_next_free_inode(fs_meta_t *fs)
{
    if (fs->sb->num_used_inode >= fs->sb->num_inodes)
        return -1;
    return fs->sb->num_used_inode++;
}

static int inode_table_add_entry(fs_meta_t *fs)
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


static int file_table_add_entry(fs_meta_t *fs, char *filename, int inode)
{
    pthread_rwlock_wrlock(&fs->file_table->lock);
    //int index = fs->file_table->num_entries;
    int index = inode;

    strncpy(fs->file_table->entries[index].file_name, filename, MAX_NAMELEN);
    fs->file_table->entries[index].inode = inode;
    pthread_rwlock_unlock(&fs->file_table->lock);
}

static int fd_table_lookup(struct fs_meta_t *fs, int fd)
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


static struct fd_info_t* fd_table_get_entry(struct fs_meta_t *fs, int fd)
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

static int get_free_fd_slot(struct fs_meta_t *fs)
{
    int i = 0;
    //int n = fs->fd_table->num_entries;
    int n = MAX_FD;
    struct fd_info_t *fd_entry;

    for (i = 0; i < n; i++) {    
        fd_entry = &(fs->fd_table->entries[i]);
        if (fd_entry->valid == 0)
            return i;
    }
}

static int fd_table_add_entry(struct fs_meta_t *fs, int inode, int mode)
{
    struct fd_info_t *fd_entry;
    int fd = -1;

    pthread_rwlock_rdlock(&fs->fd_table->lock);
    //fd = fs->fd_table->num_entries++;
    fd = get_free_fd_slot(fs);
    fd_entry = &(fs->fd_table->entries[fd]);
    fd_entry->inode = inode;
    fd_entry->offset = 0;
    fd_entry->mode = mode;
    fd_entry->valid = 1;

    pthread_rwlock_unlock(&fs->fd_table->lock);
    return inode;
}

static int read_data(struct fs_meta_t *fs, struct inode_t *ino, int block_id,
        int block_offset, char *buf, int len)
{
    // search for the requested block in inode
    int i;
    int flag = 0;
    int phy_block_id;
    int offset;
    int ret = 0;

    if (block_id < ino->num_blocks) {
        phy_block_id = ino->data_blocks[block_id];
    } else {
        return -1;
    }

    // read data
    offset = block_offset + (phy_block_id * fs->sb->block_size);

    if (len <= 0)
        return 0;

    ret = pread(fs->fd, buf, len, offset);
    return ret;
}

static int write_data(struct fs_meta_t *fs, struct inode_t *ino, int block_id,
        int block_offset, char *buf, int len)
{
    // search for the requested block in inode
    int i;
    int flag = 0;
    int phy_block_id;
    int offset;
    int ret = 0;

    if (block_id < ino->num_blocks) {
        phy_block_id = ino->data_blocks[block_id];
    } else {
        // allocate block
        phy_block_id = allocate_block(fs);
        if (phy_block_id < 0) {
            return -1;
        }
        // add to inode
        ino->data_blocks[ino->num_blocks++] = phy_block_id;
    }

    // update data
    offset = block_offset + (phy_block_id * fs->sb->block_size);
    ret = pwrite(fs->fd, buf, len, offset);
    return ret;
}

int write_file(struct fs_meta_t *fs, int fd, char *buf, int blen)
{
    int inode;
    struct inode_table_t *inotable;
    struct inode_t *ino;
    int exiting_data = 0;
    int block_start, block_end;
    int offset;
    int ret = 0;
    int len = blen;

    struct fd_info_t *fd_entry;

    inode = fd_table_lookup(fs, fd);

    fd_entry = &(fs->fd_table->entries[fd]);

    // Get inode structure entry
    ino = &(fs->inode_table->inodes[inode]);

    // lock inode
    pthread_rwlock_wrlock(&ino->lock);

    // map offset to block #
    offset = fd_entry->offset;
    int i = 0;
    int wrote = 0;
    int block_id;
    int block_offset = offset % fs->sb->block_size;
    int bytes = 0;

    // we already have write lock on inode entry.
    while (len) {
        if (block_offset + len > fs->sb->block_size) {
            // multi block or a partial write
            //
            wrote = (block_offset + len) % fs->sb->block_size;
            block_id = offset / fs->sb->block_size;
            offset += wrote;
            len -= wrote;
        } else if (offset + len <= fs->sb->block_size) {
            wrote = len;
            block_id = offset / fs->sb->block_size;
            len -= wrote;
            offset += wrote;
        }
        if (wrote <= 0)
          break;

        bytes = write_data(fs, ino, block_id, block_offset, buf, wrote);
        if (ret < 0)
            break;
        ret = ret + bytes;
        block_offset = (offset + wrote) % fs->sb->block_size;
    }

    if (ret != blen) {
        ret = -1;
    } else {
        ino->size += blen;
        fd_entry->offset += blen;
    }
err:
    pthread_rwlock_unlock(&ino->lock);
    return ret;
}

int read_file(struct fs_meta_t *fs, int fd, char *buf, int blen)
{
    int inode;
    struct inode_table_t *inotable;
    struct inode_t *ino;
    int exiting_data = 0;
    int block_start, block_end;
    int offset;
    int ret = 0;
    int len = blen;

    struct fd_info_t *fd_entry;

    inode = fd_table_lookup(fs, fd);

    fd_entry = &(fs->fd_table->entries[fd]);

    // Get inode structure entry
    ino = &(fs->inode_table->inodes[inode]);

    // lock inode
    pthread_rwlock_rdlock(&ino->lock);

    // map offset to block #
    offset = fd_entry->offset;
    int i = 0;
    int wrote = 0;
    int block_id;
    int block_offset = offset % fs->sb->block_size;
    int bytes = 0;

    // we already have write lock on inode entry.
    while (len) {
        if (block_offset + len > fs->sb->block_size) {
            // multi block or a partial write
            //
            wrote = (block_offset + len) % fs->sb->block_size;
            block_id = offset / fs->sb->block_size;
            offset += wrote;
            len -= wrote;
        } else if (offset + len <= fs->sb->block_size) {
            wrote = len;
            block_id = offset / fs->sb->block_size;
            len -= wrote;
            offset += wrote;
        }

        if (wrote <= 0)
            break;

        bytes = read_data(fs, ino, block_id, block_offset, buf, wrote);
        if (bytes <= 0)
            break;
        ret += bytes;    
        block_offset = (offset + wrote) % fs->sb->block_size;
    }

    if (ret != blen) {
        ret = -1;
    } else {
        fd_entry->offset += blen;
    }
err:
    pthread_rwlock_unlock(&ino->lock);
    return ret;
}

static int update_fd_table(struct fs_meta_t *fs, int fd)
{
    struct fd_table_t *fdt;
    int ret = -1;
    int inode = 0;

    fdt = fs->fd_table;
    pthread_rwlock_wrlock(&fdt->lock);

    struct fd_info_t *fd_entry = &(fdt->entries[fd]);
    if (fd_entry->valid) {
        fd_entry->offset = 0;
        ret = 0;
    }
    pthread_rwlock_unlock(&fdt->lock);
    return ret;
}

int seek_file(struct fs_meta_t *fs, int fd, int offset)
{
    int inode;
    struct inode_table_t *inotable;
    struct inode_t *ino;
    int valid_offset;
    struct fd_info_t *fd_entry;

    fd_entry = fd_table_get_entry(fs, fd);
    inode = fd_entry->inode;

    ino = &(fs->inode_table->inodes[inode]);

    // lock inode to test valid offset to seek
    pthread_rwlock_rdlock(&ino->lock);
    if (ino->size < offset)
        valid_offset = ino->size;
    pthread_rwlock_unlock(&ino->lock);
    pthread_rwlock_unlock(&fs->fd_table->lock);

    update_fd_table(fs, offset);
}

static int get_next_ino(struct fs_meta_t *fs)
{
    if(fs->sb->num_used_inode <= fs->sb->num_inodes)
        return fs->sb->num_used_inode++;
    return -1;    
}

static int create(struct fs_meta_t *fs, char *filename, int mode)
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

static int search_for_free_slot(struct fd_table_t *fdt)
{
    // traverse all fd entries and find an invalid entry
}

static int create_new_fd(struct fs_meta_t *fs, int inode, int mode)
{
    struct fd_table_t *fdt = fs->fd_table;
    int fd = -1;

    pthread_rwlock_wrlock(&fdt->lock);

    fd = get_free_fd_slot(fs);

    struct fd_info_t *fd_entry = &(fdt->entries[fd]);
    fd_entry->offset = 0;
    fd_entry->valid = 1;
    fd_entry->inode = inode;
    pthread_rwlock_unlock(&fdt->lock);

    return fd;
}

int lookup_file_table(struct fs_meta_t *fs, char *filename)
{
    int i;
    struct file_table_entry_t *ft = NULL;

    for (i = 0; i < fs->sb->num_inodes; i++) {
        ft = &fs->file_table->entries[i];
        if (0 == strcmp(ft->file_name, filename)) {
            return i;
        }
    }
    return -1;
}

int open_file(struct fs_meta_t *fs, char *filename, int mode)
{
    int inode;
    int fd = -1;

    if (mode == READ) {
        pthread_rwlock_rdlock(&fs->file_table->lock);
        inode = lookup_file_table(fs, filename);
        if (inode >= 0) { // file exists
            fd = create_new_fd(fs, inode, mode);
        }
        pthread_rwlock_unlock(&fs->file_table->lock);
    }

    if (mode == WRITE) {
        pthread_rwlock_rdlock(&fs->file_table->lock);
        inode = lookup_file_table(fs, filename);
        if (inode >= 0) { // file exists
            fd = create_new_fd(fs, inode, mode);
            pthread_rwlock_unlock(&fs->file_table->lock);
            return fd;
        } else { // create file
            pthread_rwlock_unlock(&fs->file_table->lock);
            fd = create(fs, filename, mode);
        }
    }
    return fd;
}

int close_file (struct fs_meta_t *fs, int fd)
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
