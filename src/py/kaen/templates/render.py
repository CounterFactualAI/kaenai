import yaml
import tempfile

from .. import templates
from functools import reduce
from operator import getitem

def k8s_image_pull_job_yaml(image, replicas):
	try:
			import importlib.resources as pkg_resources
	except ImportError:
			#support py<37
			import importlib_resources as pkg_resources	

	with pkg_resources.open_text(templates, 'image.pull.job.yaml') as template:
		docs = yaml.load_all(template, Loader=yaml.Loader)
		src = next(docs)

		#BATCH JOB COMPLETIONS AND PARALLELISM
		spec = reduce(getitem, ['spec'], src)
		spec['completions'] = int(replicas)
		spec['parallelism'] = int(replicas)

		container = reduce(getitem, ['spec', 'template', 'spec', 'containers', 0], src)
		container['image'] = image

		out = str(yaml.dump(src, allow_unicode=True, default_flow_style=False, explicit_start=True))
		return out

def k8s_create_job_yaml(job, gpu, replicas, nproc_per_node, image, opt_args):
	gpu = True if gpu == "1" else False
	if gpu:
		out = k8s_create_gpu_job_yaml(job, replicas, nproc_per_node, image, opt_args)
	else:
		out = k8s_create_cpu_job_yaml(job, replicas, nproc_per_node, image, opt_args)

	return out

def k8s_create_cpu_job_yaml(job, replicas, nproc_per_node, image, opt_args):
	try:
			import importlib.resources as pkg_resources
	except ImportError:
			#support py<37
			import importlib_resources as pkg_resources	

	with pkg_resources.open_text(templates, 'job.cpu.yaml') as template:
		docs = yaml.load_all(template, Loader=yaml.Loader)
		mgr_svc, mgr, agent = list(docs)		
		

		#KAEN_WORLD_SIZE
		mgr_kaen_world_size = reduce(getitem, ['spec', 'containers', 0, 'env', 0], mgr)
		mgr_kaen_world_size['value'] = int(replicas)

		#KAEN_JOB_MANAGER_HOST
		mgr_kaen_job_manager_host = reduce(getitem, ['spec', 'containers', 0, 'env', 3], mgr)
		mgr_kaen_job_manager_host['value'] = f"kaen-pytorch-manager-pod.kaen-k8s-manager.{job}.svc.cluster.local"

		#IMAGE
		mgr_container = reduce(getitem, ['spec', 'containers', 0], mgr)
		mgr_container['image'] = image

		#OPT_ARGS
		exec_args = reduce(getitem, ['spec', 'containers', 0, 'args'], mgr)
		exec_args[0] = f"set | grep KAEN ; ./main.sh main.py {opt_args if opt_args else ''};"

		#BATCH JOB COMPLETIONS AND PARALLELISM
		spec = reduce(getitem, ['spec'], agent)
		spec['completions'] = int(replicas - 1)
		spec['parallelism'] = int(replicas - 1)
		
		#KAEN_WORLD_SIZE
		agent_kaen_world_size = reduce(getitem, ['spec', 'template','spec', 'containers', 0, 'env', 0], agent)
		agent_kaen_world_size['value'] = int(replicas)
		
		#KAEN_JOB_MANAGER_HOST
		agent_kaen_job_manager_host = reduce(getitem, ['spec', 'template','spec', 'containers', 0, 'env', 2], agent)
		agent_kaen_job_manager_host['value'] = f"kaen-pytorch-manager-pod.kaen-k8s-manager.{job}.svc.cluster.local"

		#IMAGE
		agent_container = reduce(getitem, ['spec', 'template','spec', 'containers', 0], agent)
		agent_container['image'] = image

		#OPT_ARGS
		exec_args = reduce(getitem, ['spec', 'template','spec', 'containers',0, 'args'], agent)
		exec_args[0] = f"export KAEN_RANK=$(expr $JOB_COMPLETION_INDEX + 1) ; set | grep KAEN ; ./main.sh main.py {opt_args if opt_args else ''};"
		


		out = str("".join([yaml.dump(i, allow_unicode=True, default_flow_style=False, explicit_start=True) for i in [mgr_svc, mgr, agent]]))
		# import tempfile
		# with tempfile.NamedTemporaryFile(delete = False) as file:
		# 	file.write(bytes(out, 'utf-8'))
		# 	print(file.name)
		return out

