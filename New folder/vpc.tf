module "vpc" {
  source = "./prakash/"

  vpc_cidr = "10.0.0.0/16"
  vpc_name = "my-vpc"

  public_subnet_cidr = "10.0.1.0/24"
  public_subnet_name = "public-subnet"
  public_subnet_az   = "ap-south-1a"

  private_subnet_cidr = "10.0.2.0/24"
  private_subnet_name = "private-subnet"
  private_subnet_az   = "ap-south-1a"
}


module "ec2_instance" {
  source  = "terraform-aws-modules/ec2-instance/aws"

  name = "single-instance"

  instance_type = "t3.micro"
  ami          = "ami-081b0a6eac00b4f53"
  key_name      = "iy-nvir"
  monitoring    = true
  subnet_id     = module.vpc.public_subnet_id

  tags = {
    Terraform   = "true"
    Environment = "dev"
  }
}



# variable "aws_profile" {
#     default = "class"
# }