from cloudpickle import dumps, loads


channels = {}

def serialize(thing : object) -> bytes :
    return dumps(thing)

def unserialize(thing : bytes) -> object :
    return loads(thing)

def send(thing : bytes, channel : int) -> None :
    channels[channel] = thing

def receive(channel : int) -> None :
    try :
        return channels[channel]
    except KeyError :
        return None