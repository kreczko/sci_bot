import os
import pickle


def cached(cachefile, expirationTime=60 * 60 * 24):
    """
    From https://goo.gl/yJpP1r
    A function that creates a decorator which will use "cachefile" for caching
    the results of the decorated function "fn".
    """
    def decorator(fn):
        def wrapped(*args, **kwargs):

            if os.path.exists(cachefile):
                if os.path.getmtime(cachefile) > expirationTime:
                    with open(cachefile, 'rb') as cachehandle:
                        print(
                            "using cached result from '{0}'".format(cachefile))
                        return pickle.load(cachehandle)

            # execute the function with all arguments passed
            res = fn(*args, **kwargs)

            # write to cache file
            with open(cachefile, 'wb') as cachehandle:
                print("saving result to cache '{0}'".format(cachefile))
                pickle.dump(res, cachehandle)

            return res
        return wrapped
    return decorator
