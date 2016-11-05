import importlib
import sys


def get_persistence(name):

    try:
        persistence = importlib.import_module("feedmescrap.persistence."+name)
        print "Using '{}' as persistence backend".format(name)
        persistence.init()

        return persistence
    except ImportError:
        print "ImportError while loading persistence '{}'".format(name)
        raise
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise
    return False
