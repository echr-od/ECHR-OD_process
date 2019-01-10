# European Court of Human Rights OpenData construction process

This repository contains the scripts to build the database and datasets from the European Court of Human Rights OpenData (ECHR-OD) project.
The purposes of such repository are many:

1. **Reproducibility:** everyone can rebuild the entire database from scratch,
2. **Extensibility:** any new version of the database **must** be created from a updated version of those scripts.
3. **Revision:** all cases are automatically processed. There are many corner cases and such repository allow anyone to check the intermediate files to understand if the results are correct or not and locate the root cause of parsing errors.

The building chain starts from scratch and consists in the following steps:

1. ```get_cases_info.py```: Retrieve the list and basic information about cases from HUDOC
2. ```filter_cases.py```: Remove inconsistant, ambiguous or difficult-to-process cases
3. ```preprocess_documents.py```: Analyse the raw judgments to construct a JSON nested structures representing the paragraphs
4. ```process_documents.py```: Normalize the documents and generate a Bag-of-Words and TFID representation
5. ```generate_datasets.py```: Combine all the information to generate several datasets

# Installation & Usage

## Webdrivers

In order to automatically retrieve the number of documents available on HUDOC, Selenium is installed as a dependency. For Selenium to work, a webdriver is mandatory and must be manually installed. See [Selenium documentation](https://selenium-python.readthedocs.io/installation.html#drivers) for help.


# Contributing

# Versions


# Contributors

- Alexandre Quemy <alexandre.quemy@gmail.com>
