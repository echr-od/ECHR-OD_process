# European Court of Human Rights OpenData construction process

This repository contains the scripts to build the database and datasets from the European Court of Human Rights OpenData (ECHR-OD) project.
The purposes of such repository are many:

1. **Reproducibility:** everyone can rebuild the entire database from scratch,
2. **Extensibility:** any new version of the database **must** be created from a updated version of those scripts.
3. **Revision:** all cases are automatically processed. There are many corner cases and such repository allow anyone to check the intermediate files to understand if the results are correct or not and locate the root cause of parsing errors.

<p align="center">
[DOWNLOAD DATA](https://echr-opendata.eu/download)
</p>

## General information

- Official website: [ECHR-OD project](https://echr-opendata.eu)
- Original paper: [paper](https://arxiv.org/abs/1810.03115), [code](https://github.com/aquemy/ECHR-OD_predictions), [supplementary material](https://github.com/aquemy/ECHR-OD_project_supplementary_material)
- Creation process: https://github.com/echr-od/ECHR-OD_process
- Website sources: https://github.com/echr-od/ECHR-OD_website

If you are using the project, please consider citing:
```
@article{Quemy2019_ECHROD,
  title={European Court of Human Right Open Data project},
  author={Alexandre Quemy},
  journal={CoRR},
  year={2019},
  volume={abs/1810.03115}
}
```

## Building process

The building chain starts from scratch and consists in the following steps:

1. ```get_cases_info.py```: Retrieve the list and basic information about cases from HUDOC
2. ```filter_cases.py```: Remove inconsistant, ambiguous or difficult-to-process cases
3. ```preprocess_documents.py```: Analyse the raw judgments to construct a JSON nested structures representing the paragraphs
4. ```process_documents.py```: Normalize the documents and generate a Bag-of-Words and TFID representation
5. ```generate_datasets.py```: Combine all the information to generate several datasets

# Installation & Usage


## NLTK packages

In order to parse and normalize the documents, the following packages from ```nltk``` have to be installed: ```stopwords```,  ```averaged_perceptron_tagger``` and ```wordnet```. To install them, start ```bin/download-nltk```:
```
python bin/download-nltk

```

## Webdrivers

In order to automatically retrieve the number of documents available on HUDOC, Selenium is installed as a dependency. For Selenium to work, a webdriver is mandatory and must be manually installed. See [Selenium documentation](https://selenium-python.readthedocs.io/installation.html#drivers) for help.


# Contributing

# Versions

- version 2.0.0: [Changelogs](https://github.com/echr-od/ECHR-OD_process/blob/master/changelog/2.0.0.md)
- version 1.0.2: [Changelogs](https://github.com/echr-od/ECHR-OD_process/blob/master/changelog/1.0.2.md)
- version 1.0.1: [Changelogs](https://github.com/echr-od/ECHR-OD_process/blob/master/changelog/1.0.1.md)

# Contributors

- Alexandre Quemy <aquemy@pl.ibm.com>
