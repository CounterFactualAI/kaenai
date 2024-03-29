import os
import click
import uuid

from dotenv import dotenv_values

VERSION = "0.0.1"
IMAGE_NAME = "kaenai/kaen2"
IMAGE_TAG = "latest"
IMAGE = f"{IMAGE_NAME}:{IMAGE_TAG}"

def get_or_create_job_store(dojo = None, job = None):
	if job:
		job_dir = f"{os.getcwd()}/.job/.{job}"
		os.makedirs(job_dir, exist_ok = True)
		return job_dir
	else:
		return None

def save_to_job_store(job, filename, s):
	job_dir = get_or_create_job_store(job = job)
	file_path = f"{job_dir}/{filename}"
	with open(file_path, "w") as file:
		file.write(s)
	return file_path

def get_dojo_config(dojo):
	dojo_config = {
		**dotenv_values(f"{os.getcwd()}/.dojo/.{dojo}/env.sh")
	}
	return dojo_config

def get_job_config(job):
	job_config = {
		**dotenv_values(f"{os.getcwd()}/.job/.{job}/env.sh")
	}
	return job_config
	
def get_backend_provider(dojo = None, job = None):
	if job:
		job_config = get_job_config(job)	
		dojo_config = get_dojo_config(job_config['KAEN_DOJO'])
	elif dojo:
		dojo_config = get_dojo_config(dojo)
	else:
		return None

	backend = dojo_config['KAEN_BACKEND']
	provider = dojo_config['KAEN_PROVIDER']
	
	return backend, provider

def get_volumes(provider = None):
	volumes = {f"{os.getcwd()}" : {"bind": "/workspace", "mode": "rw"},}
	if provider == 'local':
		volumes = {
			**volumes, 
			**{"/var/run/docker.sock": {"bind": "/var/run/docker.sock", "mode": "rw"}}
		}
	return volumes

def assert_aws_credentials():
	assert 'AWS_ACCESS_KEY_ID' in os.environ, "Missing environment variable AWS_ACCESS_KEY_ID"
	assert 'AWS_DEFAULT_REGION' in os.environ, "Missing environment variable AWS_DEFAULT_REGION"
	assert 'AWS_SECRET_ACCESS_KEY' in os.environ, "Missing environment variable AWS_SECRET_ACCESS_KEY"

def prepare_docker():
	# print(f"Checking for the latest updates...", end='')
	client = prepare_docker_image(f"{IMAGE_NAME}:{IMAGE_TAG}", IMAGE_NAME, IMAGE_TAG)
	# print('Done')
	
	return client

def prepare_docker_image(image, name, tag):

	import docker
	client = docker.from_env()
	images = client.images.list(image)
	if len(images):
		image = images[0]
	else:
		print(f'Unable to find {image} in local storage. Pulling the image...', end = '')
		image = client.images.pull(name, tag)
		print('Done')

	return client


def _pty(cmd):
	import os
	import pty
	import tempfile
	with tempfile.TemporaryFile() as pty_output:
		def read_pty(fds):
				"""Append tty output to file descriptor."""
				data = os.read(fds, 1024)
				pty_output.write(data)
				return data

		status = pty.spawn(cmd, read_pty)
		assert status == 0, f"ERROR: Status code {status}"

def _docker_run_str(image, command, volumes, environment):
	docker_str = f"""docker run -it"""
	env_str = [f"""--env {k}={v}""" for k,v in environment.items()]
	vol_str = []
	for vol, params in volumes.items():
			bind = params['bind'] if 'bind' in params else None
			mode = params['mode'] if 'mode' in params else None
			vol_str.append(None if None in (vol, bind, mode) else f"""-v {vol}:{bind}:{mode}""")
	run_str = f"""{docker_str} {' '.join(env_str)} {' '.join(vol_str)} {image} {command}"""
	return run_str

def _docker_run(client, volumes, environment, command):
	container = None
	try:
		container = client.containers.create(
			image = IMAGE, 
			command = command,
			volumes = volumes ,
			environment = environment,
			detach = True 
		)
		container.start()
		logs = container.logs(stream = True)
		for s in logs:
			print(s.decode('utf-8').strip())	
	finally:
		container.remove() if container is not None else None


@click.group()
def cli():
	f"""Kaen helps you train distributed PyTorch deep learning models in AWS, Azure, and Google Cloud.

	You are using Kaen version {VERSION}.
	"""
	pass

