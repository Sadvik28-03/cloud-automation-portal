provider "aws" {
  region = var.region
}

variable "ami_map" {
  type = map(string)
  default = {
    us-east-1  = "ami-0c02fb55956c7d316"
    eu-west-1  = "ami-0a8e758f5e873d1c1"
    ap-south-1 = "ami-0da59f1af71ea4ad2"
  }
}

resource "aws_instance" "demo" {
  ami           = var.ami_map[var.region]
  instance_type = var.instance_type

  tags = {
    Name = "Cloud-Automation-Instance"
  }
}
