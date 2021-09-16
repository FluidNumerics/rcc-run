
Benchmark Dataset Schema
=========================
With each `execution_command` in your CI file, fluid-run will align variables about your build and testing environment along with runtimes to create a fully auditable record of the execution. This allows you to naturally generate a database over time that can track how your application performs over time and on all available hardware on Google Cloud. Knowing this information is critical for optimizing costs for your applications on public cloud systems. The table below provides an overview of the current schema.

============================  ===========  ========  ===============  ==================================================
Field name                    Type         Mode      Cluster Type(s)  Description
============================  ===========  ========  ===============  ==================================================
allocated_cpus                INTEGER      NULLABLE  RCC              The number of CPUs that are allocated to run the execution_command. 
allocated_gpus                INTEGER      NULLABLE  RCC              The number of GPUs that are allocated to run the execution_command. 
batch_options                 STRING       NULLABLE  RCC              Additional options sent to the batch scheduler
command_group                 STRING       REQUIRED  RCC, GCE         An identifier to allow grouping of execution_commands in reporting.
execution_command             STRING       REQUIRED  RCC, GCE         The full command used to execute this benchmark.
build_id                      STRING       REQUIRED  RCC, GCE         The Cloud Build build ID associated with this build. 
machine_type                  STRING       NULLABLE  RCC, GCE         Node types as classified by the system provider. 
gpu_type                      STRING       NULLABLE  RCC, GCE         The vendor and model name of the GPU (e.g. nvidia-tesla-v100) 
gpu_count                     INTEGER      NULLABLE  RCC, GCE         The number of GPUs, per compute node, on this compute system. 
node_count                    INTEGER      NULLABLE  RCC, GCE         The number of nodes used in testing. 
datetime                      DATETIME     REQUIRED  RCC, GCE         The UTC date and time of the build. 
exit_code                     INTEGER      REQUIRED  RCC, GCE         The system exit code thrown when executing the execution_command 
git_sha                       STRING       REQUIRED  RCC, GCE         The git SHA associated with the version / commit being tested. 
max_memory_gb                 FLOAT        NULLABLE  RCC              The maximum amount of memory used for the execution_command in GB. 
stderr                        STRING       NULLABLE  RCC, GCE         Standard error produced from running execution command.
stdout                        STRING       NULLABLE  RCC, GCE         Standard output produced from running execution command.
partition                     STRING       NULLABLE  RCC              The name of the scheduler partition to run the job under.
runtime                       FLOAT        NULLABLE  RCC, GCE         The runtime for the execution_command in seconds. 
compiler                      STRING       NULLABLE  RCC, GCE         Compiler name and version, e.g. `gcc@10.2.0`, used to build application.
target_arch                   STRING       NULLABLE  RCC, GCE         Architecture targeted by compiler during application build process. 
controller_machine_type       STRING       NULLABLE  RCC              Machine type used for the controller, for Slurm based test environments. 
controller_disk_size_gb       INTEGER      NULLABLE  RCC              The size of the controller disk in GB. 
controller_disk_type          STRING       NULLABLE  RCC              The type of disk used for the controller. 
filestore                     BOOLEAN      NULLABLE  RCC              A flag to indicated if filestore is used for workspace. 
filestore_tier                STRING       NULLABLE  RCC              The filestore tier used for file IO. 
filestore_capacity_gb         INTEGER      NULLABLE  RCC              The size of the filestore disk capacity in GB. 
lustre                        BOOLEAN      NULLABLE  RCC              A flag to indicated if lustre is used for workspace. 
lustre_mds_node_count         INTEGER      NULLABLE  RCC              Number of Lustre metadata servers 
lustre_mds_machine_type       STRING       NULLABLE  RCC              The machine type for the Lustre MDS servers. 
lustre_mds_boot_disk_type     STRING       NULLABLE  RCC              The boot disk type for the Lustre MDS servers. 
lustre_mds_boot_disk_size_gb  INTEGER      NULLABLE  RCC              The size of the Lustre boot disk in GB.
lustre_mdt_disk_type          STRING       NULLABLE  RCC              The mdt disk type for the Lustre MDS servers. 
lustre_mdt_disk_size_gb       INTEGER      NULLABLE  RCC              The size of the Lustre boot disk in GB. 
lustre_mdt_per_mds            INTEGER      NULLABLE  RCC              The number of metadata targets per MDS. 
lustre_oss_node_count         INTEGER      NULLABLE  RCC              Number of Lustre metadata servers 
lustre_oss_machine_type       STRING       NULLABLE  RCC              The machine type for the Lustre OSS servers. 
lustre_oss_boot_disk_type     STRING       NULLABLE  RCC              The boot disk type for the Lustre OSS servers. 
lustre_oss_boot_disk_size_gb  INTEGER      NULLABLE  RCC              The size of the Lustre boot disk in GB. 
lustre_ost_disk_type          STRING       NULLABLE  RCC              The ost disk type for the Lustre OSS servers. 
lustre_ost_disk_size_gb       INTEGER      NULLABLE  RCC              The size of the Lustre boot disk in GB. 
lustre_ost_per_oss            INTEGER      NULLABLE  RCC              The number of object storage targets per OSS. 
compact_placement             BOOLEAN      NULLABLE  RCC              A flag to indicate if compact placement is used. 
gvnic                         BOOLEAN      NULLABLE  RCC              A flag to indicate if Google Virtual NIC is used. 
lustre_image                  STRING       NULLABLE  RCC              The VM image used for the Lustre deployment. 
vm_image                      STRING       NULLABLE  RCC              VM image used for the GCE instance running the fluid-cicb cluster.
============================  ===========  ========  ===============  ==================================================