@cli.command("init")
@click.option('--provider', required=False, default='local', show_default=True, type=click.Choice(['aws', 'azure', 'gcp', 'local'], case_sensitive=False))
@click.option('--backend', default='docker', type=click.Choice(['docker', 'k8s'], case_sensitive=False), show_default=True)
@click.option('--worker-instances', default='1', type=int, show_default=True)
@click.option('--worker-instance-type', default='t3.micro', show_default=True)
@click.option('--manager-instances', default='1', type=int, show_default=True)
@click.option('--manager-instance-type', default='t3.micro', show_default=True)
@click.option('--volume-size', default='16', type=int, show_default=True)
@click.option('--gpu', is_flag=True, required = False, default = False, show_default=True, help="Enable GPU usage when supported by the instance type. [default: 0]")
@click.option('--ssh-connection-timeout', default='5', type=int, show_default=True)
@click.option('--ssh-connection-attempts', default='1', type=int, show_default=True)
def init(provider, 
			backend, 
			worker_instances, 
			worker_instance_type, 
			manager_instances, 
			manager_instance_type,
			volume_size,
			gpu,
			ssh_connection_timeout,
			ssh_connection_attempts):			
	"""Initialize a training dojo in a specified infrastructure provider."""
	DojoCLI.init(provider, 
			backend, 
			worker_instances, 
			worker_instance_type, 
			manager_instances, 
			manager_instance_type,
			volume_size,
			gpu,
			ssh_connection_timeout,
			ssh_connection_attempts)

