from _thread import start_new_thread, get_ident, interrupt_main
from collections.abc import Callable
from time import sleep
from typing import Literal
from contextlib import suppress
from stop_thread import stop_thread
from .synchronization.module import *
from logzero import loglevel, logger
from sys import flags
from threading import Thread as threading_Thread
import atexit


loglevel(99999988) # just disable the logger idk

def setdebug() :
    loglevel(1)

class TerminatedExit(SystemExit) : ...

class Config() :
    '''Config for the multithreaded library.'''
    def __init__(self):
        self._exit_break_mode : Literal['terminate', 'confirm', 'suppress'] = 'confirm'
    
    @property
    def exit_break_mode(self) -> Literal['terminate', 'confirm','suppress'] :
        '''Determines what happens when you press CTRL+C while non-daemon threads are still running.
        
        terminate: exit immediately
        confirm: ask for confirmation before exiting
        suppress: do not ask for confirmation and continue'''
        return self._exit_break_mode

    @exit_break_mode.setter
    def exit_break_mode(self, value : Literal['terminate', 'confirm','suppress']) :
        self._exit_break_mode = value    

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
main_thread_running = True

def exiting() -> bool :
    'Returns if the current thread is exiting. This could be if the main thread is no longer running, or if this thread has been terminated non-forcefully.'
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
    '*The main attraction.* The docstring is in the constructor!'
    def __init__(self, target : Callable, *args : tuple, kwargs : dict = {}, daemon : bool = False, capture_exc : bool = True) :
        '''Thread class constructor. Arguments :
        
        target : callable, the function to be called in the thread.
        args : pass anything after the target and it'll be the argument for the function.
        kwargs : the keyword arguments for the function.
        daemon : if this is True, the process will exit even if this thread is still running.
        capture_exc : if this is True, exceptions during the execution of the target function will be captured and stored in the thread data. otherwise, they will be propagated.
        '''
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
        '*THIS DOES NOT STOP THE THREAD, IT MAY BREAK IT*, it just deletes the handler for the Thread. Use this if you want to cleanup the thread if you don\'t need it anymore.'

        logger.info(f'Disposing of thread {thread_assignments[self]}.')

        if self.running :
            logger.warning('The thread is still running! This may cause major problems with the thread handler itself. Please only use this when the thread is done and you don\'t need it anymore.')

        del thread_handles[thread_assignments[self]]
    
    def start(self) :
        'Starts the thread with target(*args, **kwargs).'

        global wait_thread_init

        if self.started :
            raise RuntimeError('Thread is already started.')

        logger.debug(f'Starting thread {thread_assignments[self]}, you will (hopefully) see another message shortly.')

        wait_thread_init += 1
        start_new_thread(_thread_runner, (thread_assignments[self],))
    
    def join(self, timeout : float = -1) :
        'Waits until the thread is finished running. Raises TimeoutError if the thread is still running after the timeout in seconds.'

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
                    raise TimeoutError('Still running after timeout.')
        
        logger.info(f'Thread with native_id {get_ident()} has finished joining thread with native id {self.native_id}.')
    
    def terminate(self, timeout : float = 0, forceful : bool = False) -> bool :
        'Terminate or stop the thread. It will raise the exiting flag for the thread, and returns True if the thread is still running. If forceful is set, the thread will be terminated.'

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
        
        return self.running
            

    @property
    def flags(self) :
        'The thread flags. I recommend using the properties, not the dict.'
        return _get_thread_data(self)['flags']
    
    @property
    def running(self) :
        'Returns True if the thread is running.'
        return self.flags['running']
    
    @property
    def started(self) :
        'Returns True if the thread has started.'
        return self.flags['started']
    
    @property
    def finished(self) :
        'Returns True if the thread has finished execution.'
        return self.flags['finished']
    
    @property
    def crashed(self) :
        'Returns True if the thread has crashed.'
        return self.flags['crashed']
    
    @property
    def daemon(self) :
        'Returns True if the thread is a daemon thread.'
        return self.flags['daemon']
    
    @property
    def execution_data(self) :
        'The execution data. I recommend using the properties, not the dict.'
        return _get_thread_data(self)['execution']
    
    @property
    def native_id(self) :
        'The native id of the thread.'
        return _get_thread_data(self)['native_id']
   
    @property
    def target(self) :
        'The target function for the thread.'
        return self.execution_data['target']
    
    @property
    def arguments(self) :
        'The arguments for the target function.'
        return self.execution_data['args']
    
    @property
    def kwarguments(self) :
        'The keyword arguments for the target function.'
        return self.execution_data['kwargs']
    
    @property
    def output(self) :
        'The output of the target function. Raises RuntimeError if the thread has not finished execution.'
        if not self.finished :
            raise RuntimeError('The thread has not finished execution, cannot get output.')
        
        return _get_thread_data(self)['output']
    
    def raise_exc(self) :
        'Raises the stored exception if any.'
        if _get_thread_data(self)['exc_info'] is not None :
            raise _get_thread_data(self)['exc_info']
    
    @property
    def locals(self) :
        'The locals of the thread. Raises RuntimeError if the thread has not started yet, or if the thread has finished execution.'
        if self.native_id is None :
            raise RuntimeError('Thread not started yet, do not have the locals for it.')

        return _DictProxy('_thread_data', self.native_id)


