import os, time, math, json, re
from collections import defaultdict
import panel as pn
import pandas as pd
import psycopg
from decimal import Decimal

pn.extension('ipywidgets')
pn.extension('tabulator')
pn.extension(sizing_mode='stretch_width')


class NSDFCatalogDashboard:
    def __init__(self):
        self.conn = psycopg.connect(
            host=os.environ["POSTGRES_HOST"],
            port=os.environ["POSTGRES_PORT"],
            dbname=os.environ["POSTGRES_DB"],
            user=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
        )

        self._ensure_tables_exist()

        def fetchall(sql, params=None):
            with self.conn.cursor() as cur:
                cur.execute(sql, params or ())
                return cur.fetchall()

        # lookup rows
        self.source_rows = fetchall(
            "SELECT source_config_id, source, description FROM nsdf.source_config ORDER BY source_config_id"
        )
        self.shield_rows = fetchall(
            "SELECT shield_config_id, description FROM nsdf.shield_config ORDER BY shield_config_id"
        )
        self.trigger_rows = fetchall(
            "SELECT trigger_config_id, description, configuration FROM nsdf.trigger_config ORDER BY trigger_config_id"
        )
        self.run_rows = fetchall(
            "SELECT run_number, run_summary, image_links FROM nsdf.run_context ORDER BY run_number"
        )

        # source name -> [source_config_id, ...]
        self.source_name_to_ids = defaultdict(list)
        for sid, source, _ in self.source_rows:
            self.source_name_to_ids[source].append(sid)

        # trigger combo label -> [trigger_config_id, ...]
        self.trigger_combo_map = defaultdict(list)
        for tid, _, cfg in self.trigger_rows:
            types = sorted(set(self._trigger_types(cfg)))
            combo = " + ".join(types) if types else "Unknown"
            self.trigger_combo_map[combo].append(tid)

        self.shield_combo_map = defaultdict(list)
        for sid, _, cfg in fetchall(
            "SELECT shield_config_id, description, configuration FROM nsdf.shield_config ORDER BY shield_config_id"
        ):
            label = self._shield_combo_label(cfg)
            if label:
                self.shield_combo_map[label].append(sid)

        self.source_inspect_map = {str(sid): sid for sid, _, _ in self.source_rows}
        self.shield_inspect_map = {str(sid): sid for sid, _ in self.shield_rows}
        self.trigger_inspect_map = {str(tid): tid for tid, _, _ in self.trigger_rows}
        self.run_inspect_map = {str(rn): rn for rn, _, _ in self.run_rows}

        # filter widgets (show labels, map to ids in refresh)
        self.source_filters = pn.widgets.CheckBoxGroup(
            name="Source",
            options=sorted(self.source_name_to_ids.keys()),
            value=sorted(self.source_name_to_ids.keys()),
        )
        self.shield_filters = pn.widgets.CheckBoxGroup(
            name="Shield Combination",
            options=sorted(self.shield_combo_map.keys()),
            value=sorted(self.shield_combo_map.keys()),
        )
        self.trigger_filters = pn.widgets.CheckBoxGroup(
            name="Trigger Combination",
            options=sorted(self.trigger_combo_map.keys()),
            value=sorted(self.trigger_combo_map.keys()),
        )

        self.source_filters.param.watch(lambda evt: self.refresh(), "value")
        self.shield_filters.param.watch(lambda evt: self.refresh(), "value")
        self.trigger_filters.param.watch(lambda evt: self.refresh(), "value")

        # inspect widgets
        self.source_inspect_dropdown = pn.widgets.Select(
            name="Source Config ID",
            options=self.source_inspect_map,
            value=next(iter(self.source_inspect_map.values()), None),
        )
        self.shield_inspect_dropdown = pn.widgets.Select(
            name="Shield Config ID",
            options=self.shield_inspect_map,
            value=next(iter(self.shield_inspect_map.values()), None),
        )
        self.trigger_inspect_dropdown = pn.widgets.Select(
            name="Trigger Config ID",
            options=self.trigger_inspect_map,
            value=next(iter(self.trigger_inspect_map.values()), None),
        )
        self.run_inspect_dropdown = pn.widgets.Select(
            name="Run Number",
            options=self.run_inspect_map,
            value=next(iter(self.run_inspect_map.values()), None),
        )

        self.source_inspect_dropdown.param.watch(lambda evt: self.show_source_config(), "value")
        self.shield_inspect_dropdown.param.watch(lambda evt: self.show_shield_config(), "value")
        self.trigger_inspect_dropdown.param.watch(lambda evt: self.show_trigger_config(), "value")
        self.run_inspect_dropdown.param.watch(lambda evt: self.show_run_context(), "value")

        self.source_config_display = pn.pane.Markdown("")
        self.shield_config_display = pn.pane.Markdown("")
        self.trigger_config_display = pn.pane.Markdown("")
        self.run_context_display = pn.pane.Markdown("")

        # query/results
        self.query = pn.widgets.input.TextAreaInput(height=160)
        self.status = pn.widgets.input.StaticText(value="Ready to run a query")
        self.run_button = pn.widgets.Button(name="Run", button_type="primary")
        self.run_button.on_click(lambda evt: self.runQuery())
        self.tabulator = pn.widgets.Tabulator(pagination="remote", page_size=10)
        self.series_download = pn.widgets.FileDownload(
            label="Download series file",
            filename="files.txt",
            callback=self._build_series_file,
            button_type="primary",
        )
        self.material = pn.template.MaterialTemplate(title="NSDF-Catalog")

        schema_path = os.path.join(os.path.dirname(__file__), "umn_schema.png")
        if os.path.exists(schema_path):
            self.schema_pane = pn.pane.PNG(
            schema_path,
            sizing_mode="stretch_width",
            max_width=784,)

            self.schema_centered = pn.Row(
                pn.layout.HSpacer(),
                self.schema_pane,
                pn.layout.HSpacer(),
                sizing_mode="stretch_width",)
        else:
            self.schema_pane = pn.pane.Markdown(
            "Schema image not found at catalog/umn_schema.png")

        self.material.main.append(
            pn.Column(
                pn.pane.Markdown("## NSDF Metadata Explorer"),

                pn.pane.Markdown("### 1. Metadata Schema"),
                self.schema_centered,
                pn.Spacer(height=20),

                pn.pane.Markdown("### 2. Filter Metadata"),
                pn.Row(
                    pn.Column(pn.pane.Markdown("**Filter by Source**"), self.source_filters),
                    pn.Column(pn.pane.Markdown("**Filter by Shield**"), self.shield_filters),
                    pn.Column(pn.pane.Markdown("**Filter by Trigger**"), self.trigger_filters),
                    ),

                pn.pane.Markdown("### 3. Filtered Metadata Results"),
                pn.Row(self.query, self.run_button),
                self.status,
                self.tabulator,
                self.series_download,

                pn.Spacer(height=30),

                pn.pane.Markdown("### 4. Inspect Config / Run Context"),
                pn.Row(
                    pn.Column(self.source_inspect_dropdown, self.source_config_display),
                    pn.Column(self.shield_inspect_dropdown, self.shield_config_display),
                    pn.Column(self.trigger_inspect_dropdown, self.trigger_config_display),
                    pn.Column(self.run_inspect_dropdown, self.run_context_display),
                ),
            )
        )

        self.show_source_config()
        self.show_shield_config()
        self.show_trigger_config()
        self.show_run_context()
        self.refresh()


    def _ensure_tables_exist(self):
        #Ensure that the required tables exist in the database, and if not, create them using the 01_init_postgres.sql script.
        required_tables = [
            "source_config",
            "shield_config",
            "trigger_config",
            "run_context",
            "metadata",
        ]

        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT COUNT(*) = %s
                    FROM information_schema.tables
                    WHERE table_schema = 'nsdf'
                      AND table_name = ANY(%s)
                    """,
                    (len(required_tables), required_tables),
                )
                schema_exists = cur.fetchone()[0]

                if not schema_exists:
                    migration_path = os.path.join(
                        os.path.dirname(__file__),
                        "postgres_catalog",
                        "migrations",
                        "01_init_postgres.sql",
                    )

                    with open(migration_path, encoding="utf-8") as migration_file:
                        migration_sql = migration_file.read()

                    cur.execute(migration_sql)

            self.conn.commit()

        except Exception:
            self.conn.rollback()
            raise

    def _trigger_types(self, cfg):
        """Extract trigger types from trigger config JSON"""
        try:
            data = cfg if isinstance(cfg, (dict, list)) else json.loads(cfg)
            if not isinstance(data, dict):
                return []
            detectors = data.get("detectors", [])
            return [
                d.get("type")
                for d in detectors
                if isinstance(d, dict) and d.get("type")
            ]
        except Exception:
            return []

    def _shield_combo_label(self, cfg):
        """Extract shield combo label from shield config JSON.
        - shielding_bool false -> No shielding
        - otherwise -> Type1 + Type2 + ...
        """
        try:
            data = cfg if isinstance(cfg, (dict, list)) else json.loads(cfg)
            if not isinstance(data, dict):
                return None

            if data.get("shielding_bool") is False:
                return "No shielding"

            structure = data.get("structure", [])
            types = [
                d.get("type")
                for d in structure
                if isinstance(d, dict) and d.get("type")
            ]
            if not types:
                return None

            return " + ".join(sorted(set(types)))
        except Exception:
            return None
        
    def _pretty_json(self, text):
        try:
            obj = text if isinstance(text, (dict, list)) else json.loads(text)
            return "```json\n" + json.dumps(obj, indent=2) + "\n```"
        except Exception:
            return f"```\n{text}\n```"

    def _validate_readonly_sql(self, sql):
        if not sql or not sql.strip():
            return False, "query is empty"

        cleaned = sql.strip()

        # Allow one optional trailing semicolon, but block multi-statement SQL.
        no_trailing_semicolon = re.sub(r";\s*$", "", cleaned)
        if ";" in no_trailing_semicolon:
            return False, "multiple statements are not allowed"

        # Only allow read-only entry points.
        if not re.match(r"^\s*(SELECT|WITH)\b", cleaned, flags=re.IGNORECASE):
            return False, "only SELECT/WITH read-only queries are allowed"

        # Block destructive/admin commands anywhere in the statement.
        blocked = re.search(
            r"\b(INSERT|UPDATE|DELETE|ALTER|DROP|TRUNCATE|CREATE|GRANT|REVOKE|MERGE|CALL|DO|COPY|VACUUM|ANALYZE|COMMENT|SET|RESET)\b",
            cleaned,
            flags=re.IGNORECASE,
        )
        if blocked:
            return False, f"blocked keyword detected: {blocked.group(1).upper()}"

        return True, ""


    def show_source_config(self):
        selected_id = self.source_inspect_dropdown.value
        if selected_id is None:
            self.source_config_display.object = "No source configs available"
            return

        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT source, description, configuration FROM nsdf.source_config WHERE source_config_id = %s",
                (selected_id,),
            )
            row = cur.fetchone()

        if row:
            source, description, configuration = row
            self.source_config_display.object = (
                f"**Source:** {source}\n\n"
                f"**Description:** {description}\n\n"
                f"{self._pretty_json(configuration)}"
            )

    def show_shield_config(self):
        selected_id = self.shield_inspect_dropdown.value
        if selected_id is None:
            self.shield_config_display.object = "No shield configs available"
            return

        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT description, configuration FROM nsdf.shield_config WHERE shield_config_id = %s",
                (selected_id,),
            )
            row = cur.fetchone()

        if row:
            description, configuration = row
            self.shield_config_display.object = (
                f"**Description:** {description}\n\n{self._pretty_json(configuration)}"
            )

    def show_trigger_config(self):
        selected_id = self.trigger_inspect_dropdown.value
        if selected_id is None:
            self.trigger_config_display.object = "No trigger configs available"
            return

        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT description, configuration FROM nsdf.trigger_config WHERE trigger_config_id = %s",
                (selected_id,),
            )
            row = cur.fetchone()

        if row:
            description, configuration = row
            self.trigger_config_display.object = (
                f"**Description:** {description}\n\n{self._pretty_json(configuration)}"
            )

    def show_run_context(self):
        selected_id = self.run_inspect_dropdown.value
        if selected_id is None:
            self.run_context_display.object = "No run context available"
            return

        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT run_summary, image_links FROM nsdf.run_context WHERE run_number = %s",
                (selected_id,),
            )
            row = cur.fetchone()

        if row:
            run_summary, image_links = row
            links = "\n".join(f"- {x}" for x in (image_links or [])) or "- None"
            self.run_context_display.object = (
                f"**Run summary:** {run_summary}\n\n"
                f"**Image links:**\n{links}"
            )



    def refresh(self):
        selected_source_labels = list(self.source_filters.value)
        selected_shield_labels = list(self.shield_filters.value)
        selected_trigger_labels = list(self.trigger_filters.value)

        selected_sources = sorted({
            sid
            for label in selected_source_labels
            for sid in self.source_name_to_ids.get(label, [])
        })
        selected_shields = sorted({
            sid
            for label in selected_shield_labels
            for sid in self.shield_combo_map.get(label, [])
        })
        selected_triggers = sorted({
            tid
            for label in selected_trigger_labels
            for tid in self.trigger_combo_map.get(label, [])
        })

        # If any section has nothing selected (or maps to no ids), return no rows
        if (
            not selected_source_labels
            or not selected_shield_labels
            or not selected_trigger_labels
            or not selected_sources
            or not selected_shields
            or not selected_triggers
        ):
            self.query.value = """
