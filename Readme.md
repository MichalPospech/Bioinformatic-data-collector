# Bioinformatic data collector
This tool is used for generation and execution of SPARQL queries for usage in bioinformatics. Currently only UniProt endpoint is supported.

## Installation
Install dependencies 
```
 pip -r requirements.txt
```
and clone the repository.

## Usage

```
Usage: data_collector.py [OPTIONS] CONFIG_PATH

  Generate query based on config saved in config_path

Options:
  -q, --print-query  Toggle to show generated query
  --out-path PATH    Path where to save result of the query, must have either
                     csv or xlsx extension
  --help             Show this message and exit.
```

## Config file format

Config file is in JSON format with two fields, `dataSelector` for column selection and `dataFilter` for filtering.

`dataSelector` contains `columns` list which lists selected columns. Currently available values are `Protein, ProteinId, Name, Sequence, Reaction`.

`dataFilter` describes how will the data be filtered. The `pfams` list contains PFAMs that will be included (has to have at least one of them), similarly with `supfams`. `reviewed` sets whether to select reviews or unreviewed records. And `taxa` list contains UniProt IDs of taxas and only proteins that belong to an organism that belongs into at least on of the listed taxa. All fields are optional. 

See `sample_config.json` for example.