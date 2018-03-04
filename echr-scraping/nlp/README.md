# Natural Language Processing for SEO

## Installation

Note: The package requires Python 3

Locally deploy the package:
```
python setup.py develop
```

Install the necessary NLP corpuses:
```
python bin/download-nltk

```

### Update

```
git pull (--rebase) origin master
python setup.py develop
```

## Usage

In the root directory:
```
python nlp_process.py [options]
```

For help: ```python nlp_process.py --help```

### Options:

1. -i, --input TEXT [required]: path to the input file
2. -l, --limit TEXT [optional]: limit the process to the specified number of lines (for debug / fast tests)
3. -d, --disambiguation: keep the city with the largest population in case of ambiguity
4. -s, --step [normalize|ngrams|locations|all]: steps to perform (default is 'all')
5. -f, --force [optional]: does not check output file existence

### Examples:

Perform all the steps and output the results in several files in the current directory:
```
python nlp_process.py -i ./input_utf8.txt
```

Perform the step 'location' on the first 500 lines of 'input_utf8.txt' without any check on the output file already existing:
```
python nlp_process.py -i ./input_utf8.txt -s locations -l 500 -f
```

### Configuration

The configuration file is located in ```config.json```:

The section ```ngrams``` allow you to tweak the ngrams extraction step. The first number represents the number of token in the ngrams and the second the minimal number of occurrences to consider the ngram.

**Example:**    

```
{
    "ngrams": {
        "1": 5, 
        "2": 3, 
        "3": 2,
        "4": 2
    }
}
```

A 2-grams is reported only if it appears at least twice, a 1-gran m, etc.