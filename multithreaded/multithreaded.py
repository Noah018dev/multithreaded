from _thread import start_new_thread, get_ident, interrupt_main
from collections.abc import Callable
from time import sleep
from typing import Literal
from contextlib import suppress
from stop_thread import stop_thread
from .synchronization.module import *
from logzero import loglevel, logger
from sys import flags
import atexit


loglevel(9999999) # just disable the logger idk

def setdebug() :
    loglevel(1)

class TerminatedExit(SystemExit) : ...

class Config() :
    def __init__(self):
        self.exit_break_mode : Literal['terminate', 'confirm', 'suppress'] = 'confirm'

_thread_data : dict[int, dict] = {}
thread_handles : dict[int, dict] = {}
thread_assignments : dict[object, int] = {}
used_handles = []
_exiting = False
main_thread = get_ident()
main_thread_data = {}
wait_thread_init = 0
multithreaded_config = Config()
terminating_threads = []

def exiting() -> bool :
    if get_ident() in terminating_threads :
        return True
    return _exiting

class _DictProxy() :
    def __init__(self, dictname : str, key : object) :
        self._dictname = dictname
        self._key = key

        globals()[self._dictname][self._key] = {}
    
    def __setitem__(self, key : object, value : object) :
        globals()[self._dictname][self._key][key] = value
    
    def __getitem__(self, key : object) -> object :
        return globals()[self._dictname][self._key][key]

class _BasicDictProxy() :
    def __init__(self, dictname : str):
        self._dictname = dictname
    
    def __setitem__(self, key, value) :
        globals()[self._dictname][key] = value

    def __getitem__(self, key) :
        return globals()[self._dictname][key]

def _thread_runner(handle : int) :
    global thread_handles, wait_thread_init

    logger.info(f'Started thread with native_id of {get_ident()}. Multithreaded id is {handle}.')

    thread_handles[handle]['flags']['running'] = True
    thread_handles[handle]['flags']['started'] = True
    thread_handles[handle]['native_id'] = get_ident()
    
    wait_thread_init -= 1

    try :
        thread_handles[handle]['output'] = thread_handles[handle]['execution']['target'](*thread_handles[handle]['execution']['args'], 
            **thread_handles[handle]['execution']['kwargs']
        )
    except SystemExit :
        logger.info(f'Thread {handle} exited with SystemExit.')
        thread_handles[handle]['exc_info'] = SystemExit()
    except BaseException as e :
        logger.error(f'Thread {handle} exited with an exception.', exc_info=True)
        if thread_handles[handle]['execution']['capture'] :
            e.add_note('Exception captured during runtime.')
        thread_handles[handle]['exc_info'] = e
        thread_handles[handle]['flags']['crashed'] = True

        if not thread_handles[handle]['execution']['capture'] :
            logger.critical('Propagating exception, capture exception was false.')
            raise
    finally :
        thread_handles[handle]['flags']['finished'] = True
        thread_handles[handle]['flags']['running'] = False
    
    if get_ident() in terminating_threads :
        terminating_threads.remove(get_ident())
    
def _get_thread_data(thread_class) -> dict :
    return thread_handles[thread_assignments[thread_class]]

