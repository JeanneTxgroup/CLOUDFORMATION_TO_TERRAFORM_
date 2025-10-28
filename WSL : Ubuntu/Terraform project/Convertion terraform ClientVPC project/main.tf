terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "eu-west-1"
}

resource "aws_sns_topic" "vpc_ip_addresses_topic" {
  # tu peux omettre les arguments optionnels ou définir les propriétés que tu veux gérer
  name = "VpcIpAddressesCustomResource"
}


resource "aws_vpc" "SC_VPC" {
  cidr_block                           = "10.130.35.0/24"
  tags = {
    Description = "Géré par Terraform"
    Name        = "SC-VPC"
  }
}

resource "aws_subnet" "SC_VPC_PrivateSubnet1" {
  cidr_block                                     = "10.130.35.0/26"
  map_public_ip_on_launch                        = "false"
  vpc_id = aws_vpc.SC_VPC.id
  tags = {
    Name = "SC-VPC-PrivateSubnet1"
  }
}

resource "aws_subnet" "SC_VPC_PrivateSubnet2" {
  cidr_block                                     = "10.130.35.64/26"
  map_public_ip_on_launch                        = "false"
  vpc_id = aws_vpc.SC_VPC.id
  tags = {
    Name = "SC-VPC-PrivateSubnet2"
  }
}

resource "aws_subnet" "SC_VPC_PrivateSubnet3" {
  cidr_block                                     = "10.130.35.128/26"
  map_public_ip_on_launch                        = "false"
  vpc_id = aws_vpc.SC_VPC.id
  tags = {
    Name = "SC-VPC-PrivateSubnet3"
  }
}

resource "aws_subnet" "SC_VPC_PublicSubnet1" {
  cidr_block                                     = "10.130.35.192/28"
  map_public_ip_on_launch                        = "true"
  vpc_id = aws_vpc.SC_VPC.id
  tags = {
    Name = "SC-VPC-PublicSubnet1"
  }
}

resource "aws_subnet" "SC_VPC_PublicSubnet2" {
  cidr_block                                     = "10.130.35.208/28"
  map_public_ip_on_launch                        = "true"
  vpc_id = aws_vpc.SC_VPC.id
  tags = {
    Name = "SC-VPC-PublicSubnet2"
  }
}

resource "aws_subnet" "SC_VPC_PublicSubnet3" {
  cidr_block                                     = "10.130.35.224/28"
  map_public_ip_on_launch                        = "true"
  vpc_id = aws_vpc.SC_VPC.id
  tags = {
    Name = "SC-VPC-PublicSubnet3"
  }
}
resource "aws_internet_gateway" "SC_VPC_InternetGateway" {
  tags = {
    Name = "SC-VPC-InternetGateway"
  }
  vpc_id = aws_vpc.SC_VPC.id
}

resource "aws_ec2_transit_gateway" "TransitGateway" {
  auto_accept_shared_attachments     = "enable"
  default_route_table_association    = "disable"
  default_route_table_propagation    = "disable"
  description                        = "Tgw Route Integration"
}


resource "aws_eip" "EIP_Instance1" {
    domain               = "vpc"
}

resource "aws_eip" "EIP_Instance2" {
    domain               = "vpc"
}

resource "aws_eip" "EIP_Instance3" {
    domain               = "vpc"
}