@atexit.register
def _wait_for_threads() :
    global _exiting, main_thread_running

    _exiting = True
    main_thread_running = False
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
    'Does standard exit procedures.'
    _wait_for_threads()
    if get_ident() == main_thread :
        raise SystemExit

    interrupt_main(1)
    raise SystemExit

def force_stop_all() :
    'Exits the process, and doesn\'t wait for any threads to finish.'
    atexit.unregister(_wait_for_threads)
    interrupt_main(1)
    raise SystemExit

def thread_data() :
    'Returns the thread data for the current thread. This is local- per thread.'
    if get_ident() == main_thread :
        return _BasicDictProxy('main_thread_data')
    
    if not get_ident() in _thread_data :
        _thread_data[get_ident()] = {}

    return _DictProxy('_thread_data', get_ident())

highest_ids : dict = {}

@call_lock
def id_finder(channel : int) -> int :
    'Finds the highest id for the given channel.'
    if not channel in highest_ids :
        highest_ids[channel] = -1
    
    highest_ids[channel] += 1

    return highest_ids[channel]

class ThreadPool() :
    def __init__(self, thread_count : int) :
        'Create a new thread pool. Use the function id_finder to find an id for each thread. Return values are NOT supported.'
        self.task_queue = []
        self.count = thread_count
        self.running = False

    def start_threads(self) :
        'Starts all of the threads.'

        self.running = True
        self._init_barrier = Barrier(self.count)
        self._next_task = [Condition()]
        for _ in range(self.count) :
            Thread(_thread_pool_worker).start()
    
    def add_task(self, function : Callable) :
        'Adds a function for all of the threads to execute.'

        self._next_task.append(function)
        self._next_task.append(Condition())
        self._next_task[-3].trigger()

def _thread_pool_worker(pool : ThreadPool) :
    pool._init_barrier.push()
    while pool.running :
        wait_until(lambda: pool._next_task[-1].triggered)

def _get_global_name(name : str) -> object :
    return globals()[name]

class Counter() :
    def __init__(self) :
        'A thread-safe counter.'
        self._value = 0
        self._lock = Lock()
    
    @property
    def value(self) -> int :
        'Acquires a lock, then returns the value.'
        with self._lock :
            return self._value
    
    @property
    def increment(self) -> None :
        'Acquires a lock, then increments the value.'
        with self._lock :
            self._value += 1
    
    def set_counter(self, value : int) -> None :
        'Acquires a lock, then sets the value.'
        with self._lock :
            self._value = value

class PromiseNotResolved(object): pass

class Promise() :
    def __init__(self, function : Callable, *args, **kwargs) :
        'Promise object. Pass in a function and it will start running.'
        self._thread = Thread(function, *args, kwargs=kwargs)
        self._thread.start()
    
    @property
    def value(self) -> object :
        'Returns the value of the function, or, if not done, returns PromiseNotResolved.'

        if self._thread.crashed :
            self._thread.raise_exc()
        
        if self._thread.finished :
            return self._thread.output
        
        return PromiseNotResolved()

def run_async(function : Callable) -> Callable[[object], Promise] :
    'Wraps a function in a Promise object.'
    def wrapper(*args, **kwargs) -> Promise :
        return Promise(function, *args, **kwargs)
    return wrapper

def await_call(function : Callable[[object], Promise], *args, **kwargs) -> object :
    'Awaits an async function to be called with @run_async.'

    promise = function(*args, **kwargs)
    promise._thread.join()

    return promise.value

def to_threading(thread : Thread) -> threading_Thread :
    _thread = threading_Thread(target=thread.target, args=thread.arguments, kwargs=thread.kwarguments, daemon=thread.daemon)
    thread.dispose()
    return _thread

def to_multithreaded(thread : threading_Thread) -> Thread :
    _thread = Thread(thread._target, thread._args, thread._kwargs, thread.daemon)
    return _thread