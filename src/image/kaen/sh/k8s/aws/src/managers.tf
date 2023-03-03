data "template_file" "init_k3s_manager" {
  count    = var.managers
  template = file("${path.module}/init_k3s_manager.sh")

  vars = {

    k3s_token           = random_string.k3s_token.id
    k3s_kubeconfig_mode = var.k3s_kubeconfig_mode
    k3s_git_commit      = var.k3s_git_commit    

    gpu                 = var.gpu

    # daemon_count   = var.daemon_count
    # daemon_tls     = var.daemon_tls ? "True" : "False"
    instance_index = count.index
    # private_key    = count.index < var.daemon_count ? element(concat(var.daemon_private_key_pems, [""]), count.index) : ""
    # cert           = count.index < var.daemon_count ? element(concat(var.daemon_cert_pems, [""]), count.index) : ""
    # ca_cert        = var.daemon_ca_cert_pem
  }
}

data "template_file" "init_manager" {
  count    = var.managers
  template = file("${path.module}/init_node.py")

  vars = {
    s3_bucket                 = var.store_join_tokens_as_tags ? "" : aws_s3_bucket.terraform[0].bucket
    region_name               = data.aws_region.current.name
    instance_index            = count.index
    vpc_name                  = local.dns_name
    cloudwatch_log_group      = var.cloudwatch_logs ? (var.cloudwatch_single_log_group ? local.dns_name : aws_cloudwatch_log_group.managers[count.index].name) : ""
    group                     = "manager"
    store_join_tokens_as_tags = var.store_join_tokens_as_tags ? 1 : 0
    ssh_authorization_method  = var.ssh_authorization_method
    k3s_join_token            = random_string.k3s_token.id
  }
}

data "cloudinit_config" "managers" {
  count         = var.managers
  gzip          = "true"
  base64_encode = "true"

  part {
    content = file("${path.module}/common.cloud-config")
  }

  part {
    filename     = "extra.cloud-config"
    content      = var.cloud_config_extra
    content_type = "text/cloud-config"
    merge_type   = var.cloud_config_extra_merge_type
  }

  part {
    filename     = "init_daemon.py"
    content      = data.template_file.init_daemon[count.index].rendered
    content_type = "text/x-shellscript"
  }

  part {
    filename     = "init_node.py"
    content      = data.template_file.init_manager[count.index].rendered
    content_type = "text/x-shellscript"
  }

  part {
    filename     = "init_k3s_manager.sh"
    content      = data.template_file.init_k3s_manager[count.index].rendered
    content_type = "text/x-shellscript"
  }

  part {
    filename     = "extra.sh"
    content      = var.cloud_config_extra_script
    content_type = "text/x-shellscript"
  }
}

resource "aws_instance" "managers" {
  depends_on = [
    aws_s3_bucket.terraform,
    aws_cloudwatch_log_group.managers,
    aws_cloudwatch_log_group.main,
  ]

  count         = var.managers
  ami           = data.aws_ami.base_ami.id
  instance_type = local.instance_type_manager
  subnet_id     = aws_subnet.managers[count.index % length(data.aws_availability_zones.azs)].id
  private_ip = cidrhost(
    aws_subnet.managers[count.index % length(data.aws_availability_zones.azs)].cidr_block,
    10 + count.index,
  )


  # workaround as noted by https://github.com/hashicorp/terraform/issues/12453#issuecomment-284273475
  vpc_security_group_ids = split(
    ",",
    count.index < var.daemon_count ? join(",", local.daemon_security_group_ids) : join(",", local.security_group_ids),
  )

  iam_instance_profile = aws_iam_instance_profile.ec2.name
  user_data_base64     = data.cloudinit_config.managers[count.index].rendered
  key_name             = var.key_name

  tags = {
    Name             = "${var.name} manager ${count.index}"
    Role             = "manager"
    ManagerJoinToken = ""
    WorkerJoinToken  = ""
    K3sJoinToken     = ""
  }

  root_block_device {
    volume_size = var.volume_size
  }

  ebs_block_device {
    device_name = "xvdf"
    volume_size = var.swap_size
  }

  lifecycle {
    ignore_changes = [
      ami,
      ebs_block_device,
      user_data_base64,
      subnet_id,
      private_ip,
      availability_zone,
      tags["ManagerJoinToken"],
      tags["WorkerJoinToken"],
      tags["K3sJoinToken"],      
    ]
  }

  credit_specification {
    cpu_credits = "standard"
  }
}

resource "aws_cloudwatch_metric_alarm" "low-cpu-credit-managers" {
  count           = local.burstable_instance_type_manager ? var.managers : 0
  actions_enabled = true
  alarm_actions = flatten([
    aws_sns_topic.alarms.arn,
    var.additional_alarm_actions,
  ])
  alarm_name          = "${local.dns_name}-low-cpu-credit-manager${count.index}"
  comparison_operator = "LessThanThreshold"
  datapoints_to_alarm = 1
  dimensions = {
    "InstanceId" = aws_instance.managers[count.index].id
  }
  evaluation_periods        = 1
  insufficient_data_actions = []
  metric_name               = "CPUCreditBalance"
  namespace                 = "AWS/EC2"
  ok_actions                = []
  period                    = 300
  statistic                 = "Average"
  tags                      = {}
  threshold                 = 75
  treat_missing_data        = "missing"
}

resource "aws_cloudwatch_metric_alarm" "high-cpu-managers" {
  count           = var.managers
  actions_enabled = true
  alarm_actions = [
    aws_sns_topic.alarms.arn,
  ]
  alarm_name          = "${local.dns_name}-high-cpu-manager${count.index}"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  datapoints_to_alarm = 5
  dimensions = {
    "InstanceId" = aws_instance.managers[count.index].id
  }
  evaluation_periods        = 5
  insufficient_data_actions = []
  metric_name               = "CPUUtilization"
  namespace                 = "AWS/EC2"
  ok_actions                = []
  period                    = 60
  statistic                 = "Average"
  tags                      = {}
  threshold                 = 85
}

resource "aws_cloudwatch_log_group" "managers" {
  count             = (var.cloudwatch_logs && ! var.cloudwatch_single_log_group) ? var.managers : 0
  name              = "${local.dns_name}-manager${count.index}"
  retention_in_days = var.cloudwatch_retention_in_days

  tags = {
    Environment = var.name
    Name        = "${var.name} manager ${count.index}"
    Node        = "${local.dns_name}-manager${count.index}"
  }
}
