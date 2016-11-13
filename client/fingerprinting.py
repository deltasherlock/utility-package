# DeltaSherlock. See README.md for usage. See LICENSE for MIT/X11 license info.
# pylint: disable=W0201,W1401,R0903
"""
DeltaSherlock client fingerprinting module. Contains methods for generating a
filesystem fingerprint based on a changeset
"""
from math import sqrt
from enum import Enum, unique
from gensim.models import Word2Vec
import numpy as np
from ..common.changesets import Changeset


@unique
class FingerprintingMethod(Enum):
    """
    An enumerated type containing representations of each fingerprinting method.
    Notice how adding the integer values of two or more "basic" methods results
    in the appropriate "combination" method. Also, all odd values incorporate a
    histogram fingerprint, while the evens do not.
    """
    undefined = 0
    histogram = 1
    filetree = 2
    histofiletree = 3
    neighbor = 4
    histoneighbor = 5
    filetreeneighbor = 6
    combined = 7


class Fingerprint(np.ndarray):
    """
    A wrapper around a numpy array designed to handle numerical vector
    representations of changesets.

    :attribute method: the FingerprintingMethod used to create this fingerprint
    :attribute labels: a list of labels contained within this fingerprint

    Adapted from https://docs.scipy.org/doc/numpy/user/basics.subclassing.html
    """
    def __new__(cls, input_array, method=FingerprintingMethod.undefined):
        # Input array is an already formed ndarray instance
        # We first cast to be our class type
        obj = np.asarray(input_array).view(cls)
        # add the new attribute to the created instance
        obj.method = method
        obj.labels = []
        # Finally, we must return the newly created object:
        return obj

    def __array_finalize__(self, obj):
        if obj is None:
            return
        self.method = getattr(obj, 'method', FingerprintingMethod.undefined)

    def __add__(self, other):
        if other is None:
            return self

        # First, concatenate the underlying numpy arrays together
        sum_fp = Fingerprint(np.concatenate([self, other]))

        if self.method is not other.method:
            # Then, try to combine the FingerprintingMethod types
            try:
                sum_fp.method = FingerprintingMethod(
                    self.method.value + other.method.value)
            except ValueError:
                """
                The numbers don't add up! Probably happened because we tried to
                add a basic type fingerprint with an incompatible combination
                type
                """
                raise ArithmeticError("Cannot add incompatible fingerprints")
        else:
            sum_fp.method = self.method

        # Then, add the labels together
        sum_fp.labels = self.labels + other.labels

        # All done
        return sum_fp

    def __radd__(self, other):
        return self.__add__(other)


def changeset_to_fingerprint(changeset: Changeset, method: FingerprintingMethod,
                             w2v_dictionary: Word2Vec=None) -> Fingerprint:
    """
    Primary method of this module. Creates a numerical fingerprint vector
    representation of a Changeset using the specified method. This should always
    be used instead of the __private fingerprint generation functions.

    :param changeset: a closed Changeset object
    :param method: one of the FingerprintingMethod enumerated types
    :param w2v_dictionary: a gensim Word2Vec object containing a numerical
    dictionary. This required if using anything other than the histogram method
    :returns: the resulting Fingerprint object
    """
    # First, a few sanity checks
    if changeset.open:
        raise ValueError("Cannot convert an open changeset to a fingerprint")
    if method is FingerprintingMethod.undefined:
        raise ValueError(
            "Cannot create a fingerprint with an undefined creation method")
    if method.value > 1 and w2v_dictionary is None:
        raise ValueError(
            "Cannot create a non-histogram fingerprint without a w2v dictionary")

    # Start by fetching the file basenames from the changeset
    basenames = changeset.get_basenames()
    result_fingerprint = None

    # Then generate a histogram fingerprint
    if method.value % 2 == 1:
        # All odd methods contain a histogram
        result_fingerprint += __histogram_fingerprint(basenames)

    # Then generate a filetree fingerprint
    if (method is FingerprintingMethod.filetree
            or method is FingerprintingMethod.histofiletree
            or method is FingerprintingMethod.combined):
        result_fingerprint += __filetree_fingerprint(basenames, w2v_dictionary)

    # Then the neighbor fingerprint
    if (method is FingerprintingMethod.neighbor
            or method is FingerprintingMethod.histoneighbor
            or method is FingerprintingMethod.combined):
        result_fingerprint += __neighbor_fingerprint(basenames, w2v_dictionary)

    # Then add the labels
    result_fingerprint.labels = changeset.labels

    # All done!
    return result_fingerprint


