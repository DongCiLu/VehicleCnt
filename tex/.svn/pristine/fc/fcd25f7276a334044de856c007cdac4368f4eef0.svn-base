import lp_counters
# import hyperloglog
import hll as hyperloglog
import random

if __name__ == '__main__':
    # input_size = 1000000 # 1 million distinct vehicles
    input_size = 100000 # number of distinct vehicles
    total_vehicles = 254639386 # total number of possible vehicles
    lpc_size = 128 # linear prob counter in KB size
    hllc_exp_error = 0.01 # preset error rate for hyperloglog counter

    lpc_error_list = []
    hllc_error_list = []

    while(input_size <= 10000000):
        lpc = lp_counters.LPCounter(lpc_size)
        hllc = hyperloglog.HyperLogLog(hllc_exp_error)
        print 'lpc size: ', lpc.get_size()

        items = set();
        while(len(items) < input_size):
            i = random.randrange(0, total_vehicles)
            while i in items:
                i = random.randrange(0, total_vehicles)
            items.add(i)

            lpc.increment(i)
            hllc.add(i)

        lpc_error = float(abs(input_size - lpc.current_count())) \
                / input_size
        hllc_error = float(abs(input_size - len(hllc))) / input_size
        lpc_error_list.append(lpc_error)
        hllc_error_list.append(hllc_error)
        print input_size, lpc.current_count(), len(hllc)
        input_size *= 10

    print 'LPC error rate: ', lpc_error_list
    print 'HLLC error rate: ', hllc_error_list
