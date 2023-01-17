# prep1.py

import urllib.request as ur
import pandas as pd
import pathlib

best_urls = {
    '2020-jan-dec': r'https://datahub.duramat.org/dataset/72334fe1-fa52-45f8-a43c-836a35b9c526/resource/b7e35897-4d32-48fc-b53c-7b780537d87d/download/data_release__sep2022_period_2020_0112.csv'
    , '2021-jan-dec': r'https://datahub.duramat.org/dataset/72334fe1-fa52-45f8-a43c-836a35b9c526/resource/264212b8-800e-47b5-80ac-1dd2c644aa74/download/data_release__sep2022_period_2021_0112.csv'
    , '2022-jan-aug': r'https://datahub.duramat.org/dataset/72334fe1-fa52-45f8-a43c-836a35b9c526/resource/2fb7b6f4-a916-40e8-831c-dd2c445852d7/download/data_release__sep2022_period_2022_0108.csv'
    , '2019-jul-dec': r'https://datahub.duramat.org/dataset/72334fe1-fa52-45f8-a43c-836a35b9c526/resource/f32ba09d-f750-4746-82ec-5f930c18437a/download/data_release_sep2022_period_2019_0712.csv'
}


def prep_dirs() -> tuple[pathlib.Path, pathlib.Path, pathlib.Path]:
    """Set up working directories."""
    dtadir = pathlib.Path('data')
    if not dtadir.exists():
        raise Exception('data directory does exist: are you in the right working directory?')
    elif not dtadir.is_dir():
        raise Exception('"data" name in filesystem is not a directory: rename or move existing file, or move to correct working directory')
    elif not (dtadir / 'config').is_dir():
        raise Exception('data directory does not have a config subdirectory: are you in the right working directory?')
    cachedir = dtadir / 'cache'
    cachedir.mkdir(exist_ok=True)
    rawdir = dtadir / 'raw'
    rawdir.mkdir(exist_ok=True)
    return dtadir, cachedir, rawdir


def url_fname(best_url_key: str, rawdir: pathlib.Path) -> pathlib.Path:
    """Make local filename for storing BEST data."""
    return rawdir / f'{best_url_key}.csv'

# Define a function to safely read the data
# If download fails, user will have to identify and then rename
# or delete the bad file
def read_best_data(
    best_url_key: str
    , best_url: str
    , rawdir: pathlib.Path
):
    """Download data from Duramat Datahub.

    Parameters
    ----------
    best_url_key : str
        Key of url to download. Used in local filename.
    best_url : str
        URL of source data.
    rawdir : pathlib.Path
        Directory for storing raw data files.

    """
    fname = url_fname(best_url_key, rawdir=rawdir)
    if not fname.exists():
        print(f'Downloading {fname}')
        ur.urlretrieve(
            url=best_url
            , filename=fname)
    else:
        print(f'{fname} already exists')


def prep1_data():
    """Prepare data directories for analysis."""
    # prep directories
    dtadir, cachedir, rawdir = prep_dirs()
    # download files to raw data directory
    print('Downloading...')
    for k, u in best_urls.items():
        read_best_data(k, u, rawdir=rawdir)
    # assemble all data into one dataframe
    print('Combining raw files...')
    dta = pd.concat([
        pd.read_csv(
            url_fname(k, rawdir=rawdir)
            , parse_dates=True
            , index_col=0)
        for k in best_urls.keys()])
    # insure sorted
    dta.sort_index(inplace=True)
    # Save parquet of all data into cache
    print('Saving combined dataframes to cache...')
    dta.to_parquet(cachedir / 'dta.parquet')


if __name__ == "__main__":
    prep1_data()
