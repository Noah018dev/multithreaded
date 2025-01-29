from collections.abc import Callable
from time import sleep
from typing import TypeAlias


function_locks = {}
WaitOnCondition: TypeAlias = Callable[[None], bool]

def call_lock(func : Callable) :
    def wrapper(*args, **kwargs) :
        if func in function_locks :
            while function_locks[func] :
                sleep(0.05)

        function_locks[func] = True
        func(*args, **kwargs)
        function_locks[func] = False
    
    return wrapper

class Mutex() :
    def __init__(self) :
        self.locked = False
    
    def acquire(self) :
        while self.locked :
            sleep(0.05)
        self.locked = True
    
    def release(self) :
        self.locked = False
    
    def __enter__(self) :
        self.acquire()
    
    def __exit__(self, *args) :
        self.release()



def wait_until(condition : Callable[[None], bool] | WaitOnCondition) :
    while not condition() :
        sleep(0.05)

class Lock(Mutex) :
    def __init__(self):
        super().__init__()

class Condition() :
    def __init__(self):
        self.triggered = False
    
    def wait_for(self) :
        wait_until(lambda: self.triggered)
    
    def trigger(self) :
        self.triggered = True
    
    def cancel(self) :
        self.triggered = False

class Semaphore() :
    def __init__(self) :
        self.acquired = 0
    
    def acquire(self) :
        self.acquired += 1
    
    def release(self) :
        self.acquired -= 1
        if self.acquired < 0 :
            raise ValueError('Semaphore cannot be negative.')

class BoundedSemaphore(Semaphore) :
    def __init__(self, max_acquired : int):
        super().__init__()
        self.max = max_acquired
    
    def acquire(self, wait_on : bool = True) :
        if self.acquired == self.max :
            if wait_on :
                wait_until(lambda: self.acquired < self.max)
            else :
                raise ValueError('BoundedSemaphore at maximum, cannot acquire.')

        return super().acquire()

class Barrier() :
    def __init__(self, locks_needed : int) :
        self._locked = True
        self._locks_needed = locks_needed
        self.locks = 0
        self._received_broken = 0
    
    def push(self) :
        self.locks += 1

        while self.locks < self._locks_needed :
            sleep(0.05)
        
        self._received_broken += 1

        wait_until(lambda: self._received_broken == self.locks)

        self._received_broken -= 1
        self.locks -= 1