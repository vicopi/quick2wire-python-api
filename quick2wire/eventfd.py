
from ctypes import *
import os
import errno

# From sys/eventfd.h

EFD_SEMAPHORE = 1
EFD_CLOEXEC = 0o2000000
EFD_NONBLOCK = 0o4000

_libc = cdll.LoadLibrary(None)

eventfd_t = c_uint64
eventfd = _libc.eventfd


class Semaphore:
    """A Semaphore implemented with eventfd so that it can be used with epoll."""
    
    def __init__(self, blocking=True):
        self._fd = eventfd(0, EFD_SEMAPHORE|((not blocking)*EFD_NONBLOCK))
    
    def close(self):
        os.close(self._fd)
    
    def fileno(self):
        return self._fd
    
    def signal(self):
        return os.write(self._fd, eventfd_t(1))
    
    def receive(self):
        try:
            os.read(self._fd, 8)
            return True
        except OSError as e:
            if e.errno == errno.EAGAIN:
                return False
            else:
                raise