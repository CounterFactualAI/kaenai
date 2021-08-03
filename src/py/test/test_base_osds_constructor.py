import os
import tempfile

def get_numeric_csv_data(header = True):
	header = """
DATE,PRCP,SNWD,SNOW,TMAX,TMIN,AWND,WDF2,WDF5,WSF2,WSF5,FMTM,WT14,WT01,WT17,WT05,WT02,WT22,WT04,WT13,WT16,WT08,WT18,WT03
"""
	csv = """
20120101,0,0,0,128,50,47,100,90,89,112,-9999,1,-9999,-9999,-9999,-9999,-9999,-9999,-9999,-9999,-9999,-9999,-9999
20120102,109,0,0,106,28,45,180,200,130,179,-9999,-9999,1,-9999,-9999,-9999,-9999,-9999,1,1,-9999,-9999,-9999
20120103,8,0,0,117,72,23,180,170,54,67,-9999,-9999,-9999,-9999,-9999,-9999,-9999,-9999,-9999,1,-9999,-9999,-9999
20120104,203,0,0,122,56,47,180,190,107,148,-9999,-9999,1,-9999,-9999,-9999,-9999,-9999,1,1,-9999,-9999,-9999
20120105,13,0,0,89,28,61,200,220,107,165,-9999,-9999,1,-9999,-9999,-9999,-9999,-9999,-9999,1,-9999,-9999,-9999
20120106,25,0,0,44,22,22,180,180,45,63,-9999,1,1,-9999,-9999,-9999,-9999,-9999,-9999,1,-9999,-9999,-9999
20120107,0,0,0,72,28,23,170,180,54,63,-9999,-9999,1,-9999,-9999,-9999,-9999,-9999,1,1,-9999,-9999,-9999
20120108,0,0,0,100,28,20,160,200,45,63,-9999,-9999,-9999,-9999,-9999,-9999,-9999,-9999,-9999,-9999,-9999,-9999,-9999
"""	
	return header + csv if header is True else csv

def get_csv_file(header = True):
	import re
	csv = get_numeric_csv_data(header = header).strip()
	csv = re.sub(" +", ' ', csv)
	csv = re.sub("\n+", '\n', csv)
	tmp = tempfile.NamedTemporaryFile(delete=False)
	with open(tmp.name, "w") as csv_file:
		csv_file.write(csv)
		csv_file.close()
	with open (tmp.name, "r") as csv_file:
		csv_saved = ''.join(csv_file.readlines())
	assert csv_saved.strip() == csv.strip(), f"""Failed to persist the following CSV data to a temporary file name {tmp.name} {csv}"""
	return tmp.name, csv

def test_import():
	from kaen.osds import BaseObjectStorageDataset

def test_local_instantiate_headerless():
	csv, data = get_csv_file(header = False)
	from kaen.osds import BaseObjectStorageDataset
	osds = BaseObjectStorageDataset(f"file://{csv}")
	return osds

def test_local_instantiate_header():
	csv, data = get_csv_file(header = True)
	from kaen.osds import BaseObjectStorageDataset
	osds = BaseObjectStorageDataset(f"file://{csv}")
	return osds

def test_local_instantiate_headerless_1_example():
	osds = 	test_local_instantiate_headerless()
	return osds

def test_local_instantiate_header_shard_size_2():
	csv, data = get_csv_file(header = True)
	from kaen.osds import BaseObjectStorageDataset
	osds = BaseObjectStorageDataset(f"file://{csv}", 
															shard_size = 2, 
															max_shards = 4)
	return osds

def test_https_instantiate_headerless_shard_size_default():
	from kaen.osds import BaseObjectStorageDataset
	osds = BaseObjectStorageDataset(f"https://raw.githubusercontent.com/osipov/smlbook/master/train.csv")
	return osds

def test_http_noheader_shard_size_4_iter_2():
	from kaen.osds import BaseObjectStorageDataset
	osds = BaseObjectStorageDataset(f"https://raw.githubusercontent.com/osipov/smlbook/master/train.csv",
																	shard_size = 4)
	df = next(iter(osds))
	assert len(df) == 4

	df = next(iter(osds))
	assert len(df) == 4

	return osds
	

def test_s3_aws_credentials():
	assert 'AWS_ACCESS_KEY_ID' in os.environ, "AWS_ACCESS_KEY_ID not specified, S3 tests that require credentials will fail"
	assert 'AWS_SECRET_ACCESS_KEY' in os.environ, "AWS_SECRET_ACCESS_KEY not specified, S3 tests that require credentials will fail"

def test_s3_instantiate_noheader_shard_size_2():
	test_s3_aws_credentials()
	from kaen.osds import BaseObjectStorageDataset
	osds = BaseObjectStorageDataset(f"s3://noaa-ghcn-pds/csv/1763.csv",
															header = None,
															shard_size = 2, 
															max_shards = 1)
	return osds															

def test_s3_instantiate_noheader_shard_size_365_iter_2():
	test_s3_aws_credentials()
	from kaen.osds import BaseObjectStorageDataset
	osds = BaseObjectStorageDataset(f"s3://noaa-ghcn-pds/csv/1763.csv",
															header = None,
															shard_size = 365, 
															max_shards = 2)
	return osds															

def test_s3_noheader_shard_size_2_iter():	
	osds = test_s3_instantiate_noheader_shard_size_2()
	df = next(iter(osds))	
	a = df._get_numeric_data()
	import numpy as np
	b = np.array([[ 1.7630101e+07, -3.6000000e+01, np.nan, np.nan, np.nan],
								[ 1.7630101e+07, -5.0000000e+01, np.nan, np.nan, np.nan],])							
	np.testing.assert_equal(a, b, verbose = True)

def test_s3_noheader_shard_size_365_iter_2():	
	osds = test_s3_instantiate_noheader_shard_size_365_iter_2()
	it = iter(osds)
	a = next(it)
	b = next(it)
	assert len(a) == len(b) == 365

def test_s3_noheader_shard_size_365_enumerate_2():	
	osds = test_s3_instantiate_noheader_shard_size_365_iter_2()
	for idx, df in enumerate(osds):
		pass
	assert idx == 1


# osds = BaseObjectStorageDataset(f"s3://nyc-tlc/trip data/yellow_tripdata_2009-01.csv", 
# 														shard_size = 2, 
# 														max_shards = 4)

# def test_local_instantiate_shard_size_2():
# 	csv, data = get_csv_file()
# 	from kaen.osds import BaseObjectStorageDataset
# 	osds = BaseObjectStorageDataset(f"file://{csv}", shard_size = 2)
# 	return osds

# def test_local_dataloader():
# 	osds = test_local_instantiate()

# 	from torch.utils.data import DataLoader
# 	ds = next(iter(DataLoader(osds)))