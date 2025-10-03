terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.90"
    }
  }
}

provider "azurerm" {
  features {}
}

variable "workspace_name" {
  type        = string
  description = "Log Analytics workspace name"
}

variable "resource_group_name" {
  type        = string
  description = "Resource group name"
}

resource "azurerm_sentinel_automation_rule" "alert_enrichment" {
  name                = "ai-security-auto-enrich"
  log_analytics_workspace_id = data.azurerm_log_analytics_workspace.workspace.id
  order               = 1
  display_name        = "Enrich AI Security Alerts"
  condition_json      = jsonencode({
    operator = "AND",
    children = [
      {
        operator = "Contains",
        property = "IncidentTitle",
        value = "AI Security"
      }
    ]
  })
  actions_json = jsonencode([
    {
      order = 1,
      actionType = "ModifyProperties",
      actionConfiguration = {
        Classification       = "TruePositive",
        ClassificationReason  = "SuspiciousActivity"
      }
    }
  ])
}

data "azurerm_log_analytics_workspace" "workspace" {
  name                = var.workspace_name
  resource_group_name = var.resource_group_name
}
