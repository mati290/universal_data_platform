output "resource_group_name" {
  description = "Resource group name."
  value       = module.resource_group.name
}

output "aks_cluster_name" {
  description = "AKS cluster name."
  value       = module.aks.name
}

output "acr_login_server" {
  description = "Azure Container Registry login server."
  value       = module.acr.login_server
}

output "postgresql_fqdn" {
  description = "PostgreSQL Flexible Server FQDN."
  value       = module.postgresql.fqdn
}
