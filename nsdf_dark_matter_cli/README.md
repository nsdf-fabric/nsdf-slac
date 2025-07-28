# NSDF Dark Matter CLI

The `nsdf_dark_matter` CLI offers a pool of operations to access and download the R76 dark matter dataset. The CLI serves as a top level component to access data in a workflow which can
then be analyzed with the [NSDF Dark Matter Library](https://nsdf-fabric.github.io/nsdf-slac/library/). Check the [CLI guide](https://nsdf-fabric.github.io/nsdf-slac/cli/) for a step by step walkthrough.

## NSDF CLI Usage Example

### Listing remote files

```bash
nsdf-cli ls
```

### Downloading a dataset

```bash
nsdf-cli download 07180827_0000_F0001
```
