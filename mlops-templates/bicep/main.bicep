// Deploy secure Azure ML workspace with supporting resources
param location string = resourceGroup().location
param workspaceName string
param keyVaultName string
param storageAccountName string
param appInsightsName string
param containerRegistryName string

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    enabledForTemplateDeployment: true
    enableSoftDelete: true
    enablePurgeProtection: true
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    accessPolicies: []
  }
}

resource storage 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_GRS'
  }
  properties: {
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
  }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    Flow_Type: 'Bluefield'
    Request_Source: 'AzureTemplate'
  }
}

resource registry 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' = {
  name: containerRegistryName
  location: location
  sku: {
    name: 'Premium'
  }
  properties: {
    adminUserEnabled: false
    policies: {
      exportPolicy: {
        status: 'disabled'
      }
      quarantinePolicy: {
        status: 'enabled'
      }
      trustPolicy: {
        status: 'enabled'
        type: 'Notary'
      }
    }
  }
}

resource workspace 'Microsoft.MachineLearningServices/workspaces@2023-04-01' = {
  name: workspaceName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    containerRegistry: registry.id
    keyVault: keyVault.id
    storageAccount: storage.id
    applicationInsights: appInsights.id
    encryption: {
      status: 'Enabled'
      keyVaultProperties: {
        keyIdentifier: 'https://${keyVaultName}.vault.azure.net/keys/mlops-cmk'
      }
    }
    publicNetworkAccess: 'Disabled'
    sharedPrivateLinkResources: []
    managedVirtualNetwork: {
      isolationMode: 'AllowOnlyApprovedOutbound'
    }
  }
}

output workspaceId string = workspace.id
