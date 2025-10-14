# SSL Monitor Pro - Production Terraform Configuration
# Provider: Hetzner Cloud (EU-based, GDPR compliant)

terraform {
  required_version = ">= 1.0"
  required_providers {
    hcloud = {
      source  = "hetznercloud/hcloud"
      version = "~> 1.42"
    }
  }
  
  # Backend configuration for state management
  backend "s3" {
    bucket = "ssl-monitor-terraform-state"
    key    = "production/terraform.tfstate"
    region = "eu-central-1"
  }
}

# Configure Hetzner Cloud Provider
provider "hcloud" {
  token = var.hcloud_token
}

# Variables
variable "hcloud_token" {
  description = "Hetzner Cloud API token"
  type        = string
  sensitive   = true
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "region" {
  description = "Hetzner region"
  type        = string
  default     = "nbg1" # Nuremberg, Germany
}

variable "domain" {
  description = "Primary domain"
  type        = string
  default     = "sslmonitor.pro"
}

# Data sources
data "hcloud_ssh_keys" "default" {
  with_selector = "environment=${var.environment}"
}

data "hcloud_locations" "all" {}

# VPC Network
resource "hcloud_network" "ssl_monitor" {
  name     = "ssl-monitor-${var.environment}"
  ip_range = "10.0.0.0/16"
}

resource "hcloud_network_subnet" "ssl_monitor" {
  network_id   = hcloud_network.ssl_monitor.id
  type         = "cloud"
  network_zone = "eu-central"
  ip_range     = "10.0.1.0/24"
}

# Security Groups
resource "hcloud_firewall" "ssl_monitor" {
  name = "ssl-monitor-${var.environment}"

  rule {
    direction = "in"
    port      = "22"
    protocol  = "tcp"
    source_ips = ["0.0.0.0/0"]
  }

  rule {
    direction = "in"
    port      = "80"
    protocol  = "tcp"
    source_ips = ["0.0.0.0/0"]
  }

  rule {
    direction = "in"
    port      = "443"
    protocol  = "tcp"
    source_ips = ["0.0.0.0/0"]
  }

  rule {
    direction = "in"
    port      = "3000"
    protocol  = "tcp"
    source_ips = ["10.0.0.0/16"] # Grafana only internal
  }

  rule {
    direction = "in"
    port      = "9090"
    protocol  = "tcp"
    source_ips = ["10.0.0.0/16"] # Prometheus only internal
  }
}

# Load Balancer
resource "hcloud_load_balancer" "ssl_monitor" {
  name     = "ssl-monitor-lb-${var.environment}"
  location = var.region
  load_balancer_type = "lb11"
  
  network_zone = "eu-central"
  
  labels = {
    environment = var.environment
    service     = "ssl-monitor"
  }
}

resource "hcloud_load_balancer_network" "ssl_monitor_lb" {
  load_balancer_id = hcloud_load_balancer.ssl_monitor.id
  network_id       = hcloud_network.ssl_monitor.id
}

# Primary Application Server
resource "hcloud_server" "ssl_monitor_primary" {
  name        = "ssl-monitor-primary-${var.environment}"
  image       = "ubuntu-22.04"
  server_type = "cx21" # 2 vCPU, 4GB RAM, 40GB SSD
  
  location = var.region
  ssh_keys = data.hcloud_ssh_keys.default.ssh_key_ids
  
  firewall_ids = [hcloud_firewall.ssl_monitor.id]
  
  network {
    network_id = hcloud_network.ssl_monitor.id
    ip         = "10.0.1.10"
  }
  
  labels = {
    environment = var.environment
    service     = "ssl-monitor"
    role        = "primary"
  }
  
  user_data = templatefile("${path.module}/scripts/primary-server.sh", {
    environment = var.environment
    domain      = var.domain
  })
}

# Standby Application Server (for HA)
resource "hcloud_server" "ssl_monitor_standby" {
  name        = "ssl-monitor-standby-${var.environment}"
  image       = "ubuntu-22.04"
  server_type = "cx21"
  
  location = var.region
  ssh_keys = data.hcloud_ssh_keys.default.ssh_key_ids
  
  firewall_ids = [hcloud_firewall.ssl_monitor.id]
  
  network {
    network_id = hcloud_network.ssl_monitor.id
    ip         = "10.0.1.11"
  }
  
  labels = {
    environment = var.environment
    service     = "ssl-monitor"
    role        = "standby"
  }
  
  user_data = templatefile("${path.module}/scripts/standby-server.sh", {
    environment = var.environment
    domain      = var.domain
  })
}

# Monitoring Server
resource "hcloud_server" "ssl_monitor_monitoring" {
  name        = "ssl-monitor-monitoring-${var.environment}"
  image       = "ubuntu-22.04"
  server_type = "cx21"
  
  location = var.region
  ssh_keys = data.hcloud_ssh_keys.default.ssh_key_ids
  
  firewall_ids = [hcloud_firewall.ssl_monitor.id]
  
  network {
    network_id = hcloud_network.ssl_monitor.id
    ip         = "10.0.1.20"
  }
  
  labels = {
    environment = var.environment
    service     = "monitoring"
  }
  
  user_data = templatefile("${path.module}/scripts/monitoring-server.sh", {
    environment = var.environment
  })
}

# Managed Database (PostgreSQL)
resource "hcloud_database" "ssl_monitor" {
  name     = "ssl-monitor-db-${var.environment}"
  type     = "db-postgresql-13"
  location = var.region
  
  network_id = hcloud_network.ssl_monitor.id
  
  labels = {
    environment = var.environment
    service     = "ssl-monitor"
  }
}

# Redis for sessions and caching
resource "hcloud_database" "ssl_monitor_redis" {
  name     = "ssl-monitor-redis-${var.environment}"
  type     = "db-redis-7"
  location = var.region
  
  network_id = hcloud_network.ssl_monitor.id
  
  labels = {
    environment = var.environment
    service     = "ssl-monitor"
  }
}

# Load Balancer Targets
resource "hcloud_load_balancer_target" "ssl_monitor_primary" {
  type             = "server"
  load_balancer_id = hcloud_load_balancer.ssl_monitor.id
  server_id        = hcloud_server.ssl_monitor_primary.id
  use_private_ip   = true
}

resource "hcloud_load_balancer_target" "ssl_monitor_standby" {
  type             = "server"
  load_balancer_id = hcloud_load_balancer.ssl_monitor.id
  server_id        = hcloud_server.ssl_monitor_standby.id
  use_private_ip   = true
}

# Load Balancer Services
resource "hcloud_load_balancer_service" "ssl_monitor_http" {
  load_balancer_id = hcloud_load_balancer.ssl_monitor.id
  protocol         = "http"
  listen_port      = 80
  destination_port = 8000
  
  health_check {
    protocol = "http"
    port     = 8000
    path     = "/health"
    interval = 15
    timeout  = 10
    retries  = 3
  }
}

resource "hcloud_load_balancer_service" "ssl_monitor_https" {
  load_balancer_id = hcloud_load_balancer.ssl_monitor.id
  protocol         = "https"
  listen_port      = 443
  destination_port = 8000
  
  health_check {
    protocol = "https"
    port     = 8000
    path     = "/health"
    interval = 15
    timeout  = 10
    retries  = 3
  }
}

# DNS Records (using Hetzner DNS)
resource "hcloud_primary_ip" "ssl_monitor" {
  name          = "ssl-monitor-ip-${var.environment}"
  type          = "ipv4"
  datacenter    = "${var.region}-1"
  assignee_type = "load_balancer"
  assignee_id   = hcloud_load_balancer.ssl_monitor.id
  
  labels = {
    environment = var.environment
    service     = "ssl-monitor"
  }
}

# Outputs
output "load_balancer_ip" {
  value = hcloud_load_balancer.ssl_monitor.ipv4
}

output "primary_server_ip" {
  value = hcloud_server.ssl_monitor_primary.ipv4_address
}

output "standby_server_ip" {
  value = hcloud_server.ssl_monitor_standby.ipv4_address
}

output "monitoring_server_ip" {
  value = hcloud_server.ssl_monitor_monitoring.ipv4_address
}

output "database_connection_string" {
  value = "postgresql://${hcloud_database.ssl_monitor.user}:${hcloud_database.ssl_monitor.password}@${hcloud_database.ssl_monitor.private_network}:${hcloud_database.ssl_monitor.port}/${hcloud_database.ssl_monitor.name}"
  sensitive = true
}

output "redis_connection_string" {
  value = "redis://${hcloud_database.ssl_monitor_redis.private_network}:${hcloud_database.ssl_monitor_redis.port}"
  sensitive = true
}
