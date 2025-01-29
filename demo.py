from multithreaded import Thread, exiting, setdebug
from time import sleep


setdebug()

def test() :
    for i in range(5) :
        print(i + 1)
        sleep(1)
        if exiting() :
            print('Exiting!')

thread = Thread(test)
thread.start()
sleep(3)
thread.terminate(forceful=True)