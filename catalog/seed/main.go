package main

import (
    "context"
    "fmt"
    "os"
    "strconv"
    "time"
    "database/sql"

    "github.com/jackc/pgx/v5"
    "github.com/joho/godotenv"
)

type DB struct {
    conn *pgx.Conn
}

type SourceConfig struct {
    SourceConfigID int
    Source         string
    X              float64
    Y              float64
    Description    string
    Configuration  string // JSON string
}

type ShieldConfig struct {
    ShieldConfigID int
    Configuration  string // JSON string
    Description    string
}

type TriggerConfig struct {
    TriggerConfigID int
    Configuration   string // JSON string
    Description     string
}

type RunContext struct {
    RunNumber    int
    RunSummary   string
    ImageLinks   []string
}

type Metadata struct {
    Series          string
    RunNumber       int
    SourceConfigID  int
    ShieldConfigID  int
    TriggerConfigID int
    DurationMinutes int
    Bias            int
    Notes           string
    Timestamp       time.Time
    TriggerRate     sql.NullFloat64
    RunDiary        string

}


func NewDB() *DB {
    conn, err := connect()
    if err != nil {
        panic(err)
    }
    return &DB{
        conn: conn,
    }
}

func (db DB) TotalRows() (int64, error) {
    ctx := context.Background()
    var count int64

    err := db.conn.QueryRow(ctx, `SELECT COUNT(*) FROM nsdf.metadata`).Scan(&count)
    if err != nil {
        return count, err
    }
    return count, nil
}

//Creating synthetic data for testing

func sampleSourceConfigs() []SourceConfig {
    return []SourceConfig{
        {
            1,
            "PuBe",
            0.02,
            0.3,
            "PuBe source set west to the tower",
            `{"type": "PuBe", "activation": {"strength": 1.96e6, "strength_units": "nC/s", "date_ISO8601": "2013-04-13:00:00.000"}, "inside_cryostat": false,
                "isotopes": ["231Pu", "248Am"], "geometry": {"shape": "cylinder", "height_inch": 0.65, "diameter_inch": 0.2},
                "image_links": ["https://example.com/pube1.jpg", "https://example.com/pube2.jpg"]}`,
        },
        {
            2,
            "PuBe",
            0.02,
            0.3,
            "PuBe source set east to the tower",
            `{"type": "PuBe", "activation": {"strength": 1.96e6, "strength_units": "nC/s", "date_ISO8601": "2013-04-14:00:00.000"}, "inside_cryostat": true,
                "isotopes": ["231Pu", "248Am"], "geometry": {"shape": "cylinder", "height_inch": 0.65, "diameter_inch": 0.2},
                "image_links": ["https://example.com/pube3.jpg", "https://example.com/pube4.jpg"]}`,
        },
        {
            3,
            "Bg",
            0.02,
            0.3,
            "Background run with no source",
            `{"type": "Bg", "activation": {"strength": 0, "strength_units": "nC/s", "date_ISO8601": "2013-04-15:00:00.000"}, "inside_cryostat": false,
                "isotopes": [], "geometry": {"shape": "cylinder", "height_inch": 0.65, "diameter_inch": 0.2},
                "image_links": ["https://example.com/bg1.jpg", "https://example.com/bg2.jpg"]}`,
        },
    }
}

func sampleShieldConfigs() []ShieldConfig {
    return []ShieldConfig{
        {
            1,
            `{"shielding_bool": true,
                "structure": [{"type": "HDPE", "purpose": "neutron blocking", "description": "HDPE shield 1", "placement": "placement 1", "image_links": ["https://example.com/hdpe1.jpg", "https://example.com/hdpe2.jpg"]},
                               {"type": "Lead", "purpose": "gamma rays blocking", "description": "Lead Shield", "placement": "placement 2", "image_links": ["https://example.com/lead1.jpg", "https://example.com/lead2.jpg"]},
                               {"type": "Boron", "purpose": "neutron blocking", "description": "boron socks", "placement": "placement 3", "image_links": ["https://example.com/boron1.jpg", "https://example.com/boron2.jpg"]}]}`,
            "Using 3 shields",
        },
        {
            2,
            `{"shielding_bool": false}`,
            "No shielding",
        },
        {
            3,
            `{"shielding_bool": true,
                "structure": [{"type": "HDPE", "purpose": "neutron blocking", "description": "HDPE shield 1", "placement": "placement 1", "image_links": ["https://example.com/hdpe1.jpg", "https://example.com/hdpe2.jpg"]}]}`,
            "Using 1 shield",
        },
    }
}

