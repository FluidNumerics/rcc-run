
builds = [
          {
            name = "fluid-run-main-latest"
            branch="main"
            project = "research-computing-cloud"
            description = "Fluid Run Main branch builds for the latest stable release"
            artifact_tag = "latest"
            disabled = false
          }
         ]

releases = [
          {
            name = "fluid-run-version-releases"
            tag="v.*"
            project = "research-computing-cloud"
            description = "Version releases"
            disabled = false
          }
         ]
