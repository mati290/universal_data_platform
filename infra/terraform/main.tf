locals {
  name_prefix = lower(replace("${var.project_name}-${var.environment}", "_", "-"))

  tags = merge(
    {
      project     = var.project_name
      environment = var.environment
      managed_by  = "terraform"
    },
    var.tags,
  )
}

module "resource_group" {
  source = "./modules/resource_group"

  name     = "rg-${local.name_prefix}"
  location = var.location
  tags     = local.tags
}

module "network" {
  source = "./modules/network"

  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  vnet_name           = "vnet-${local.name_prefix}"
  address_space       = var.address_space
  aks_subnet_name     = "snet-aks-${local.name_prefix}"
  aks_subnet_cidr     = var.aks_subnet_cidr
  data_subnet_name    = "snet-data-${local.name_prefix}"
  data_subnet_cidr    = var.data_subnet_cidr
  tags                = local.tags
}

module "acr" {
  source = "./modules/acr"

  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  name                = substr(lower(replace(replace("acr${var.project_name}${var.environment}", "-", ""), "_", "")), 0, 50)
  sku                 = var.acr_sku
  tags                = local.tags
}

module "postgresql" {
  source = "./modules/postgresql"

  resource_group_name    = module.resource_group.name
  location               = module.resource_group.location
  name                   = "psql-${local.name_prefix}"
  administrator_login    = var.postgres_admin_username
  administrator_password = var.postgres_admin_password
  database_name          = var.postgres_db_name
  sku_name               = var.postgres_sku_name
  storage_mb             = var.postgres_storage_mb
  engine_version         = var.postgres_engine_version
  delegated_subnet_id    = module.network.data_subnet_id
  virtual_network_id     = module.network.vnet_id
  tags                   = local.tags
}

module "aks" {
  source = "./modules/aks"

  resource_group_name = module.resource_group.name
  location            = module.resource_group.location
  cluster_name        = "aks-${local.name_prefix}"
  dns_prefix          = "aks-${local.name_prefix}"
  kubernetes_version  = var.kubernetes_version
  node_count          = var.aks_node_count
  vm_size             = var.aks_vm_size
  subnet_id           = module.network.aks_subnet_id
  acr_id              = module.acr.id
  tags                = local.tags
}
