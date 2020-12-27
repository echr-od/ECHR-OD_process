# European Court of Human Rights OpenData construction process

This repository contains the scripts to build the database and datasets from the 
European Court of Human Rights OpenData (ECHR-OD) project.
The purposes of such repository are many:

1.  **Reproducibility:** everyone can rebuild the entire database from scratch,
    
2.  **Extensibility:** any new version of the database **must** be created from a updated version of those scripts.

3.  **Revision:** all cases are automatically processed. There are many corner cases and such repository allow anyone 
to check the intermediate files to understand if the results are correct or not and locate the root cause of parsing errors.

<p align="center">
<a href="https://echr-opendata.eu/download">DOWNLOAD DATA</a>
</p>

![](https://img.shields.io/endpoint?url=https%3A%2F%2Fgist.githubusercontent.com%2Faquemy%2F0a01112a76f73945a9f27710cf9c7a25%2Fraw%2Fcoverage.json&logo=coveralls)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/8a607d6bc2324e0eabb11741e762fbbb)](https://app.codacy.com/gh/echr-od/ECHR-OD_process?utm_source=github.com&utm_medium=referral&utm_content=echr-od/ECHR-OD_process&utm_campaign=Badge_Grade)
![](https://img.shields.io/github/license/echr-od/ECHR-OD_process)

![](https://github.com/echr-od/ECHR-OD_process/workflows/Image%20Building/badge.svg?branch=develop)
![](https://img.shields.io/docker/image-size/aquemy1/echr_build/develop)

![](https://img.shields.io/endpoint?url=https%3A%2F%2Fechr-opendata.eu%2Fapi%2Fv1%2Fbuild%2Fstatus)

## General information

-   Official website: [ECHR-OD project](https://echr-opendata.eu)
    
-   Original paper: [paper](https://arxiv.org/abs/1810.03115), [code](https://github.com/aquemy/ECHR-OD_predictions), 
[supplementary material](https://github.com/aquemy/ECHR-OD_project_supplementary_material)

-   Creation process: https://github.com/echr-od/ECHR-OD_process

-   Explorer sources: https://github.com/echr-od/ECHR-OD_explorer

If you are using the project, please consider citing:
```bibtex
@article{ECHRDB,
  title        = {On Integrating and Classifying Legal Text Documents},
  author       = {Quemy, A. and Wrembel, R.},
  year         = 2020,
  journal      = {International Conference on Database and Expert Systems Applications (DEXA)}
}
```

## Versioning and deployment

There are two distinct type of versions:

1.  Semantic versioning (e.g. 2.0.1) that indicates the version of the process. It relates only to the code and 
the type of data available.
    1.  major revision indicates a change in the type of version available
    2.  minor and patches related concern bugfix and improvements
2.  Date of release (e.g. 2020-11-01), that indicates a when a build has been generated.

The database is meant to be updated every month with new cases. New releases are built upon an image created from the latest sources.
Therefore, the date of release is technically enough to identify the semantic versioning. 
However, semantic versioning helps the maintainers and contributors with the development.

## Installation & Usage

Recreating the database requires ```docker```.

To build the environment image:
```sh
docker build -f Dockerfile -t echr_build .
```
As long as dependencies are not changed, there is no need to rebuild the image.

Once the image is built, the container help can be displayed with:
```sh
docker run -ti --mount src=$(pwd),dst=/tmp/echr_process/,type=bind echr_build -h
```

In particular, to build the database:
```sh
docker run -ti --mount src=$(pwd),dst=/tmp/echr_process/,type=bind echr_build build
```

## Build, Steps & Workflow

The entrypoint of the Extract-transform-load (ETL) process is `build.py`.  
The different ETL steps can be found in the subfolder `echr/steps`.   

The main build script load a **workflow** made of **steps** and execute each of them.
Workflows are YAML files and can be found in the folder `workflows`.

The workflows provided with the project are:

-   **Local** (`local.yml`): full ETL build locally,
-   **Release** (`release.yml`): full ETL including deployment to the server,
-   **Database** (`database.yml`): build the database only (no NLP model, no datasets),
-   **Datasets** (`datasets.yml`): build the datasets only (does not generate the database),
-   **NLP Model** (`NLP_model.yml`): build only the NLP model,
-   **Runner** (`runner.yml`): execute a workflow on an external runner.

We have the following relations:
-   `Datasets = NLP Model + datasets generation step`
-   `Local = Database + Datasets`
-   `Release = Local + deployment step`

This separation have been made because generating the NLP model takes up 95% of the whole `Release` workflow time 
and a tremendous amount of RAM (>16 Go).

Workflows may define variables using uppercase name starting by `$` (e.g. `$MAX_DOCUMENTS`).
The variables are replaced during the build process using the following order of priority:
1.  Environment variable
2.  CLI parameter
3.  From the configuration file, under `build.env.`
4.  Global variable defined in `build.py`

## Configuration

The general configuration file is `config.yml` and contains three parts:

1.  **logging:** related to logging files
    
2.  **steps:** configuration for each step on top of the workflow
    
3.  **build:** specific build configuration, in particular the section `env` contains the variables available to the 
whole workflow

## Logs

There are two log files:
1.  The build log file: `build/<build>/logs/build.html` and `build/<build>/logs/build.txt`
2.  The process log file, mostly used for debug: `logs/build.log`

## Tests & Coverage

To run the tests:
```sh
docker run -ti --mount src=$(pwd),dst=/tmp/echr_process/,type=bind echr_build test
```

## Versions

-   version 2.0.0: [Changelogs](https://github.com/echr-od/ECHR-OD_process/blob/master/changelog/2.0.0.md)
-   version 1.0.2: [Changelogs](https://github.com/echr-od/ECHR-OD_process/blob/master/changelog/1.0.2.md)
-   version 1.0.1: [Changelogs](https://github.com/echr-od/ECHR-OD_process/blob/master/changelog/1.0.1.md)

## Contributors

-   Alexandre Quemy <mailto:alexandre.quemy@gmail.com>
