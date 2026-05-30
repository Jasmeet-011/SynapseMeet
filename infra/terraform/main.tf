terraform {
  required_version = ">= 1.7.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  backend "gcs" {
    bucket = "synapsemeet-tfstate"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# ─── Cloud Run — AI Worker ────────────────────────────────────────────────────

resource "google_cloud_run_v2_service" "ai_worker" {
  name     = "synapsemeet-ai-worker"
  location = var.region

  template {
    containers {
      image = "gcr.io/${var.project_id}/synapsemeet-backend:latest"
      command = ["celery"]
      args    = ["-A", "app.workers.celery_app", "worker", "--loglevel=info"]

      resources {
        limits = {
          cpu    = "2"
          memory = "4Gi"
        }
      }

      env {
        name  = "DATABASE_URL"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.db_url.secret_id
            version = "latest"
          }
        }
      }
    }

    scaling {
      min_instance_count = 1
      max_instance_count = 10
    }
  }
}

# ─── GCS Bucket — Audio Archive ───────────────────────────────────────────────

resource "google_storage_bucket" "audio_archive" {
  name          = "${var.project_id}-synapsemeet-audio"
  location      = var.region
  force_destroy = false

  lifecycle_rule {
    condition { age = 365 }
    action { type = "Delete" }
  }

  uniform_bucket_level_access = true
}

# ─── Secret Manager ───────────────────────────────────────────────────────────

resource "google_secret_manager_secret" "db_url" {
  secret_id = "synapsemeet-db-url"
  replication { auto {} }
}
