# NSDF Dark Matter CLI

The `nsdf_dark_matter` CLI offers a pool of operations to access the R68 dark matter dataset. The CLI can be used as component in a workflow to download data which can
then be analyzed with the [NSDF Dark Matter Library](https://github.com/nsdf-fabric/nsdf-slac/tree/main/nsdf_dark_matter)

## CLI usage example

### Listing remote files

To identify which files are available for download, we can use `ls` as follows.

```bash
nsdf-cli ls --limit 10
```

Output

```console
$ nsdf-cli ls --limit 10
07180827_0000_F0001
07180903_0000_F0001
07180916_0000_F0001
07180925_0000_F0001
07180926_0000_F0001
07181005_0000_F0001
07181007_0000_F0001
07180827_0000_F0002
07180903_0000_F0002
07180916_0000_F0002
```

### Downloading a dataset locally

To download a dataset from remote, we can use `download` as follows

```bash
nsdf-cli download 07180827_0000_F0001
```

Output

```console
$ nsdf-cli download 07180827_0000_F0001
07180808_1558_F0001 processed files have been downloaded!
```

Datasets are downloaded into the `idx` directory and organized by `mid_id` into directories. After subsequent downloads
we can have the following.

```console
idx/
   |
   07180925_0000_F0001/
   |
   07181007_0000_F0001/
   |
   07180916_0000_F0002/
```

## Next steps

Check how to manipulate the dataset with the [NSDF Dark Matter Library](https://github.com/nsdf-fabric/nsdf-slac/tree/main/nsdf_dark_matter)
