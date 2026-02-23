package clickhouse

import (
	"context"
	"fmt"
	"math/rand"
	"net"
	"os"
	"time"

	"github.com/ClickHouse/clickhouse-go/v2"
	"github.com/ClickHouse/clickhouse-go/v2/lib/driver"
	"github.com/aws/aws-sdk-go-v2/service/s3/types"
	"github.com/nsdf-services/catalog/nexusdm/pkg/aws"
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

// initialize a new clickhouse db connection
func NewDB() *DB {
	conn, err := connect()
	if err != nil {
		panic(err)
	}
	return &DB{
		conn: conn,
	}
}

// return the number of rows from the catalog table
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

// inserts an s3 record into the catalog table
func (db DB) InsertBatch(objects []types.Object) error {
	batch, err := db.conn.PrepareBatch(context.Background(), "INSERT INTO nsdf.catalog")
	if err != nil {
		return err
	}
	defer batch.Close()

	for _, obj := range objects {
		note := "Red"
		if rand.Intn(2) == 1 {
			note = "Blue"
		}
		err := batch.Append(
			aws.CATALOG,
			aws.BUCKET,
			*obj.Key,
			*obj.Size,
			*obj.LastModified,
			*obj.ETag,
			time.Now(),
			note,
		)
		if err != nil {
			return err
		}
	}

	return batch.Send()
}

// create the connection to the clickhouse db
func connect() (driver.Conn, error) {
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

	if err := conn.Ping(context.Background()); err != nil {
		if exception, ok := err.(*clickhouse.Exception); ok {
			fmt.Printf("Exception [%d] %s \n%s\n", exception.Code, exception.Message, exception.StackTrace)
		}
		return nil, err
	}
	return conn, nil
}
