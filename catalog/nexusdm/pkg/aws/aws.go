package aws

import (
	"context"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/s3"
	"github.com/aws/aws-sdk-go-v2/service/s3/types"
)

const (
	CATALOG string = "Nexus-DM"
	BUCKET  string = "scientistcloud"
	PREFIX  string = "cdms/umn/slac/idx/"
)

type Client struct {
	s3Client *s3.Client
}

// Initializes a new s3 client
func NewClient() (Client, error) {
	var client Client
	cfg, err := config.LoadDefaultConfig(context.Background(),
		config.WithSharedConfigProfile("scientistcloud"),
		config.WithRegion("us-east-1"),
		config.WithBaseEndpoint("https://s3.us-east-1.wasabisys.com"))

	if err != nil {
		return client, err
	}

	s3Client := s3.NewFromConfig(cfg, func(o *s3.Options) {
		o.UsePathStyle = true
	})

	client = Client{
		s3Client: s3Client,
	}

	return client, nil
}

// Return a list of all the CDMS objects in the scientistcloud
func (c Client) Objects() ([]types.Object, error) {
	var files []types.Object
	var continuationToken *string

	for {
		resp, err := c.s3Client.ListObjectsV2(context.Background(), &s3.ListObjectsV2Input{
			Bucket:            aws.String(BUCKET),
			Prefix:            aws.String(PREFIX),
			ContinuationToken: continuationToken,
		})

		if err != nil {
			return nil, err
		}

		for _, obj := range resp.Contents {
			if obj.Key != nil {
				files = append(files, obj)
			}
		}

		if resp.IsTruncated == nil || !*resp.IsTruncated {
			break
		}

		continuationToken = resp.NextContinuationToken
	}

	return files, nil
}
