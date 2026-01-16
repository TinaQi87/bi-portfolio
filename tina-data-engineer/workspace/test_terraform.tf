terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "ap-southeast-2"  # Sydney region
}

# Simple security group for testing
resource "aws_security_group" "test_sg" {
  name        = "tina-test-sg"
  description = "Test security group created by Terraform"

  ingress {
    description = "SSH"
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

  tags = {
    Name        = "tina-test-sg"
    Environment = "test"
    ManagedBy   = "terraform"
  }
}

output "security_group_id" {
  value       = aws_security_group.test_sg.id
  description = "The ID of the security group"
}

output "security_group_name" {
  value       = aws_security_group.test_sg.name
  description = "The name of the security group"
}
