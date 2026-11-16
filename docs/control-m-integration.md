# GitHub Actions → Control-M integration

## Dataset publication contract

Each dataset lives in its own folder under `datasets/classification/` or
`datasets/regression/`. Upload all files first and add `_READY` only when the
folder is complete. The workflow listens only for `datasets/**/_READY`, so
intermediate uploads do not start processing.

The marker must be committed in the same push as, or after, the dataset files.
For reliable operation, publish the data files and marker in one commit.

## GitHub Actions event metadata

The workflow validates the marker and emits these values:

- `dataset_id`: dataset folder name
- `category`: `classification` or `regression`
- `dataset_path`: repository-relative dataset folder
- `repository`: GitHub owner/repository
- `commit_sha`: exact published revision

## Remaining Control-M configuration

The workflow currently validates publication and prepares metadata. It does not
call Control-M yet. Before enabling that step, confirm from the target Control-M
Automation API Swagger documentation:

1. Automation API base URL reachable from the GitHub runner
2. Authentication method and required headers
3. Control-M instance name
4. Deployed folder name to order
5. Exact `POST /automation-api/run/order` request body and variable syntax

Then create GitHub Actions secrets for the API credential (and variables for
non-secret endpoint/instance/folder settings). Do not store credentials in the
repository. If the API is only reachable inside the corporate network, use a
self-hosted GitHub Actions runner with approved network access.

The GitHub Actions token used to read the repository is not a substitute for
the credentials Control-M or Fabric may need to download private datasets.
