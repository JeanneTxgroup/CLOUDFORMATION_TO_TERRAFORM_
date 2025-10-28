provider "aws" {
  region = "eu-west-1" # ou la région de votre choix
}

data "aws_region" "current" {}
data "aws_caller_identity" "current" {}
data "aws_availability_zones" "available" {}

locals {
  # Conditions converties de CloudFormation
  create_tgw_attachment           = var.connect_to_central_router == "yes"
  create_intra_vpc                = !contains(["S", "S2"], var.vpc_size)
  create_scalable_platform_subnets = var.scalable_platform_subnets == "yes"
  create_per_az_nat_gateways      = var.per_az_nat_gateways == "yes"
  associate_mediait_resolver_rule = var.use_internal_dns == "yes"
  create_s3_vpc_endpoint          = var.use_s3_vpc_endpoint == "yes"

  # Mappings de CloudFormation
  region_map = {
    "eu-west-1" = {
      transit_gateway_id = "tgw-009829a53d1bc69b8"
    }
    "eu-central-1" = {
      transit_gateway_id = "tgw-09b008f794dcaf554"
    }
  }

  transit_gateway_id = lookup(local.region_map, data.aws_region.current.name, null).transit_gateway_id
  
  # Logique pour remplacer la Custom Resource VpcIpAddresses
  # Ceci est une approximation. Adaptez les CIDRs de base si nécessaire.
  vpc_cidrs = {
    "S"   = "10.0.0.0/22", "S2"  = "10.0.4.0/22",
    "M"   = "10.0.8.0/21", "M2"  = "10.0.16.0/21",
    "L"   = "10.0.32.0/20", "L2"  = "10.0.48.0/20",
    "XL"  = "10.0.64.0/19", "XL2" = "10.0.96.0/19",
  }
  vpc_cidr_block = local.vpc_cidrs[var.vpc_size]
  
  # Calcul des CIDRs des subnets
  # Les paramètres de cidrsubnet sont (base_cidr, new_bits, net_num)
  public_subnet_cidrs = [
    for i in range(3) : cidrsubnet(local.vpc_cidr_block, 3, i) // Crée 3 subnets /25
  ]
  private_subnet_cidrs = [
    for i in range(3) : cidrsubnet(local.vpc_cidr_block, 3, i + 3) // Crée 3 subnets /25
  ]
  intra_vpc_subnet_cidrs = [
    for i in range(3) : cidrsubnet(local.vpc_cidr_block, 3, i + 6) // Crée 3 subnets /25
  ]
  scalable_platform_subnet_cidrs = [
    "10.200.0.0/20",
    "10.200.16.0/20",
    "10.200.32.0/20",
  ]
  
  # Routes vers le Transit Gateway
  tgw_destination_cidrs = ["145.234.0.0/16", "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]
}

# --- VPC et Réseau de Base ---

resource "aws_vpc" "main" {
  cidr_block           = local.vpc_cidr_block
  enable_dns_support   = true
  enable_dns_hostnames = true
  
  tags = merge(var.tags, {
    Name = "SC-VPC"
  })
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(var.tags, {
    Name = "SC-VPC-InternetGateway"
  })
}

# --- Subnets ---

resource "aws_subnet" "public" {
  count                   = 3
  vpc_id                  = aws_vpc.main.id
  cidr_block              = local.public_subnet_cidrs[count.index]
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = merge(var.tags, {
    Name = "SC-VPC-PublicSubnet${count.index + 1}"
  })
}

resource "aws_subnet" "private" {
  count             = 3
  vpc_id            = aws_vpc.main.id
  cidr_block        = local.private_subnet_cidrs[count.index]
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = merge(var.tags, {
    Name = "SC-VPC-PrivateSubnet${count.index + 1}"
  })
}

resource "aws_subnet" "intra_vpc" {
  count             = local.create_intra_vpc ? 3 : 0
  vpc_id            = aws_vpc.main.id
  cidr_block        = local.intra_vpc_subnet_cidrs[count.index]
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = merge(var.tags, {
    Name = "SC-VPC-IntraVpcSubnet${count.index + 1}"
  })
}

resource "aws_vpc_ipv4_cidr_block_association" "scalable" {
  count     = local.create_scalable_platform_subnets ? 1 : 0
  vpc_id    = aws_vpc.main.id
  cidr_block = "10.200.0.0/16"
}

resource "aws_subnet" "scalable_platform" {
  count             = local.create_scalable_platform_subnets ? 3 : 0
  vpc_id            = aws_vpc.main.id
  cidr_block        = local.scalable_platform_subnet_cidrs[count.index]
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  depends_on = [aws_vpc_ipv4_cidr_block_association.scalable]

  tags = merge(var.tags, {
    Name = "SC-VPC-ScalablePlatformSubnet${count.index + 1}"
  })
}

# --- NAT Gateways ---

resource "aws_eip" "nat" {
  count  = local.create_per_az_nat_gateways ? 3 : 1
  domain = "vpc"
  
  tags = merge(var.tags, {
    Name = "SC-VPC-NatEIP-${count.index + 1}"
  })
}

resource "aws_nat_gateway" "main" {
  count         = local.create_per_az_nat_gateways ? 3 : 1
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = merge(var.tags, {
    Name = "SC-VPC-NatGateway${count.index + 1}"
  })
  
  depends_on = [aws_internet_gateway.main]
}

# --- Tables de Routage et Routes ---

# Table de routage publique
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  
  route {
    cidr_block = "145.234.240.0/22"
    gateway_id = aws_internet_gateway.main.id
  }
  
  dynamic "route" {
    for_each = local.create_tgw_attachment ? local.tgw_destination_cidrs : []
    content {
      cidr_block         = route.value
      transit_gateway_id = local.transit_gateway_id
    }
  }

  tags = merge(var.tags, { Name = "SC-VPC-Public" })
}

