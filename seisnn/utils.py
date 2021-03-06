"""
Utilities
"""

import functools
import multiprocessing as mp
import os

import numpy as np
import tqdm
import yaml


def get_config():
    """
    Returns path dict in config.yaml.

    :rtype: dict
    :return: Dictionary contains predefined workspace paths.
    """
    config_file = os.path.abspath(
        os.path.join(os.path.expanduser("~"), 'config.yaml'))
    with open(config_file, 'r') as file:
        config = yaml.full_load(file)
    return config


def make_dirs(path):
    """
    Create dir if path does not exist.

    :param str path: Directory path.
    """
    if not os.path.isdir(path):
        os.makedirs(path, mode=0o777)


def batch(iterable, size=1):
    """
    Yields a batch from a list.

    :param iterable: Data list.
    :param int size: Batch size.
    """
    iter_len = len(iterable)
    for ndx in range(0, iter_len, size):
        yield iterable[ndx:min(ndx + size, iter_len)]


def batch_operation(data_list, func, **kwargs):
    """
    Unpacks and repacks a batch.

    :param data_list: List of data.
    :param func: Targeted function.
    :param kwargs: Fixed function parameter.

    :return: List of results.
    """
    return [func(data, **kwargs) for data in data_list]


def _parallel_process(file_list, par, batch_size=None):
    """
    Parallelize a partial function and return results in a list.

    :param list file_list: Process list for partial function.
    :param par: Partial function.
    :rtype: list

    :return: List of results.
    """
    cpu_count = mp.cpu_count()
    print(f'Found {cpu_count} cpu threads:')
    pool = mp.Pool(processes=cpu_count, maxtasksperchild=1)

    if batch_size is None:
        batch_size = int(np.ceil(len(file_list) / cpu_count))
    total = int(np.ceil(len(file_list) / batch_size))
    map_func = pool.imap_unordered(par, batch(file_list, batch_size))

    result = [output for output in tqdm.tqdm(map_func, total=total)]

    pool.close()
    pool.join()
    return result


def parallel(data_list, func, batch_size=None, **kwargs):
    """
    Parallels a function.

    :param data_list: List of data.
    :param func: Paralleled function.
    :param kwargs: Fixed function parameters.

    :return: List of results.
    """
    par = functools.partial(batch_operation, func=func, **kwargs)

    result_list = _parallel_process(data_list, par, batch_size)
    return result_list


def _parallel_iter(par, iterator):
    """
    Parallelize a partial function and return results in a list.

    :param par: Partial function.
    :param iterator: Iterable object.
    :rtype: list
    :return: List of results.
    """
    pool = mp.Pool(processes=mp.cpu_count(), maxtasksperchild=1)
    output = []
    for thread_output in tqdm.tqdm(pool.imap_unordered(par, iterator)):
        if thread_output:
            output.extend(thread_output)

    pool.close()
    pool.join()
    return output


def get_dir_list(file_dir, suffix=""):
    """
    Returns directory list from the given path.

    :param str file_dir: Target directory.
    :param str suffix: (Optional.) File extension.
    :rtype: list
    :return: List of file name.
    """
    file_list = []
    for file_name in os.listdir(file_dir):
        f = os.path.join(file_dir, file_name)
        if file_name.endswith(suffix):
            file_list.append(f)

    file_list = sorted(file_list)

    return file_list


def unet_padding_size(trace, pool_size=2, layers=4):
    """
    Return left and right padding size for a given trace.

    :param np.array trace: Trace array.
    :param int pool_size: (Optional.) Unet pool size, default is 2.
    :param int layers: (Optional.) Unet stages, default is 4.
    :return: (left padding size, right padding size)
    """
    length = len(trace)
    output = length
    for _ in range(layers):
        output = int(np.ceil(output / pool_size))

    padding = output * (pool_size ** layers) - length
    lpad = 0
    rpad = padding

    return lpad, rpad


if __name__ == "__main__":
    pass
