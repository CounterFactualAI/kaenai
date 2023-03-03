provider "aws" {
}

provider "random" {
}

resource "aws_vpc" "main" {
  cidr_block                        = "10.95.0.0/16"
  enable_dns_hostnames              = true
  assign_generated_ipv6_cidr_block  = true
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
}

resource "aws_egress_only_internet_gateway" "ipv6" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "worker ipv6 internet egress"
  }
}

resource "aws_route" "internet_access" {
  route_table_id         = aws_vpc.main.main_route_table_id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.main.id
}

resource "aws_route" "ipv6_internet_access" {
  route_table_id              = aws_vpc.main.main_route_table_id
  destination_ipv6_cidr_block = "::/0"
  gateway_id                  = aws_egress_only_internet_gateway.ipv6.id
}

resource "aws_security_group" "exposed" {
  name   = "exposed"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }
}

