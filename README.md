# Enabling Design Space Exploration of DRAM Caches in Emerging Memory Systems

This branch of the dram-cache-model repo contains gem5 DRAM cache model associated to the paper titled "Enabling Design Space Exploration of DRAM Caches in Emerging Memory Systems". This cycle-level DRAM cache model can used for evaluation of heterogeneous and disaggregated memory systems which 
employ hardware managed DRAM caches. 

This model relies on the following components:

- **DRAM cache manager:** DRAM cache manager implements different DRAM caching policies and interacts with the local and far memory controllers.
- **Local memory controller:** Local memory controller controls the accesses to the local DRAM device (DRAM cache).
- **Far memory controller:** Far memory controller controls the accesses the far DRAM device (backing store/main memory).

This is a flexible and discrete DRAM cache model and does not require the near and far memory to share the same data bus.

For testing, you can look at the sample script: disaggregated_dram_cache_script.py



