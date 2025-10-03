terraform {
  required_version = ">= 1.2.0"
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

variable "prefix" {
  description = "Short prefix applied to all resources"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "eastus"
}

locals {
  workspace_name          = "${var.prefix}-mlw"
  key_vault_name          = "${var.prefix}kv"
  storage_account_name    = lower(replace("${var.prefix}store", "-", ""))
  container_registry_name = "${var.prefix}acr"
  insights_name           = "${var.prefix}-appi"
}

resource "azurerm_resource_group" "mlops" {
  name     = "${var.prefix}-rg"
  location = var.location
}

resource "azurerm_key_vault" "mlops" {
  name                = local.key_vault_name
  location            = azurerm_resource_group.mlops.location
  resource_group_name = azurerm_resource_group.mlops.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "standard"
  purge_protection_enabled = true
  soft_delete_retention_days = 90
}

data "azurerm_client_config" "current" {}

resource "azurerm_storage_account" "mlops" {
  name                     = local.storage_account_name
  resource_group_name      = azurerm_resource_group.mlops.name
  location                 = azurerm_resource_group.mlops.location
  account_tier             = "Standard"
  account_replication_type = "GRS"
  allow_blob_public_access = false
  min_tls_version          = "TLS1_2"
}

resource "azurerm_container_registry" "mlops" {
  name                = local.container_registry_name
  resource_group_name = azurerm_resource_group.mlops.name
  location            = azurerm_resource_group.mlops.location
  sku                 = "Premium"
  admin_enabled       = false

  trust_policy {
    enabled = true
    type    = "Notary"
  }

  quarantine_policy_enabled = true
}

resource "azurerm_application_insights" "mlops" {
  name                = local.insights_name
  location            = azurerm_resource_group.mlops.location
  resource_group_name = azurerm_resource_group.mlops.name
  application_type    = "web"
}

resource "azurerm_machine_learning_workspace" "mlops" {
  name                    = local.workspace_name
  location                = azurerm_resource_group.mlops.location
  resource_group_name     = azurerm_resource_group.mlops.name
  application_insights_id = azurerm_application_insights.mlops.id
  key_vault_id            = azurerm_key_vault.mlops.id
  storage_account_id      = azurerm_storage_account.mlops.id
  container_registry_id   = azurerm_container_registry.mlops.id
  public_network_access   = "Disabled"

  identity {
    type = "SystemAssigned"
  }

  encryption {
    status = "Enabled"
    key_vault_key_id = "https://${local.key_vault_name}.vault.azure.net/keys/mlops-cmk"
  }
}

output "workspace_id" {
  value = azurerm_machine_learning_workspace.mlops.id
}
