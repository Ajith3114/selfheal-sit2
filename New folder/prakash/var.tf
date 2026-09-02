variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
}

variable "vpc_name" {
  description = "Name of the VPC"
  type        = string
}

variable "public_subnet_cidr" {
  description = "CIDR block for public subnet"
  type        = string
}

variable "public_subnet_name" {
  description = "Name of public subnet"
  type        = string
}

variable "public_subnet_az" {
  description = "Availability Zone for public subnet"
  type        = string
}

variable "private_subnet_cidr" {
  description = "CIDR block for private subnet"
  type        = string
}

variable "private_subnet_name" {
  description = "Name of private subnet"
  type        = string
}

variable "private_subnet_az" {
  description = "Availability Zone for private subnet"
  type        = string
}