class Thread() :
    def __init__(self, target : Callable, *args : tuple, kwargs : dict = {}, daemon : bool = False, capture_exc : bool = True) :
        global thread_assignments, thread_data, thread_handles, used_handles

        thread_num = 0

        while thread_num in used_handles :
            thread_num += 1

        thread_assignments[self] = thread_num
        used_handles.append(thread_num)
        thread_handles[thread_num] = {
            'flags' : {
                'running' : False,
                'started' : False,
                'finished' : False,
                'crashed' : False,
                'daemon' : daemon
            },
            'exc_info' : None,
            'output' : None,
            'execution' : {
                'target' : target,
                'args' : args,
                'kwargs' : kwargs,
                'capture' : capture_exc
            },
            'native_id' : None
        }
    
    def dispose(self) :
        logger.info(f'Disposing of thread {thread_assignments[self]}.')

        if self.running :
            logger.warning('The thread is still running! This may cause major problems with the thread handler itself. Please only use this when the thread is done and you don\'t need it anymore.')

        del thread_handles[thread_assignments[self]]
    
    def start(self) :
        global wait_thread_init

        logger.debug(f'Starting thread {thread_assignments[self]}, you will (hopefully) see another message shortly.')

        wait_thread_init += 1
        start_new_thread(_thread_runner, (thread_assignments[self],))
    
    def join(self, timeout : float = -1) :
        logger.info(f'Thread with native_id {get_ident()} joining thread with native id {self.native_id}...')

        while wait_thread_init > 0 :
            sleep(0.05)

        if not self.started :
            raise RuntimeError('Cannot join thread that hasn\'t been started.')
        
        time = 0

        while self.running :
            sleep(0.05)
            if timeout > 0 :
                time += 0.05
                
                if time >= timeout :
                    logger.critical('Join timeout is over, and thread is still running! Panic!')
                    raise RuntimeError('Still running after timeout.')
        
        logger.info(f'Thread with native_id {get_ident()} has finished joining thread with native id {self.native_id}.')
    
    def terminate(self, timeout : float = 0, forceful : bool = False) -> bool :
        wait_until(lambda: wait_thread_init == 0)

        if not self.running :
            raise RuntimeError('Thread is not running, cannot terminate it.')

        logger.info(f'Terminating... [forceful={forceful}]')

        terminating_threads.append(self.native_id)
        if timeout > 0 :
            sleep(timeout)

        if forceful :
            stop_thread(self.native_id)
            thread_handles[thread_assignments[self]]['flags']['finished'] = True
            thread_handles[thread_assignments[self]]['flags']['running'] = False
            thread_handles[thread_assignments[self]]['flags']['crashed'] = True
            thread_handles[thread_assignments[self]]['exc_info'] = TerminatedExit()
            

    @property
    def flags(self) :
        return _get_thread_data(self)['flags']
    
    @property
    def running(self) :
        return self.flags['running']
    
    @property
    def started(self) :
        return self.flags['started']
    
    @property
    def finished(self) :
        return self.flags['finished']
    
    @property
    def crashed(self) :
        return self.flags['crashed']
    
    @property
    def daemon(self) :
        return self.flags['daemon']
    
    @property
    def execution_data(self) :
        return _get_thread_data(self)['execution']
    
    @property
    def native_id(self) :
        return _get_thread_data(self)['native_id']
   
    @property
    def target(self) :
        return self.execution_data['target']
    
    @property
    def arguments(self) :
        return self.execution_data['args']
    
    @property
    def kwarguments(self) :
        return self.execution_data['kwargs']
    
    @property
    def output(self) :
        if not self.finished :
            raise RuntimeError('The thread has not finished execution, cannot get output.')
        
        return _get_thread_data(self)['output']
    
    def raise_exc(self) :
        if _get_thread_data(self)['exc_info'] is not None :
            raise _get_thread_data(self)['exc_info']
    
    @property
    def locals(self) :
        if self.native_id is None :
            raise RuntimeError('Thread not started yet, do not have the locals for it.')

        return _DictProxy('_thread_data', self.native_id)
    

@atexit.register
def _wait_for_threads() :
    global _exiting

    _exiting = True
    confirm = 0

    while wait_thread_init > 0 :
        with suppress(KeyboardInterrupt) :
            sleep(0.05)
    for thread in thread_handles.values() :
        if not thread['flags']['daemon'] :
            while thread['flags']['running'] :
                try :
                    sleep(0.05)
                except KeyboardInterrupt :
                    match multithreaded_config.exit_break_mode :
                        case 'suppress' :
                            continue
                        case 'terminate' :
                            quit()
                        case 'confirm' :
                            if confirm == 1 :
                                quit()

                            print('Waiting for all threads to finish...\nBREAK again to terminate')
                            confirm = 1


def stop_all() :
    _wait_for_threads()
    if get_ident() == main_thread :
        raise SystemExit

    interrupt_main(1)
    raise SystemExit

def force_stop_all() :
    atexit.unregister(_wait_for_threads)
    interrupt_main(1)
    raise SystemExit

def thread_data() :
    if get_ident() == main_thread :
        return _BasicDictProxy('main_thread_data')
    
    if not get_ident() in _thread_data :
        _thread_data[get_ident()] = {}

    return _DictProxy('_thread_data', get_ident())

highest_ids : dict = {}

@call_lock
def id_finder(channel : int) -> int :
    if not channel in highest_ids :
        highest_ids[channel] = -1
    
    highest_ids[channel] += 1

    return highest_ids[channel]

class ThreadPool() :
    def __init__(self, task_queue : list[Callable[[None], None]], thread_count : int) :
        self.task_queue = task_queue
        self.count = thread_count
        self.running = False

    def start_threads(self) :
        self.running = True
        self._init_barrier = Barrier(self.count)
        self._next_task = [Condition()]
        for _ in range(self.count) :
            Thread(_thread_pool_worker).start()
    
    def add_task(self, function : Callable) :
        self._next_task.append(function)
        self._next_task.append(Condition())
        self._next_task[-3].trigger()

def _thread_pool_worker(pool : ThreadPool) :
    pool._init_barrier.push()
    while pool.running :
        wait_until(lambda: pool._next_task[-1].triggered)

def _get_global_name(name : str) -> object :
    return globals()[name]