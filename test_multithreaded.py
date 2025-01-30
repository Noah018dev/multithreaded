from time import sleep
import multithreaded as mt


def wait_infinite() :
    while True :
        sleep(1)

def double(number) :
    return number * 2

def return_exiting() :
    sleep(1)
    return mt.exiting()

def test_exiting() :
    assert not mt.exiting()

def test_thread_init() :
    thread = mt.Thread(print, 'hello', 'world', kwargs={'hello':'world'}, daemon=True, capture_exc=True)

    assert not thread.finished
    assert not thread.running
    assert not thread.started
    assert thread.target == print
    assert thread.daemon
    assert thread.arguments == ('hello', 'world')
    assert thread.kwarguments == {'hello':'world'}

def test_terminate() :
    thread = mt.Thread(wait_infinite, daemon=True)
    
    thread.start()
    sleep(0.1)

    assert thread.running

    thread.terminate(forceful=True)
    sleep(0.1)

    assert not thread.running

def test_output() :
    thread = mt.Thread(double, 20)

    thread.start()
    sleep(0.1)

    assert thread.output == 40

def test_weak_terminate() :
    thread = mt.Thread(return_exiting)

    thread.start()
    sleep(0.1)

    thread.terminate(timeout=2)

    assert thread.output == True

def wait_on_lock(lock : mt.Mutex) :
    lock.acquire()
    sleep(1)
    lock.release()

def test_threaded_lock() :
    lock = mt.Mutex()

    thread1 = mt.Thread(wait_on_lock, lock)
    thread2 = mt.Thread(wait_on_lock, lock)

    thread1.start()
    sleep(0.1)
    thread2.start()
    sleep(0.1)
    assert thread1.running
    assert thread2.running

    sleep(1)
    assert not thread1.running
    assert thread2.running

    thread2.terminate(forceful=True)
    sleep(0.1)
    assert not thread2.running