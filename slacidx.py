import OpenVisus as ov
import sys
from typing import DefaultDict, List
import panel as pn
from bokeh.plotting import figure
import os
from collections import defaultdict
from bokeh.models import (
    GlyphRenderer,
    HoverTool,
    BoxZoomTool,
    PanTool,
    ResetTool,
    SaveTool,
    WheelZoomTool,
)
import numpy as np
import matplotlib.colors as mcolors
import csv
from svgs import *
from bisect import bisect_left


# detectors_map = {'10000_2_Phonon4096': False, '10000_1_Phonon4096': False}
# channel_to_renderer = {'10000_2_Phonon4096_C1': GlyphRender(), '10000_1_Phonon4096_C1': GlyphRenderer()}

MID_FILES_DIR = "./raw/"
IDX_FILES_DIR = "./idx/"
EVENT_METADATA_DIR = "./metadata/"
COLORS = [
    "#ff0000",  # Red
    "#ffff00",  # Yellow
    "#0000ff",  # Blue
    "#ff00ff",  # Magenta
    "#00ff00",  # Green
    "#800080",  # Purple
    "#00ffff",  # Cyan
]


class EventMetadata:
    def __init__(self):
        self.trigger_type = "Unknown"
        self.readout_type = "None"
        self.global_timestamp = 0

    def extract(self, headers: List[str], metadata: List[str]):
        for i, h in enumerate(headers):
            match h.strip():
                case "trigger_type":
                    self.trigger_type = metadata[i].strip()
                case "readout_type":
                    self.readout_type = metadata[i].strip()
                case "global_timestamp":
                    self.global_timestamp = int(metadata[i].strip())
                case _:
                    continue

def create_channel_metadata_map(filepath: str) -> DefaultDict[str, List]:
    mp = defaultdict(list)
    with open(filepath, "r") as f:
        for line in f:
            channel_name, lo, hi = line.split(" ")
            mp[channel_name].append(int(lo))
            mp[channel_name].append(int(hi))
    f.close()
    return mp


def create_event_metadata_map(filepath: str) -> DefaultDict[str, EventMetadata]:
    mp = defaultdict(EventMetadata)
    i = 0
    headers = []
    with open(filepath, "r") as f:
        reader = csv.reader(f)
        for line in reader:
            if i == 0:
                headers = line
            else:
                evt_metadata = EventMetadata()
                evt_metadata.extract(headers, line)
                mp[line[0]] = evt_metadata
            i += 1
    f.close()
    return mp


def generate_palette(hex_color, steps=8):
    """Generate a palette of 20 colors from a given hex color"""
    cmap = mcolors.LinearSegmentedColormap.from_list(
        "gradient", [hex_color, "#FFFFFF"], N=steps
    )
    palette = [mcolors.to_hex(cmap(i)) for i in range(steps)]
    return palette


def get_mid_files(remote_url: str):
    mid_files = []
    if remote_url != "":
        pass
    else:
        for filename in os.listdir(MID_FILES_DIR):
            if filename.endswith(".mid") or filename.endswith(".mid.gz"):
                mid_files.append(filename.split(".")[0])
    return mid_files