SELECT
    m.series,
    m.run_number,
    m.source_config_id,
    m.shield_config_id,
    m.trigger_config_id,
    m.duration_minutes,
    m.bias,
    m.notes,
    m.timestamp,
    m.trigger_rate,
    m.run_diary
FROM nsdf.metadata m
WHERE FALSE
ORDER BY m.timestamp DESC
"""
            self.runQuery([])
            return

        where_parts = []
        params = []

        where_parts.append("m.source_config_id = ANY(%s)")
        params.append(selected_sources)

        where_parts.append("m.shield_config_id = ANY(%s)")
        params.append(selected_shields)

        where_parts.append("m.trigger_config_id = ANY(%s)")
        params.append(selected_triggers)

        where_clause = " AND ".join(where_parts)

        self.query.value = f"""
SELECT
    m.series,
    m.run_number,
    m.source_config_id,
    m.shield_config_id,
    m.trigger_config_id,
    m.duration_minutes,
    m.bias,
    m.notes,
    m.timestamp,
    m.trigger_rate,
    m.run_diary
FROM nsdf.metadata m
WHERE {where_clause}
ORDER BY m.timestamp DESC
"""
        self.runQuery(params)

    def runQuery(self, params=None):
        """Execute query and display results"""
        sql = self.query.value or ""
        ok, reason = self._validate_readonly_sql(sql)
        if not ok:
            self.status.value = f"Blocked query: {reason}"
            return

        self.status.value = "Running query..."
        t1 = time.time()

        try:
            with self.conn.cursor() as cur:
                cur.execute(sql, params or [])
                records = cur.fetchall()
                cols = [d.name for d in cur.description]
        except Exception as e:
            # Clear failed transaction state so next valid query can run.
            self.conn.rollback()
            self.status.value = f"Query failed safely: {e.__class__.__name__}: {e}"
            return

        sec = time.time() - t1
        df = pd.DataFrame(records, columns=cols)
        df = df.applymap(lambda x: int(x) if isinstance(x, Decimal) else x)

        self.tabulator.value = df
        self.tabulator.hidden_columns = []

        self.status.value = f"Elapsed {int(sec)} seconds | Records: {len(records):,}"

    def _build_series_file(self):
        import tempfile

        df = self.tabulator.value
        if df is None or len(df) == 0 or "series" not in df.columns:
            return None

        series_list = sorted(set(df["series"].dropna().astype(str)))

        lines = []
        for series in series_list:
            for i in range(1, 11):
                lines.append(f"{series}_F{i:04d}")

        fd, path = tempfile.mkstemp(prefix="files_", suffix=".txt")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

        return path
    

# //////////////////////////////////////////////////////////////////////////////////////
if True:
    exp = NSDFCatalogDashboard()
    exp.material.servable()