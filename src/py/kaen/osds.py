import re
import fsspec
import tempfile
import warnings

import pandas as pd

def make_metadata_df(glob = None, df = None, header = 'infer', sep = ','): 
    assert glob is not None or df is not None, "Either glob or df must be specified"
    df = pd.read_csv(f"filecache::{glob}", sep = sep, header = header) if glob else df
    assert set(df.columns) == set(['id', 'count']), "The metadata source must include id and count columns"
    df = df.sort_values(by='id', ignore_index=True)
    df['end_idx'] = df['count'].cumsum()
    df['start_idx'] = df['end_idx'] - df['count']
    df = df[['id', 'start_idx', 'end_idx']]
    return df

def objs_to_metadata_df(objs, header = None):
    rows = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for idx, obj in enumerate(objs):
            try:
                df = pd.read_csv(f"filecache::{obj}", header = header)
                rows.append({"id": idx, "count": len(df),})
            except pd.errors.EmptyDataError:           
                pass
                # ignore empty shards      
                # rows.append({"id": idx, "count": 0,})
    return pd.DataFrame(rows)

def df_read_spec(df, row_count, row_start_idx, row_end_idx):

    assert row_start_idx > -1 and row_start_idx < row_count, f"row_start_idx must be in the range({0, row_count}]"
    assert row_end_idx > -1 and row_end_idx < row_count, f"row_end_idx must be in the range({0, row_count}]"

    start_obj_idx = df[ (row_start_idx >= df['start_idx']) & (row_start_idx < df['end_idx']) ]['id'].item()
    #max is needed to handle the case when the row_end_idx matches the end row of a partition and the start row of a partition
    #if the row_end_idx matches 2 partitions, calling item results in ValueError: can only convert an array of size 1 to a Python scalar
    end_obj_idx_res = df[ (row_end_idx >= df['start_idx']) & (row_end_idx <= df['end_idx']) ]['id'].max()    
    end_obj_idx = end_obj_idx_res if isinstance(end_obj_idx_res, int) else end_obj_idx_res.item()

    start_obj_idx = df [ df['id'] == start_obj_idx ].index.values.item()
    end_obj_idx = df [ df['id'] == end_obj_idx ].index.values.item()

    if row_end_idx > row_start_idx:
        
        df_spec = df.iloc[start_obj_idx : end_obj_idx + 1]
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df_spec.loc[:, 'skiprows'] = df_spec['start_idx'].apply(lambda i: max(0, row_start_idx - i))
            df_spec.loc[:, 'numrows'] = df_spec['end_idx'].apply(lambda i: min(i, row_end_idx)) - (df_spec['start_idx'] + df_spec['skiprows'])
            
        df_values = df_spec[['skiprows', 'numrows', 'uri']].values
    
    #handle the wrap-around case
    #when the shard consists
    #of a tail of a dataset
    #followed by the dataset head
    else:

        head_df = df.iloc[start_obj_idx : ]
        tail_df = df.iloc[ : end_obj_idx + 1] #if end_obj_idx > start_obj_idx else None
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            head_df.loc[:, 'skiprows'] = head_df['start_idx'].apply(lambda i: max(0, row_start_idx - i))
            head_df.loc[:, 'numrows'] = head_df['end_idx'] - (head_df['start_idx'] + head_df['skiprows'])

            if tail_df is not None:
                tail_df.loc[:, 'skiprows'] = 0
                tail_df.loc[:, 'numrows'] = tail_df['end_idx'].apply(lambda i: min(i, row_end_idx)) - tail_df['start_idx']

        df_values = pd.concat([head_df, tail_df], ignore_index = True)[['skiprows', 'numrows', 'uri']].values
        
    return [ (skiprows, numrows, uri) for (skiprows, numrows, uri) in df_values ]

