terraform {
  required_version = ">= 1.5.0"

  required_providers {
    huaweicloud = {
      source  = "huaweicloud/huaweicloud"
      version = "~> 1.60"
    }
  }

  backend "local" {
    path = "terraform-cce.tfstate"
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

variable "cluster_name" {
  description = "CCE cluster name"
  type        = string
  default     = "todo-cce-cluster"
}

variable "cluster_version" {
  description = "Kubernetes version for CCE"
  type        = string
  default     = "v1.28"
}

variable "node_flavor_id" {
  description = "ECS flavor for worker nodes"
  type        = string
  default     = "s6.large.2"
}

variable "node_count" {
  description = "Number of worker nodes"
  type        = number
  default     = 2
}

resource "huaweicloud_vpc_v1" "cce" {
  name = "todo-cce-vpc"
  cidr = "10.0.0.0/16"
}

resource "huaweicloud_vpc_subnet_v1" "cce" {
  name       = "todo-cce-subnet"
  cidr       = "10.0.0.0/24"
  vpc_id     = huaweicloud_vpc_v1.cce.id
  gateway_ip = "10.0.0.1"
}

resource "huaweicloud_cce_cluster_v3" "main" {
  name                   = var.cluster_name
  cluster_version        = var.cluster_version
  vpc_id                 = huaweicloud_vpc_v1.cce.id
  subnet_id              = huaweicloud_vpc_subnet_v1.cce.id
  cluster_type           = "VirtualMachine"
  container_network_type = "overlay_l2"
  container_network_cidr = "172.16.0.0/16"
}

resource "huaweicloud_cce_node_v3" "workers" {
  count           = var.node_count
  cluster_id      = huaweicloud_cce_cluster_v3.main.id
  name            = "${var.cluster_name}-node-${count.index + 1}"
  flavor_id       = var.node_flavor_id
  availability_zone = "cn-north-4a"

  root_volume {
    size       = 40
    volumetype = "SSD"
  }

  data_volumes {
    size       = 100
    volumetype = "SSD"
  }
}

resource "huaweicloud_networking_secgroup_v2" "cce" {
  name        = "todo-cce-security-group"
  description = "Security group for CCE cluster"
}

resource "huaweicloud_networking_secgroup_rule_v2" "ssh" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 22
  port_range_max    = 22
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = huaweicloud_networking_secgroup_v2.cce.id
}

resource "huaweicloud_networking_secgroup_rule_v2" "http" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 80
  port_range_max    = 80
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = huaweicloud_networking_secgroup_v2.cce.id
}

resource "huaweicloud_networking_secgroup_rule_v2" "https" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 443
  port_range_max    = 443
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = huaweicloud_networking_secgroup_v2.cce.id
}

resource "huaweicloud_networking_secgroup_rule_v2" "nodeport" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 30000
  port_range_max    = 32767
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = huaweicloud_networking_secgroup_v2.cce.id
}

output "cluster_id" {
  description = "CCE cluster ID"
  value       = huaweicloud_cce_cluster_v3.main.id
}

output "cluster_endpoint" {
  description = "CCE cluster API endpoint"
  value       = huaweicloud_cce_cluster_v3.main.external_endpoint
}

output "worker_node_ips" {
  description = "Worker node private IPs"
  value       = huaweicloud_cce_node_v3.workers[*].private_ip
}