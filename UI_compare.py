import lp_counters
import hll as hyperloglog
import mincount
import random
import UI
from math import ceil
from numpy import log
import sys

if __name__ == '__main__':
    # input_size = 1000000 # 1 million distinct vehicles
    total_vehicles = 254639386 # total number of possible vehicles
    max_size = 128000 # use 128k as size limit for practical reason
    max_js = 0.64 # maximum jaccard simularity

    exp_error = 0.01 # use 0.05 to avoid small range correction in hll
    lpc_load_factor = 3 
    minc_load_factor = 0.001
    lpc_size = 0 # linear prob counter in KB size
    hllc_exp_error = 0 # preset error rate for hyperloglog counter
    minc_size = 0 # k for min count

    repeat_cnt = 10 # number of experiments for each settings

    # initial size for A and B, A always has larger size
    size_a = 1000 
    while size_a <= max_size:
        size_b = 1000
        while size_b <= size_a:
            max_possible_js = float(size_b) / float(size_a)
            js = 0.01
            while js <= min(max_possible_js, max_js):
                # setting parameters
                # we use same size to simplify calculation
                lpc_size = int(ceil(size_a / \
                        log(2 * size_a * exp_error))) * lpc_load_factor
                hllc_exp_error = exp_error
                minc_size = int(ceil(96 / (exp_error ** 2))) * \
                        minc_load_factor
                # repeat the experiment several times with same setting
                lpc_a_error = 0
                hllc_a_error = 0
                mc_a_error = 0
                lpc_error = 0
                hllc_error = 0
                mc_error = 0
                for exp_i in range(repeat_cnt):
                    # initiate counters
                    lpc_a = lp_counters.LPCounter(lpc_size)
                    lpc_b = lp_counters.LPCounter(lpc_size)
                    hllc_a = hyperloglog.HyperLogLog(hllc_exp_error)
                    hllc_b = hyperloglog.HyperLogLog(hllc_exp_error)
                    # simplify solution for hll
                    hllc_u = hyperloglog.HyperLogLog(hllc_exp_error)
                    mc_a = mincount.MinCount(minc_size)
                    mc_b = mincount.MinCount(minc_size)
                    # create items
                    common = size_a * js
                    items_a = set()
                    items_b = set()
                    while len(items_a) < size_a:
                        while True:
                            i = random.randrange(0, total_vehicles)
                            if i not in items_a:
                                items_a.add(i)
                                lpc_a.increment(i)
                                hllc_a.add(i)
                                hllc_u.add(i)
                                mc_a.add(i)
                                if len(items_a) < common:
                                    items_b.add(i)
                                    lpc_b.increment(i)
                                    hllc_b.add(i)
                                    mc_b.add(i)
                                break
                    while len(items_b) < size_b:
                        while True:
                            i = random.randrange(0, total_vehicles)
                            if i not in items_b:
                                items_b.add(i)
                                lpc_b.increment(i)
                                hllc_b.add(i)
                                hllc_u.add(i)
                                mc_b.add(i)
                                break

                    lpc_i = UI.LPCUIEstimator(lpc_a, lpc_b)
                    hllc_i = UI.HLLUIEstimator(hllc_a, hllc_b, hllc_u)
                    lr = UI.MCUIEstimator(mc_a, mc_b)
                    lr.linear_reweight()
                    mc_i = lr.intersection

                    lpc_a_error += abs(size_a - lpc_a.current_count())\
                            / float(size_a)
                    hllc_a_error += abs(size_a - len(hllc_a)) / \
                            float(size_a)
                    mc_a_error += abs(size_a - len(mc_a)) / \
                            float(size_a)
                    lpc_error += abs(common - lpc_i) / float(common)
                    hllc_error += abs(common - hllc_i) / float(common)
                    mc_error += abs(common - mc_i) / float(common)

                # calculate average error rate
                lpc_a_error /= repeat_cnt
                hllc_a_error /= repeat_cnt
                mc_a_error /= repeat_cnt
                lpc_error /= repeat_cnt
                hllc_error /= repeat_cnt
                mc_error /= repeat_cnt

                # the minimum required size in theory
                lpc_virtual_size = lpc_load_factor * \
                        (int(size_a / log(2 * size_a * exp_error)) + \
                        int(size_b / log(2 * size_b * exp_error))) / \
                        8192.0
                hllc_virtual_size = ((1.04 / exp_error) ** 2) * 5 / \
                        8192.0
                minc_virtual_size = (int(ceil(96 / (\
                        exp_error ** 2)))) * 64 * minc_load_factor / \
                        8192.0

                sys.stdout.write('{},{},{},{},{},{},{},{},{},{},{},{}\n'.\
                        format(size_a, size_b, js, \
                        lpc_error, hllc_error, mc_error, \
                        lpc_virtual_size, hllc_virtual_size, \
                        minc_virtual_size, \
                        lpc_a_error, hllc_a_error, mc_a_error))
                sys.stdout.flush()

                js *= 2

            size_b *= 2

        size_a *= 2
