resource "aws_eip" "managers" {
  count    = "1"
  instance = module.docker.manager_instance_ids[count.index]
  vpc      = true
}
  
output "manager_ip_address" {
  value = aws_eip.managers[0].public_ip
}

output "manager_ip_addresses" {
  value = aws_eip.managers.*.public_ip
}