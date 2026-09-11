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

# Le plan gratuit Render n'autorise qu'une seule base par compte. Renseigner
# cette variable fait réutiliser une base existante au lieu d'en créer une.
variable "database_url" {
  type      = string
  default   = ""
  sensitive = true
}

# Tag déployé à la création du service. Ensuite, c'est la CI qui décide.
variable "image_tag" {
  type    = string
  default = ""
}

locals {
  name         = "le-bon-coin-${var.environment}"
  image_tag    = var.image_tag != "" ? var.image_tag : var.environment
  creates_db   = var.database_url == ""
  database_url = local.creates_db ? replace(render_postgres.db[0].connection_info.internal_connection_string, "postgresql://", "postgresql+asyncpg://") : var.database_url
}

# --- Base de données ----------------------------------------------------------

resource "render_postgres" "db" {
  count = local.creates_db ? 1 : 0

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
      tag       = local.image_tag
    }
  }

  env_vars = {
    DATABASE_URL = {
      value = local.database_url
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
