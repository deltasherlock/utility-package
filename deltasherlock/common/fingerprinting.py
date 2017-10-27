# DeltaSherlock. See README.md for usage. See LICENSE for MIT/X11 license info.
# pylint: disable=W0201,W1401,R0903
"""
DeltaSherlock fingerprinting module. Contains methods for generating a
filesystem fingerprint based on a changeset
"""
from math import sqrt
from enum import Enum, unique
from gensim.models import Word2Vec
import numpy as np
from deltasherlock.common.changesets import Changeset


@unique
class FingerprintingMethod(Enum):
    """
    An enumerated type containing representations of each fingerprinting method.
    Notice how adding the integer values of two or more "basic" methods results
    in the appropriate "combination" method. Also, all odd values incorporate a
    histogram fingerprint, while the evens do not. This numbering scheme should
    remain as backward compatible as possible, since these values are used in
    the server's database (see source for FingerprintWrapper)
    """
    undefined = 0
    histogram = 1
    filetree = 2
    histofiletree = 3
    neighbor = 4
    histoneighbor = 5
    filetreeneighbor = 6
    combined = 7

    def requires_filetree_dict(self):
        return (self.value == self.filetree.value or self.value == self.histofiletree.value or self.value == self.combined.value)

    def requires_neighbor_dict(self):
        return (self.value == self.neighbor.value or self.value == self.histoneighbor.value or self.value == self.combined.value)


class Fingerprint(np.ndarray):
    """
    A wrapper around a numpy array designed to handle numerical vector
    representations of changesets. The best way to instantiate a Fingerprint
    is by providing a raw numpy array and FingerprintingMethod as parameters
    (ie. fp = Fingerprint(arr, method=neighbor)), and then manually setting the
    remaining attributes

    :attribute method: the FingerprintingMethod used to create this fingerprint
    :attribute labels: a list of labels contained within this fingerprint
    :attribute predicted_quantity: the quantity of events (ie an application
    installation) that probably occurred during the recording interval.
    Determined by the original Changeset
    :attribute db_id: an optional identifier populated when a fingerprint is
    "unwrapped" from the database
    :attribute cs_db_id: an optional identifier populated when a fingerprint is
    "unwrapped" from the database. This points to the fingerprint's origin
    changeset

    Adapted from https://docs.scipy.org/doc/numpy/user/basics.subclassing.html
    """
    def __new__(cls, input_array, method=FingerprintingMethod.undefined):
        """
        Our "constructor." Required for subclassing of numpy array. See link in
        class docstring
        """
        # Input array is an already formed ndarray instance
        # We first cast to be our class type
        obj = np.asarray(input_array).view(cls)
        # add the new attribute to the created instance
        obj.method = method
        obj.labels = []
        obj.predicted_quantity = -1
        obj.db_id = None
        obj.cs_db_id = None
        # Finally, we must return the newly created object:
        return obj

    def __array_finalize__(self, obj):
        """
        Required for subclassing of ndarray. See link in class docstring
        """
        if obj is None:
            return
        # Redeclare all member attributes here, for subclassing purposes
        self.method = getattr(obj, 'method', FingerprintingMethod.undefined)
        self.labels = getattr(obj, 'labels', [])
        self.predicted_quantity = getattr(obj, 'predicted_quantity', -1)
        self.db_id = getattr(obj, 'db_id', None)
        self.cs_db_id = getattr(obj, 'cs_db_id', None)

    def __reduce__(self):
        """
        Reduction method, for pickling. We have to override this because ndarray's
        __reduce__ does not handle our custom attributes. Adapted from:
        http://stackoverflow.com/a/26599346
        """
        # Call parent __reduce__
        pickled_state = super().__reduce__()
        # Create our own tuple to pass to __setstate__
        new_state = pickled_state[
            2] + (self.method, self.labels, self.predicted_quantity, self.db_id, self.cs_db_id)
        # Return a tuple that replaces the parent's __setstate__ tuple with our
        # own
        return (pickled_state[0], pickled_state[1], new_state)

    def __setstate__(self, state):
        """
        Set-state method, for pickling. Wee have to override this because ndarray's
        __setstate__ does not handle our custom attributes. Adapted from:
        http://stackoverflow.com/a/26599346
        """
        # Recall our own member attributes from state
        self.method = state[-5]
        self.labels = state[-4]
        self.predicted_quantity = state[-3]
        self.db_id = state[-2]
        self.cs_db_id = state[-1]
        # Call the parent's __setstate__ with the other tuple elements.
        super().__setstate__(state[0:-5])

    def __add__(self, other):
        """
        Allows for "adding" (read: concatenating) of fingerprints
        """
        if other is None:
            return self

        # First, concatenate the underlying numpy arrays together
        sum_fp = Fingerprint(np.concatenate([self, other]))

        if self.method.value != other.method.value:
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

        # Then, adopt the original quantities
        sum_fp.predicted_quantity = self.predicted_quantity

        # All done
        return sum_fp

    def __radd__(self, other):
        """
        "Reverse-add" helper. Required in order to use the += operator
        """
        return self.__add__(other)


def changeset_to_fingerprint(changeset: Changeset, method: FingerprintingMethod,
                             filetree_dictionary: Word2Vec=None,
                             neighbor_dictionary: Word2Vec=None) -> Fingerprint:
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
    if method == FingerprintingMethod.undefined:
        raise ValueError(
            "Cannot create a fingerprint with an undefined creation method")

    # Start by fetching the file basenames from the changeset
    basenames = changeset.get_basenames()
    result_fingerprint = None

    # Then generate a histogram fingerprint
    if method.value % 2 == 1:
        # All odd methods contain a histogram
        result_fingerprint += __histogram_fingerprint(basenames)

    # Then generate a filetree fingerprint
    if method.requires_filetree_dict():
        if filetree_dictionary is None:
            raise ValueError("Missing filetree w2v dictionary")
        result_fingerprint += __filetree_fingerprint(
            basenames, filetree_dictionary)

    # Then the neighbor fingerprint
    if method.requires_neighbor_dict():
        if neighbor_dictionary is None:
            raise ValueError("Missing neighbor w2v dictionary")
        result_fingerprint += __neighbor_fingerprint(
            basenames, neighbor_dictionary)

    # Then add the labels
    result_fingerprint.labels = changeset.labels

    # Then use quantity prediction
    result_fingerprint.predicted_quantity = changeset.predicted_quantity

    # Then add the origin changeset's database ID
    try:
        result_fingerprint.cs_db_id = changeset.db_id
    except AttributeError:
        result_fingerprint.cs_db_id = None

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
    ybin = ybin + list(range(min_bin, max_bin - bin_size, bin_size))
    ybin.append(10000)
    if ele_num == 0:
        ele_num = 1
    raw_histogram = np.histogram(ascii_sum_vector, bins=ybin)[0]
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
        # Clean up the basenames, just in case
        basename = basename.rstrip('\",\n').strip('[').strip(' ').strip('\"')
        basename = basename.strip('\,').rstrip(',\"').strip('\t').strip(',')
        # Now look up each basename in the dictionary
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
