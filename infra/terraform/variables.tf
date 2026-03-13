variable "project_name" {
  description = "Base project name used for resource naming."
  type        = string
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
}

variable "location" {
  description = "Azure region for all resources."
  type        = string
}

variable "tags" {
  description = "Common tags applied to Azure resources."
  type        = map(string)
  default     = {}
}

variable "address_space" {
  description = "Address space for the virtual network."
  type        = list(string)
  default     = ["10.10.0.0/16"]
}

variable "aks_subnet_cidr" {
  description = "CIDR block for the AKS subnet."
  type        = list(string)
  default     = ["10.10.1.0/24"]
}

variable "data_subnet_cidr" {
  description = "CIDR block for the data subnet."
  type        = list(string)
  default     = ["10.10.2.0/24"]
}

variable "acr_sku" {
  description = "SKU for Azure Container Registry."
  type        = string
  default     = "Standard"
}

variable "aks_node_count" {
  description = "Initial AKS node count."
  type        = number
  default     = 2
}

variable "aks_vm_size" {
  description = "VM size for AKS system nodes."
  type        = string
  default     = "Standard_D4s_v5"
}

variable "kubernetes_version" {
  description = "Optional AKS version pin."
  type        = string
  default     = null
}

variable "postgres_admin_username" {
  description = "Administrator username for PostgreSQL Flexible Server."
  type        = string
}

variable "postgres_admin_password" {
  description = "Administrator password for PostgreSQL Flexible Server."
  type        = string
  sensitive   = true
}

variable "postgres_db_name" {
  description = "Application database name."
  type        = string
  default     = "udp"
}

variable "postgres_sku_name" {
  description = "SKU for PostgreSQL Flexible Server."
  type        = string
  default     = "B_Standard_B2s"
}

variable "postgres_storage_mb" {
  description = "Storage size for PostgreSQL Flexible Server in MB."
  type        = number
  default     = 32768
}

variable "postgres_engine_version" {
  description = "PostgreSQL engine version."
  type        = string
  default     = "16"
}
