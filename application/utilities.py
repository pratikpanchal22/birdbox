import inspect

def logger(logLevel, *argsv):
    s=""
    if(str(argsv[0]).startswith('\n')):
        s+="\n"

    s += "{}{:<16.16}{}".format("[", inspect.stack()[1][3], "]")
    for arg in argsv:
        if(str(arg).startswith('\n')):
            s += " " + str(arg).lstrip()
        else:
            s += " " + str(arg)
    print (s)