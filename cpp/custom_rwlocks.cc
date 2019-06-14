#define _GNU_SOURCE

#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <assert.h>
#include <fcntl.h>
#include <unistd.h>
#include <malloc.h>

#define NUM 512
#define SZ 512

#define DEV "/tmp/xxx"

char s[SZ], d[SZ];
int active_rd = 0, active_wr = 0;
int flag = 0;

#define START 0
#define WRITE 1
#define READ 2
#define READ_WAIT 3

#define atomic_inc(x) (void)__sync_fetch_and_add(&(x), 1);
#define atomic_dec(x) (void)__sync_fetch_and_sub(&(x), 1);
//#define atomic_get(x) __sync_fetch_and_or(&(x), 0)
#define atomic_get(x) (x)
#define atomic_test_and_set(x, old, new)  __sync_val_compare_and_swap(&(x), old, new)

pthread_cond_t cv_r = PTHREAD_COND_INITIALIZER;
pthread_cond_t cv_w = PTHREAD_COND_INITIALIZER;
pthread_mutex_t mx = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t mx_w = PTHREAD_MUTEX_INITIALIZER;

pthread_rwlock_t       rwlock;

__thread int rd = 0;
int wr = 0;
int sum_readers = 0;
int state = START;

static void read_unlock()
{
	--rd;
	assert(!rd);
	atomic_dec(sum_readers);
	//printf("sum_readers=%d\n", sum_readers);

	// Determine if number of readers drop to zero
	if (state == READ_WAIT) {
		if (sum_readers == 0) {
			//printf("read unlock waking writer\n");
			pthread_mutex_lock(&mx);
			pthread_cond_signal(&cv_w);
			pthread_mutex_unlock(&mx);
		}
	}
}

static void read_lock()
{
begin_read_lock:
	assert(!rd);

	if (START == atomic_test_and_set(state, START, READ)) {
		//printf("stderr, read start->read\n");
		(++rd);
		atomic_inc(sum_readers);
		assert(!wr);
		return;
	}

	if (WRITE == state) {
		//printf("stderr, read waiting for write\n");
		pthread_mutex_lock(&mx);
		pthread_cond_wait(&cv_r, &mx);
		pthread_mutex_unlock(&mx);
		// wait for a signal
	}

	if (READ == state) {
		(++rd);
		atomic_inc(sum_readers);
		//printf("stderr, read read->read %d\n", sum_readers);
		assert(!wr);
		return;
	}

	if (READ_WAIT == state) {
		pthread_mutex_lock(&mx);
		pthread_cond_wait(&cv_r, &mx);
		pthread_mutex_unlock(&mx);
		// wait for writer to complete
		//printf("Reader woke up, retrying\n");
	}
	goto begin_read_lock;
}

static void write_lock()
{
	pthread_mutex_lock(&mx);

retry_write_lock:

	if ((START == atomic_test_and_set(state, START, WRITE))) {
		assert(sum_readers == 0);
		goto exit_write_lock;
	}

	if (state == WRITE) {
		pthread_cond_wait(&cv_r, &mx);
	}

	if (state == READ_WAIT) {
		pthread_cond_wait(&cv_r, &mx);
	}

	if (READ == atomic_test_and_set(state, READ, READ_WAIT)) {
		assert(state == READ_WAIT);

		while (sum_readers) {
			// wait while signalled
			pthread_cond_wait(&cv_w, &mx);
		}
		assert(READ_WAIT == atomic_test_and_set(state, READ_WAIT, WRITE));
		assert(sum_readers == 0);
		++wr;
		goto exit_write_lock;
	}

	//printf("writer retrying state=%d sum_readers=%d\n", state, sum_readers);
	goto retry_write_lock;

exit_write_lock:
	printf("Writer started. Readers=%d\n", sum_readers);
	pthread_mutex_unlock(&mx);
}

static void write_unlock()
{
	printf("Writer end. Readers=%d\n", sum_readers);
	if (WRITE == atomic_test_and_set(state, WRITE, START)) {
		--wr;
		pthread_mutex_lock(&mx);
		//pthread_cond_signal(&cv_w);
		pthread_cond_broadcast(&cv_r);
		pthread_mutex_unlock(&mx);
	} else {
		//assert(0);
	}
}


void *stats( void *ptr );
void *reader( void *ptr );
void *writer( void *ptr );

main(int argc, char**argv)
{
	pthread_t thread[NUM];
	const char *message1 = "Thread 1";
	const char *message2 = "Thread 2";
	int  iret[NUM + 1];
	int rc;
	int i;
	int n_threads, n_rd, n_wr;
	int r = 0, w = 0;

	if (argc < 4) {
		fprintf(stderr, "./a.out <stock/custom 0/1> <reader count> <writer count>\n");
		exit(-1);
	}

	flag = atoi(argv[1]);
	n_rd = atoi(argv[2]);
	n_wr = atoi(argv[3]);

	/* Create independent threads each of which will execute function */

	while (r++ < n_rd) {
		pthread_create( &thread[r], NULL, reader, NULL);
	}

	while (w++ < n_wr) {    
		pthread_create( &thread[w], NULL, writer, NULL);
	}

	pthread_create( &thread[r+w], NULL, stats, NULL);

	/* Wait till threads are complete before main continues. Unless we  */
	/* wait we run the risk of executing an exit which will terminate   */
	/* the process and all threads before the threads have completed.   */
	for (i = 0; i< (r+w+1); i++) {
		pthread_join(thread[i], NULL);
	}

	exit(EXIT_SUCCESS);
}

void *stats( void *ptr )
{
	while(1) {
		fprintf(stderr, "rd=%d\n", sum_readers);
		if (atomic_get(wr) > 1)
			assert(0);
		if (atomic_get(active_rd) > 0 && atomic_get(active_wr) != 0)
			assert(0);

		sleep(1);
	}
}

void *reader( void *ptr )
{
	int i, n;
	int fd = 0;

	fd = open(DEV, O_RDONLY | O_DIRECT);
	if (fd < 0) {
		perror("open:");
		assert(0);
	}

	while (1)
	{
		for (i = 0; i < SZ; i++) {
			if(flag == 0) {
				pthread_rwlock_rdlock(&rwlock);
				atomic_inc(active_rd);
			} else {
				read_lock();
			}
			char *buf = memalign(8192, 8192);
			assert(buf);
			n = read(fd, buf, 8192);
			//n = 8192;
			if (n != 8192) {
				assert(0);
			}
			free(buf);

			if(flag == 0) {
				pthread_rwlock_unlock(&rwlock);
				atomic_dec(active_rd);
			} else {
				read_unlock();
			}
		}
	}
}

void *writer( void *ptr )
{
	int i, n;
	int fd = 0;

	fd = open(DEV, O_RDONLY | O_DIRECT);
	if (fd < 0) {
		perror("open:");
		assert(0);
	}

	while (1)
	{
		for (i = 0; i < SZ; i++) {
			if(flag == 0) {
				pthread_rwlock_wrlock(&rwlock);
				atomic_inc(active_wr);
			} else {
				write_lock();
			}

			char *buf = memalign(8192, 8192);
			assert(buf);
			n = read(fd, buf, 8192);
			if (n != 8192) {
				assert(0);
			}
			free(buf);
			if(flag == 0) {
				pthread_rwlock_unlock(&rwlock);
				atomic_dec(active_wr);
			} else {
				write_unlock();
				sleep(5);
			}
		}
	}
}
