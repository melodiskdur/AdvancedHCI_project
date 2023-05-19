import os


# CONSTANTS.
_VALID_SUFFIXES = {'.jpg', '.png', '.json'}


def parse_directory(folder_path: str, suffix: str = "") -> set:
    '''
    Returns a set of file paths for all files with a given suffix within a folder.

    Notes
    -----
    Leaving 'suffix' empty returns all files in the folder.
    '''
    _verify_directory(folder_path)
    if suffix != "":
        _verify_suffix(suffix)
    return {os.path.join(folder_path, file_name) for file_name in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, file_name)) and suffix in file_name}


def order_parsed_files(file_paths: set, order_type: str = 'ascending') -> list:
    '''
    Returns a list of file paths ordered by 'order_type' ('ascending' by default).

    Notes
    -----
    Allowed values for 'order_type' are 'ascending' and 'descending'.
    '''
    _verify_order_type(order_type=order_type)
    order_by = {'ascending': False, 'descending': True}
    return sorted(list(file_paths), reverse=order_by[order_type])


def _verify_directory(folder_path: str):
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Directory '{folder_path}' was not found.")
    elif not os.path.isdir(folder_path):
        raise NotADirectoryError(f"'{folder_path}' is not a valid directory.")


def _verify_suffix(suffix: str):
    if suffix not in _VALID_SUFFIXES:
        raise ValueError(f"Suffix '{suffix}' is not valid. See DirectoryParser.py or more information.")


def _verify_order_type(order_type: str):
    if order_type not in {'ascending', 'descending'}:
        raise ValueError(f"'order_type': {order_type} is not allowed. Allowed values are 'ascending' or 'descending'.")
