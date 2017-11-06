from hashlib import sha1
from sortedcontainers import SortedSet

class MinCount(object):
    def __init__(self, k):
        self.k = k
        # self.R = set()
        self.R = SortedSet()
        self.maxhashedvalue = long("ffffffffffffffff", 16)

    def add(self, value):
        hashedvalue = long(sha1(bytes(value.encode() if isinstance(value, unicode) else value)).hexdigest()[:16], 16)
        if len(self.R) < self.k:
            self.R.add(hashedvalue)
        else:
            if hashedvalue < self.R[-1]:
                del self.R[-1]
                self.R.add(hashedvalue)
            '''
            if hashedvalue < max(self.R):
                self.R.remove(max(self.R))
                self.R.add(hashedvalue)
            '''

    def __len__(self):
        # return (self.k - 1) / (float(max(self.R)) / self.maxhashedvalue)
        return (len(self.R) - 1) / (float(self.R[-1]) / self.maxhashedvalue)
