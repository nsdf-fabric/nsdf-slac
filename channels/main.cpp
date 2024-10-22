#include "../../IOLibrary/src/cdms_iolibrary.h"
#include "../../IOLibrary/src/midas_file_reader.h"
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <ostream>
#include <string>

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

void printChannelData(uint16_t* addr, int N) {
    std::cout << "[ ";
    for(size_t i = 0; i < N; i++) {
        std::cout << addr[i] << " ";
    }
    std::cout <<  "]" << std::endl;
}

int main(int argc, char **argv) {
  int debug = 0;
  int eventsToRead = 1;
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
    } catch (const std::exception&) {
      break;
    }

    int numberOfDetectors = event.detectors.size();
    if(numberOfDetectors != 0) { 
        std::cout << "Event ID: " << event.eventNumber << std::endl;
        std::cout << "Total number of detectors: " << numberOfDetectors << std::endl;

        for(auto d: event.detectors) {
            std::cout << "Number of channels in detector " << d.channels.size() << std::endl;
            for(auto chan: d.channels) {
                if(debug) {
                    printChannelInfo(chan);
                    printChannelData(chan.data, chan.totalLength());
                } 
            }
        }

    }
  }
}