class DojoCLI(click.MultiCommand):
	@cli.command("init")
	@click.option('--provider', required=False, default='local', show_default=True, type=click.Choice(['aws', 'azure', 'gcp', 'local'], case_sensitive=False))
	@click.option('--backend', default='docker', type=click.Choice(['docker', 'k8s'], case_sensitive=False), show_default=True)
	@click.option('--worker-instances', default='1', type=int, show_default=True)
	@click.option('--worker-instance-type', default='t3.micro', show_default=True)
	@click.option('--manager-instances', default='1', type=int, show_default=True)
	@click.option('--manager-instance-type', default='t3.micro', show_default=True)
	@click.option('--volume-size', default='16', type=int, show_default=True)
	@click.option('--gpu', is_flag=True, required = False, default = False, show_default=True, help="Enable GPU usage when supported by the instance type. [default: 0]")
	@click.option('--ssh-connection-timeout', default='5', type=int, show_default=True)
	@click.option('--ssh-connection-attempts', default='1', type=int, show_default=True)
	def init(provider, 
				backend, 
				worker_instances, 
				worker_instance_type, 
				manager_instances, 
				manager_instance_type,
				volume_size,
				gpu,
				ssh_connection_timeout,
				ssh_connection_attempts):			
		"""Initialize a training dojo in a specified infrastructure provider."""
		provider = provider.strip().lower() if provider is not None and str == type(provider) and len(provider) > 0 else None
		assert provider == 'aws' or provider == 'local', f"Provider {provider} is not publicly available in version {VERSION}"
		assert backend == 'docker' or backend == 'k8s', f"Backend {backend} is not publicly available in version {VERSION}"
		
		#check for the aws settings
		if (provider == 'aws'):
			assert_aws_credentials()

			# #drop the provider prefix for the instance type, e.g. aws:t3.micro -> t3.micro
			# assert worker_instance_type[:len(provider) + 1] == provider + ":",\
			# 	f"Worker instance type {worker_instance_type} is missing a prefix {provider}:"
			# worker_instance_type = worker_instance_type[len(provider) + 1:]

			# manager_instance_type = manager_instance_type[len(provider) + 1:]

		client = prepare_docker()

		dojo = os.environ['KAEN_DOJO'] if 'KAEN_DOJO' in os.environ else None
		while not dojo or dojo[:1].isalpha() is False:
			dojo = uuid.uuid4().hex[:8]
		print(f"Using a dojo store at {os.getcwd()}/.dojo/.{dojo}")

		environment = { "KAEN_DOJO": dojo, 
						"KAEN_VERSION": VERSION,
						"KAEN_BACKEND": backend,
						"KAEN_PROVIDER": provider,
						"KAEN_DOJO_GPU": "1" if gpu else "0",
						}

		# volumes = {f"{os.getcwd()}" : {"bind": "/workspace", "mode": "rw"},}

		# volumes = get_volumes(provider)
		
		# if provider == 'local':
		# 	
		# 	volumes = {
		# 		**volumes, 
		# 		**{"/var/run/docker.sock": {"bind": "/var/run/docker.sock", "mode": "rw"}}
		# 	}
		# else:
		if provider in ('local'):
			print(f"Preparing a dojo using {backend} on {provider} ...")
		else:
			print(f"Preparing a dojo using {backend} on {provider} with {worker_instances} worker(s) and {manager_instances} manager(s){', also enabling GPU support' if gpu else ', no GPU support'}...")
			environment = { **environment, **{
				"KAEN_DOJO_WORKER_INSTANCES": worker_instances,
				"KAEN_DOJO_WORKER_INSTANCE_TYPE": worker_instance_type,
				"KAEN_DOJO_MANAGER_INSTANCES": manager_instances,
				"KAEN_DOJO_MANAGER_INSTANCE_TYPE": manager_instance_type,
				"KAEN_DOJO_VOLUME_SIZE": volume_size,
				"KAEN_DOJO_CONNECT_TIMEOUT": ssh_connection_timeout,
				"KAEN_DOJO_CONNECT_ATTEMPTS": ssh_connection_attempts,
				"AWS_ACCESS_KEY_ID": os.environ['AWS_ACCESS_KEY_ID'],
				"AWS_DEFAULT_REGION": os.environ['AWS_DEFAULT_REGION'],
				"AWS_SECRET_ACCESS_KEY": os.environ['AWS_SECRET_ACCESS_KEY'],}
			}

		_docker_run(client,
								get_volumes(provider), 
								environment,
								f"/bin/bash -c '/opt/kaen/{backend}/{provider}/dojo_init.sh'")

		# command = f"/bin/bash -c '/opt/kaen/{backend}/{provider}/dojo_init.sh'"

		# container = client.containers.run(	image = IMAGE, 
		# 	volumes = volumes,
		# 	environment = environment,
		# 	command = command,
		# 	auto_remove = True,
		# 	detach=True,
		# )
			
		# logs = container.attach(stream = True, logs = True)
		# for s in logs:
		# 	print(s.decode('utf-8').strip())	

		print(dojo)

	@click.command()	
	@click.argument('dojo')
	def activate(dojo):
		print(f"Activating dojo {dojo}")
		backend, provider = get_backend_provider(dojo)
		if 'aws' == provider:
			assert_aws_credentials()

		client = prepare_docker()
		# volumes = get_volumes(provider)

		_docker_run(client,
								get_volumes(provider), 
								{ "KAEN_DOJO": dojo,},
								f"/bin/bash -c '/opt/kaen/{backend}/{provider}/dojo_activate.sh'")

		# container = client.containers.run(	
		# 	image = IMAGE, 
		# 	command = f"/bin/bash -c '/opt/kaen/{backend}/{provider}/dojo_activate.sh'",
		# 	volumes = volumes ,
		# 	environment = { "KAEN_DOJO": dojo, 
		# 					},
		# 	auto_remove = True,
		# 	detach = True )

		# logs = container.attach(stream = True, logs = True)
		# for s in logs:
		# 	print(s.decode('utf-8').strip())	

		

	@click.command()	
	@click.option('--reverse', '-r',  is_flag = True, default = False)
	def ls(reverse):		
		"""Output a list with the training dojo(s) in the current workspace.		
		By default, the dojo that was created most recently in the workspace is listed first.
		Use the --reverse option to reverse the order of the dojo listing."""

		# client = prepare_docker()
		
		environment = {
			"KAEN_DOJO_LS_REVERSE": "" if not reverse else "-r"
		}

		_docker_run(prepare_docker(), 
								get_volumes(), 
								{"KAEN_DOJO_LS_REVERSE": "" if not reverse else "-r",},
								f"/bin/bash -c '/opt/kaen/dojo_ls.sh'")

		# container = None
		# try:

		# 	container = client.containers.create(
		# 		image = IMAGE, 
		# 		command = f"/bin/bash -c '/opt/kaen/dojo_ls.sh'",
		# 		volumes = get_volumes() ,
		# 		environment = environment,
		# 		# auto_remove = True,
		# 		detach = True 
		# 	)
		# 	container.start()
		# 	logs = container.logs(stream = True)
		# 	for s in logs:
		# 		print(s.decode('utf-8').strip())	

		# finally:
		# 	container.remove() if container is not None else None

		# container = client.containers.run(	
		# 	image = IMAGE, 
		# 	command = f"/bin/bash -c '/opt/kaen/dojo_ls.sh'",
		# 	volumes = get_volumes() ,
		# 	environment = environment,
		# 	auto_remove = True,
		# 	detach = True )
		# logs = container.attach(stream = True, logs = True)
		# for s in logs:
		# 	print(s.decode('utf-8').strip())	

		# result = client.containers.run(	
		# 	image = IMAGE, 
		# 	command = f"/bin/bash -c '/opt/kaen/dojo_ls.sh'",
		# 	volumes = get_volumes() ,
		# 	environment = environment,
		# 	auto_remove = False,
		# 	tty = True,
		# 	stdout = True,
		# 	stderr = True,
		# 	stream = False,
		# 	detach = True )			
		# print(result.decode('utf-8').strip())


	@click.command()
	def prune():
		"""Remove deactivated dojo instances.
		
		Finds all dojo instances with the state equal to inactive and force deletes them."""
		client = prepare_docker()
		
		vol = get_volumes()
		env = {}
		
		_docker_run(client,
					vol,
					env,
					f"/bin/bash -c '/opt/kaen/dojo_prune.sh'")

		# container = client.containers.run(	
		# 	image = IMAGE, 
		# 	command=f"/bin/bash -c '/opt/kaen/dojo_prune.sh'",
		# 	volumes = get_volumes() ,
		# 	auto_remove = True,
		# 	detach = True )

		# logs = container.attach(stream = True, logs = True)
		# for s in logs:
		# 	s = s.decode('utf-8').strip()
		# 	if len(s):
		# 		print(s)
	
	@click.command()
	@click.argument('dojo')
	def rm(dojo):
		print(f"Removing dojo {dojo} and deactivating store {os.getcwd()}/.dojo/.{dojo}")

		backend, provider = get_backend_provider(dojo)
		environment = {}
		if 'aws' == provider:
			assert_aws_credentials()
			environment = {
				"AWS_ACCESS_KEY_ID": os.environ['AWS_ACCESS_KEY_ID'],
				"AWS_DEFAULT_REGION": os.environ['AWS_DEFAULT_REGION'],
				"AWS_SECRET_ACCESS_KEY": os.environ['AWS_SECRET_ACCESS_KEY'],				
			}
		
		client = prepare_docker()

		volumes = get_volumes(provider)
		
		container = client.containers.run(	
			image = IMAGE, 
			command=f"/bin/bash -c '/opt/kaen/{backend}/{provider}/dojo_rm.sh'",
			volumes = volumes,
			environment = { **{"KAEN_DOJO": dojo,}, 
							**environment,},
			auto_remove = True,
			detach=True )

		logs = container.attach(stream = True, logs = True)
		for s in logs:
			print(s.decode('utf-8').strip())	

	@click.command()	
	@click.argument('dojo')
	def ssh(dojo):	
		"""Connect using ssh to the specified dojo."""
		backend, provider = get_backend_provider(dojo)
		
		if 'aws' == provider:
			assert_aws_credentials()
		
		client = prepare_docker()

		volumes = get_volumes(provider)
		environment = { "KAEN_DOJO": dojo, }
		cmd = _docker_run_str(f"{IMAGE_NAME}:{IMAGE_TAG}",
										f"/bin/bash -c '/opt/kaen/dojo_ssh.sh'",
									volumes, environment, )
		_pty(cmd.split(' '))

	@click.command()	
	@click.argument('dojo')
	def inspect(dojo):	
		"""Return key value settings for the specified dojo."""
		backend, provider = get_backend_provider(dojo)
		if 'aws' == provider:
			assert_aws_credentials()

		client = prepare_docker()

		volumes = get_volumes(provider)
		environment = { "KAEN_DOJO": dojo, }
		_docker_run(client, 
									volumes, 
									environment, 
									f"/bin/bash -c '/opt/kaen/dojo_inspect.sh'")
		
		# container = client.containers.run(	
		# 	image = IMAGE, 
		# 	command=f"/bin/bash -c '/opt/kaen/dojo_inspect.sh'",
		# 	volumes = ,
		# 	environment = 
		# 	auto_remove = False,
		# 	detach = True )

		# logs = container.attach(stream = True, logs = True, stdout = True, stderr = True)
		# for s in logs:
		# 	print(s.decode('utf-8').strip())
		# container.remove()

	def list_commands(self, ctx):
		return ['ls', 'rm', 'prune', 'activate', 'inspect', 'init']

	def get_command(self, ctx, name):
		return {"ls": DojoCLI.ls,
				"rm": DojoCLI.rm,
				"prune": DojoCLI.prune,
				"inspect": DojoCLI.inspect,
				"ssh": DojoCLI.ssh,
				"init": DojoCLI.init,
				'activate': DojoCLI.activate}[name]