class BaseObjectStorageDataset():        
    def __init__(self, 
                 glob, 
                 header = 'infer', 
                 index_metadata = None,
                 metadata_glob = None, 
                 make_metadata_df_fn = make_metadata_df, 
                 objs_to_metadata_df_fn = objs_to_metadata_df,
                 worker = 0, 
                 replicas = 1, 
                 shard_size = 1,                   
                 max_shards = None,
                 storage_options = None, 
                 cache_dir = None,):
        assert glob, "glob must be specified"
        self.glob = glob
        
        self.header = header

        if index_metadata is None:
            if metadata_glob is None:
                index_metadata = True
                import warnings
                warnings.warn("metadata_glob is not specified at initialization, attempting to proceed with index_metadata=True which can take a while for large objects.")
            else:
                index_metadata = False
        else:
            assert isinstance(index_metadata, bool), "index_metadata must be set to True or False"

        assert make_metadata_df_fn, "make_metadata_df_fn must be specified"
        self.make_metadata_df_fn = make_metadata_df_fn

        if index_metadata is None \
                or index_metadata is True \
                or metadata_glob is not None:
            assert objs_to_metadata_df_fn, "objs_to_metadata_df_fn must be specified"
            self.objs_to_metadata_df_fn = objs_to_metadata_df_fn

        assert worker is not None or replicas is not None, "Both worker and replicas must be specified together along with shard_size"
        assert worker > -1 and worker < replicas, f"worker must be in the range [0, {replicas})"
        self.worker = worker
        self.replicas = replicas

        if self.replicas > 1:
            assert shard_size, "shard_size must be specified if replicas is greater than 1"
        self.shard_size = shard_size

        self.max_shards = max_shards if max_shards else float('nan')

        # set the platform-specific temporary directory
        cache_dir = cache_dir if cache_dir else tempfile.gettempdir()

        # find out the protocol of the glob, e.g. s3, gs, hdfs, etc
        protocol, _ = fsspec.core.split_protocol(glob)
