terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "reddit_bucket" {
  bucket = var.s3_bucket
  force_destroy = true
}

resource "aws_s3_bucket_acl" "s3_reddit_bucket_acl" {
  bucket = aws_s3_bucket.reddit_bucket.id
  acl    = "private"
}

resource "aws_redshift_cluster" "redshift" {
  cluster_identifier = "reddit-redshift-cluster"
  skip_final_snapshot = true
  master_username = "reddit"
  master_password = var.db_password
  node_type = "dc2.large"
  cluster_type = "single_node"
  publicly_accessible = "true"
  iam_roles = [ aws_iam_role.redshift_role.arn ]
  vpc_security_group_ids = [ aws_security_group.sg_redshift.id ]
}


resource "aws_security_group" "sg_redshift" {
  name        = "sg_redshift"
  ingress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
  }
  egress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
  }
}


resource "aws_iam_role" "redshift_role" {
  name = "RedShiftLoadRole"
  managed_policy_arns = ["arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"]
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "redshift.amazonaws.com"
        }
      },
    ]
  })
}