func sampleTriggerConfigs() []TriggerConfig {
    return []TriggerConfig{
        {
            1,
            `{"detectors": [{"type": "NaI", "purpose": "gamma ray detection", "channel": "DCRCX (4)"},
                            {"type": "SiHV", "purpose": "phonon detection", "channel": "DCRCX (33)", "wiring_scheme": {}}]}`,
            "Using 2 triggers",
        },
        {
            2,
            `{"detectors": [{"type": "NaI", "purpose": "gamma ray detection", "channel": "DCRCX (4)"}]}`,
            "Using 1 trigger",
        },
    }
}


func sampleRunContexts() []RunContext {
    return []RunContext {
        {68, "Run 68 summary", []string{"https://example.com/run68_1.jpg", "https://example.com/run68_2.jpg"}},
        {76, "Run 76 summary", []string{"https://example.com/run76_1.jpg", "https://example.com/run76_2.jpg"}},
    }
}

func nullFloatNil() sql.NullFloat64 {
    return sql.NullFloat64{Valid: false}
}

func nullFloat(f float64) sql.NullFloat64 {
    return sql.NullFloat64{Float64: f, Valid: true}
}

func sampleMetadata() []Metadata {
    return []Metadata {
        {"07180530_2500", 68, 1, 1, 1, 60, -100, "Notes for exp 1", time.Now(), nullFloat(0.5), "Run diary 1"},
        {"07220909_1340", 76, 1, 1, 2, 70, -110, "Notes for exp 2", time.Now(), nullFloatNil(), "Run diary 2"},
        {"07220909_2243", 68, 1, 2, 1, 80, -120, "Notes for exp 3", time.Now(), nullFloatNil(), "Run diary 3"},
        {"07220913_1546", 76, 1, 2, 2, 90, -130, "Notes for exp 4", time.Now(), nullFloatNil(), "Run diary 4"},
        {"07180602_2139", 68, 1, 3, 1, 100, -140, "Notes for exp 5", time.Now(), nullFloat(0.3), "Run diary 5"},
        {"07180603_1702", 76, 1, 3, 2, 110, -150, "Notes for exp 6", time.Now(), nullFloatNil(), "Run diary 6"},
        {"07180604_0403", 68, 2, 1, 1, 120, -160, "Notes for exp 7", time.Now(), nullFloat(0.2), "Run diary 7"},
        {"07180630_0932", 76, 2, 1, 2, 130, -170, "Notes for exp 8", time.Now(), nullFloatNil(), "Run diary 8"},
        {"07180702_1742", 68, 2, 2, 1, 140, -180, "Notes for exp 9", time.Now(), nullFloatNil(), "Run diary 9"},
        {"07220826_2007", 76, 2, 2, 2, 150, -190, "Notes for exp 10", time.Now(), nullFloatNil(), "Run diary 10"},
        {"07220909_1256", 68, 2, 3, 1, 160, -200, "Notes for exp 11", time.Now(), nullFloat(0.4), "Run diary 11"},
        {"07220910_1517", 76, 2, 3, 2, 170, -210, "Notes for exp 12", time.Now(), nullFloatNil(), "Run diary 12"},
        {"07220917_1039", 68, 3, 1, 1, 180, -220, "Notes for exp 13", time.Now(), nullFloat(0.3), "Run diary 13"},
        {"07220712_1324", 76, 3, 1, 2, 190, -230, "Notes for exp 14", time.Now(), nullFloatNil(), "Run diary 14"},
        {"07220705_0646", 68, 3, 2, 1, 200, -240, "Notes for exp 15", time.Now(), nullFloat(0.2), "Run diary 15"},
        {"07220707_0639", 76, 3, 2, 2, 210, -250, "Notes for exp 16", time.Now(), nullFloatNil(), "Run diary 16"},
        {"07220709_0935", 68, 3, 3, 1, 220, -260, "Notes for exp 17", time.Now(), nullFloat(0.1), "Run diary 17"},
        {"07220830_1829", 76, 3, 3, 2, 230, -270, "Notes for exp 18", time.Now(), nullFloatNil(), "Run diary 18"},
    }
}

