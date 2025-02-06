from multithreaded import thread_data, setdebug, Thread


setdebug()

def test_function() :
    thread_data()['fizz'] = 'buzz'
    print(thread_data()['fizz'])

Thread(test_function).start()