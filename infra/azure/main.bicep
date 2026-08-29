@description('Deployment region')
param location string = resourceGroup().location

@description('Short unique suffix')
param suffix string = uniqueString(resourceGroup().id)

var tags = {
  project: 'CompoundCloud AI Delivery Fabric'
  purpose: 'architecture-benchmark-evidence'
  managedBy: 'bicep'
  website: 'a2zsoc.com'
}

resource logs 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: 'ccadf-law-${suffix}'
  location: location
  tags: tags
  properties: {
    retentionInDays: 30
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
    sku: {
      name: 'PerGB2018'
    }
  }
}

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: 'ccadf${suffix}'
  location: location
  tags: tags
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    allowBlobPublicAccess: false
    allowSharedKeyAccess: true
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
  }
}

resource evidence 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  name: '${storage.name}/default/architecture-decisions'
  properties: {
    publicAccess: 'None'
  }
}

resource insights 'Microsoft.Insights/components@2020-02-02' = {
  name: 'ccadf-ai-${suffix}'
  location: location
  kind: 'web'
  tags: tags
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logs.id
  }
}

output logAnalyticsWorkspace string = logs.name
output storageAccount string = storage.name
output evidenceContainer string = evidence.name
output applicationInsights string = insights.name
output evidenceStatement string = 'Azure evidence plane deployed for CompoundCloud architecture decisions and benchmark telemetry.'

