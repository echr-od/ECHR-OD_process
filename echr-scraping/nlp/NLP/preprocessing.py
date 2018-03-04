from collections import defaultdict
import re
import logging
from unidecode import unidecode
import nltk
from nltk.corpus import wordnet
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import WordPunctTokenizer

log = logging.getLogger(__name__)


def TreebankToWordnetTag(treebank_tag):
    """
        Convert a Treebank taf to a Wordnet Tag

        Lemmatization using Wordnet needs a tag on the type of
        the word (verb, noun,...). Howver, the Treebank Part of Speech
        Tagging returns tags that are not compatible with Treebank.

        :param treebank_tag: The tag to convert
        :type treebank_tag: String
        :return: The corresponding tag if it exists
        :rtype: String or None
    """
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    elif treebank_tag.startswith('CD'):
        return wordnet.NOUN
    else:
        return None


def convertToWordnetTag(tokens):
    """
        Convert a list of tokens tagged by Treebank to Wordnet tags.

        :param tokens: List of tagged tokens
        :type tokens: List of pair (String, String)
        :return: List of tokens with a non-empty Wordnet tag
        :rtype: [(String, String)]

        .. seealso:: TreebankToWordnetTag()
    """
    res = [(i, TreebankToWordnetTag(j)) for i, j in tokens]
    return [(i, j) for i, j in res if j]


def filterTokensWords(tokens, accepted=None, rejected=None):
    """
        Filter a list of tokens depending on their tag.

        :param tokens: List of tagged tokens
        :type tokens: [(String, String)]
        :param accepted: List of tokens to keep. All if None.
        :type accepted: [String]
        :param rejected: List of tokens to reject. None if None.
        :type rejected: [String]

        :return: List of non-rejected tokens
        :rtype: [(String, String)]
    """
    if accepted is not None:
        tokens = [(i, j) for i, j in tokens if j in accepted]

    if rejected is not None:
        tokens = [(i, j) for i, j in tokens if j not in rejected]

    return tokens


def cleanTokens(tokens):
    """
        Remove the english stopwords from the text as well as the
        words with less than a certain amount of characters.

        :param tokens: List of tokens
        :type tokens: [String]
        :param min_length: Minimal number of characters for a token
        :type min_length: Int

        :return: List of cleaned tokens
        :rtype: [String]
    """
    stopset = set(nltk.corpus.stopwords.words('english'))
    punctuation = [',', "\"", ")", "(", "\\", "\\\"),", "."]
    clean = [token.lower() for token in tokens if token.lower() not in stopset and token.lower() not in punctuation]
    for i, t in enumerate(clean):
        for p in punctuation:
            clean[i] = clean[i].replace(p, '')
    clean = [unidecode(token) for token in clean]
    clean = [token for token in clean if len(token) > 2]
    return clean

def generateNGrams(tokens, n):
    """
        Generate the n-grams from 2 to n. The separator is '_'.

        :param tokens: List of tokens
        :type tokens: [String]
        :param n: Limit of n-grams to generate
        :type n: Int

        :return: Map of n-grams
        :rtype: {Int:[String]}
    """
    results = {}
    for i in range(1, n + 1):
        results[i] = []
        ngrams = nltk.ngrams(tokens, i)
        results[i].extend(['_'.join(words) for words in ngrams])
    return results


def countOccurrences(tokens):
    """
        Count the occurrences of each token.

        :param tokens: List of tokens
        :type tokens: [String]

        :return: Map of occurrences
        :rtype: {String:Int}
    """
    frequency = defaultdict(int)
    for token in tokens:
        frequency[token] += 1
    return frequency


def countOccurrenceForNGrams(allgrams):
    """
        Generate the occurrences map for all n-grams

        :param allgrams: Map of n-grams
        :type allgrams: {Int:[String]}

        :return: Map of n-grams occurrences
        :rtype: {Int:{String:Int}}
    """
    frequencies = {}
    for i, ngrams in allgrams.items():
        frequencies[i] = countOccurrences(ngrams)
    return frequencies


def correctTheFrequencies(frequencies):
    """
        Correct the frequencies to avoid multiple counting due to n-grams.

        :param frequencies: Map of n-grams occurrences
        :type frequencies: {Int:{String:Int}}

        :return: Map of n-grams occurrences
        :rtype: {Int:{String:Int}}
    """
    for i, ngrams in frequencies.items():
        if i + 1 not in frequencies:
            break
        for gram in ngrams:
            for nextgram in frequencies[i + 1]:
                if '_' + gram in nextgram:
                    frequencies[i][gram] -= 1
                if '_' + gram + '_' in nextgram:
                    frequencies[i][gram] -= 1
                if gram + '_' in nextgram:
                    frequencies[i][gram] -= 1
    return frequencies


def filterByFrequency(frequencies, minlimits):
    """
        Remove the n-grams with a number of occurrences lower than 
        a certain amount

        :param frequencies: Map of n-grams occurrences
        :type frequencies: {Int:{String:Int}}
        :param minlimits: Minimal number of occurrences
        :type minlimits: Int

        :return: Map of n-grams occurrences
        :rtype: {Int:{String:Int}}
    """
    for i, ngrams in frequencies.items():
        frequencies[i] = {grams: f for grams,
                          f in ngrams.items() if f > minlimits[i] - 1}
    return frequencies


def concatenateToken(tokens):
    """
        Concatenate the n-grams into a single string taking
        into account the number of occurrences.
        It is needed because the models works on String only.

        :param tokens: Map of n-grams occurrences
        :type tokens: {Int:{String:Int}}

        :return: Concateneted tokens
        :rtype: String
    """
    res = []
    for i, ngrams in tokens.items():
        for token, f in ngrams.items():
            res += [token] * f
    return res


def prepareText(text, lemmatization=True):
    """
        Prepare a string for the learning model or for a query.

        :param text: Text to prepare
        :type text: String

        :return: Prepared text
        :rtype: String
    """
    tokens = WordPunctTokenizer().tokenize(text)
    tokens = cleanTokens(tokens)
    tokens = nltk.pos_tag(tokens)
    tokens = convertToWordnetTag(tokens)
    if lemmatization:
        lemmatizer = WordNetLemmatizer()
        tokens = [(lemmatizer.lemmatize(i, j), j) for i, j in tokens]
    
    return tokens

def frequencies(tokens, n=3, minlimits=None):
    return generateNGrams(tokens, n)

p = re.compile('(\d+)(\D+)')

def rectify_missing_space(token):
    r = p.search(token)
    if r is not None:
        l = list(r.groups())
        if l[-1].startswith(' '):
            return None
        return l
    return None
