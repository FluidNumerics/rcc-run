

variable "builds" {
  type = list(object({
    name = string
    branch = string
    project = string
    description = string
    artifact_tag = string
    disabled = bool
  }))
  description = "List of branch build triggers"
}
