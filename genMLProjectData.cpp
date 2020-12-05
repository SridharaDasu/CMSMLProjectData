#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>

#include <iostream>
#include <fstream>
#include <iomanip>
#include <string>
#include <random>

#include <argp.h>

//#include "algo_top_parameters.h"
//#include "algo_top.h"

#include "APxLinkData.hh"
#include "UCTRegion.hh"

using namespace std;

/* argp declarations */
const char *algo_top_tb_version = "genMLProjectData 1.0";
const char *algo_top_tb_bug_address = "<dasu@hep.wisc.edu>";

static char doc[] = "APx HLS Firmware Development - Data Generator";

static struct argp_option options[] = {
                                       {"read", 'r', "FILE", 0, "Reads target file and writes contexts to AXI streams", 0},
                                       {"write", 'w', "FILE", 0, "Writes output data to target file in APx format", 0},
                                       {"dump", 'd', "FILE", 0, "Dumps output data to a CSV file for non-APx usage", 0},
                                       {"compare", 'c', "FILE", 0, "Compare the algorithm output to target file", 0},
                                       {"background", 'b', "SEED", 0, "Generates a background file given seed", 0},
                                       {"electron", 'e', "ET", 0, "Generates a electron signal file given et in GeV", 0},
                                       {"tau", 't', "ET", 0, "Generates a tau signal file given et in GeV", 0},
                                       {"met", 'm', "MET", 0, "Generates a met signal file given MET in GeV", 0},
                                       {"jets", 'j', "HET", 0, "Generates a jets signal file given HET in GeV", 0},
                                       {"verbose", 'v', 0, 0, "Produce verbose output", 0},
                                       {0},
};

struct arguments {
  char *readfile;
  char *writefile;
  char *csvfile;
  char *cmpfile;
  char *background;
  char *electron;
  char *tau;
  char *met;
  char *jets;
  bool verbose;
};

static error_t parse_opt(int key, char *arg, struct argp_state *state) {
  struct arguments *arguments = (struct arguments *)state->input;

  switch (key) {
  case 'r': arguments->readfile = arg; break;
  case 'w': arguments->writefile = arg; break;
  case 'd': arguments->csvfile = arg; break;
  case 'c': arguments->cmpfile = arg; break;
  case 'b': arguments->background = arg; break;
  case 'e': arguments->electron = arg; break;
  case 't': arguments->tau = arg; break;
  case 'm': arguments->met = arg; break;
  case 'j': arguments->jets = arg; break;
  case 'v': arguments->verbose = true; break;
  default: return ARGP_ERR_UNKNOWN; break;
  }

  return 0;
}

static struct argp argp = { options, parse_opt, NULL, doc };

