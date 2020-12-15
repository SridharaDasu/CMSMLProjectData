
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>

#include <iostream>
#include <fstream>
#include <iomanip>
#include <string>
#include <random>
#include <string.h>

#include "APxLinkData.hh"
#include "UCTRegion.hh"

using namespace std;

const char *algo_top_tb_version = "genMLProjectData 1.0";
const char *algo_top_tb_bug_address = "<dasu@hep.wisc.edu>";

static char doc[] = "APx HLS Firmware Development - Data Generator";

char parse(char *arg, char *&name, char *&value) {
  char *decorated_name = strtok(arg, "=");
  value = strtok(NULL, "\0");
  char key = 0;
  if (strncmp(decorated_name, "--", 2) == 0) {
    key = decorated_name[2];
    name = &decorated_name[2];
  }
  else if (decorated_name[0] == '-') {
    key = decorated_name[1];
    name = NULL;
  }
  return key;
}


int main(int argc, char **argv) {
  
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
  struct arguments arguments = {0, 0, 0, 0, 0, 0, 0, 0, 0, false};
  const char* arg_names[10] = {
			       "read",
			       "write",
			       "dump",
			       "compare",
			       "background",
			       "electron",
			       "tau",
			       "met",
			       "jets",
			       "verbose"
  };

  char argv_copy[argc][1024];
  char key, *name, *value;
  for (size_t i = 1; i < argc; i++) {
    strcpy(argv_copy[i], argv[i]);
    key = parse(&argv_copy[i][0], name, value);
    bool match = false;
    if (name == NULL) {
      match = true;
    }
    else{
      for (size_t j = 0; j < sizeof(arg_names); j++) {
	if(strncmp(arg_names[j], name, strlen(name)) == 0) {
	  match = true;
	  break;
	}
      }
    }
    if (match) {
      switch (key) {
      case 'r': arguments.readfile = value; break;
      case 'w': arguments.writefile = value; break;
      case 'd': arguments.csvfile = value; break;
      case 'c': arguments.cmpfile = value; break;
      case 'b': arguments.background = value; break;
      case 'e': arguments.electron = value; break;
      case 't': arguments.tau = value; break;
      case 'm': arguments.met = value; break;
      case 'j': arguments.jets = value; break;
      case 'v': arguments.verbose = true; break;
      default: break;
      }
    }
    else {
      cerr << "Failed to parse: " << argv[i] << endl;
      cerr << "Valid options are:" << endl;
      for (size_t j = 0; j < sizeof(arg_names); j++) {
	cerr << "\t--" << arg_names[j] << endl;
      }
    }
  }
  
  double object_et = 0;
  
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
  if (arguments.electron) {
    cout << "Generated data will include an electron with PT = " << arguments.electron << endl;
    object_et = atoi(arguments.electron);
  }
  if (arguments.tau) {
    cout << "Generated data will include an tau with PT = " << arguments.tau << endl;
    object_et = atoi(arguments.tau);
  }
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
  const size_t N_INPUT_LINKS = N_REGIONS_PHI;
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
      std::uniform_int_distribution<int> object_phi_distribution(0, N_REGIONS_PHI);
      std::uniform_int_distribution<int> object_eta_distribution(0, N_REGIONS_ETA);
      ofstream csvfilestream;
      if (arguments.csvfile) {
	if (!csvfilestream.is_open()) {
	  csvfilestream.open(arguments.csvfile, ofstream::out);
	  csvfilestream << "event,eta,phi,et,position,electron,tau" << endl;
	}
      }
      for (size_t i = 0; i < N_EVENTS; i++) {
	cout << i;
	size_t object_phi = object_phi_distribution(generator);
	size_t object_eta = object_eta_distribution(generator);
        for (size_t eta = 0; eta < N_REGIONS_ETA; eta++) {
	  for (size_t phi = 0; phi < N_REGIONS_PHI; phi++) {
	    cout << ".";
	    size_t j = eta / N_WORDS_PER_FRAME; // Four eta fit in a 64-bit word
	    size_t l = eta % N_WORDS_PER_FRAME; // Four 64-bit words per link
	    if (l == 0) link_out[j][phi] = 0;
	    double et = et_distribution(generator);
	    int pos = position_distribution(generator);
	    bool tau_bit = false;
	    if(arguments.tau) {
                if (phi == object_phi && eta == object_eta) {
                  et += object_et; cout << et;
                  if(tau_id(generator) < 0.8) tau_bit = true;
                }
	    }
	    if(tau_id(generator) < 0.3) tau_bit = true;
	    bool ele_bit = false;
	    if(arguments.electron) {
	      if (phi == object_phi && eta == object_eta) {
		et += object_et; cout << et;
		if(ele_id(generator) < 0.9) ele_bit = true;
	      }
	    }
	    if(ele_id(generator) < 0.1) ele_bit = true;
	    UCTRegion region(et, pos, ele_bit, tau_bit);
	    uint64_t region_bits = region.bits();
	    link_out[j][phi] |= (region_bits << l * 16); // pack regions in link word
	    if (csvfilestream.is_open()) {
	      csvfilestream << i << "," << eta << "," << phi << "," << et << "," << pos << "," << ele_bit << "," << tau_bit << endl;
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
	cout << endl;
      }
    }
    datafile_out.write(arguments.writefile);
    if (arguments.verbose) {
      cout << "Output data:" << endl;
      datafile_out.print();
    }
  }
  
  if (arguments.cmpfile) {
    cout << arguments.cmpfile << endl;
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
