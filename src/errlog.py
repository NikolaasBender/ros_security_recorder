import datetime


# This turns all information to a string
def arg2String(*args, **kwargs):
    s = ""
    for a in args:
        if type(a) == tuple or type(a) == list:
            s += arg2String(*a)
        else:
            s += str(a)
    return s


switcher = {
    0: ' ===INFO=== ',
    1: ' ===WARN=== ',
    2: ' ===ERROR=== '
}

# This prints and writes down all information
def progLog(*args, **kwargs):
    value = 0
    try:
        value = kwargs['level']
    except:
        pass
    data = datetime.datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)") + switcher.get(value) + arg2String(args)
    if value >=0:
        print(data)
    if value >=0:
        f = open("logs.txt", "a")
        f.write(data + "\n")
        f.close()