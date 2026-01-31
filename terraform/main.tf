provider "aws" {
  region = var.region
}

variable "ami_map" {
  type = map(string)
  default = {
    us-east-1  = "ami-0c02fb55956c7d316"
    ap-south-1 = "ami-0f5ee92e2d63afc18"
    us-west-2  = "ami-03f65b8614a860c29"
  }
}

resource "aws_instance" "demo" {
  ami           = var.ami_map[var.region]
  instance_type = var.instance_type

  tags = {
    Name = "Cloud-Automation-Instance"
  }
}