@cli.command(cls=DojoCLI)
def dojo():
	"""Manage a dojo training environment."""
	pass

class JobCLI(click.MultiCommand):
	def parse_args(self, ctx, args):
		if "--" in args:
			idx = args.index("--")
			opt_args = " ".join(args[idx + 1:])
			ctx.meta['kaen_opt_args'] = opt_args
			args = args[:idx]
		
		super(JobCLI, self).parse_args(ctx, args)

	# @click.command()
	# @click.option('--dojo', required = True)
	# @click.option('--image', required = True)
	# @click.pass_context
	# def run(ctx, image, dojo, subnet, manager_ip):
	# 	job = JobCLI.create(image, dojo, None, None)
	# 	JobCLI.start(ctx, job)

	@click.command()
	@click.option('--dojo', required = True)
	@click.option('--image', required = True)
	@click.option('--subnet', required = False)
	@click.option('--manager-ip', required = False)
	def create(image, dojo, subnet, manager_ip):
		"""Create a training job in a specified dojo training environment. 
		The training job must be packaged as a container and available to docker pull 
		command, in other words docker pull <image> must pull the image."""

		dojo_config = get_dojo_config(dojo)
		assert len(dojo_config) > 0 and 'KAEN_DOJO_WORKER_INSTANCES' in dojo_config and 'KAEN_DOJO_MANAGER_INSTANCES' in dojo_config, \
			f"Unable to lookup a valid dojo configuration for dojo {dojo}"
		replicas = int(dojo_config['KAEN_DOJO_WORKER_INSTANCES']) + int(dojo_config['KAEN_DOJO_MANAGER_INSTANCES'])

		if subnet is not None or manager_ip is not None:
			assert subnet is not None and manager_ip is not None, "Both --subnet and --manager-ip must be specified"
			from ipaddress import ip_network, ip_address
			net = ip_network(subnet)
			assert ip_address(manager_ip) in net, f"Manager IP {manager_ip} is not in the CIDR subnet {subnet} range"

		job = None
		while not job or job[:1].isalpha() is False:
			job = uuid.uuid4().hex[:8]			
		print(f"Creating a job {job} using image {image} in dojo {dojo}...")

		from .templates.render import k8s_image_pull_job_yaml
		yaml = k8s_image_pull_job_yaml(image, replicas)
		file_path = save_to_job_store(job, f"img.pull.{job}.yaml", yaml)
		# with open(file_path, "r") as file:
		# 	src = file.read().rstrip()
		# 	print(src)		
		# return

		backend, provider = get_backend_provider(dojo)

		client = prepare_docker()

		volumes = get_volumes(provider)
		environment = { "KAEN_DOJO": dojo,
							"KAEN_JOB": job,
							"KAEN_JOB_IMAGE": image,
							"KAEN_JOB_SUBNET": subnet if subnet else None,
							"KAEN_JOB_MANAGER_IP": manager_ip if subnet else None,
							}


		_docker_run(client,
								volumes,
								environment,
								f"/bin/bash -c '/opt/kaen/{backend}/{provider}/job_create_2.sh'",
								)


		# container = client.containers.run(image = IMAGE, 
		# 	command=f"/bin/bash -c '/opt/kaen/{backend}/{provider}/job_create.sh'",
		# 	volumes = get_volumes(provider),
		# 	environment = { "KAEN_DOJO": dojo,
		# 					"KAEN_JOB": job,
		# 					"KAEN_JOB_IMAGE": image,
		# 					"KAEN_JOB_SUBNET": subnet if subnet else None,
		# 					"KAEN_JOB_MANAGER_IP": manager_ip if subnet else None,
		# 					},
		# 	auto_remove = True,
		# 	detach=True)
		
		# logs = container.attach(stream = True, logs = True)
		# for s in logs:
		# 	print(s.decode('utf-8').strip())	
		
		print(job)			

		return job

	@click.command()	
	@click.argument('job')
	def inspect(job):
		"""Return key value settings for the specified job."""
		
		client = prepare_docker()

		backend, provider = get_backend_provider(job = job)

		vol = get_volumes(provider)
		env = { "KAEN_JOB": job, }
		_docker_run(client,
								vol,
								env,
								f"/bin/bash -c '/opt/kaen/{backend}/{provider}/job_inspect.sh'")
		
		# container = client.containers.run(	
		# 	image=IMAGE, 
		# 	command=f"/bin/bash -c '/opt/kaen/{backend}/{provider}/job_inspect.sh'",
		# 	volumes = get_volumes(provider) ,
		# 	environment = { "KAEN_JOB": job, },
		# 	auto_remove = False,
		# 	detach = True )

		# logs = container.attach(stream = True, logs = True, stdout = True, stderr = True)
		# for s in logs:
		# 	print(s.decode('utf-8').strip())
		# container.remove()

	@click.command()
	@click.argument('job')
	def terminate(job):
		"""Terminate a started job. Once terminated, the job no longer runs but remains until removed or pruned."""

		job_config = get_job_config(job)
		dojo_config = get_dojo_config(job_config['KAEN_DOJO'])

		gpu = dojo_config['KAEN_DOJO_GPU']
		image = job_config['KAEN_JOB_IMAGE']
		
		# from .templates.render import k8s_create_job_yaml
		# yaml = k8s_create_job_yaml(job, gpu, -1, replicas, image)
		# file_path = save_to_job_store(job, f"job.{job}.yaml", yaml)
		# with open(file_path, "r") as file:
		# 	src = file.read().rstrip()
		# 	print(src)

		client = prepare_docker()

		backend, provider = get_backend_provider(job = job)

		env = dict({ "KAEN_JOB": job,})

		vol = get_volumes(provider)

		_docker_run(client, 
								vol,
								env,
								f"/bin/bash -c '/opt/kaen/{backend}/{provider}/job_stop_2.sh'")

		# container = client.containers.run(	image = IMAGE, 
		# 	command=f"/bin/bash -c '/opt/kaen/{backend}/{provider}/job_start.sh'",
		# 	volumes = vol ,
		# 	environment = env,
		# 	auto_remove = True,
		# 	detach = True)

		# if not detach:
		# 	logs = container.attach(stream = True, logs = True)
		# 	for s in logs:
		# 		print(s.decode('utf-8').strip())	


	@click.command(context_settings=dict(
			ignore_unknown_options=True,
	))	
	@click.pass_context
	@click.argument('job')
	@click.option('--replicas', required = False, default=-1, type=int, help="Number of the nodes to execute the job. Must be a number in the range starting from 1 and up to the total number of instances in the dojo, or -1. The default value of -1 means use all manager and worker instance nodes to run the job.")
	@click.option('--nproc_per_node', required = False, default = 1, type=int)
	@click.option('--detach', is_flag = True, default = False)
	@click.option('--port', '-p', required = False, default = [], multiple = True, type=click.Tuple([str, str]) )	
	@click.option('--env', '-e', required = False, default = [], multiple = True, type=click.Tuple([str, str]) )
	@click.argument('opt_args', nargs=-1, type=click.UNPROCESSED)
	def start(ctx, job, replicas, nproc_per_node, detach, port, env, opt_args):
		"""Start an existing job using the specified number of worker replicas."""

		job_config = get_job_config(job)
		if len(job_config) == 0 or 'KAEN_DOJO' not in job_config:
			raise click.BadParameter(
				f"Unable to lookup a valid dojo for job {job}",
				param_hint=["job"],
			)

		dojo_config = get_dojo_config(job_config['KAEN_DOJO'])

		gpu = dojo_config['KAEN_DOJO_GPU']
		image = job_config['KAEN_JOB_IMAGE']
		
		#if use all available 
		if -1 == replicas:
			replicas = int(dojo_config['KAEN_DOJO_WORKER_INSTANCES']) + int(dojo_config['KAEN_DOJO_MANAGER_INSTANCES'])
		elif not(replicas >= 1 and replicas <= (int(dojo_config['KAEN_DOJO_WORKER_INSTANCES']) + int(dojo_config['KAEN_DOJO_MANAGER_INSTANCES']))):
			raise click.BadParameter(
            "Must be a number in the range starting from 1 and up to the total number of instances in the dojo, or -1. The default value of -1 means use all manager and worker instance nodes to run the job.",
            param_hint=["--replicas"],
        )
		else:
			replicas = int(replicas)

		opt_args = ctx.meta['kaen_opt_args'] if 'kaen_opt_args' in ctx.meta else None
		
		from .templates.render import k8s_create_job_yaml
		yaml = k8s_create_job_yaml(job, gpu, replicas, nproc_per_node, image, opt_args)
		file_path = save_to_job_store(job, f"job.{job}.yaml", yaml)
		# with open(file_path, "r") as file:
		# 	src = file.read().rstrip()
		# 	print(src)		
		# return
		
		client = prepare_docker()

		backend, provider = get_backend_provider(job = job)

		env = dict({ "KAEN_JOB": job,
					 "KAEN_JOB_REPLICAS": replicas,
					 "KAEN_JOB_CFG_DETACH": 1 if detach else 0,
					 },
					 **{"KAEN_JOB_ARG_" + k : v for k, v in env},
					 **{"KAEN_JOB_PORT_" + k : v for k, v in port})

		vol = get_volumes(provider)

		_docker_run(client, 
								vol,
								env,
								f"/bin/bash -c '/opt/kaen/{backend}/{provider}/job_start_2.sh'")

		# container = client.containers.run(	image = IMAGE, 
		# 	command=f"/bin/bash -c '/opt/kaen/{backend}/{provider}/job_start.sh'",
		# 	volumes = vol ,
		# 	environment = env,
		# 	auto_remove = True,
		# 	detach = True)

		# if not detach:
		# 	logs = container.attach(stream = True, logs = True)
		# 	for s in logs:
		# 		print(s.decode('utf-8').strip())	

	# @click.command(context_settings=dict(
	# 		ignore_unknown_options=True,
	# ))	
	@click.command()	
	@click.option('--reverse', '-r',  is_flag = True, default = False)
	# @click.argument('opt_args', nargs=-1, type=click.UNPROCESSED)
	def ls(reverse, opt_args):		
		"""List existing jobs in the current workspace.
		By default, the dojo that was created first in the workspace is listed first."""

		client = prepare_docker()
		
		env = {
			"KAEN_JOB_LS_REVERSE": "" if not reverse else "-r"
		}

		volumes = get_volumes()

		_docker_run(client, 
								volumes,
								env,
								f"/bin/bash -c '/opt/kaen/job_ls.sh'")
		
		container = client.containers.run(	
			image=IMAGE, 
			command=f"/bin/bash -c '/opt/kaen/job_ls.sh'",
			environment = env,
			volumes = get_volumes(),
			auto_remove = False,
			detach = True )

		logs = container.attach(stream = True, logs = True)
		for s in logs:
			print(s.decode('utf-8').strip())

	@click.command()
	@click.argument('job')
	def rm(job):
		"""Remove the specified job and associated resources."""
		client = prepare_docker()
		env = dict({ "KAEN_JOB": job,})
		backend, provider = get_backend_provider(job = job)
		
		volumes = get_volumes(provider)

		container = client.containers.run(	
			image=IMAGE, 
			command=f"/bin/bash -c '/opt/kaen/{backend}/{provider}/hpo_disable.sh'",
			volumes = volumes,
			environment = env,
			auto_remove = False,
			detach = True )

		logs = container.attach(stream = True, logs = True)
		for s in logs:
			print(s.decode('utf-8').strip())			
		
		container = client.containers.run(	
			image=IMAGE, 
			command=f"/bin/bash -c '/opt/kaen/{backend}/{provider}/job_rm.sh'",
			volumes = volumes,
			environment = env,
			auto_remove = False,
			detach = True )

		logs = container.attach(stream = True, logs = True)
		for s in logs:
			print(s.decode('utf-8').strip())	


	def list_commands(self, ctx):
		return ['ls', 'rm', 'create', 'inspect', 'start', 'terminate']

	def get_command(self, ctx, name):
		return {"ls": JobCLI.ls,
				"rm": JobCLI.rm,
				'create': JobCLI.create,
				'inspect': JobCLI.inspect,
				"start": JobCLI.start,
				"terminate": JobCLI.terminate}[name]

