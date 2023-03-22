from m5.objects import *
import m5
import argparse
from m5.objects.DRAMInterface import *
from m5.objects.NVMInterface import *


args = argparse.ArgumentParser()

# This scipt takes these arguments [device model for dram cache]
# [dram cache size] [maximum orb size]
# [traffic mode] [duration of simulation in ticks]
# [max address] [request injection period in ticks] [rd percentage]
# min address is 0, data limit is 0, block size is 64B.
# crb_max_size is 32 by default.

# sample cmd: gem5.opt traffGen.py DDR3_1600_8x8  16MiB
#             32 linear 100000000 128MiB 1000 100
# sample cmd: gem5.opt traffGen.py DDR4_2400_16x4 1GB
#             32 random 100000000 2GB    1000 100

args.add_argument(
    "device",
    type = str,
    help = "Memory device to use as a dram cache"
)

args.add_argument(
    "dram_cache_size",
    type = str,
    help = "Duration of simulation"
)

args.add_argument(
    "max_orb",
    type = int,
    help = "Duration of simulation"
)

args.add_argument(
    "traffic_mode",
    type = str,
    help = "Traffic type to use"
)

args.add_argument(
    "duration",
    type = int,
    help = "Duration of simulation"
)

args.add_argument(
    "max_address",
    type=str,
    help="End address of the range to be accessed",
)

args.add_argument(
    "inj_period",
    type = int,
    help = "Period to inject reqs"
)

args.add_argument(
    "rd_prct",
    type=int,
    help="Read Percentage",
)

options = args.parse_args()

system = System()
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = "4GHz"
system.clk_domain.voltage_domain = VoltageDomain()
system.mem_mode = 'timing'

system.generator = PyTrafficGen()

system.mem_ctrl = DcacheCtrl()
system.mem_ctrl.dram = eval(options.device)(range=AddrRange('8GB'),
                                                in_addr_map=False)
system.mem_ctrl.nvm = NVM_2400_1x64(range=AddrRange('8GB'))

#system.mem_ctrl.dram.tREFI = "200"
system.mem_ctrl.dram_cache_size = options.dram_cache_size
system.mem_ctrl.orb_max_size = options.max_orb
system.mem_ctrl.crb_max_size = "32"

system.mem_ranges = [AddrRange('8GB')]

system.generator.port = system.mem_ctrl.port

def createRandomTraffic(tgen):
    yield tgen.createRandom(options.duration,   # duration
                            0,              # min_addr
                            AddrRange(options.max_address).end,  # max_adr
                            64,             # block_size
                            options.inj_period,       # min_period
                            options.inj_period,       # max_period
                            options.rd_prct,          # rd_perc
                            0)              # data_limit
    yield tgen.createExit(0)

def createLinearTraffic(tgen):
    yield tgen.createLinear(options.duration,   # duration
                            0,              # min_addr
                            AddrRange(options.max_address).end,  # max_adr
                            64,             # block_size
                            options.inj_period,   # min_period
                            options.inj_period,   # max_period
                            options.rd_prct,       # rd_perc
                            0)              # data_limit
    yield tgen.createExit(0)


root = Root(full_system=False, system=system)

m5.instantiate()

if options.traffic_mode == 'linear':
    system.generator.start(createLinearTraffic(system.generator))
elif options.traffic_mode == 'random':
    system.generator.start(createRandomTraffic(system.generator))
else:
    print('Wrong traffic type! Exiting!')
    exit()

exit_event = m5.simulate()