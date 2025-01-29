'Threading library that expands upon stdlib "threading."'

##############################

# TODO Add the below features :
# ThreadGroup class

##############################

from .multithreaded import (Thread, exiting, stop_all, force_stop_all, 
                            thread_data, Barrier, call_lock, wait_until, 
                            multithreaded_config, Config, Condition, 
                            Semaphore, BoundedSemaphore, id_finder,
                            setdebug)

from ._mt_primatives import (to_multithreaded, to_threading)
from . import communication
from . import synchronization
from .synchronization import *


# Will be removed in version 0.1.0, as well as merging .mt_primatives with .multithreaded.
# Note to contributors : you can add stuff to .mt_primatives, but please make sure merging it into .multithreaded
# cause any import loops!     (╯°□°）╯︵ ┻━┻
def __enable_internal() :
    'Used in ._mt_primatives.run, which is going to be removed in 0.0.9! Will not be updated!'

    __internal_features__ = {
        'WaitOnCondition' : 0x00,
        '_thread_data' : 0x01,
        'thread_handles' : 0x02,
        'thread_assignments' : 0x03,
        'used_handles' : 0x04,
        '_exiting' : 0x05,
        'main_thread' : 0x06,
        'main_thread_data' : 0x07,
        'wait_thread_init' : 0x08,
        'function_locks' : 0x09,
        'multithreaded_config' : 0x0A,
        '_DictProxy' : 0x0B,
        '_BasicDictProxy' : 0x0C,
        '_thread_runner' : 0x0D,
        '_get_thread_data' : 0x0E,
        '_wait_for_threads' : 0x0F,
        'highest_ids' : 0x10,
        '_thread_pool_worker' : 0x11,
        '_get_global_name' : 0x12
    }

    class InternalFeature() :
        def __init__(self, feature : int) :
            from .multithreaded import _get_global_name

            self.feature = _get_global_name({v: k for k, v in __internal_features__.items()}[feature])

    return __internal_features__, InternalFeature


__all__ = ['Thread', 'exiting', 'stop_all', 'force_stop_all', 
           'thread_data', 'Barrier', 'call_lock', 'Lock', 
           'wait_until', 'multithreaded_config', 'Config',
           'Condition', 'Semaphore', 'BoundedSemaphore', 
           'id_finder', 'Mutex', 'to_multithreaded', 
           'to_threading', 'communication',
           'synchronization', 'setdebug']

__version__ = '0.0.3'
__name__ = 'multithreaded'

