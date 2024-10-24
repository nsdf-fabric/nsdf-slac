#include "../../IOLibrary/src/cdms_iolibrary.h"
#include "../..//IOLibrary/src/midas_file_reader.h"
#include "../../cnpy/cnpy.h"
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <ostream>
#include <string>
#include <vector>

std::string channelType(int t) {
    return t == 0 ? "Charge" : "Phonon";
}

std::string baselineControl(int b) {
    return b == 0 ? "Inactive" : "Active";
}

void printChannelInfo(CDMSIOLIB::CHANNEL chan) {
    std::cout << "\n{" << "\nName: " << chan.channelName <<
        "\nType: " << channelType(chan.channelType) <<
        "\nBaseline Control: "  << baselineControl(chan.baselineControlActive) << 
        "\nSampling Rate Low: " << chan.samplerateLow << 
        "\nSampling Rate High: " << chan.samplerateHigh << 
        "\nNumber of samples: " << chan.totalLength() << 
        "\nNumber of Pre-Pulse samples: " << chan.prepulseLength << 
        "\nNumber of On-Pulse samples: " << chan.onpulseLength << 
        "\nNumber of Post-Pulse samples: " << chan.postpulseLength << "\n}\n";
}

void printVector(std::vector<uint16_t> v) {
    for(int i = 0; i < v.size(); i++) {
        std::cout << v[i] << " ";
    }
    std::cout << std::endl;
}

std::string generateFilename(unsigned int evtID, int detectorNumber , int chanNumber, CDMSIOLIB::DETECTOR &detector, CDMSIOLIB::CHANNEL &chan) {
    /*
     * Filename format:
     * eventid - dectectornumber - channelnumber- channeltype - channelsamples
     * */
    return std::to_string(evtID) + "_" + std::to_string(detectorNumber) + "_" + std::to_string(chanNumber) + "_" + 
    channelType(chan.channelType) + "_" + std::to_string(chan.totalLength());
}

void np(uint16_t* addr, int N, std::string fname) {
    std::vector<uint16_t> channels(N);
    for(size_t i = 0; i < N; i++) {
        channels[i] = addr[i];
    }
    std::string zipname = "out.npz";
    cnpy::npz_save(zipname, fname, &channels[0], {channels.size()}, "a");
}

int main(int argc, char **argv) {
  int debug = 0;
  int eventsToRead = 10;
  int count = 1;
  if(argc == 2) {
     debug = std::string(argv[1]) == "debug" ? 1 : 0;
  }
 // Open the file
  CDMSIOLIB::MidasFileReader reader;
  reader.OpenFile("./07180808_1558_F0001.mid.gz");
 
  // Read events
  CDMSIOLIB::CDMS_EVENT event;
  while (eventsToRead--) {
    try {
      event = reader.GetNextEvent();
            std::cout << "sim series: " << event.SIMSeriesNumber << std::endl;
    } catch (const std::exception&) {
      break;
    }

    int numberOfDetectors = event.detectors.size();
    if(numberOfDetectors != 0) { 
        for(size_t i = 0; i < event.detectors.size(); i++) {
            for(size_t j = 0; j < event.detectors[i].channels.size(); j++){
                if(debug) {
                    std::string fname = generateFilename(event.eventNumber, i, j, event.detectors[i], event.detectors[i].channels[j]);
                    np(event.detectors[i].channels[j].data, event.detectors[i].channels[j].totalLength(), fname);
                }
            }
        }

    }
  }
}



