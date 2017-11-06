import mincount
import hll as hyperloglog
import lp_counters
import numpy

def h(s, t):
    n = set()
    for item in s:
        if item <= t:
            n.add(item)
    return n

class MCUIEstimator(object):
    def __init__(self, mc1, mc2):
        self.threshold = min(max(mc1.R), max(mc2.R))
        R = mc1.R.union(mc2.R)
        self.n = (len(mc1), len(mc2))
        self.R = (mc1.R, mc2.R)
        self.k = (mc1.k, mc2.k)
        self.UR = h(R, self.threshold)
        self.IR = mc1.R.intersection(mc2.R)
        self.maxhashedvalue = long("ffffffffffffffff", 16)

    def simple_union(self):
        return (len(self.UR) - 1) / (float(self.threshold) / self.maxhashedvalue)  

    def simple_intersection(self):
        tao = 0
        if self.threshold in self.IR:
            tao = 1
        return (len(self.IR) - tao) / (float(self.threshold) / self.maxhashedvalue)  

    def linear_reweight(self):
        Ra1 = h(self.R[0], self.threshold)
        Ra2 = h(self.R[1], self.threshold)
        self.Ra = (Ra1, Ra2)

        a1 = float(len(self.IR)) / len(Ra1)
        a2 = float(len(self.IR)) / len(Ra2)
        self.a = (a1, a2)

        self.var = []
        for i in range(2):
            temp1 = float(1 - self.a[i]) / (self.a[i] * len(self.Ra[i])) + 1.0 / (2 * self.k[i])
            temp2 = (self.a[i] * self.n[i]) ** 2
            self.var.append(temp1 * temp2)

        self.z = 1.0 / ((1.0 / self.var[0]) + (1.0 / self.var[1]))

        self.intersection = self.z \
                * (self.a[0] * self.n[0] / self.var[0] \
                + self.a[1] * self.n[1] / self.var[1])

def HLLUIEstimator(hll1, hll2, hll_total):
    return len(hll1) + len(hll2) - len(hll_total)

def LPCUIEstimator(lpc1, lpc2):
    bm = lpc1.bit_map & lpc2.bit_map
    sz = float(bm.length())
    va0 = float(max(1, lpc1.bit_map.count(False))) / sz
    vb0 = float(max(1, lpc2.bit_map.count(False))) / sz
    vs1 = float(max(1, bm.count(True))) / sz

    est = (numpy.log(va0) + numpy.log(vb0) - \
            numpy.log(vs1 + va0 + vb0 -1)) / \
            numpy.log(1 - (1 / sz))

    return est

if __name__ == '__main__':
    minc_size = 1024
    hllc_exp_error = 0.02
    lpc_size = 4

    mc1 = mincount.MinCount(minc_size)
    mc2 = mincount.MinCount(minc_size)
    hll1 = hyperloglog.HyperLogLog(hllc_exp_error)
    hll2 = hyperloglog.HyperLogLog(hllc_exp_error)
    # just for naive implementation
    hll_total = hyperloglog.HyperLogLog(hllc_exp_error)
    lpc1 = lp_counters.LPCounter(lpc_size)
    lpc2 = lp_counters.LPCounter(lpc_size)

    for i in range(0, 10000):
        mc1.add(i)
        hll1.add(i)
        hll_total.add(i)
        lpc1.increment(i)

    for i in range(8000, 20000):
        mc2.add(i)
        hll2.add(i)
        hll_total.add(i)
        lpc2.increment(i)
    
    print '------'
    print len(mc1), len(mc2)
    print len(hll1), len(hll2), len(hll_total)
    print lpc1.current_count(), lpc2.current_count()

    ui = MCUIEstimator(mc1, mc2)
    print ui.simple_union(), ui.simple_intersection()

    ui.linear_reweight()
    print ui.intersection

    hll_intersection = HLLUIEstimator(hll1, hll2, hll_total)
    print hll_intersection

    lpc_intersection = LPCUIEstimator(lpc1, lpc2)
    print lpc_intersection