class AppState:
    def __init__(self, url):
        self.palettes = {color: generate_palette(color) for color in COLORS}
        self.gradient_idx = 0
        self.mid_files = []
        self.scene_data: np.ndarray
        self.event_idx = 0
        self.events = []
        self.detectors = []
        self.detectors_map = {}
        self.channels_data = []
        self.channel_to_renderer = defaultdict(GlyphRenderer)
        self.figure_title = ""
        self.detector_to_channels = defaultdict(List)
        self.event_to_metadata = defaultdict(EventMetadata)
        self.event_metadata: EventMetadata

        # widgets
        self.fig = self.new_fig("")
        self.load_mid_files(url)

        self.prev_event_button = pn.widgets.Button(
            icon=LEFT_ARROW, button_type="primary", icon_size="1.5em"
        )
        self.next_event_button = pn.widgets.Button(
            icon=RIGHT_ARROW, button_type="primary", icon_size="1.5em"
        )
        self.first_event_button = pn.widgets.Button(
            icon=LEFT_DOUBLE_ARROW, button_type="success", icon_size="1.5em"
        )
        self.last_event_button = pn.widgets.Button(
            icon=RIGHT_DOUBLE_ARROW, button_type="success", icon_size="1.5em"
        )
        self.event_metadata_widget = pn.pane.Markdown("""
        **Event Information**
        """)

    def reset_gradient_idx(self):
        self.gradient_idx = 0

    def update_event_idx(self, idx):
        self.event_idx = idx

    def new_fig(self, mid_file):
        fig = figure(
            title=mid_file,
            x_axis_label="Time",
            y_axis_label="Amplitude (ADC Channels)",
            tools=[
                PanTool(),
                BoxZoomTool(),
                WheelZoomTool(),
                SaveTool(),
                ResetTool(),
                HoverTool(
                    tooltips=[("x", "@x"), ("y", "@y"), ("Channel", "$name")],
                ),
            ],
            sizing_mode="stretch_both",
        )

        fig.toolbar.active_scroll = fig.select_one(WheelZoomTool)
        return fig

    def load_mid_files(self, remote_url):
        self.mid_files = get_mid_files(remote_url)

    def load_scene_data(self, mid_file):
        self.detector_to_channels = create_channel_metadata_map(
            os.path.join(IDX_FILES_DIR, f"{mid_file}_metadata.txt")
        )
        self.event_to_metadata = create_event_metadata_map(
            os.path.join(EVENT_METADATA_DIR, f"{mid_file}.csv")
        )
        self.scene_data = ov.LoadDataset(
            os.path.join(IDX_FILES_DIR, f"{mid_file}.idx")
        ).read(field="data")

    def load_events(self):
        if self.scene_data.any():
            st = set()
            for k in self.detector_to_channels.keys():
                evt = k.split("_")[0]
                if evt not in st:
                    st.add(evt)
            events = list(st)
            events.sort()
            self.events = events

    def load_detectors(self, event_id):
        if self.scene_data.any():
            detectors, detectors_map = [], defaultdict(bool)
            for k in self.detector_to_channels.keys():
                if event_id in k:
                    multichoice_detectors = k.split("_")[1]
                    detectors.append(f"D{multichoice_detectors}")
                    detectors_map[f"{event_id}_{multichoice_detectors}_Phonon_4096"] = (
                        True
                    )

            self.detectors, self.detectors_map = detectors, detectors_map

    def update_detectors_map(self, detectors):
        detectors = set([d[1] for d in detectors])
        for k in self.detectors_map.keys():
            if k.split("_")[1] not in detectors:
                self.detectors_map[k] = False
            else:
                self.detectors_map[k] = True

    def load_channel_data(self, detectors):
        if self.scene_data.any() and len(detectors) > 0:
            channels = []
            for k in self.detectors_map.keys():
                lo, hi = self.detector_to_channels[k]
                data = self.scene_data[lo:hi]
                channels.append((k, data))
            self.channels_data = channels
        else:
            self.channels_data = []

    def load_event_metadata(self, eventID):
        self.event_metadata = self.event_to_metadata[eventID]

    def add_channel(self, channel_name, line: GlyphRenderer):
        self.channel_to_renderer[channel_name] = line

    def handle_channel_selection(self, channel_name, state):
        """
        Parameters
        ----------
        channel_name (str): the name of the channel (C1, C2, ..., Cn).
        state (bool): the visibility state to transition to.
        """
        for k in self.channel_to_renderer.keys():
            if channel_name in k and self.detectors_map[k.split("_C")[0]]:
                self.channel_to_renderer[k].visible = state

    def fig_deep_clean(self):
        for renderer in self.channel_to_renderer.values():
            self.fig.renderers.remove(renderer)
        self.channel_to_renderer = defaultdict(GlyphRenderer)

    def clean_channels(self):
        for renderer in self.channel_to_renderer.values():
            renderer.visible = False

    def toggle_event_controls(self, state):
        self.first_event_button.disabled = state
        self.prev_event_button.disabled = state
        self.next_event_button.disabled = state
        self.last_event_button.disabled = state

    def add_line_glyph(self, data, label):
        d_num = label.split("_")[1]
        self.add_channel(
            label,
            self.fig.line(
                x=list(range(len(data))),
                y=data,
                name=label,
                color=self.palettes[COLORS[int(d_num)]][self.gradient_idx],
                line_width=3,
            ),
        )
        self.gradient_idx += 1 if self.gradient_idx + 1 < 20 else 0

    def add_legend_glyph(self):
        for d in self.detectors_map.keys():
            d_num = d.split("_")[1]
            self.fig.line(
                legend_label=f"D{d_num}", line_color=COLORS[int(d_num)], line_width=3
            )

    def render_event_metadata(self):
        self.event_metadata_widget.object = f"""
       <style>
       .title {{
            text-align: center;
            font-size: 22px;
            font-weight: 500;
       }}
        .styled-table {{
            width: 100%;
            margin: 0 auto;
            border-collapse: collapse;
            font-size: 16px;
        }}
        .styled-table th, .styled-table td {{
            padding: 4px;
            text-align: center;
        }}
        .styled-table th {{
            background-color: #0072b5;
            color: #ffffff;
            border: black solid 1px;
        }}
        </style>
        <div class="title">Event Metadata</div>
        <table class="styled-table">
            <thead>
                <tr>
                    <th>Trigger Type</th>
                    <th>Readout Type</th>
                    <th>Global Timestamp</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>{self.event_metadata.trigger_type}</td>
                    <td>{self.event_metadata.readout_type}</td>
                    <td>{self.event_metadata.global_timestamp}</td>
                </tr>
            </tbody>
        </table>
    """

    def render_channels(self, detectors):
        detectors = set([d[1] for d in detectors])
        # create renderers for new detectors, if any
        for channel in self.channels_data:
            channel_name, datarows = channel
            self.reset_gradient_idx()
            for i, data in enumerate(datarows):
                channel_ID = f"{channel_name}_C{str(i+1)}"
                if channel_ID not in self.channel_to_renderer:
                    self.add_line_glyph(data, channel_ID)
                else:
                    self.channel_to_renderer[channel_ID].visible = True

        # check any deselected detectors that are currently shown in the plot, hide them
        if len(detectors) > 0:
            for d in self.channel_to_renderer.keys():
                if d.split("_")[1] not in detectors:
                    self.channel_to_renderer[d].visible = False
        else:
            self.clean_channels()


