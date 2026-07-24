terraform {
  required_version = ">= 1.5.0"

  required_providers {
    huaweicloud = {
      source  = "huaweicloud/huaweicloud"
      version = "~> 1.60"
    }
  }

  backend "local" {
    path = "terraform.tfstate"
  }
}

provider "huaweicloud" {
  region = var.region
}

variable "region" {
  description = "Huawei Cloud region"
  type        = string
  default     = "cn-north-4"
}

variable "instance_name" {
  description = "ECS instance name"
  type        = string
  default     = "todo-list-server"
}

variable "flavor_id" {
  description = "ECS flavor ID"
  type        = string
  default     = "s6.large.2"
}

variable "image_id" {
  description = "ECS image ID (Ubuntu 22.04)"
  type        = string
  default     = "a0b1c2d3-e4f5-6789-abcd-ef0123456789"
}

variable "ssh_key_name" {
  description = "SSH key pair name in Huawei Cloud"
  type        = string
  default     = "todo-deploy-key"
}

resource "huaweicloud_vpc_v1" "main" {
  name = "todo-vpc"
  cidr = "192.168.0.0/16"
}

resource "huaweicloud_vpc_subnet_v1" "main" {
  name       = "todo-subnet"
  cidr       = "192.168.1.0/24"
  vpc_id     = huaweicloud_vpc_v1.main.id
  gateway_ip = "192.168.1.1"
}

resource "huaweicloud_networking_secgroup_v2" "main" {
  name        = "todo-security-group"
  description = "Security group for Todo List application"
}

resource "huaweicloud_networking_secgroup_rule_v2" "ssh" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 22
  port_range_max    = 22
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = huaweicloud_networking_secgroup_v2.main.id
}

resource "huaweicloud_networking_secgroup_rule_v2" "http" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 80
  port_range_max    = 80
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = huaweicloud_networking_secgroup_v2.main.id
}

resource "huaweicloud_networking_secgroup_rule_v2" "api" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 8000
  port_range_max    = 8000
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = huaweicloud_networking_secgroup_v2.main.id
}

resource "huaweicloud_compute_instance_v2" "main" {
  name              = var.instance_name
  flavor_id         = var.flavor_id
  image_id          = var.image_id
  key_pair          = var.ssh_key_name
  security_groups   = [huaweicloud_networking_secgroup_v2.main.name]

  network {
    uuid = huaweicloud_vpc_subnet_v1.main.id
  }
}

resource "huaweicloud_compute_eip_associate_v2" "main" {
  public_ip   = huaweicloud_vpc_eip_v1.main.address
  instance_id = huaweicloud_compute_instance_v2.main.id
}

resource "huaweicloud_vpc_eip_v1" "main" {
  publicip {
    type = "5_bgp"
  }
  bandwidth {
    name        = "todo-bandwidth"
    size        = 5
    share_type  = "PER"
    charge_mode = "traffic"
  }
}

output "ecs_public_ip" {
  description = "Public IP of the ECS instance"
  value       = huaweicloud_vpc_eip_v1.main.address
}

output "ecs_instance_id" {
  description = "ECS instance ID"
  value       = huaweicloud_compute_instance_v2.main.id
}