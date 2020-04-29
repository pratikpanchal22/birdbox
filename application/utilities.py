import inspect
from json import JSONEncoder

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

def comma_separated_params_to_list(param):
    result = []
    for val in param.split(','):
        if val:
            result.append(val)
    return result    

class DateTimeEncoder(JSONEncoder):
        #Override the default method
        def default(self, obj):
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()