def __histogram_fingerprint(basenames: list, num_bins: int=200) -> Fingerprint:
    """
    Creates an ASCII histogram fingerprint of the characters from a list of
    basenames.

    :param basenames: the list of basenames
    :param numBins: The number of bins to use in the histogram
    :returns: a normalized NumPy histogram
    """
    ascii_sum_vector = []

    for name in basenames:
        name_cha = ''.join([i for i in name if i.isalpha()])
        name_asc = sum(ord(c) for c in name_cha)
        ascii_sum_vector.append(name_asc)    # list of ASCII sum

    # Normalized Hist
    ele_num = len(ascii_sum_vector)    # length of ASCII sum list
    ybin = [0]
    min_bin = 200
    max_bin = 2000
    bin_size = int((max_bin - min_bin) / (int(num_bins) - 1))
    ybin = ybin + list(range(min_bin, max_bin, bin_size))
    ybin.append(10000)
    if ele_num is 0:
        ele_num = 1
    raw_histogram = np.histogram(ascii_sum_vector, ybin)[0]
    normalized_histogram = raw_histogram * 1.0 / ele_num   # Normalized hist
    return Fingerprint(normalized_histogram, method=FingerprintingMethod.histogram)


def __w2v_fingerprint_array(basenames: list, w2v_dictionary: Word2Vec) -> np.ndarray:
    """
    Creates an array that could be used to create a Fingerprint using a provided
    word2vec dictionary from a list of basenames. This function should not be
    used directly; instead, use either of the the __filetree_fingerprint or
    __neighbor_fingerprint wrapper functions.

    :param basenames: the list of basenames
    :param w2v_dictionary: a gensim.models.Word2Vec object representing the
    pre-made dictionary
    :returns: a NumPy array that could be used to create a Fingerprint
    """
    fingerprint_arr = np.array([0] * 200)

    for basename in basenames:
        #Clean up the basenames, just in case
        basename = basename.rstrip('\",\n').strip('[').strip(' ').strip('\"')
        basename = basename.strip('\,').rstrip(',\"').strip('\t').strip(',')
        #Now look up each basename in the dictionary
        if basename in w2v_dictionary:
            fingerprint_arr = w2v_dictionary[basename] + fingerprint_arr

    # Normalization Math
    fin = fingerprint_arr * fingerprint_arr
    vector_size = sqrt(fin.sum())
    # Hack to make sure fingerprint doesn't get divided by 0
    if vector_size == 0:
        vector_size = 1
    fingerprint_arr = fingerprint_arr / vector_size

    return fingerprint_arr


def __filetree_fingerprint(basenames: list, w2v_dictionary: Word2Vec) -> Fingerprint:
    """
    A wrapper function that creates a Fingerprint using
    FingerprintingMethod.filetree. See __w2v_fingerprint_array for more details
    """
    return Fingerprint(__w2v_fingerprint_array(basenames, w2v_dictionary),
                       method=FingerprintingMethod.filetree)


def __neighbor_fingerprint(basenames: list, w2v_dictionary: Word2Vec) -> Fingerprint:
    """
    A wrapper function that creates a Fingerprint using
    FingerprintingMethod.neighbor. See __w2v_fingerprint_array for more details
    """
    return Fingerprint(__w2v_fingerprint_array(basenames, w2v_dictionary),
                       method=FingerprintingMethod.neighbor)
