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
                            to_multithreaded, EventTrigger,
                            ScheduleHandler, schedule, map, imap, a_map,
                            a_imap, k_map, k_imap)

from . import communication
from . import synchronization
from .synchronization import (Condition, call_lock, wait_until, 
                            WaitOnCondition, Semaphore, 
                            BoundedSemaphore, Barrier,
                            Barrier, Mutex, Lock)


# mt_primatives removed. merged. it SUCKED, alright?

Predicate = WaitOnCondition

__all__ = ['Thread', 'exiting', 'stop_all', 'force_stop_all', 
           'thread_data', 'Barrier', 'call_lock', 'Lock', 
           'wait_until', 'multithreaded_config', 'Config',
           'Condition', 'Semaphore', 'BoundedSemaphore', 
           'id_finder', 'Mutex', 'to_multithreaded', 
           'to_threading', 'communication',
           'synchronization', 'setdebug', 'await_call',
           'run_async', 'Promise', 'PromiseNotResolved',
           'EventTrigger', 'ScheduleHandler', 'schedule',
           'map', 'imap', 'a_map', 'a_imap', 'k_map', 
           'k_imap', 'WaitOnCondition', 'Predicate']

__version__ = '0.0.6'
__name__ = 'multithreaded'
__author__ = 'noah018dev'