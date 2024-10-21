#include "../IOLibrary/src/cdms_iolibrary.h"
#include "../IOLibrary/src/midas_file_reader.h"
#include <cstdint>
#include <iostream>
#include <string>

std::string channelType(int t) {
    return t == 0 ? "Charge" : "Phonon";
}

std::string baselineControl(int b) {
    return b == 0 ? "Inactive" : "Active";
}

void printChannelInfo(CDMSIOLIB::CHANNEL chan) {
    std::cout << "\n{\n" << "Name: " << chan.channelName << "\n" << "Type: " << channelType(chan.channelType) << "\n" << "Baseline Control: "  << baselineControl(chan.baselineControlActive) <<  "\n" << "Number of samples: " << chan.totalLength() <<  "\n}\n";
}

void printChannelData(uint16_t* addr) {

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
                if(debug) printChannelInfo(chan);
            }
        }

    }
  }
}