def main():
    remote_url = ""
    if len(sys.argv) == 2:
        remote_url = sys.argv[1]

    app_state = AppState(remote_url)
    pn.extension(design="material", sizing_mode="stretch_width")

    # ---------------- WIDGETS ---------------------------
    select_scene = pn.widgets.Select(name="Scene", options=app_state.mid_files)

    event_controls_tooltip = pn.widgets.TooltipIcon(
        value="first event, prev event, next event, last event"
    )

    input_event = pn.widgets.AutocompleteInput(
        name="Event ID",
        restrict=True,
        options=[],
        case_sensitive=False,
        search_strategy="includes",
        placeholder="Search Event",
        value="",
    )

    event_controls = pn.layout.Row(
        pn.Spacer(width=50),
        app_state.first_event_button,
        app_state.prev_event_button,
        app_state.next_event_button,
        app_state.last_event_button,
        event_controls_tooltip,
    )

    multichoice_detectors = pn.widgets.MultiChoice(
        name="Detectors",
        options=[],
        value=[],
        solid=False,
    )

    checkbox_toggle_detectors = pn.widgets.Checkbox(
        name="Select/Deselect All Detectors", disabled=True
    )

    # ------------------- REACTIVITY ---------------------

    def filter_channels(evt):
        state = True if evt.obj.button_type == "primary" else False
        channel_name = evt.obj.name
        app_state.handle_channel_selection(channel_name, not state)
        evt.obj.button_type = (
            "default" if evt.obj.button_type == "primary" else "primary"
        )

    def update_events(mid_file):
        app_state.load_scene_data(mid_file)
        app_state.load_events()
        input_event.options = app_state.events
        # needs to transition from empty to trigger update_detectors
        input_event.value = ""
        input_event.value = input_event.options[0]

    def update_detectors(eventID):
        if eventID != "":
            app_state.fig_deep_clean()
            app_state.load_detectors(eventID)
            app_state.add_legend_glyph()
            app_state.load_event_metadata(eventID)
            app_state.render_event_metadata()
            multichoice_detectors.options = app_state.detectors
            checkbox_toggle_detectors.disabled = False

            # update event index on search (options is sorted)
            idx = bisect_left(input_event.options, eventID)
            if idx >= 0 and idx < len(input_event.options):
                app_state.update_event_idx(idx)
            # needs to transition from empty to trigger update_fig
            multichoice_detectors.value = []
            multichoice_detectors.value = app_state.detectors
            checkbox_toggle_detectors.value = True

    def toggle_detectors(state):
        multichoice_detectors.value = app_state.detectors if state else []

    def update_fig(detectors):
        app_state.toggle_event_controls(True)
        app_state.update_detectors_map(detectors)
        app_state.load_channel_data(detectors)
        disable_buttons()
        app_state.render_channels(detectors)
        app_state.toggle_event_controls(False)

    def update_event_to_first(_):
        input_event.value = input_event.options[0]
        app_state.event_idx = 0

    def update_event_to_last(_):
        input_event.value = input_event.options[-1]
        app_state.event_idx = len(app_state.events) - 1

    def update_event_to_next(_):
        app_state.event_idx = (
            app_state.event_idx
            if app_state.event_idx + 1 >= len(app_state.events)
            else app_state.event_idx + 1
        )
        input_event.value = input_event.options[app_state.event_idx]

    def update_event_to_prev(_):
        app_state.event_idx = (
            0 if app_state.event_idx - 1 < 0 else app_state.event_idx - 1
        )
        input_event.value = input_event.options[app_state.event_idx]

    app_state.first_event_button.on_click(update_event_to_first)
    app_state.prev_event_button.on_click(update_event_to_prev)
    app_state.next_event_button.on_click(update_event_to_next)
    app_state.last_event_button.on_click(update_event_to_last)

    evt_bind = pn.bind(update_events, select_scene)
    detectors_bind = pn.bind(update_detectors ,input_event)
    toggle_detectors_bind = pn.bind(toggle_detectors, checkbox_toggle_detectors)
    fig_bind = pn.bind(update_fig, multichoice_detectors)
    # ---------------------------------------------------

    channels_grid = pn.GridBox(
        *[
            pn.widgets.Button(
                name=f"C{i+1}", button_type="primary", on_click=filter_channels
            )
            for i in range(20)
        ],
        ncols=5,
    )

    def disable_buttons():
        """
        Disable buttons up to max channel count (e.g. if D1 has the most detectors at 4 disable 5-20)
        """
        limit = 0
        for _, arr in app_state.channels_data:
            limit = max(limit, len(arr))
        for i in range(20):
            channels_grid[i].disabled = False if i < limit else True

    main_layout = pn.template.MaterialTemplate(
        title="NSDF SLAC",
        header=[evt_bind,detectors_bind ,toggle_detectors_bind, fig_bind],
        sidebar=[
            select_scene,
            input_event,
            event_controls,
            multichoice_detectors,
            checkbox_toggle_detectors,
            channels_grid,
            app_state.event_metadata_widget
        ],
        main=[app_state.fig],
        sidebar_width=420,
    )

    main_layout.servable()

main()
