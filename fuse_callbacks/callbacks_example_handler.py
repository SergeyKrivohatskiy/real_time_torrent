#!/usr/bin/env python
__author__ = 'Sergey Krivohatskiy'
import sys
import sysv_ipc

def main():
        requests_queue = sysv_ipc.MessageQueue(87532)
        responces_queue = sysv_ipc.MessageQueue(98531)
        while True:
            request_str, request_id = requests_queue.receive()
            print("%d: %s" % (request_id, request_str))
            bytes_allowed_to_read = 1024 # 0 not alowed. < 0 - error(TODO)
            responces_queue.send(str(bytes_allowed_to_read) + '\0', type=request_id)


        return 0

if __name__ == "__main__":
    sys.exit(main())