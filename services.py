import os
import glob
import pickle
import json


def listmerge(lstlst):
    all = []
    [all.extend(lst) for lst in lstlst]
    return all


def storage_picle_io(in_data, picle_file_pathname):
    """DATA: input/output Picle file."""
    if not os.path.exists(picle_file_pathname):
        with open(picle_file_pathname, 'wb') as f:
            pickle.dump(in_data, f)
        return in_data
    else:
        with open(picle_file_pathname, 'rb') as f:
            out_data = pickle.load(f)
        return out_data


def delete_pickle_files():
    try:
        for pathname in glob.glob(r'*.pickle'):
            if os.path.exists(pathname):
                os.remove(pathname)
    except OSError:
        pass


def print_results(results_str_name, results_list):
    json_results = json.dumps({results_str_name: dict(results_list)})
    print(json.dumps(json.loads(json_results), indent=4))



