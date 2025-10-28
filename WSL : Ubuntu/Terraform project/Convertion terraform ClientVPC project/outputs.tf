# ID of the VPC
output "vpc_id" {
  value       = aws_vpc.SC_VPC.id
  description = "The ID of the VPC"
}

output "public_subnet_cidrs" {
  value = [
    aws_subnet.SC_VPC_PublicSubnet1.cidr_block,
    aws_subnet.SC_VPC_PublicSubnet2.cidr_block,
    aws_subnet.SC_VPC_PublicSubnet3.cidr_block,
  ]
}

output "private_subnet_cidrs" {
  value = [
    aws_subnet.SC_VPC_PrivateSubnet1.cidr_block,
    aws_subnet.SC_VPC_PrivateSubnet2.cidr_block,
    aws_subnet.SC_VPC_PrivateSubnet3.cidr_block,
  ]
}