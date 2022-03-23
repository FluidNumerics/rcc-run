
builds = [
          {
            name = "rcc-run-main-latest"
            branch="main"
            project = "research-computing-cloud"
            description = "RCC Run Main branch builds for the latest stable release"
            artifact_tag = "latest"
            disabled = false
          }
         ]

releases = [
          {
            name = "rcc-run-version-releases"
            tag="v.*"
            project = "research-computing-cloud"
            description = "Version releases"
            disabled = false
          }
         ]
