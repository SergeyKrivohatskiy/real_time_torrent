#define FUSE_USE_VERSION 26

#include <fuse.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <dirent.h>
#include <string.h>
#include <errno.h>
#include <sys/time.h>
#include <sys/ipc.h>
#include <sys/msg.h>


#define MAX_PATH_LEN 1024

static char PATH_BUFFER[MAX_PATH_LEN];
static int TORRENTS_DIR_LEN;


static long requests_count = 0;
static int request_queue;
static int responce_queue;

struct read_request
{
	long request_id;
	char request_str[MAX_PATH_LEN + 20]; // for path + offset string. Format: $offset$ $full path$ 
};

struct read_responce
{
	long request_id;
	char responce_str[20]; // For integer value(available bytes)
};

static int on_read(const char *path, off_t offset)
{
	int res;
	int req_len;
	int bytes_allowed;
	struct read_request req;
	struct read_responce resp;
	requests_count += 1;

	req.request_id = requests_count;
	req_len = sprintf(req.request_str, "%zd %s", offset, path);

	res = msgsnd(request_queue, &req, req_len, 0);
	if (res == -1)
	{
		return -EIO; // Can't find better error code
	}
	res = msgrcv(responce_queue, &resp, sizeof(struct read_responce) - sizeof(long), req.request_id, 0);
	if (res == -1)
	{
		return -EIO;
	}

	res = sscanf(resp.responce_str, "%d", &bytes_allowed);
	if (res == -1)
	{
		return -EIO;
	}

	return bytes_allowed;
}

static char* to_real_path(const char *path)
{
	strcpy(PATH_BUFFER + TORRENTS_DIR_LEN, path);
	return PATH_BUFFER;
}

static int callbacks_getattr(const char *path, struct stat *stbuf)
{
	int res;

	res = lstat(to_real_path(path), stbuf);
	if (res == -1)
		return -errno;

	return 0;
}

static int callbacks_access(const char *path, int mask)
{
	int res;

	res = access(to_real_path(path), mask);
	if (res == -1)
		return -errno;

	return 0;
}

static int callbacks_readlink(const char *path, char *buf, size_t size)
{
	int res;

	res = readlink(to_real_path(path), buf, size - 1);
	if (res == -1)
		return -errno;

	buf[res] = '\0';
	return 0;
}


static int callbacks_readdir(const char *path, void *buf, fuse_fill_dir_t filler,
		       off_t offset, struct fuse_file_info *fi)
{
	DIR *dp;
	struct dirent *de;

	(void) offset;
	(void) fi;

	dp = opendir(to_real_path(path));
	if (dp == NULL)
		return -errno;

	while ((de = readdir(dp)) != NULL) {
		struct stat st;
		memset(&st, 0, sizeof(st));
		st.st_ino = de->d_ino;
		st.st_mode = de->d_type << 12;
		if (filler(buf, de->d_name, &st, 0))
			break;
	}

	closedir(dp);
	return 0;
}

static int callbacks_open(const char *path, struct fuse_file_info *fi)
{
	int res;

	res = open(to_real_path(path), fi->flags);
	if (res == -1)
		return -errno;

	close(res);
	return 0;
}

static int callbacks_read(const char *path, char *buf, size_t size, off_t offset,
		    struct fuse_file_info *fi)
{
	int fd;
	int res;

	(void) fi;

	path = to_real_path(path);
	res = on_read(path, offset);
	if (res < 0)
		return res;
	fd = open(path, O_RDONLY);
	if (fd == -1)
		return -errno;

	res = pread(fd, buf, res < size ? res : size, offset);
	if (res == -1)
		res = -errno;

	close(fd);
	return res;
}

static int callbacks_statfs(const char *path, struct statvfs *stbuf)
{
	int res;

	res = statvfs(to_real_path(path), stbuf);
	if (res == -1)
		return -errno;

	return 0;
}

static int callbacks_release(const char *path, struct fuse_file_info *fi)
{
	(void) path;
	(void) fi;
	return 0;
}

static int callbacks_fsync(const char *path, int isdatasync,
		     struct fuse_file_info *fi)
{
	(void) path;
	(void) isdatasync;
	(void) fi;
	return 0;
}

static struct fuse_operations callbacks_oper = {
	.getattr	= callbacks_getattr,
	.access		= callbacks_access,
	.readlink	= callbacks_readlink,
	.readdir	= callbacks_readdir,
	.open		= callbacks_open,
	.read		= callbacks_read,
	.statfs		= callbacks_statfs,
	.release	= callbacks_release,
	.fsync		= callbacks_fsync,
};

int main(int argc, char *argv[])
{
	int fuse_ret;
   	key_t req_key;
   	key_t res_key;
   	char *torrents_dir;

	if (argc < 2)
	{
		perror("argc < 2");
		return -1;
	}
	torrents_dir = argv[1];
	TORRENTS_DIR_LEN = strlen(torrents_dir);
	strcpy(PATH_BUFFER, torrents_dir);
	argc -= 1;
	argv[1] = argv[0];
	argv += 1;

   	req_key = 87532;//ftok(torrents_dir, 'q');
	request_queue = msgget(req_key, IPC_CREAT | 0660);
	if (request_queue == -1) {
		perror("Creating request queue failed");
		return -2;
	}
   	res_key = 98531;//ftok(torrents_dir, 's');
	responce_queue = msgget(res_key, IPC_CREAT | 0660);
	if (responce_queue == -1) {
		perror("Creating responce queue failed");
		return -3;
	}

	fuse_ret = fuse_main(argc, argv, &callbacks_oper, NULL);

	msgctl(req_key, IPC_RMID, 0);
	msgctl(res_key, IPC_RMID, 0);

	return fuse_ret;
}
