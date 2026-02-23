package main

import (
	"context"
	"fmt"
	"math/rand"
	"net"
	"os"
	"strconv"
	"time"

	"github.com/ClickHouse/clickhouse-go/v2"
	"github.com/ClickHouse/clickhouse-go/v2/lib/driver"
	"github.com/joho/godotenv"
)

type DB struct {
	conn driver.Conn
}

type CatalogRecord struct {
	Catalog      string    `json:"catalog"`
	Bucket       string    `json:"bucket"`
	Name         string    `json:"name"`
	Size         uint64    `json:"size"`
	LastModified string    `json:"last_modified"`
	Etag         string    `json:"etag"`
	CreatedAt    time.Time `json:"inserted_at"`
	Ext          string    `json:"ext"`
}

func NewRandomCatalogRecord() CatalogRecord {
	var catalogs = [4]string{"aws-open-data", "ranch", "arecibo", "scicloud"}
	var names = [6]string{"f1.png", "f2.csv", "f3.gz", "f4.tar", "f5.jpeg", "07180808_1558_F0001.idx"}
	var bucket = [3]string{"PHY20003", "CTS20009", "scientistcloud"}
	var size = [6]uint64{1_000_000, 3_424_424, 1000, 100, 500}
	var etag = [2]string{"t1", "t2"}

	return CatalogRecord{
		Catalog:      catalogs[rand.Intn(len(catalogs))],
		Bucket:       bucket[rand.Intn(len(bucket))],
		Name:         names[rand.Intn(len(names))],
		Size:         size[rand.Intn(len(size))],
		Etag:         etag[rand.Intn(len(etag))],
		CreatedAt:    time.Now(),
		LastModified: time.Now().String(),
	}
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

func (db DB) TotalRows() (uint64, error) {
	ctx := context.Background()
	var count uint64

	rows, err := db.conn.Query(ctx, "SELECT count(*) FROM nsdf.catalog")
	if err != nil {
		return count, err
	}
	defer rows.Close()

	for rows.Next() {
		if err := rows.Scan(&count); err != nil {
			return count, err
		}
	}

	if err := rows.Err(); err != nil {
		return count, err
	}
	return count, nil
}

func (db DB) InsertBatch(n int) error {
	batch, err := db.conn.PrepareBatch(context.Background(), "INSERT INTO nsdf.catalog")
	if err != nil {
		return err
	}
	defer batch.Close()

	for range n {
		record := NewRandomCatalogRecord()
		note := "Nothing"
		if rand.Intn(2) == 1 {
			note = "Chosen"
		}
		err := batch.Append(
			record.Catalog,
			record.Bucket,
			record.Name,
			record.Size,
			record.LastModified,
			record.Etag,
			record.CreatedAt,
			note,
		)
		if err != nil {
			return err
		}
	}

	return batch.Send()
}

func main() {
	db := NewDB()

	// insert synthetic data into db
	if len(os.Args) == 2 {
		n, err := strconv.Atoi(os.Args[1])
		if err != nil {
			panic(err)
		}

		err = db.InsertBatch(n)
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

func connect() (driver.Conn, error) {
	if _, err := os.Stat(".env"); err == nil {
		err := godotenv.Load()
		if err != nil {
			return nil, err
		}
	}

	ctx := context.Background()
	conn, err := clickhouse.Open(&clickhouse.Options{
		Addr: []string{net.JoinHostPort(os.Getenv("CLICKHOUSE_HOST"), os.Getenv("CLICKHOUSE_PORT"))},
		Auth: clickhouse.Auth{
			Database: os.Getenv("CLICKHOUSE_DB"),
			Username: os.Getenv("CLICKHOUSE_USER"),
			Password: os.Getenv("CLICKHOUSE_PASSWORD"),
		},
		Debugf: func(format string, v ...any) {
			fmt.Printf(format, v)
		},
	})

	if err != nil {
		return nil, err
	}

	if err := conn.Ping(ctx); err != nil {
		if exception, ok := err.(*clickhouse.Exception); ok {
			fmt.Printf("Exception [%d] %s \n%s\n", exception.Code, exception.Message, exception.StackTrace)
		}
		return nil, err
	}
	return conn, nil
}
