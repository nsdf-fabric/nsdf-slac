package main

import (
	"log"

	"github.com/joho/godotenv"
	"github.com/nsdf-services/catalog/nexusdm/pkg/aws"
	"github.com/nsdf-services/catalog/nexusdm/pkg/clickhouse"
)

func main() {

	if err := godotenv.Load(); err != nil {
		log.Println("No .env file found")
	}

	db := clickhouse.NewDB()
	c, err := aws.NewClient()
	if err != nil {
		panic(err)
	}

	objects, err := c.Objects()
	if err != nil {
		panic(err)
	}

	err = db.InsertBatch(objects)
	if err != nil {
		panic(err)
	}
}
