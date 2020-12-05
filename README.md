This package contains a simple program to generate mock data, which is not realistic at all, for detector background and single electron or tau signal superimposed on the background for the moment.  The output file format is that which can be used for downloading to the Wisconsin APx boards with Xilinx VU9P FPGAs using APx core software tools.

The goal of the ML project is to develop techniques for separating background from signal.

Data files produced by this code contains:

```
  const size_t N_REGIONS_ETA = 14;                                             // Number of eta divisions
  const size_t N_REGIONS_PHI = 18;                                             // Number of phi divisions
  const size_t N_REGIONS = N_REGIONS_ETA * N_REGIONS_PHI;                      // 252 numbers
  const size_t N_REGION_BITS = 16;                                             // each of 16-bits width
  const size_t N_WORD_SIZE = 64;                                               // Each 64-bit word packs data
  const size_t N_REGIONS_PER_WORD = N_WORD_SIZE / N_REGION_BITS;               // for 4 regions
  const size_t N_BITS_PER_EVENT = N_REGION_BITS * N_REGIONS;                   // Each event has 4032 bits of data
  const size_t N_WORDS_PER_FRAME = 4;                                          // Event is read out in a 4-clock cycle frame
  const size_t N_BITS_PER_FRAME = N_WORD_SIZE * N_WORDS_PER_FRAME;             // So, each link can accomodate 256-bits
  size_t N_INPUT_LINKS;                                                        // needing 16 links
  if (N_BITS_PER_EVENT % N_BITS_PER_FRAME)
    N_INPUT_LINKS = (N_BITS_PER_EVENT / N_BITS_PER_FRAME) + 1;
  else
    N_INPUT_LINKS = (N_BITS_PER_EVENT / N_BITS_PER_FRAME);
  const size_t N_OUTPUT_LINKS = N_INPUT_LINKS;
  const size_t MAX_MEMORY_WORDS = 1024;                                        // Firmware uses 1024 64-bit wide memories
  const size_t N_EVENTS = MAX_MEMORY_WORDS / N_WORDS_PER_FRAME;                // So, each file can accommodate 256 events
```

To get started get code and compile it (verified to work on MacOS and Linux):

```
git clone <>
cd <>
c++ *.cpp -L/usr/local/lib/ -largp -o genMLProjectData
```

You can run to produce data.  The random number seed is provided as the value of the option --background, which is necessary to produce data. You have to use --write to save the produced data. You can produce single electron and single tau signals by using the --electron or --tau options.  The value of those variables specifies the transverse momentum of the particle.

The goal of the  ML project is to  produca a model that would have good efficiency >70% to identify 25 GeV objects. The efficiency for 50-GeV objects should be very good >95%.  The background fakes should be 10% or less.

```
genMLProjectData --background=232341231 --write=BackgroundRegionData.txt
genMLProjectData --background=987654323 --electron=50 --write=ElectronRegionData.txt
genMLProjectData --background=478343223 --tau=50 --write=TauRegionData.txt
```
