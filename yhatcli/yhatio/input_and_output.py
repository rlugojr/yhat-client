import warnings
import json

try:
    import pandas as pd
except:
    warnings.warn("Could not import pandas")

def make_df(data):
    """
    Takes an arbitrary data structure and tries to convert it into a data frame

    Parameters
    ----------
    data: object
        data to be converted into data frame

    Returns
    -------
    data: data frame
    """
    if isinstance(data, pd.DataFrame):
        return data
    elif isinstance(data, dict):
        key = data.keys()[0]
        if isinstance(data[key], list):
            pass
        else:
            data = {k: [v] for k,v in data.items()}
    data = pd.DataFrame(data)
    return data


def parse_json(somejson):
    """
    Attempts to parse JSON and return a serialized object

    Parameters
    ----------
    somejson: object

    Returns
    -------
    object: dictionary or list
    """
    try:
        return json.loads(somejson)
    except Exception, e:
        print "Input was not valid JSON."
        print "==> %s" % str(e)

class df_to_df(object):
    """
    Decorator that coreces input and outputs into data frames.
    """
    def __init__(self, func):
        self.func = func
    
    def __call__(self, *args):
        data = args[0]
        data = make_df(data)
        result = self.func(self, data)
        return make_df(result)

class df_to_dict(object):
    """
    Decorator that coreces input to a data frame and requires the output to be
    a dictionary.
    """
    def __init__(self, func):
        self.func = func
    
    def __call__(self, *args):
        data = args[0]
        data = make_df(data)
        result = self.func(self, data)
        if isinstance(result, dict):
            return result
        else:
            msg = "Dictionary was not returned. '%s' was returned instead"
            msg = msg % str(type(result))
            raise Exception(msg)


class dict_to_dict(object):
    """
    Decorator that needs inputs and outputs to be dictionaries.
    """
    def __init__(self, func):
        self.func = func
    
    def __call__(self, *args):
        data = args[0]
        if isinstance(result, dict)==False:
            msg = "Dictionary was not given. '%s' was input instead"
            msg = msg % str(type(result))
            raise Exception(msg)
        result = self.func(self, data)
        if isinstance(result, dict):
            return result
        else:
            msg = "Dictionary was not returned. '%s' was returned instead"
            msg = msg % str(type(result))
            raise Exception(msg)

def handle_nulls(features, data):
    """
    Helper function for indicating how null values should be handled during
    production.

    Parameters
    ----------
    features: list
        a list of features that contains the name and imputation strategy for 
        each
    data: list, dictionary, data frame
        data to be imputed

    Returns
    -------
    data: data frame
        data frame with no null/NA/missing values
    """
    data = make_df(data)
    for feature in features:
        name = feature["name"]
        strategy = feature["na_filler"]
        if hasattr(strategy, '__call__')==False:
            strategy_func = lambda x: strategy
        else:
            strategy_func = strategy
        if name not in data:
            data[name] = None
        mask = data[name].isnull()
        data[name][mask] = data[mask].apply(strategy_func, axis=1)
    return data


def preprocess(func=None, **options):
    """
    Decorator for defining the following:
        1) data type for incoming data
        2) data type for returned data
        3) how to handle null values

    Parameters
    ----------
    func: function
        function being decorated
    in_type: dictionary or data frame
        indicates what the input data type should be
    out_type: dictionary or data frame
        indicates what the returned data type should be

    Returns
    -------
    partial/inner: function
        a function
    """
    if func != None:
        # We received the function on this call, so we can define
        # and return the inner function
        def inner(*args, **kwargs):        
            in_type = options.get('in_type', pd.DataFrame)
            out_type = options.get('out_type', pd.DataFrame)
            null_handler = options.get('null_handler', None)
            data = args[1]
            if in_type==pd.DataFrame:
                data = make_df(data)
            if null_handler:
                data = handle_nulls(null_handler, data)
            data = func(args[0], data)
            if out_type==pd.DataFrame:
                data = make_df(data)
            return data
   
        return inner
  
    else:
        # We didn't receive the function on this call, so the return value
        # of this call will receive it, and we're getting the options now.
        def partial_inner(func):
            return preprocess(func, **options)   
        return partial_inner

