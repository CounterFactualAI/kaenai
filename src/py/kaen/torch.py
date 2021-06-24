import torch as pt
from kaen.osds import BaseObjectStorageDataset

class ObjectStorageDataset(BaseObjectStorageDataset, pt.utils.data.IterableDataset):
	def __iter__(self):        
		it = BaseObjectStorageDataset.__iter__(self)
		val = next(it)
		while val is not None:
			try:
				numpy_array = val._get_numeric_data().values
				pt_tensor = pt.from_numpy(numpy_array)        
				yield pt_tensor
				val = next(it)
			except ValueError as err:
				raise ValueError(f"Failed data type conversion, use header='infer' or header = True if the dataset has a header:  {err}")