def k8s_create_gpu_job_yaml(job, replicas, nproc_per_node, image, opt_args):
	try:
			import importlib.resources as pkg_resources
	except ImportError:
			#support py<37
			import importlib_resources as pkg_resources	

	with pkg_resources.open_text(templates, 'job.gpu.yaml') as template:
		docs = yaml.load_all(template, Loader=yaml.Loader)
		mgr_svc, mgr, agent = list(docs)				

		#KAEN_WORLD_SIZE
		mgr_kaen_world_size = reduce(getitem, ['spec', 'containers', 0, 'env', 0], mgr)
		mgr_kaen_world_size['value'] = str(replicas)

		#KAEN_JOB_MANAGER_HOST
		mgr_kaen_job_manager_host = reduce(getitem, ['spec', 'containers', 0, 'env', 3], mgr)
		mgr_kaen_job_manager_host['value'] = str(f"kaen-pytorch-manager-pod.kaen-k8s-manager.{job}.svc.cluster.local")

		#KAEN_NPROC_PER_NODE
		mgr_kaen_nproc_per_node = reduce(getitem, ['spec', 'containers', 0, 'env', 4], mgr)
		mgr_kaen_nproc_per_node['value'] = str(nproc_per_node)

		#NVIDIA GPU
		# mgr_nvidia_gpu = reduce(getitem, ['spec', 'containers', 0, 'resources', 'limits', ], mgr)
		# mgr_nvidia_gpu['nvidia.com/gpu'] = nproc_per_node

		#IMAGE
		mgr_container = reduce(getitem, ['spec', 'containers', 0], mgr)
		mgr_container['image'] = image

		#OPT_ARGS
		exec_args = reduce(getitem, ['spec', 'containers', 0, 'args'], mgr)
		exec_args[0] = f"set | grep KAEN ; ./main.sh main.py {opt_args if opt_args else ''};"
		# exec_args[0] = "export KAEN_RANK=$(expr $JOB_COMPLETION_INDEX + 1) ; set | grep KAEN ; echo torchrun --nnodes ${KAEN_WORLD_SIZE:-1} --rdzv_id ${KAEN_JOB:-0} --rdzv_backend c10d --rdzv_endpoint=${KAEN_JOB_MANAGER_HOST:-localhost}:${KAEN_JOB_MANAGER_PORT:-23400} main.py $@ ; torchrun --nnodes ${KAEN_WORLD_SIZE:-1} --rdzv_id ${KAEN_JOB:-0} --rdzv_backend c10d --rdzv_endpoint=${KAEN_JOB_MANAGER_HOST:-localhost}:${KAEN_JOB_MANAGER_PORT:-23400} main.py $@  ;"		


		#BATCH JOB COMPLETIONS AND PARALLELISM
		spec = reduce(getitem, ['spec'], agent)
		spec['completions'] = int(replicas - 1)
		spec['parallelism'] = int(replicas - 1)
		
		#KAEN_WORLD_SIZE
		agent_kaen_world_size = reduce(getitem, ['spec', 'template','spec', 'containers', 0, 'env', 0], agent)
		agent_kaen_world_size['value'] = str(replicas)

		#KAEN_NPROC_PER_NODE
		agent_kaen_nproc_per_node = reduce(getitem, ['spec', 'template','spec', 'containers', 0, 'env', 1], agent)
		agent_kaen_nproc_per_node['value'] = str(nproc_per_node)

		#KAEN_JOB_MANAGER_HOST
		agent_kaen_job_manager_host = reduce(getitem, ['spec', 'template','spec', 'containers', 0, 'env', 2], agent)
		agent_kaen_job_manager_host['value'] = str(f"kaen-pytorch-manager-pod.kaen-k8s-manager.{job}.svc.cluster.local")

		#IMAGE
		agent_container = reduce(getitem, ['spec', 'template','spec', 'containers', 0], agent)
		agent_container['image'] = image

		#NVIDIA GPU
		# agent_nvidia_gpu = reduce(getitem, ['spec', 'template','spec', 'containers', 0, 'resources', 'limits'], agent)
		# agent_nvidia_gpu['nvidia.com/gpu'] = nproc_per_node

		#OPT_ARGS
		exec_args = reduce(getitem, ['spec', 'template','spec', 'containers',0, 'args'], agent)
		exec_args[0] = f"export KAEN_RANK=$(expr $JOB_COMPLETION_INDEX + 1) ; set | grep KAEN ; ./main.sh main.py {opt_args if opt_args else ''};"
		# exec_args[0] = "export KAEN_RANK=$(expr $JOB_COMPLETION_INDEX + 1) ; set | grep KAEN ; echo torchrun --nnodes ${KAEN_WORLD_SIZE:-1} --rdzv_id ${KAEN_JOB:-0} --rdzv_backend c10d --rdzv_endpoint=${KAEN_JOB_MANAGER_HOST:-localhost}:${KAEN_JOB_MANAGER_PORT:-23400} main.py $@ ; torchrun --nnodes ${KAEN_WORLD_SIZE:-1} --rdzv_id ${KAEN_JOB:-0} --rdzv_backend c10d --rdzv_endpoint=${KAEN_JOB_MANAGER_HOST:-localhost}:${KAEN_JOB_MANAGER_PORT:-23400} main.py $@  ;"		


		out = str("".join([yaml.dump(i, allow_unicode=True, default_flow_style=False, explicit_start=True) for i in [mgr_svc, mgr, agent]]))
		# import tempfile
		# with tempfile.NamedTemporaryFile(delete = False) as file:
		# 	file.write(bytes(out, 'utf-8'))
		# 	print(file.name)
		return out