int main(int argc, char **argv) {
  
  struct arguments arguments = {0, 0, 0, 0, 0, 0, 0, 0, 0, false};

  argp_parse(&argp, argc, argv, 0, 0, &arguments);

  if (arguments.readfile)
    cout << "Will read file " << arguments.readfile << endl;
  if (arguments.writefile)
    cout << "Will write file " << arguments.writefile << endl;
  if (arguments.csvfile)
    cout << "Will write csv file " << arguments.csvfile << endl;
  if (arguments.cmpfile) 
    cout << "Will compare to file " << arguments.cmpfile << endl;
  if (arguments.background)
    cout << "Will generate data with seed = " << arguments.background << endl;
  if (arguments.electron)
    cout << "Generated data will include an electron with PT = " << arguments.electron << endl;
  if (arguments.tau)
    cout << "Generated data will include an tau with PT = " << arguments.tau << endl;
  if (arguments.met)
    cout << "Generated data will include with MET = " << arguments.met << endl;
  if (arguments.jets)
    cout << "Generated data will include 2 or more jets with TotaET = " << arguments.jets << endl;
  if (arguments.verbose)
    cout << "Verbose output =" << arguments.verbose << endl;


  const size_t N_REGIONS_ETA = 14;
  const size_t N_REGIONS_PHI = 18;
  const size_t N_REGIONS = N_REGIONS_ETA * N_REGIONS_PHI;
  const size_t N_REGION_BITS = 16;
  const size_t N_WORD_SIZE = 64;
  const size_t N_REGIONS_PER_WORD = N_WORD_SIZE / N_REGION_BITS;
  const size_t N_BITS_PER_EVENT = N_REGION_BITS * N_REGIONS;
  const size_t N_WORDS_PER_FRAME = 4;
  const size_t N_BITS_PER_FRAME = N_WORD_SIZE * N_WORDS_PER_FRAME;
  size_t N_INPUT_LINKS;
  if (N_BITS_PER_EVENT % N_BITS_PER_FRAME)
    N_INPUT_LINKS = (N_BITS_PER_EVENT / N_BITS_PER_FRAME) + 1;
  else
    N_INPUT_LINKS = (N_BITS_PER_EVENT / N_BITS_PER_FRAME);
  const size_t N_OUTPUT_LINKS = N_INPUT_LINKS;
  const size_t MAX_MEMORY_WORDS = 1024;
  const size_t N_EVENTS = MAX_MEMORY_WORDS / N_WORDS_PER_FRAME;
  
  uint64_t link_in[N_WORDS_PER_FRAME][N_INPUT_LINKS];
  uint64_t link_out[N_WORDS_PER_FRAME][N_OUTPUT_LINKS];

  if (arguments.readfile) {
    APxLinkData datafile_in(N_INPUT_LINKS);

    datafile_in.read(arguments.readfile);

    // Copy the file data to the stream
    for (size_t i = 0; i < datafile_in.getCycles(); i++) {
      for (size_t k = 0; k < N_INPUT_LINKS; k++) {
        APxLinkData::LinkValue v;
        if (datafile_in.get(i, k, v)) {
          size_t j = i % N_WORDS_PER_FRAME;
          link_in[j][k] = v.data;
        }
      }
    }

    if (arguments.verbose) {
      cout << "Input data:" << endl;
      datafile_in.print();
    }

  }

  APxLinkData datafile_out(N_OUTPUT_LINKS);
  if (arguments.writefile) {
    if (arguments.background) {
      unsigned seed = atoi(arguments.background);
      std::default_random_engine generator(seed);
      std::normal_distribution<double> et_distribution(10.0, 3.0); // 10-GeV mean; 3-GeV SD
      std::uniform_real_distribution<double> tau_id(0., 1.0);
      std::uniform_real_distribution<double> ele_id(0., 1.0);
      std::uniform_int_distribution<int> position_distribution(0, 16);
      std::uniform_int_distribution<int> object_link_distribution(0, N_OUTPUT_LINKS);
      std::uniform_int_distribution<int> object_word_distribution(0, N_REGIONS_PER_WORD);
      double object_et = 0;
      if (arguments.electron)
        object_et = atoi(arguments.electron);
      if (arguments.tau)
        object_et = atoi(arguments.tau);
      ofstream csvfilestream;
      if (arguments.csvfile) {
	if (!csvfilestream.is_open()) {
	  csvfilestream.open(arguments.csvfile, ofstream::out);
	  csvfilestream << "event,cycle,link,region,et,position,electron,tau" << endl;
	}
      }
      for (size_t i = 0; i < N_EVENTS; i++) {
        for (size_t j = 0; j < N_WORDS_PER_FRAME; j++) {
          for (size_t k = 0; k < N_OUTPUT_LINKS; k++) {
            link_out[j][k] = 0;
            for (size_t l = 0; l < N_REGIONS_PER_WORD; l++) {
              double et = et_distribution(generator);
              int pos = position_distribution(generator);
              bool tau_bit = false;
              if(arguments.tau) {
                size_t object_l = object_link_distribution(generator);
                size_t object_w = object_word_distribution(generator);
                if (k == object_l and j == object_w) {
                  et += object_et;
                  if(tau_id(generator) < 0.8) tau_bit = true;
                }
              }
              if(tau_id(generator) < 0.3) tau_bit = true;
              bool ele_bit = false;
              if(arguments.electron) {
                size_t object_l = object_link_distribution(generator);
                size_t object_w = object_word_distribution(generator);
                if (k == object_l and j == object_w) {
                  et += object_et;
                  if(ele_id(generator) < 0.9) ele_bit = true;
                }
              }
              if(ele_id(generator) < 0.1) ele_bit = true;
              UCTRegion region(et, pos, ele_bit, tau_bit);
	      uint64_t region_bits = region.bits();
              link_out[j][k] |= (region_bits << l * 16); // pack regions in link word
	      if (csvfilestream.is_open()) {
		csvfilestream << i << "," << j << "," << k << "," << l << "," << et << "," << pos << "," << ele_bit << "," << tau_bit << endl;
	      }
            }
          }
        }
        uint16_t last_cycle_of_event = 0;
        for (size_t j = 0; j < N_WORDS_PER_FRAME; j++) {
          for (size_t k = 0; k < N_OUTPUT_LINKS; k++) {
            if (j == (N_WORDS_PER_FRAME - 1)) {
              last_cycle_of_event = 1;
            }
            else {
              last_cycle_of_event = 0;
            }
            size_t c = i * N_WORDS_PER_FRAME + j;
	    APxLinkData::LinkValue v = {last_cycle_of_event, link_out[j][k]};
            datafile_out.add(c, k, v);
          }
        }
      }
    }
    datafile_out.write(arguments.writefile);
    if (arguments.verbose) {
      cout << "Output data:" << endl;
      datafile_out.print();
    }
  }
  
  if (arguments.cmpfile) {
    APxLinkData datafile_cmp(N_OUTPUT_LINKS);
    datafile_cmp.read(arguments.cmpfile);

    if (datafile_cmp != datafile_out) {
      cout << "HLS output DOES NOT match!" << endl;
      return -1;
    } else {
      cout << "HLS output matches!" << endl;
    }
  }

  return 0;
}
