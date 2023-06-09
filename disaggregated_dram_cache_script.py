# Copyright (c) 2023 The Regents of the University of California
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from m5.objects import *
import m5
import argparse
from m5.objects.DRAMInterface import *
from m5.objects.NVMInterface import *


args = argparse.ArgumentParser()

# This scipt has the following arguments
# device model for dram cache = HBM2 with two pseud-channels
# device model for backing store of DRAM cache = DDR4
# dram cache size = 128 MiB
# maximum orb size = 128
# [traffic mode] = must be given in cmd (linear or random)
# duration of simulation in ticks
# max address = size of main memory
# request injection period in ticks = 1000
# [rd percentage] = must be given in cmd
# min address is 0.
# data limit is 0.
# block size is 64B.
# crb_max_size is 32 by default.

# sample cmd: build/X86/gem5.opt disaggregated_dram_cache_script.py linear 70

args.add_argument(
    "traffic_mode",
    type = str,
    help = "Traffic type to use"
)
args.add_argument(
    "rd_prct",
    type = int,
    help = "Read Percentage",
)

options = args.parse_args()

system = System()
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = "4GHz"
system.clk_domain.voltage_domain = VoltageDomain()
system.mem_mode = 'timing'

system.generator = PyTrafficGen()

system.mem_ctrl = PolicyManager(range=AddrRange('1GiB'))
system.mem_ctrl.dram_cache_size = '128MiB'
# ORB is Outstanding Request Buffer, a buffer for reads and writes requests to the DRAM cache.
system.mem_ctrl.orb_max_size = "128"
# CRB is Conflicting Request Buffer, a buffer for serializing the outstanding requests that map to the same cache location.
system.mem_ctrl.crb_max_size = "32"

system.loc_mem_ctrl = HBMCtrl()
system.loc_mem_ctrl.dram = HBM_2000_4H_1x64(range=AddrRange('1GiB'), in_addr_map=False, null=True)
system.loc_mem_ctrl.dram_2 = HBM_2000_4H_1x64(range=AddrRange('1GiB'), in_addr_map=False, null=True)
system.loc_mem_ctrl.dram.read_buffer_size = 32
system.loc_mem_ctrl.dram.write_buffer_size = 32
system.loc_mem_ctrl.dram_2.read_buffer_size = 32
system.loc_mem_ctrl.dram_2.write_buffer_size = 32

# for HBM2
system.mem_ctrl.tRP = '14ns'
system.mem_ctrl.tRCD_RD = '12ns'
system.mem_ctrl.tRL = '18ns'

system.far_mem_ctrl = MemCtrl()
system.far_mem_ctrl.dram = DDR4_2400_16x4(range=AddrRange('1GiB'),in_addr_map=False, null=True)
system.far_mem_ctrl.dram.read_buffer_size = 64
system.far_mem_ctrl.dram.write_buffer_size = 64

system.generator.port = system.mem_ctrl.port
system.loc_mem_ctrl.port = system.mem_ctrl.loc_req_port
system.far_mem_ctrl.port = system.mem_ctrl.far_req_port

def createRandomTraffic(tgen):
    yield tgen.createRandom(10000000000,           # duration
                            0,                     # min_addr
                            AddrRange('1GB').end,  # max_adr
                            64,                    # block_size
                            1000,                  # min_period
                            1000,                  # max_period
                            options.rd_prct,       # rd_perc
                            0)                     # data_limit
    yield tgen.createExit(0)

def createLinearTraffic(tgen):
    yield tgen.createRandom(10000000000,           # duration
                            0,                     # min_addr
                            AddrRange('1GB').end,  # max_adr
                            64,                    # block_size
                            1000,                  # min_period
                            1000,                  # max_period
                            options.rd_prct,       # rd_perc
                            0)                     # data_limit
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