# Tables de routage privées (une par AZ si HA, sinon une seule)
resource "aws_route_table" "private" {
  count  = local.create_per_az_nat_gateways ? 3 : 1
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[count.index].id
  }
  
  route {
    cidr_block     = "145.234.240.0/22"
    nat_gateway_id = aws_nat_gateway.main[count.index].id
  }

  dynamic "route" {
    for_each = local.create_tgw_attachment ? local.tgw_destination_cidrs : []
    content {
      cidr_block         = route.value
      transit_gateway_id = local.transit_gateway_id
    }
  }

  tags = merge(var.tags, { Name = "SC-VPC-Private${count.index + 1}" })
}

# Tables de routage IntraVPC
resource "aws_route_table" "intra_vpc" {
  count  = local.create_intra_vpc ? (local.create_per_az_nat_gateways ? 3 : 1) : 0
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[count.index].id
  }

  tags = merge(var.tags, { Name = "SC-VPC-IntraVpc${count.index + 1}" })
}

# --- Associations de tables de routage ---

resource "aws_route_table_association" "public" {
  count          = 3
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private" {
  count          = 3
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = local.create_per_az_nat_gateways ? aws_route_table.private[count.index].id : aws_route_table.private[0].id
}

resource "aws_route_table_association" "intra_vpc" {
  count          = local.create_intra_vpc ? 3 : 0
  subnet_id      = aws_subnet.intra_vpc[count.index].id
  route_table_id = local.create_per_az_nat_gateways ? aws_route_table.intra_vpc[count.index].id : aws_route_table.intra_vpc[0].id
}

resource "aws_route_table_association" "scalable_platform" {
  count          = local.create_scalable_platform_subnets ? 3 : 0
  subnet_id      = aws_subnet.scalable_platform[count.index].id
  route_table_id = local.create_per_az_nat_gateways ? aws_route_table.private[count.index].id : aws_route_table.private[0].id
}

# --- Transit Gateway ---

resource "aws_ec2_transit_gateway_vpc_attachment" "main" {
  count              = local.create_tgw_attachment ? 1 : 0
  subnet_ids         = aws_subnet.private[*].id
  transit_gateway_id = local.transit_gateway_id
  vpc_id             = aws_vpc.main.id

  tags = merge(var.tags, {
    Name = "${data.aws_caller_identity.current.account_id}-AttachToTransitGateway"
  })
}

# NOTE: La ressource personnalisée 'TGWattachementCustomResource' qui publie sur un SNS
# n'est pas traduite ici. Si vous avez besoin d'exécuter une action après l'attachement,
# vous pourriez utiliser un `null_resource` avec un `local-exec` provisioner pour appeler un script.

# --- Services Additionnels ---

resource "aws_route53_resolver_rule_association" "media_it" {
  count            = local.associate_mediait_resolver_rule ? 1 : 0
  resolver_rule_id = "rslvr-rr-19d7f32e7a0a41959" # ID de la règle hardcodé
  vpc_id           = aws_vpc.main.id
  name             = "MediaItDnsRuleAssociation"
}

resource "aws_vpc_endpoint" "s3" {
  count           = local.create_s3_vpc_endpoint ? 1 : 0
  vpc_id          = aws_vpc.main.id
  service_name    = "com.amazonaws.${data.aws_region.current.name}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids = aws_route_table.private[*].id
}