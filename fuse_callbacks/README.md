#Callbacks VFS

##Description
**Callbacks VFS** is virtual file system that can create read-only mirror of any real file system directory and call callbacks via IPC message queue mechanizm

##Usage
To use **Callbacks VFS** you should write your callback handler.
Callback handler may be written is any programming language.
Callback handler should read requests from requests queue(key=87532) and write responces to responce queue(key=98531).
Request contains request id(==message type) and string containing offset and file absolute path in format `$offset$ $path$`.
Responce contains responce id(==request id) and string containing available bytes for reading(>0) or error code(<0, see error codes section).

**Callbacks VFS** won't allow any to read its files until it recives the responce from callback handler

##Error codes
TODO

##Building and running **Callbacks VFS**
* Download fuse(tested with fuse 2.9.3) from http://fuse.sourceforge.net/
* Go to fuse directory
* Run `./configure && make && make install` to make and install fuse
* Go to fuse_callbacks directory
* Run `make` to make **Callbacks VFS**
* Run `./run.sh $DIRECTORY_TO_CLONE$ $MOUNT_POINT$` to mount **Callbacks VFS** to `$MOUNT_POINT$` directory

##callbacks_example_handler.py description
callbacks_example_handler.py reads **Callbacks VFS** requests and prints them in next format: `$request_id$: $offset$ $path$` and responce to **Callbacks VFS** with available bytes for reading == 1024

###Running callbacks_example_handler.py
* Download sysv_ipc(tested with version 0.6.8) from http://semanchuk.com/philip/sysv_ipc/
* Extract and install sysv_ipc(see INSTALL file)
* Run **Callbacks VFS** and then run `python callbacks_example_handler.py`