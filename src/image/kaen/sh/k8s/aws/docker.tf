data "template_file" "cloud-config" {
  template = file("template.cloud-config")

  vars = {
    ssh_key       = var.ssh_key
  }
}

variable "ssh_key" {
  type = string
}

variable "name" {
  type = string
}

variable "instances" {
  type = number
  default = 1
}

variable "worker_instance_type" {
  type = string
  default = "t3.micro"
}

variable "manager_instances" {
  type = number
  default = 1
}

variable "manager_instance_type" {
  type = string
  default = "t3.micro"
}

variable "volume_size" {
  type = number
  default = 8
}

variable "gpu" {
  description = "True if the nodes are configured with a GPU. False by default"
  default = 0
}

variable "gpu_per_node_count" {
  description = "Number of GPUs to use per node. Use -1 to use all GPUs on the node. Variable gpu must be nonzero to use the GPUs."
  type = number
  default = -1
}

variable "k3s_git_commit" {
  description = "Github commit for the k3s version to use"
  type = string
  default = "fae8817655a8ad1250d40e5b4f9a938cbb9c960a"
}


module "docker" {
  source = "./src"

  name               = var.name
  vpc_id             = aws_vpc.main.id
  cloud_config_extra          = data.template_file.cloud-config.rendered

  daemon_ssh = "true"
  daemon_tls = "false"

  gpu = var.gpu
  gpu_per_node_count = var.gpu_per_node_count

  store_join_tokens_as_tags   = true
  cloudwatch_logs             = false

  managers = var.manager_instances
  instance_type_manager = var.manager_instance_type 

  workers = var.instances
  instance_type_worker = var.worker_instance_type #"t3.micro"

  volume_size = var.volume_size

  additional_security_group_ids = [
    aws_security_group.exposed.id,
  ]

  k3s_git_commit = var.k3s_git_commit
}

