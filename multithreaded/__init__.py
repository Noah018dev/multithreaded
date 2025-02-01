'Threading library that expands upon stdlib "threading."'

##############################

# TODO Add the below features :
# ThreadGroup class

##############################

from .multithreaded import (Thread, exiting, stop_all, force_stop_all, 
                            thread_data, Barrier, call_lock, wait_until, 
                            multithreaded_config, Config, Condition, 
                            Semaphore, BoundedSemaphore, id_finder,
                            setdebug, await_call, run_async, Promise,
                            PromiseNotResolved, to_threading, 
                            to_multithreaded)

from .communication import module as communication
from .synchronization import module as synchronization
from .synchronization.module import *


# mt_primatives removed. merged. it SUCKED, alright?


__all__ = ['Thread', 'exiting', 'stop_all', 'force_stop_all', 
           'thread_data', 'Barrier', 'call_lock', 'Lock', 
           'wait_until', 'multithreaded_config', 'Config',
           'Condition', 'Semaphore', 'BoundedSemaphore', 
           'id_finder', 'Mutex', 'to_multithreaded', 
           'to_threading', 'communication',
           'synchronization', 'setdebug', 'await_call',
           'run_async', 'Promise', 'PromiseNotResolved']

__version__ = '0.0.5'
__name__ = 'multithreaded'

