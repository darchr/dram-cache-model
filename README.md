# A Cycle-level Unified DRAM Cache Controller Model

This branch contains code associated to the paper titled "A Cycle-level Unified DRAM Cache Controller Model".

This unified DRAM cache controller (UDCC) model is a cycle-level DRAM cache model for gem5 and takes inspiration from
the actual hardware providing DRAM cache, such as Intel’s Cascade Lake, in which an NVRAM accompanies a DRAM cache as the off-chip main 
memory sharing the same bus. We model a unified DRAM cache controller (UDCC) in gem5 to control a DRAM device (which acts as a cache of 
the main memory) and an NVM device (which serves as the main memory in the system) and both devices share a data bus.

For testing, you can look at the sample script: cascadeLake_dram_cache_script.py
