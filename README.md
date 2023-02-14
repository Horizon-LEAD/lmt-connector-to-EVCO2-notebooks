# LMT-2-EVCO2

_lmt-connector-to-EVCO2-notebooks_

## Installation

The `requirements.txt` and `Pipenv` files are provided for the setup of an environment where the module can be installed. The package includes a `setup.py` file and it can be therefore installed with a `pip install .` when we are at the same working directory as the `setup.py` file. For testing purposes, one can also install the package in editable mode `pip install -e .`.

After the install is completed, an executable `lmt2evco2` will be available to the user.

Furthermore, a `Dockerfile` is provided so that the user can package the model.
To build the image the following command must be issued from the project's root directory:

```bash
docker build -t lmt-2-evco2:latest .
```

## Usage

The executable's help message provides information on the parameters that are needed.

```
$ lmt2evco2 -h
```


### Examples

In the following examples, it is assumed that the user's terminal is at the project's root directory. Also that all the necessary input files are located in the `sample-data/input` directory and that the `sample-data/output` directory exists.

The user can then execute the model by running the executable.

```bash
lmt2evco2 -vvv \
    sample-data/input/lmt.json \
    sample-data/input/factors.xlsx \
    sample-data/output
```

If the package installation has been omitted, the model can of course also be run with

```bash
python -m src.lmt2evco2.__main__ \
    sample-data/input/lmt.json \
    sample-data/input/factors.xlsx \
    sample-data/output
```

Finally, the model can be executed with `docker run`:

```bash
docker run --rm \
  -v $PWD/sample-data:/data \
  lmt-2-evco2:latest \
  /data/input/input.csv \
  /data/output/
```
