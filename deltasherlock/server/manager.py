"""
Contains methods for maintaining the fingerprint, changeset, and dictionary
databases.
"""
import os
import time
from deltasherlock.common import fingerprinting as fp
from deltasherlock.common import dictionaries as dc
from gensim.models.word2vec import Word2Vec


def generate_fingerprints_parallel(changesets: list, method: fp.FingerprintingMethod, save_path: str, use_existing_dict: bool = False) -> list:
    """
    Exactly like generate_fingerprints(), but parallelizes dictionary and
    fingerprint generation via RQ. All jobs submitted to the "manager" queue.
    Method will still block until all Fingerprints are generated
    """
    from rq import Queue
    from redis import Redis
    redis_conn = Redis()
    q = Queue('manager', connection=redis_conn, default_timeout=82800)

    save_path = os.path.abspath(save_path)
    fingerprints = []
    filetree_dict = None
    filetree_dict_job = None
    neighbor_dict = None
    neighbor_dict_job = None

    # Create req'd w2v dictionaries (or load from file)
    if method.requires_filetree_dict():
        if use_existing_dict and os.path.exists(save_path + "/filetree.dsdc"):
            filetree_dict = Word2Vec.load(save_path + "/filetree.dsdc")
        else:
            all_filetree_sentences = []
            for changeset in changesets:
                all_filetree_sentences += changeset.get_filetree_sentences()
            # Submit Job to RQ
            filetree_dict_job = q.enqueue(
                dc.create_dictionary, all_filetree_sentences)

    if method.requires_neighbor_dict():
        if use_existing_dict and os.path.exists(save_path + "/neighbor.dsdc"):
            neighbor_dict = Word2Vec.load(save_path + "/neighbor.dsdc")
        else:
            all_neighbor_sentences = []
            for changeset in changesets:
                all_neighbor_sentences += changeset.get_neighbor_sentences()
            # Submit Job to RQ
            neighbor_dict_job = q.enqueue(
                dc.create_dictionary, all_neighbor_sentences)

    if method.requires_filetree_dict() and filetree_dict is None:
        while filetree_dict_job.result is None:
            # Block until completion
            time.sleep(0.2)
        filetree_dict = filetree_dict_job.result

    if method.requires_neighbor_dict() and neighbor_dict is None:
        while neighbor_dict_job.result is None:
            # Block until completion
            time.sleep(0.2)
        neighbor_dict = neighbor_dict_job.result

    # Now generate fingerprints (using RQ)
    fingerprint_gen_jobs = []
    for changeset in changesets:
        job = q.enqueue(fp.changeset_to_fingerprint,
                        changeset=changeset,
                        method=method,
                        filetree_dictionary=filetree_dict,
                        neighbor_dictionary=neighbor_dict)
        fingerprint_gen_jobs.append(job)

    # Save the dictionaries to the specified location
    if filetree_dict is not None:
        filetree_dict.save(save_path + "/filetree.dsdc")
    if neighbor_dict is not None:
        neighbor_dict.save(save_path + "/neighbor.dsdc")

    # Now block until we collect all the new fingerprints back from RQ
    while len(fingerprints) < len(fingerprint_gen_jobs):
        for job in fingerprint_gen_jobs:
            if job.result is not None:
                fingerprints.append(job.result)
        time.sleep(0.2)

    return fingerprints


def generate_fingerprints(changesets: list, method: fp.FingerprintingMethod, save_path: str, use_existing_dict: bool = False) -> list:
    """
    Runs the entire fingerprint generation process, including saving
    dictionaries. Optionally parallelizes via RQ

    :param changesets: a list of Changeset objects to be converted. Ensure each
    changeset has a db_id attribute if you'd like the resulting Fingerprints to
    be linked to their origins.
    :param method: a FingerprintingMethod object
    :param save_path: the full path to the directory where the dictionaries
    should be saved
    :param use_existing_dict: if True and a dictionary file already exists in the
    save_path, use that instead of generating a fresh one
    """
    save_path = os.path.abspath(save_path)
    fingerprints = []
    filetree_dict = None
    neighbor_dict = None

    if method is None or method == fp.FingerprintingMethod.undefined:
        raise ValueError("Invalid fingerprinting method")

    # Create req'd w2v dictionaries (or load from file)
    if method.requires_filetree_dict():
        if use_existing_dict and os.path.exists(save_path + "/filetree.dsdc"):
            filetree_dict = Word2Vec.load(save_path + "/filetree.dsdc")
        else:
            all_filetree_sentences = []
            for changeset in changesets:
                all_filetree_sentences += changeset.get_filetree_sentences()
            filetree_dict = dc.create_dictionary(all_filetree_sentences)

    if method.requires_neighbor_dict():
        if use_existing_dict and os.path.exists(save_path + "/neighbor.dsdc"):
            neighbor_dict = Word2Vec.load(save_path + "/neighbor.dsdc")
        else:
            all_neighbor_sentences = []
            for changeset in changesets:
                all_neighbor_sentences += changeset.get_neighbor_sentences()
            neighbor_dict = dc.create_dictionary(all_neighbor_sentences)

    # Now generate fingerprints
    for changeset in changesets:
        fingerprint = fp.changeset_to_fingerprint(changeset=changeset,
                                                  method=method,
                                                  filetree_dictionary=filetree_dict,
                                                  neighbor_dictionary=neighbor_dict)
        fingerprint.cs_db_id = changeset.db_id
        fingerprints.append(fingerprint)

    # Save the dictionaries to the specified location
    if filetree_dict is not None:
        filetree_dict.save(save_path + "/filetree.dsdc")
    if neighbor_dict is not None:
        neighbor_dict.save(save_path + "/neighbor.dsdc")

    return fingerprints
