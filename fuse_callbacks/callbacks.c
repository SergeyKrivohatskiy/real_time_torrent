#define FUSE_USE_VERSION 26
#define DEBUG

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

static char PATH_BUFFER[1024];
static int TORRENTS_DIR_LEN;

static int on_read(const char *path)
{
	// TODO
	sleep(1);
	return 0;
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

	if (on_read(path) == -1)
		return -errno;
	fd = open(to_real_path(path), O_RDONLY);
	if (fd == -1)
		return -errno;

	res = pread(fd, buf, size, offset);
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
	if (argc < 2)
	{
		return -1;
	}
	char *torrents_dir = argv[1];
	TORRENTS_DIR_LEN = strlen(torrents_dir);
	strcpy(PATH_BUFFER, torrents_dir);

	argv[1] = argv[0];
	return fuse_main(argc - 1, argv + 1, &callbacks_oper, NULL);
}
