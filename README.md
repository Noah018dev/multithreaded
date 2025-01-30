# multithreaded
***advanced threading made beginner***
## installation
 Method one: The typical way.
  Run one of these commands:<br>
  * `pip install multithreaded` - Should work for Windows, but may not work if `/Scripts/` isn't on path.
  * `pip3 install multithreaded` - Should work for Windows and Linux, but it may now work if `/Scripts/` isn't on path.
  *  `py -m pip install multithreaded` - Should work for every Windows installation. If it doesn't, replace `py` with `python` or `python3`.
  * `python3 -m pip install multithreaded` - Should work for every installation (except certain Windows ones). If **this** doesn't work, use `[py/python/python3] -m ensurepip`.<br>
 Method two: The other way.
  Go into releases and download the latest one. Then run `[your pip command] install [path to .whl file]`<br>
 Method three: The dev way.
  Download the source code and there you go.
  If you don't want to edit anything, copy the `/multithreaded` directory (not the project root!) into your project directory.
## quick start
 Start a thread:
 ```python
import multithreaded as mt


def my_function(arg1 : int, arg2 : str = "Hello, world!") :
    for i in range(arg2) :
        print(arg1)

thread = mt.Thread(my_function, 5, kwargs={"arg2" : "Hello, Github!"})
thread.start()
```
