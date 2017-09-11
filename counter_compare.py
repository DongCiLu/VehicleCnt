import lp_counters
import hll as hyperloglog
import mincount
import random

if __name__ == '__main__':
    # input_size = 1000000 # 1 million distinct vehicles
    input_size = 5000 # initial number of distinct vehicles
    total_vehicles = 254639386 # total number of possible vehicles
    lpc_size = 128 * 8192 # linear prob counter in KB size
    hllc_exp_error = 0.02 # preset error rate for hyperloglog counter
    minc_size = 1024 # k for min count
    
    lpc_error_list = []
    hllc_error_list = []

    while(input_size <= 10000000):
        print "---------------------------------"
        print "Input size: ", input_size
        lpc = lp_counters.LPCounter(lpc_size)
        hllc = hyperloglog.HyperLogLog(hllc_exp_error)
        mc = mincount.MinCount(minc_size)
        print 'lpc size: ', lpc.get_size()

        items = set();
        while len(items) < input_size:
            i = random.randrange(0, total_vehicles)
            while i in items:
                i = random.randrange(0, total_vehicles)
            items.add(i)

            lpc.increment(i)
            hllc.add(i)
            mc.add(i)

        lpc_count = lpc.current_count()
        hllc_count = len(hllc)
        mc_count = len(mc)
        lpc_error = float(abs(input_size - lpc_count)) \
                / input_size
        hllc_error = float(abs(input_size - hllc_count)) / input_size
        lpc_error_list.append(lpc_error)
        hllc_error_list.append(hllc_error)
        print "result(GT, LP, HLL, MC):", input_size, lpc_count, hllc_count, mc_count
        input_size *= 10
        print "---------------------------------"

    print 'LPC error rate: ', lpc_error_list
    print 'HLLC error rate: ', hllc_error_list
