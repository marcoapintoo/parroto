#!/bin/python

class Example(object):
    """
    Example
    >>> o=Example()
    >>> print 1
    1
    """
    def __init__(self, a=None, b=None):
        """
        """
        self.a = a
        self.b = b
    def sh(self, a=None):
        """
        >>> o.sh()
        None
        """
        if not a: return self.a
        return a

if __name__ == "__main__":
    import doctest
    print "Starting..."
    doctest.testmod()
    