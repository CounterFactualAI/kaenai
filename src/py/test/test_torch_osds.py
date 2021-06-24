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
	from kaen.torch import ObjectStorageDataset
	

def test_s3_instantiate_torch_osds_shard_size_2():	
	from kaen.torch import ObjectStorageDataset
	osds = ObjectStorageDataset(f"s3://noaa-ghcn-pds/csv/1763.csv",
															shard_size = 2, 
															max_shards = 1)
	return osds															

