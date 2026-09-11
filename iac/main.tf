terraform {
  required_version = ">= 1.9"

  required_providers {
    render = {
      source  = "render-oss/render"
      version = "~> 1.7"
    }
  }
}

provider "render" {
  api_key  = var.render_api_key
  owner_id = var.render_owner_id
}

# --- Variables ---------------------------------------------------------------

variable "render_api_key" {
  type      = string
  sensitive = true
}

variable "render_owner_id" {
  type = string
}

variable "region" {
  type    = string
  default = "frankfurt"
}

variable "environment" {
  type = string

  validation {
    condition     = contains(["dev", "prod"], var.environment)
    error_message = "environment doit valoir dev ou prod."
  }
}

variable "image_url" {
  type    = string
  default = "ghcr.io/a-helkias/le-bon-coin/api"
}

locals {
  name = "le-bon-coin-${var.environment}"
}

# --- Base de données ----------------------------------------------------------

resource "render_postgres" "db" {
  name          = "${local.name}-db"
  plan          = "free"
  region        = var.region
  version       = "16"
  database_name = "le_bon_coin"
  database_user = "app"
}

# --- Déploiement --------------------------------------------------------------

resource "render_web_service" "app" {
  name              = local.name
  plan              = "free"
  region            = var.region
  health_check_path = "/health"

  runtime_source = {
    image = {
      image_url = var.image_url
      tag       = var.environment
    }
  }

  env_vars = {
    DATABASE_URL = {
      value = replace(
        render_postgres.db.connection_info.internal_connection_string,
        "postgresql://",
        "postgresql+asyncpg://",
      )
    }
    CORS_ORIGINS = {
      value = "[]"
    }
  }
}

# --- Sorties ------------------------------------------------------------------

output "url" {
  value = render_web_service.app.url
}

output "service_name" {
  value = local.name
}
