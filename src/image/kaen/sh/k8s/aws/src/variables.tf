variable "name" {
  description = "Specifies the name of the swarm that is going to be built.  It is used for names and DNS names."
}

variable "gpu" {
  description = "Specifies whether the instances should be configured with GPU drivers. The instance type must have one or more GPUs."
  default = 0
}

variable "managers" {
  description = "Number of managers in the swarm.  This should be an odd number otherwise there may be issues with raft consensus."
  default     = 1
}

variable "workers" {
  description = "Number of workers in the swarm."
  default     = 0
}

variable "create_daemon_certificate_request" {
  description = "Create daemon certificate request."
  default     = true
}

variable "vpc_id" {
  description = "The VPC that will contain the swarm."
}

variable "cloud_config_extra" {
  description = "Content added to the end of the cloud-config file."
  default     = ""
}

variable "cloud_config_extra_merge_type" {
  description = "Merge type to apply to cloud config."
  default     = "list()+dict()+str()"
}

variable "cloud_config_extra_script" {
  description = "Shell script that will be executed on every node.  This can be used to set up EFS mounts in fstab or do node specific bootstrapping. This is executed after `init_manager.py`"
  default     = ""
}

variable "cloudwatch_logs" {
  description = "Enables logging to Cloudwatch."
  default     = false
}

variable "cloudwatch_single_log_group" {
  description = "Creates a single log group for the whole swarm rather than one per node."
  default     = false
}

variable "cloudwatch_retention_in_days" {
  description = "Specifies the number of days you want to retain log events in the specified log group. Possible values are: 0, 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, and 3653.  0 means never expire."
  default     = 0
}

variable "additional_security_group_ids" {
  description = "These are security groups that are applied to the Docker swarm nodes primarily for accessing other resources or exposing to the Internet."
  type        = list(string)
  default     = []
}

variable "additional_alarm_actions" {
  description = "These are ARNs to alarm actions that will be appended to the one created by the module."
  type        = list(string)
  default     = []
}

variable "exposed_security_group_ids" {
  description = "These are security groups that are applied to the Docker swarm nodes primarily for accessing other resources or exposing to the Internet. The variable name is kept for legacy reasons, use `additional_security_group_ids`"
  type        = list(string)
  default     = []
}

variable "s3_bucket_name" {
  description = "The S3 bucket name, if not specified it will be the DNS name with .terraform added to the end."
  default     = ""
}

variable "instance_type" {
  description = "EC2 instance type.  This is can be overriden by `instance_type_manager` or `instance_type_worker`"
  default     = "t3.micro"
}

variable "instance_type_manager" {
  description = "Manager node EC2 instance type.  If not specified it will use the value of `instance_type`."
  default     = ""
}

variable "instance_type_worker" {
  description = "Worker node EC2 instance type.  If not specified it will use the value of `instance_type`"
  default     = ""
}
variable "volume_size" {
  description = "Size of root volume in gigabytes."
  default     = 8
}

variable "swap_size" {
  description = "Size of swap file in gigabytes.  It should be smaller than volume size as the file is put in the root volume."
  default     = 1
}

variable "manager_subnet_segment_start" {
  description = "This is added to the index to represent the third segment of the IP address."
  default     = 10
}

variable "worker_subnet_segment_start" {
  description = "This is added to the index to represent the third segment of the IP address."
  default     = 110
}

variable "key_name" {
  description = "The key name of the Key Pair to use for the instance; which can be managed using the aws_key_pair resource."
  default     = ""
}

variable "daemon_count" {
  description = "This is the number of daemons to expose.  This is a workaround as count in some contexts cannot be a computed value."
  default     = 0
}

variable "daemon_ssh" {
  description = "Exposes SSH port for the daemon."
  default     = true
}

variable "daemon_tls" {
  description = "Exposes TLS port for the daemon."
  default     = false
}


variable "daemon_eip_ids" {
  description = "These are elastic IP association IDs that will be attached to the daemon nodes.  The association is not performed in the module."
  type        = list(string)
  default     = []
}

variable "daemon_ca_cert_pem" {
  description = "This is the cert for the CA. If this starts with `/` then a symlink will be created instead of writing out the file."
  default     = ""
}

variable "daemon_private_key_pems" {
  description = "These are private key PEMs to the manager nodes that will have their Docker sockets exposed.  Private key generation is not performed by this module.  If this starts with `/` then a symlink will be created instead of writing out the file."
  type        = list(string)
  default     = []
}

variable "daemon_cert_pems" {
  description = "These are cert PEMs to the manager nodes that will have their Docker sockets exposed.  These are the  `daemon_cert_request_pems` that are signed by the CA.   If this starts with `/` then a symlink will be created instead of writing out the file."
  type        = list(string)
  default     = []
}

variable "daemon_private_key_algorithm" {
  description = "The name of the algorithm for the key provided in manager_private_key_pems."
  default     = "RSA"
}

variable "daemon_dns" {
  description = "Public DNS names associated with the manager."
  type        = list(string)
  default     = []
}

variable "daemon_cidr_block" {
  description = "CIDR block to allow access to the  the Docker daemon."
  default     = "0.0.0.0/0"
}

variable "store_join_tokens_as_tags" {
  description = "Store the Docker swarm join tokens as VPC tags."
  default     = false
}

variable "ssh_authorization_method" {
  description = "Authorization method for SSH.  This is one of `none`, `ec2-instance-connect` (default), `iam` (recommended)."
  default     = "ec2-instance-connect"
}

variable "ssh_users" {
  description = "A list of IAM users that will have SSH access when using `iam` for `ssh_authorization_method`"
  default     = []
}

variable "k3s_git_commit" {
  description = "Github commit for the k3s version to use"
  type = string
  default = "fae8817655a8ad1250d40e5b4f9a938cbb9c960a"
}

variable "k3s_kubeconfig_mode" {
  description = "Default mode for the file permissions of the k3s KUBECONFIG file at /etc/rancher/k3s/k3s.yaml"
  default = "644"
}

variable "k3s_manager_port" {
  description = "TCP port to use when connecting to the k3s manager node. Defaults to 6443."
  default = "6443"
}

variable "k3s_manager_protocol" {
  description = "Protocol to use when connecting to the k3s manager node. Options are http or https. Defaults to https."
  default = "https"
}

variable "gpu_per_node_count" {
  description = "Number of GPUs to use per node. Variable gpu must be True. Use -1 to use all GPUs on the node."
  type = number
  default = -1
}
