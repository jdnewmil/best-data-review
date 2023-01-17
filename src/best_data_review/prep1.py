# prep1.py

# %%
import urllib.request as ur
from joblib import Memory
import pandas as pd
import pathlib

# %%
cachedir = 'data/cache'
rawdir = 'data/raw'
mem = Memory(cachedir)
best_urls = {
    '2020-jan-dec': r'https://datahub.duramat.org/dataset/72334fe1-fa52-45f8-a43c-836a35b9c526/resource/b7e35897-4d32-48fc-b53c-7b780537d87d/download/data_release__sep2022_period_2020_0112.csv'
    , '2021-jan-dec': r'https://datahub.duramat.org/dataset/72334fe1-fa52-45f8-a43c-836a35b9c526/resource/264212b8-800e-47b5-80ac-1dd2c644aa74/download/data_release__sep2022_period_2021_0112.csv'
    , '2022-jan-aug': r'https://datahub.duramat.org/dataset/72334fe1-fa52-45f8-a43c-836a35b9c526/resource/2fb7b6f4-a916-40e8-831c-dd2c445852d7/download/data_release__sep2022_period_2022_0108.csv'
    , '2019-jul-dec': r'https://datahub.duramat.org/dataset/72334fe1-fa52-45f8-a43c-836a35b9c526/resource/f32ba09d-f750-4746-82ec-5f930c18437a/download/data_release_sep2022_period_2019_0712.csv'
}

# %%
dtadir = pathlib.Path('data')
if not dtadir.exists():
    raise Exception('data directory does exist: are you in the right working directory?')
elif not dtadir.is_dir():
    raise Exception('data name in filesystem is not a directory: rename or move existing file, or move to correct working directory')
elif not (dtadir / 'config').is_dir():
    raise Exception('data directory does not have a config subdirectory: are you in the right working directory?')
cachedir = dtadir / 'cache'
if not cachedir.exists():
    cachedir.mkdir()
rawdir = dtadir / 'raw'
if not rawdir.exists():
    rawdir.mkdir()

# %%
def url_fname(best_url_key: str) -> pathlib.Path:
    return rawdir / f'{best_url_key}.csv'

# Define a function to safely read the data
# If download fails, user will have to identify and then rename
# or delete the bad file
def read_best_data(
    best_url_key: str
    , best_url: str
) -> pd.DataFrame:
    fname = url_fname(best_url_key)
    if not fname.exists():
        print(f'Downloading {fname}')
        ur.urlretrieve(
            url=best_url
            , filename=fname)
    else:
        print(f'{fname} already exists')


# %%
# download files to raw data directory
print('Downloading...')
for k, u in best_urls.items():
    read_best_data(k, u)


# %%
# assemble all data into one dataframe
print('Combining raw files...')
dta = pd.concat([
    pd.read_csv(
        url_fname(k)
        , parse_dates=True
        , index_col=0)
    for k in best_urls.keys()])

# %%
# Save parquet of all data into cache
print('Saving combined dataframes to cache...')
dta.to_parquet(cachedir / 'dta.parquet')

# %%
