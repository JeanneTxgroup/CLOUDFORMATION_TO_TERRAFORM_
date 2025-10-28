variable "vpc_size" {
  type        = string
  description = "Select the size of your VPC."
  default     = "S"
  validation {
    condition     = contains(["S", "M", "L", "XL", "S2", "M2", "L2", "XL2"], var.vpc_size)
    error_message = "Allowed values are S, M, L, XL, S2, M2, L2, XL2."
  }
}

variable "validation_token" {
  type        = string
  description = "Token required for VPC sizes other than S or S2."
  default     = ""
  sensitive   = true
}

variable "scalable_platform_subnets" {
  type        = string
  description = "Deploy additional private subnets for a scalable platform like Kubernetes (yes/no)."
  default     = "no"
  validation {
    condition     = contains(["yes", "no"], var.scalable_platform_subnets)
    error_message = "Value must be either 'yes' or 'no'."
  }
}

variable "connect_to_central_router" {
  type        = string
  description = "Connect to central router (Transit Gateway) (yes/no)."
  default     = "yes"
  validation {
    condition     = contains(["yes", "no"], var.connect_to_central_router)
    error_message = "Value must be either 'yes' or 'no'."
  }
}

variable "use_internal_dns" {
  type        = string
  description = "Use internal DNS servers for mediait.ch (yes/no)."
  default     = "no"
  validation {
    condition     = contains(["yes", "no"], var.use_internal_dns)
    error_message = "Value must be either 'yes' or 'no'."
  }
}

variable "per_az_nat_gateways" {
  type        = string
  description = "Deploy a highly available NAT gateway (one per AZ) (yes/no)."
  default     = "yes"
  validation {
    condition     = contains(["yes", "no"], var.per_az_nat_gateways)
    error_message = "Value must be either 'yes' or 'no'."
  }
}

variable "use_s3_vpc_endpoint" {
  type        = string
  description = "Create an S3 VPC endpoint (yes/no)."
  default     = "yes"
  validation {
    condition     = contains(["yes", "no"], var.use_s3_vpc_endpoint)
    error_message = "Value must be either 'yes' or 'no'."
  }
}

variable "custom_implementation_tag" {
  type        = string
  description = "Custom ID for specific implementation, if any."
  default     = ""
}

variable "tags" {
  type        = map(string)
  description = "A map of tags to add to all resources."
  default     = {}
}