from ..multithreaded import Thread as multithreaded_Thread
from threading import Thread as threading_Thread


def run(thread : multithreaded_Thread) :
    __internal_features__, InternalFeature = NotImplemented, NotImplemented
    _bootstrap = InternalFeature(0x12).feature('start_new_thread')
    _bootstrap(InternalFeature(0x0D).feature(InternalFeature(0x03).feature[thread]), ())

def to_threading(thread : multithreaded_Thread) -> threading_Thread :
    _thread = threading_Thread(target=thread.target, args=thread.arguments, kwargs=thread.kwarguments, daemon=thread.daemon)
    thread.dispose()
    return _thread

def to_multithreaded(thread : threading_Thread) -> multithreaded_Thread :
    _thread = multithreaded_Thread(thread._target, thread._args, thread._kwargs, thread.daemon)
    return _thread