@cli.command("job", cls=JobCLI)
def job():
	"""Manage jobs in a specific dojo training environment."""
	pass

class HpoCLI(click.MultiCommand):
	def list_commands(self, ctx):
		return ["enable", "disable", 'start', 'stop', 'inspect', 'set']

	def get_command(self, ctx, name):
		return {"enable": HpoCLI.enable,
				"disable": HpoCLI.disable,
				"start": HpoCLI.start,
				"stop": HpoCLI.stop,
				"client": HpoCLI.client,
				'inspect': HpoCLI.inspect,
				'set': HpoCLI._set,
				'kv': HpoCLI.kv}[name]

	@click.command()
	@click.argument('name')
	@click.option('--parent-run', is_flag = True, required = False)
	@click.option('--active-run-params', is_flag = True, required = False)
	@click.option('--hp-set-id', required = False)
	def inspect(name, parent_run, active_run_params, hp_set_id):
		from kaen.hpo.mlflow_utils import get_client, get_parent_run, \
			get_active_child_run, get_active_run_params, \
			get_active_run_hp_set_id

		mlflow_tracking_uri = os.environ['MLFLOW_TRACKING_URI'] if 'MLFLOW_TRACKING_URI' in os.environ else None
		client = get_client(mlflow_tracking_uri)
		if parent_run:
			run = get_parent_run(client, name)
			if run is not None:
				for k, v in {"EXPERIMENT_RUN_ID": run.info.run_id, 
							"EXPERIMENT_RUN_STATUS": run.info.status, 
							# **run.data.tags, 
							}.items():
					print(f"KAEN_{k}={v}")
			else:
				return None
		elif active_run_params:
			params = get_active_run_params(mlflow_tracking_uri = mlflow_tracking_uri, mlflow_experiment_name = name)
			if params is not None:
				print(params)
		elif hp_set_id:
			hp_id = get_active_run_hp_set_id(mlflow_experiment_name=name, hp_set_id=hp_set_id)
			print(hp_id)

	@click.command()
	@click.argument('job')
	@click.option('--image', required = True)
	@click.option('--num-runs', required = False, default = 1, show_default=True)
	@click.option('--seed', required = False, default = 42, show_default=True)
	@click.option('--service-prefix', required = False, default = 'kaen.hpo.services', show_default=True)
	@click.option('--service-name', required = False, default = 'BaseMLFlowService', show_default=True)
	@click.option('--port', '-p', required = False, default = [], multiple = True, type=click.Tuple([str, str]) )	
	@click.option('--env', '-e', required = False, default = [], multiple = True, type=click.Tuple([str, str]) )
	def enable(job, image, num_runs, seed, service_prefix, service_name, port, env):
		"""Enable hyperparameter optimization(HPO) for a job using
		the HPO service packaged in the specified image."""

		client = prepare_docker()

		backend, provider = get_backend_provider(job = job)

		env = dict({ "KAEN_JOB": job,
					 "KAEN_HPO_SEED": seed,
					 "KAEN_HPO_IMAGE": image,
					 "KAEN_HPO_JOB_RUNS": num_runs,
					 "KAEN_HPO_SERVICE_PREFIX": service_prefix,
					 "KAEN_HPO_SERVICE_NAME": service_name,
					 },
					 **{"KAEN_JOB_ARG_" + k : v for k, v in env},
					 **{"KAEN_JOB_PORT_" + k : v for k, v in port})

		vol = get_volumes(provider)

		_docker_run(client, 
								vol, 
								env,
								f"/bin/bash -c '/opt/kaen/{backend}/{provider}/hpo_enable.sh'")

		# container = client.containers.run(	image = IMAGE, 
		# 	command=f"/bin/bash -c '/opt/kaen/{backend}/{provider}/hpo_enable.sh'",
		# 	volumes = vol,
		# 	environment = env,
		# 	auto_remove = True,
		# 	detach = True)

		# logs = container.attach(stream = True, logs = True)
		# for s in logs:
		# 	print(s.decode('utf-8').strip())	

	@click.command()
	@click.argument('job')
	def disable(job):
		"""Disable hyperparameter optimization(HPO) for a job.
		If a job never had HPO enabled, this command succeeds."""

		client = prepare_docker()

		backend, provider = get_backend_provider(job = job)

		env = dict({ "KAEN_JOB": job,})
		vol = get_volumes(provider)

		container = client.containers.run(	image = IMAGE, 
			command=f"/bin/bash -c '/opt/kaen/{backend}/{provider}/hpo_disable.sh'",
			volumes = vol,
			environment = env,
			auto_remove = True,
			detach = True)

		logs = container.attach(stream = True, logs = True)
		for s in logs:
			print(s.decode('utf-8').strip())	

	@click.command()
	@click.argument('name')
	def _set(name):
		from kaen.hpo.mlflow_utils import get_active_run_feature_set_id		
		print(get_active_run_feature_set_id(feature_set_id = name))

	@click.command()
	@click.option('--output', default='bash', required = False)
	def kv(output):
		from kaen.hpo.mlflow_utils import get_active_run_params
		print(get_active_run_params(output = output))

	@click.command()
	@click.option('--num_runs', required = False, default = 1)
	@click.option('--client_prefix', required = False, default = 'kaen.hpo.client')
	@click.option('--client_name', required = False, default = 'BaseMLFlowClient')
	def client(num_runs, client_prefix, client_name):
		"""Execute a run(s) of a hyperparameter optimization service client.
		
		Unless specified otherwise, the client executes a single run. The default
		implementation of the client uses kaen.hpo.client.BaseMLFlowClient.
		This implementation simply queries for a seed hyperparameter and reports
		uniform random values in a range [0., 1.) as the values for the loss metric.
		"""
		import importlib.util
		mod = importlib.import_module(client_prefix)
		klass = getattr(mod, client_name)
		client = klass()
		client.run(num_runs = num_runs)

	@click.command()
	@click.option('--name', required = True)
	@click.option('--num_runs', required = False, default = 1)
	@click.option('--hpo_seed', required = False, default = 42)
	@click.option('--service_prefix', required = False, default = 'kaen.hpo.services')
	@click.option('--service_name', required = False, default = 'BaseMLFlowService')
	def start(name, num_runs, hpo_seed, service_prefix, service_name):
		import importlib.util
		mod = importlib.import_module(service_prefix)
		klass = getattr(mod, service_name)
		hpo_service = klass()
		hpo_service.run(mlflow_experiment_name = name,
						num_trials = num_runs, 
						hpo_seed = hpo_seed)

	@click.command()
	def stop():
		from kaen.hpo.mlflow_utils import terminate_parent_run
		terminate_parent_run()


