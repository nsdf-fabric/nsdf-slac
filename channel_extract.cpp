#include "../IOLibrary/src/cdms_iolibrary.h"
#include "..//IOLibrary/src/midas_file_reader.h"
#include "../cnpy/cnpy.h"
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <ostream>
#include <string>
#include <vector>
#include <filesystem>
#include <fstream>

const std::string MID_FILES_DIR="./raw/";
const std::string NPZ_FILES_DIR="./mid_npz/";
const std::string METADATA_FILES_DIR="./metadata/";
const std::string delimeter = ".mid";

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
}

void print2dVector(std::string fname, std::vector<std::vector<uint16_t>> v) {
    std::cout << "\nFile: " << fname;
    std::cout << "\nShape (" << v.size() << "," << v[0].size() << ")";
    for(size_t i =0; i < v.size(); i++){
        std::cout << "\nChannel " << i << "\n";
        printVector(v[i]);
    }
}

void extractEventMetadata(CDMSIOLIB::CDMS_EVENT evt, std::ofstream &file) {
    file << std::to_string(evt.eventNumber) << ","
         << evt.triggerTypeAsString() << ","
         << evt.readoutTypeAsString() << ","
         << std::to_string(evt.global_timestamp) << "\n";
}

void writeCsvHeaders(std::ofstream &file) {
    file << "event,trigger_type,readout_type,global_timestamp\n";
}

std::string generateFilename(unsigned int evtID, int detectorNumber, CDMSIOLIB::CHANNEL &chan) {
    /*
     * Filename format:
     * eventid - dectectornumber - channeltype - channelsamples
     * */
    return std::to_string(evtID) + "_" + std::to_string(detectorNumber) + "_" + 
    channelType(chan.channelType) + "_" + std::to_string(chan.totalLength());
}

void np(std::vector<std::vector<uint16_t>> channels, std::string fname) {
    std::string const zipname = "07180830_0950_F0002.npz";
    print2dVector(fname, channels);
    cnpy::npz_save(zipname, fname, &channels[0][0], {channels.size(), channels[0].size()}, "a");
}

std::vector<uint16_t> extractChannel(uint16_t* addr, int N) {
    std::vector<uint16_t> channel(N);
    for(size_t i = 0; i < N; i++) {
        channel[i] = addr[i];
    }
    return channel;
}

int main(int argc, char **argv) {
  int eventsToRead = 100;
  std::string filepath = "";
  if(argc == 2)  filepath = argv[1];
  
  // create npz files  directory
  std::filesystem::create_directory(NPZ_FILES_DIR);
  std::filesystem::path midfile_path(filepath);
 // Open the file
  CDMSIOLIB::MidasFileReader reader;
  reader.OpenFile(filepath);
  
  // Read events
  CDMSIOLIB::CDMS_EVENT event;
  std::string basefile = midfile_path.stem().string();
  std::string zipname = NPZ_FILES_DIR + basefile.substr(0, basefile.find(".mid")) + ".npz";
  if(std::filesystem::exists(zipname)) return 0;

  // metadata file (trigger type, readout type, global timestamp)
  std::string csvname = METADATA_FILES_DIR + basefile.substr(0, basefile.find(".mid")) + ".csv";
  std::ofstream metadatafile(csvname);
  bool csvExists = std::filesystem::exists(csvname);
  writeCsvHeaders(metadatafile);

  while (eventsToRead--) {
    try { event = reader.GetNextEvent();} 
    catch (const std::exception&) { break;}
    
    extractEventMetadata(event, metadatafile);
    continue;
    // Parse the channels (Event-> Detectors-> Channels)
    int numberOfDetectors = event.detectors.size();
    std::string fname = "";
    if(numberOfDetectors != 0) {
        for(size_t i = 0; i < event.detectors.size(); i++) {
            // find valid channels (channels with 4096 samples or more)
            std::vector<int> validChannels;
            for(size_t j = 0; j < event.detectors[i].channels.size(); j++){
                int N = event.detectors[i].channels[j].totalLength();
                if(N >= 4096) validChannels.push_back(j);
                if(N > 1024 && N < 4096) std::cout << "we have a charge channel\n";
            }

            uint16_t channels[validChannels.size()][4096];
            for(size_t j = 0; j < validChannels.size(); j++){
                int chanIdx = validChannels[j];
                fname = generateFilename(event.eventNumber, i, event.detectors[i].channels[chanIdx]);
                for(size_t k =0; k < 4096; k++) {
                    channels[j][k] = event.detectors[i].channels[chanIdx].data[k];
                }
            }

            if(validChannels.size() > 0) cnpy::npz_save(zipname, fname, &channels[0][0], {validChannels.size(), 4096}, "a");
        }
    }
  }
  metadatafile.close();
}
