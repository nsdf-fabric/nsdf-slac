import os
import panel as pn
import plotly.graph_objects as go
from dotenv import load_dotenv
from botocore.client import Config
from boto3.session import Session
from nsdf_dark_matter.idx import load_all_data

load_dotenv()
FILES_VOLUME = os.getenv("FILES_VOLUME", "./idx/")
PREFIX = os.getenv("S3_PREFIX", "rec/cdms/umn/slac/idx/")
COLORS = ["#ff0000", "#ffff00", "#0000ff", "#ff00ff", "#00ff00", "#800080", "#00ffff"]


def get_aws_bucket():
    config = Config(signature_version="s3v4", s3={"addressing_style": "path"})

    s3 = Session().resource(
        "s3",
        endpoint_url=os.getenv("ENDPOINT_URL"),
        config=config,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
    return s3.Bucket(os.getenv("BUCKET_NAME"))


def check_s3_key_exists(key):
    bucket = get_aws_bucket()
    try:
        bucket.Object(key).load()
        return True
    except:
        return False


def download_processed_files(midfile):
    s3 = get_aws_bucket()
    filenames = [f"{midfile}.idx", "0000.bin", f"{midfile}.txt", f"{midfile}.csv"]
    for fn in filenames:
        key = f"{PREFIX}{midfile}/{fn}"
        dst = os.path.join(FILES_VOLUME, midfile, fn)
        if fn == "0000.bin":
            dst = os.path.join(FILES_VOLUME, midfile, midfile, fn)
        if os.path.exists(dst):
            continue
        print(f"Downloading key: {key}")
        if not check_s3_key_exists(key):
            raise FileNotFoundError(f"{midfile} not found in storage")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        try:
            s3.download_file(key, dst)
        except Exception as e:
            print(e)


def get_mid_files():
    with open("./uploaded_files.txt") as f:
        return [line.strip() for line in f]


def create_empty_fig(title="Select a mid file to begin"):
    fig = go.Figure()
    fig.update_layout(
        title=title,
            xaxis_title="Time (20ns intervals)",
            yaxis_title="Amplitude (ADC Channels)",
            template="plotly_white",
            hovermode="closest",
            xaxis=dict(range=[-200, 4200]),
            xaxis_title_font=dict(size=24),
            yaxis_title_font=dict(size=24),
            xaxis_tickfont=dict(size=18),
            yaxis_tickfont=dict(size=18),    )
    return fig


def main():
    pn.extension('plotly', design="material", sizing_mode="stretch_width", notifications=True)

    mid_files = get_mid_files()
    cdms_state = {"cdms": None, "detector_ids": []}
    channel_state = {"active": set()}

    mid_file = pn.widgets.AutocompleteInput(
        name="Mid File", options=mid_files, placeholder="Search Mid File",
        value=mid_files[0] if mid_files else "", restrict=True, case_sensitive=False, search_strategy="includes",
    )

    event_id = pn.widgets.AutocompleteInput(
        name="Event ID", options=[], placeholder="Select Event",
        value="", restrict=True, case_sensitive=False, search_strategy="includes",
        disabled=True,
    )

    first_btn = pn.widgets.Button(name="⏮︎", button_type="success", disabled=True, width=50)
    prev_btn = pn.widgets.Button(name="⏪︎", button_type="primary", disabled=True, width=50)
    next_btn = pn.widgets.Button(name="⏩︎", button_type="primary", disabled=True, width=50)
    last_btn = pn.widgets.Button(name="⏭︎", button_type="success", disabled=True, width=50)

    detectors = pn.widgets.MultiChoice(
        name="Detectors", options=[], value=[], solid=False, disabled=True,
    )
    channels_toggle_all = pn.widgets.Checkbox(
        name="Select/Deselect All Channels", disabled=True, value=True,
    )

    channel_toggles = pn.GridBox(
        *[pn.widgets.Button(name=f"C{i+1}", button_type="primary", width=60) for i in range(20)],
        ncols=5,
    )
    for b in channel_toggles:
        b.disabled = True

    spinner = pn.indicators.LoadingSpinner(value=False, visible=False, height=25, width=25)
    info = pn.pane.Markdown("")

    cite = pn.widgets.Button(name="Cite", button_type="success", sizing_mode="fixed")
    cite.js_on_click(args={}, code="""
    const w = window.open("https://nsdf-fabric.github.io/nsdf-slac/citations/", "_blank", "noopener,noreferrer");
    if(w) w.opener = null;
    """)

    meta = pn.pane.HTML("""<div style="text-align:center;font-size:18px;font-weight:500;">Event Metadata</div>
<div style="text-align:center;color:#666;">Select an event to view metadata.</div>""")

    plot = pn.pane.Plotly(create_empty_fig(), sizing_mode="stretch_both")

    def set_busy(busy):
        mid_file.disabled = event_id.disabled = detectors.disabled = busy
        channels_toggle_all.disabled = busy
        for b in channel_toggles:
            b.disabled = busy
        for b in (first_btn, prev_btn, next_btn, last_btn):
            b.disabled = busy
        spinner.value = spinner.visible = busy

    def build_figure():
        eid = event_id.value
        selected = detectors.value
        if not eid or not cdms_state["cdms"] or not selected:
            for b in channel_toggles:
                b.disabled = True
            return create_empty_fig(eid or "Select a mid file to begin")

        old_x_range = old_y_range = None
        if plot.object and plot.object.layout:
            xaxis = plot.object.layout.xaxis
            yaxis = plot.object.layout.yaxis
            if xaxis and not xaxis.autorange and xaxis.range:
                old_x_range = list(xaxis.range)
            if yaxis and not yaxis.autorange and yaxis.range:
                old_y_range = list(yaxis.range)

        fig = go.Figure()
        max_ch = 0

        for det_id in cdms_state["detector_ids"]:
            det_num = det_id.split("_")[1]
            if det_num not in selected:
                continue
            channels = cdms_state["cdms"].get_detector_channels(det_id)
            if len(channels) == 0:
                continue
            max_ch = max(max_ch, len(channels))
            color = COLORS[int(det_num) % len(COLORS)]
            first_active_j = next(
                (j for j, ch in enumerate(channels) if (j + 1) in channel_state["active"]),
                None,
            )
            for j, ch in enumerate(channels):
                ch_idx = j + 1
                is_active = ch_idx in channel_state["active"]
                fig.add_trace(go.Scatter(
                    x=list(range(len(ch))) if is_active else [],
                    y=ch if is_active else [],
                    mode="lines",
                    name=f"D{det_num}",
                    legendgroup=det_num,
                    hovertemplate=f"{det_id}_C{ch_idx}<extra></extra>" if is_active else None,
                    line=dict(color=color, width=2.0),
                    showlegend=j == first_active_j,
                    visible=True,
                    customdata=[ch_idx] * len(ch) if is_active else [],
                ))

        for i, b in enumerate(channel_toggles):
            ch_idx = i + 1
            if ch_idx > max_ch:
                b.disabled = True
                b.button_type = "default"
            else:
                b.disabled = False
                b.button_type = "primary" if ch_idx in channel_state["active"] else "default"

        fig.update_layout(
            xaxis_title="Time (20ns intervals)",
            yaxis_title="Amplitude (ADC Channels)",
            template="plotly_white",
            hovermode="closest",
            xaxis=dict(range=[-200, 4200]),
            xaxis_title_font=dict(size=24),
            yaxis_title_font=dict(size=24),
            xaxis_tickfont=dict(size=18),
            yaxis_tickfont=dict(size=18),
            legend=dict(
                x=1, y=1,
                bgcolor='rgba(255,255,255,0.7)',
                bordercolor='black',
                borderwidth=1,
                font=dict(size=18),
            ),
        )
        if old_x_range:
            fig.update_xaxes(range=old_x_range)
        if old_y_range:
            fig.update_yaxes(range=old_y_range)
        return fig

    def on_mid_file(evt):
        mf = evt.new
        if not mf:
            return
        set_busy(True)
        info.object = f"**Loading {mf}...**"
        try:
            download_processed_files(mf)
            cdms_state["cdms"] = load_all_data(f"{FILES_VOLUME}{mf}")
        except Exception as e:
            pn.state.notifications.error(str(e), duration=3000)
            set_busy(False)
            info.object = ""
            return
        events = cdms_state["cdms"].get_event_ids()
        event_id.options = events
        event_id.value = ""
        event_id.value = events[0]
        event_id.disabled = False
        pn.state.notifications.success(f"Loaded {mf}", duration=3000)
        plot.config = {"toImageButtonOptions": {"filename": mf, "height": None, "width": None}}
        set_busy(False)
        info.object = ""

    def on_event(evt):
        eid = evt.new
        if not eid or not cdms_state["cdms"]:
            return
        detector_ids = cdms_state["cdms"].get_detectors_by_event(eid)
        cdms_state["detector_ids"] = detector_ids
        d_labels = [d.split("_")[1] for d in detector_ids]
        detectors.options = d_labels
        detectors.value = []
        detectors.value = d_labels
        detectors.disabled = False
        max_ch = max((len(cdms_state["cdms"].get_detector_channels(d)) for d in detector_ids), default=0)
        channel_state["active"] = set(range(1, max_ch + 1))
        channels_toggle_all.value = True
        channels_toggle_all.disabled = False
        for b in (first_btn, prev_btn, next_btn, last_btn):
            b.disabled = False
        m = cdms_state["cdms"].get_event_metadata(eid)
        if m:
            meta.object = f"""
<style>
.title {{ text-align: center; font-size: 18px; font-weight: 500; }}
.styled-table {{ width: 100%; margin: 0 auto; border-collapse: collapse; font-size: 14px; }}
.styled-table th, .styled-table td {{ padding: 4px; text-align: center; }}
.styled-table th {{ background-color: #0072b5; color: #ffffff; border: black solid 1px; }}
.styled-table td {{ border: black solid 1px; }}
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
            <td>{m.trigger_type}</td>
            <td>{m.readout_type}</td>
            <td>{m.global_timestamp}</td>
        </tr>
    </tbody>
</table>
"""

    def on_detectors(evt):
        channel_state["active"] = set(range(1, 21))
        channels_toggle_all.value = True
        plot.object = build_figure()

    def on_channels_toggle_all(state):
        if cdms_state["cdms"]:
            selected = detectors.value
            max_ch = 0
            for det_id in cdms_state["detector_ids"]:
                det_num = det_id.split("_")[1]
                if det_num in selected:
                    channels = cdms_state["cdms"].get_detector_channels(det_id)
                    max_ch = max(max_ch, len(channels))
            if state:
                channel_state["active"] = set(range(1, max_ch + 1))
            else:
                channel_state["active"] = set()
            plot.object = build_figure()

    def nav_first(_):
        if event_id.options:
            event_id.value = event_id.options[0]

    def nav_prev(_):
        if event_id.value in event_id.options:
            idx = event_id.options.index(event_id.value)
            if idx > 0:
                event_id.value = event_id.options[idx - 1]

    def nav_next(_):
        if event_id.value in event_id.options:
            idx = event_id.options.index(event_id.value)
            if idx < len(event_id.options) - 1:
                event_id.value = event_id.options[idx + 1]

    def nav_last(_):
        if event_id.options:
            event_id.value = event_id.options[-1]

    def toggle_channel(evt):
        btn = evt.obj
        idx = list(channel_toggles).index(btn)
        ch_idx = idx + 1
        if ch_idx in channel_state["active"]:
            channel_state["active"].discard(ch_idx)
        else:
            channel_state["active"].add(ch_idx)
        plot.object = build_figure()

    mid_file.param.watch(on_mid_file, "value")
    event_id.param.watch(on_event, "value")
    detectors.param.watch(on_detectors, "value")
    channels_toggle_all.param.watch(lambda e: on_channels_toggle_all(e.new), "value")

    first_btn.on_click(nav_first)
    prev_btn.on_click(nav_prev)
    next_btn.on_click(nav_next)
    last_btn.on_click(nav_last)

    for b in channel_toggles:
        b.on_click(toggle_channel)

    sidebar = pn.Column(
        mid_file, event_id,
        pn.Row(first_btn, prev_btn, next_btn, last_btn),
        detectors, channels_toggle_all, channel_toggles, meta,
        pn.Row(spinner, info),
        width=420,
    )

    template = pn.template.MaterialTemplate(
        title="Nexus DM Dashboard",
        header=[pn.Row(cite, styles={"justify-content": "flex-end"})],
        sidebar=sidebar,
        main=[plot],
        sidebar_width=420,
    )
    template.servable()


main()