@cli.command(cls=HpoCLI)
def hpo():
	"""Manage hyperparameter optimization."""
	pass

@cli.command("jupyter")
def jupyter():
	"""Work with a Jupyter notebook environment."""
	IdeCLI.jupyter()

class IdeCLI(click.MultiCommand):	
	def next_available_port(port=8888):
		import socket
		skt = None
		try:		
			skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			while port < 65536:
				try:
					skt.bind(('', port))
					return port
				except OSError as e:
					#port already bound
					if e.errno == 48:
						port += 1	
					else:
						raise e
		finally:
			if skt is not None:
				skt.close()
		return None

	@cli.command()
	def jupyter():
		"""Work with a Jupyter notebook environment."""
		image_name = "kaenai/jupyter"
		image_tag = "latest"
		image = f"{image_name}:{image_tag}"
		import time		
		from hashlib import md5
		token = md5(str.encode(str(time.time()))).hexdigest()
		port = IdeCLI.next_available_port()
		
		container = IdeCLI._run(image_name, image_tag, [('8888', port), ('5000', '5000'), ('5001', '5001')], [('JPY_TKN', token)])
		logs = container.attach(stream = True, logs = True)
		for s in logs:
			s = s.decode('utf-8').strip()
			if "Use Control-C to stop this server" in s:
				break
			else:
				print(s)
		print(f"Started Jupyter. Attempting to navigate to Jupyter in your browser using http://127.0.0.1:{port}/?token={token}")
		import webbrowser
		webbrowser.open_new(f"http://127.0.0.1:{port}/?token={token}")
	
	def _run(image_name, image_tag, port = [], env = []):
		image = f"{image_name}:{image_tag}"
		client = prepare_docker_image(image = image, name = image_name, tag = image_tag)

		ports = {
			str(host): str(guest) for host, guest in port
		}
		environment = {
			str(k): str(v) for k, v in env
		}

		container = client.containers.run(image = image, 
			environment = environment,
			ports = ports,
			privileged = True,
			auto_remove = True,
			detach = True)

		return container

	@click.command()
	@click.option('--port', '-p', required = False, default = [], multiple = True, type=click.Tuple([str, str]) )	
	@click.option('--env', '-e', required = False, default = [], multiple = True, type=click.Tuple([str, str]) )
	def run(image_name, image_tag, port, env):
		"""Run an IDE image"""
		pass

	def list_commands(self, ctx):
		return [
			# 'jupyter', 
		# 'run',
		]

	def get_command(self, ctx, name):
		return {
			# "jupyter": IdeCLI.jupyter, 
		# "run": IdeCLI.run
		}[name]


# @cli.command(cls=IdeCLI)
# def ide():
# 	"""Manage an Integrated Development Environment(IDE)"""
# 	pass