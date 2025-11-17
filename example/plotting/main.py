from nsdf_dark_matter.idx import load_all_data
import matplotlib.pyplot as plt


def main():
    # specify the path to the dataset you want to use
    cdms = load_all_data('./idx/07180808_1558_F0003')

    event_id = cdms.get_event_ids()[0]
    detector_ids = cdms.get_detectors_by_event(event_id)

    # Extracting all the channel data from each detector
    channel_data = []
    for det in detector_ids:
        channel_data.append(cdms.get_detector_channels(det))

    # Visualizing the pulses
    plt.figure(figsize=(12, 6))
    plt.title(f"Visualizing 07180808_1558_F0003, Event: {event_id}", fontweight="bold")
    plt.xlabel("Time (20ns intervals)")
    plt.ylabel("Amplitude (ADC Channels)")

    cmap = plt.get_cmap('Set1')
    for i, det_channels in enumerate(channel_data):
        for row in range(det_channels.shape[0]):
            label = f"D{detector_ids[i].split('_')[1]}" if row == 0 else None
            plt.plot(det_channels[row], color=cmap(i), label=label)

    plt.legend()
    plt.show()


main()
