resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true
  instance_tenancy     = "default"

  tags = {
    Name = var.vpc_name
  }
}

# -------------------------
# Internet Gateway
# -------------------------

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id

  tags = {
    Name = "${var.vpc_name}-igw"
  }
}

# -------------------------
# Public Subnet
# -------------------------

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.this.id
  cidr_block              = var.public_subnet_cidr
  availability_zone       = var.public_subnet_az
  map_public_ip_on_launch = true

  tags = {
    Name = var.public_subnet_name
  }
}

# -------------------------
# Private Subnet
# -------------------------

resource "aws_subnet" "private" {
  vpc_id            = aws_vpc.this.id
  cidr_block        = var.private_subnet_cidr
  availability_zone = var.private_subnet_az

  tags = {
    Name = var.private_subnet_name
  }
}

# -------------------------
# Elastic IP for NAT Gateway
# -------------------------

resource "aws_eip" "this" {
  domain = "vpc"

  depends_on = [
    aws_internet_gateway.this
  ]

  tags = {
    Name = "${var.vpc_name}-nat-eip"
  }
}

# -------------------------
# NAT Gateway
# -------------------------

resource "aws_nat_gateway" "this" {
  allocation_id = aws_eip.this.id
  subnet_id     = aws_subnet.public.id

  depends_on = [
    aws_internet_gateway.this
  ]

  tags = {
    Name = "${var.vpc_name}-nat"
  }
}

# -------------------------
# Public Route Table
# -------------------------

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.this.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.this.id
  }

  tags = {
    Name = "${var.vpc_name}-public-rt"
  }
}

# -------------------------
# Private Route Table
# -------------------------

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.this.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.this.id
  }

  tags = {
    Name = "${var.vpc_name}-private-rt"
  }
}

# -------------------------
# Public Route Association
# -------------------------

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# -------------------------
# Private Route Association
# -------------------------

resource "aws_route_table_association" "private" {
  subnet_id      = aws_subnet.private.id
  route_table_id = aws_route_table.private.id
}