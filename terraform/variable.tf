variable "s3_bucket" {
  description = "Bucket name for S3"
  type        = string
  default     = "basanredditbucket"
}

variable "db_password" {
  description = "Password for Redshift"
  type = string
  default = ""
}
