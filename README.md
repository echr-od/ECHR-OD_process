# European Court of Human Rights OpenData construction process

This repository contains the scripts to build the database and datasets from the European Court of Human Rights OpenData (ECHR-OD) project.
The purposes of such repository are many:

1. **Reproducibility:** everyone can rebuild the entire database from scratch,
2. **Extensibility:** any new version of the database **must** be created from a updated version of those scripts.
3. **Revision:** all cases are automatically processed. There are many corner cases and such repository allow anyone to check the intermediate files to understand if the results are correct or not and locate the root cause of parsing errors.

<p align="center">
<a href="https://echr-opendata.eu/download">DOWNLOAD DATA</a>
</p>

## General information

- Official website: [ECHR-OD project](https://echr-opendata.eu)
- Original paper: [paper](https://arxiv.org/abs/1810.03115), [code](https://github.com/aquemy/ECHR-OD_predictions), [supplementary material](https://github.com/aquemy/ECHR-OD_project_supplementary_material)
- Creation process: https://github.com/echr-od/ECHR-OD_process
- Website sources: https://github.com/echr-od/ECHR-OD_website

If you are using the project, please consider citing:
```
@article{ECHRDB,
  title        = {On Integrating and Classifying Legal Text Documents},
  author       = {Quemy, A. and Wrembel, R.},
  year         = 2020,
  journal      = {International Conference on Database and Expert Systems Applications (DEXA)}
}
```

## Installation & Usage

Recreating the database requires ```docker```.

To build the environment image:
```
docker build -f Dockerfile -t echr_build .
```
As long as dependencies are not changed, there is no need to rebuild the image.

Once the image is built, the container help can be displayed with:
```
docker run -ti --mount src=$(pwd),dst=/tmp/echr_process/,type=bind echr_build -h
```

In particular, to build the database:
```
docker run -ti --mount src=$(pwd),dst=/tmp/echr_process/,type=bind echr_build build
```

# Build, Steps & Workflow

The entrypoint of the Extract-transform-load (ETL) process is `build.py`.   
The different ETL steps can be found in the subfolder `echr/steps`.   

The main build script load a **workflow** made of **steps** and execute each of them.
Workflows are YAML files and can be found in the folder `workflows`.

The workflows provided with the project are:
- **Local** (`release.yml`): full ETL build locally,
- **Release** (`release.yml`): full ETL including deployment to the server.

Workflows may define variables using uppercase name starting by `$` (e.g. `$MAX_DOCUMENTS`).
The variables are replaced during the build process using the following order of priority:
1. Environment variable
2. CLI parameter
3. From the configuration file, under `build.env.`
4. Global variable defined in `build.py`

# Configuration

The general configuration file is `config.yml` and contains three parts:
1. **logging:** related to logging files
2. **steps:** configuration for each step on top of the workflow
3. **build:** specific build configuration, in particular the section `env` contains the variables available by the workflow

# Logs

There are two log files:
1. The build log file: `build/<build>/logs/build.html` and `build/<build>/logs/build.txt`
2. The process log file, mostly used for debug: `logs/build.log`

# Tests & Coverage

To run the tests:
```
docker run -ti --mount src=$(pwd),dst=/tmp/echr_process/,type=bind echr_build test
```

# Versions

- version 2.0.0: [Changelogs](https://github.com/echr-od/ECHR-OD_process/blob/master/changelog/2.0.0.md)
- version 1.0.2: [Changelogs](https://github.com/echr-od/ECHR-OD_process/blob/master/changelog/1.0.2.md)
- version 1.0.1: [Changelogs](https://github.com/echr-od/ECHR-OD_process/blob/master/changelog/1.0.1.md)

# Contributors

- Alexandre Quemy <alexandre.quemy@gmail.com>