func (db *DB) SeedAll() error {
    ctx := context.Background()

    tx, err := db.conn.Begin(ctx)
    if err != nil {
        return err
    }
    defer tx.Rollback(ctx)

    //Insert sample data for each table
    for _, sc := range sampleSourceConfigs() {
        _, err := tx.Exec(ctx, "INSERT INTO nsdf.source_config (source_config_id, source, x, y, description, configuration) VALUES ($1, $2, $3, $4, $5, $6)",
            sc.SourceConfigID, sc.Source, sc.X, sc.Y, sc.Description, sc.Configuration)
        if err != nil {
            return err
        }
    }

    for _, shc := range sampleShieldConfigs() {
        _,err := tx.Exec(ctx, "INSERT INTO nsdf.shield_config (shield_config_id, configuration, description) VALUES ($1, $2, $3)",
            shc.ShieldConfigID, shc.Configuration, shc.Description)
        if err != nil {
            return err
        }
    }

    for _, tc := range sampleTriggerConfigs() {
        _, err := tx.Exec(ctx, "INSERT INTO nsdf.trigger_config (trigger_config_id, configuration, description) VALUES ($1, $2, $3)",
            tc.TriggerConfigID, tc.Configuration, tc.Description)
        if err != nil {
            return err
        }
    }

    for _, rc := range sampleRunContexts() {
        _, err := tx.Exec(ctx, "INSERT INTO nsdf.run_context (run_number, run_summary, image_links) VALUES ($1, $2, $3)",
            rc.RunNumber, rc.RunSummary, rc.ImageLinks)
        if err != nil {
            return err
        }
    }

    for _, md := range sampleMetadata() {
        _, err := tx.Exec(ctx, `INSERT INTO nsdf.metadata (series, run_number, source_config_id, shield_config_id, trigger_config_id, duration_minutes, bias, notes, timestamp, trigger_rate, run_diary) 
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)`,
            md.Series, md.RunNumber, md.SourceConfigID, md.ShieldConfigID, md.TriggerConfigID,
            md.DurationMinutes, md.Bias, md.Notes, md.Timestamp, md.TriggerRate, md.RunDiary)
        if err != nil {
            return err
        }
    }

    return tx.Commit(ctx)
}

func main() {
    db := NewDB()
    defer db.conn.Close(context.Background())

    // insert synthetic data into db
    if len(os.Args) == 2 {
        _, err := strconv.Atoi(os.Args[1])
        if err != nil {
            panic(err)
        }

        err = db.SeedAll()
        if err != nil {
            panic(err)
        }
    }

    i, err := db.TotalRows()
    if err != nil {
        panic(err)
    }

    fmt.Printf("total rows: %d\n", i)
}

func connect() (*pgx.Conn, error) {
    if _, err := os.Stat(".env"); err == nil {
        err := godotenv.Load()
        if err != nil {
            return nil, err
        }
    }

    ctx := context.Background()
    connStr := fmt.Sprintf(
        "postgres://%s:%s@%s:%s/%s",
        os.Getenv("POSTGRES_USER"),
        os.Getenv("POSTGRES_PASSWORD"),
        os.Getenv("POSTGRES_HOST"),
        os.Getenv("POSTGRES_PORT"),
        os.Getenv("POSTGRES_DB"),
    )

    conn, err := pgx.Connect(ctx, connStr)
    if err != nil {
        return nil, err
    }

    // Test connection
    err = conn.Ping(ctx)
    if err != nil {
        return nil, err
    }

    return conn, nil
}
