

variable "builds" {
  type = list(object({
    branch = string
    project = string
    description = string
  }))
  description = "List of branch build triggers"
}