#         eager_load_batches = True if protocol in ('file') and eager_load_batches is None else eager_load_batches

        # use anonymous connection unless specified otherwise
        storage_options = storage_options if storage_options else {'anon': True}
        # handle the edge case when the user passes the boolean as a non boolean, e.g. str
        if 'anon' in storage_options:
            if type(storage_options['anon']) is str:
                storage_options['anon'] = True if str(storage_options['anon']).lower() == 'true' else False
            else:
                storage_options['anon'] = bool(storage_options['anon'])
        
        if protocol in ('http', 'https'):
            # setup a caching filesystem
            self.fs = fsspec.filesystem("filecache",
                                        target_protocol = protocol,
                                        target_options = storage_options,
                                        cache_storage = cache_dir)

        else:
            # setup a caching filesystem
            self.fs = fsspec.filesystem("filecache",
                                        target_protocol = protocol,
                                        target_options = storage_options,
                                        cache_storage = cache_dir)

        # get the object paths matching the glob
        if protocol in ('http', 'https'):
            _, uri = fsspec.core.split_protocol(glob)
            self.objs = [uri]
        else:
            self.objs = self.fs.glob(glob)

        if not isinstance(self.objs, list) or not len(self.objs):
            raise RuntimeWarning(f"Specified glob pattern {self.glob} failed to match any objects. Ensure that the permission setting are configured correctly using storage_options before trying again.")

        self.objs = [f"{protocol}://{obj}" for obj in self.objs]

        # if the shard metadata is unavailable
        # use the objects in the glob to generate the metadata
        # with the count of lines of records per shard            
        if index_metadata is None or index_metadata is True:            
            self.metadata_df = make_metadata_df_fn(df = objs_to_metadata_df_fn(self.objs, header = self.header))
        else:            
            self.metadata_df = make_metadata_df_fn(glob = metadata_glob)
                
        # if the number of shards is identical to the number of metadata records
        if len(self.objs) == len(self.metadata_df):
            self.metadata_df = self.metadata_df.sort_values(by = 'id', ascending = True)
            self.metadata_df['uri'] = pd.Series(name = 'uri', data = self.objs).sort_values(ascending=True)

        else:            
            # query for obj sizes in order to later ignore the empty shards 
            # because they are not in the metadata dataframe
            glob_dict = self.fs.glob(glob, detail = True)
            kvs = glob_dict.items()

            objs_df = pd.DataFrame(data = map( lambda kv : (kv[1]['Key'], kv[1]['Size']), kvs ), columns = ['key', 'size'] )
            # use just the non-empty shards / partitions
            objs_df = objs_df[ objs_df['size'] > 0 ]

            assert len(objs_df) == len(self.metadata_df), f"The number of the non-empty objects matching the glob pattern {len(objs_df)} is not equal to the number of the non-empty shards {len(self.metadata_df)}."

            self.metadata_df['uri'] = objs_df['key'].apply(lambda s: f"{protocol}://{s}").sort_values(ascending=True)

        #TODO: improve: right now assumes that the uri has the matching ID specified in 'part-00000-' substring inthe file
        # objs_df = pd.DataFrame(columns=['uri'], data = pd.Series(self.objs).apply(lambda s: f"{protocol}://{s}"))
        # id_re = re.compile('part-(\d{5})-')
        # objs_df['id'] = objs_df['uri'].apply(lambda s: int(id_re.findall(s)[0]))
        # self.metadata_df = self.metadata_df.merge(objs_df, on = 'id')
        #TODO: improve

        self.obj_count = len(self.metadata_df)
        self.row_count = self.metadata_df.iloc[-1]['end_idx']

    def __iter__(self):
        shard_start_idx = self.worker * self.shard_size
        while self.max_shards:
            try:
                num_rows, row_start_idx, row_end_idx = self.shard_size, shard_start_idx, shard_start_idx + self.shard_size

                # the for loop handles the case where the shard
                # is larger than the number of rows in the dataset
                row_start_indicies = list(range(row_start_idx, row_end_idx, self.row_count))
                row_end_indicies = list(row_start_indicies[1:] + [row_end_idx])
                src_df_list = []
                for row_start_idx, row_end_idx in zip(row_start_indicies, row_end_indicies):

                    #query rows based on actual indicies in the dataset
                    row_start_idx = row_start_idx % self.row_count
                    row_end_idx = row_end_idx % self.row_count
                    if self.header is None:
                        for (skiprows, nrows, uri) in df_read_spec(self.metadata_df, self.row_count, row_start_idx, row_end_idx):
                            src_df_list.append( pd.read_csv(f"filecache::{uri}", header = None, nrows=nrows, skiprows=skiprows) )

                    elif self.header == 'infer' or self.header == 0:                        
                        for (skiprows, nrows, uri) in df_read_spec(self.metadata_df, self.row_count, row_start_idx, row_end_idx):

                            if (skiprows == 0):
                                #skiprows == 0 when we are at the top of the file with a (potential) header                            
                                df = pd.read_csv(f"filecache::{uri}", header = self.header, nrows = nrows, skiprows = 0)

                                # set columns to numbers since reseting the index drops the data types
                                df.columns = list(range(len(df.columns)))

                                #silly hack because pandas doesn't let me to reset the index along the columns axis
                                # df = df.T
                                # df.reset_index(drop = True, inplace = True)
                                # df = df.T

                            else:
                                #(skiprows+1) skip the extra row  to account for the skipped header
                                df = pd.read_csv(f"filecache::{uri}", header = None, nrows = nrows, skiprows = skiprows + 1) 

                            src_df_list.append(df)

                    else:
                        raise ValueError(f"header attribute cannot be set to {self.header}")

                    # map(lambda df: df.columns, src_df_list)
                    # assert len(set(map(lambda df: df.shape[1], src_df_list))) == 1, f"Failed to process in the following fragment of the dataset {df_read_spec(self.metadata_df, self.row_count, row_start_idx, row_end_idx)} due to a change in the number of the columns."

                yield pd.concat(
                    objs = src_df_list,
                    copy = False,
                    ignore_index=True,
                )
                                
            finally:
                shard_start_idx += (self.replicas * self.shard_size)
                self.max_shards -= 1
                