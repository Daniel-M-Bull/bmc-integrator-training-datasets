# BMC Integrator training datasets

A small collection of public datasets for experimenting with model training workflows orchestrated by **BMC Integrator**. Datasets are organized by the common supervised-learning task they can support.

## Dataset collections

- [Classification](datasets/classification/README.md): WBCD (Wisconsin Breast Cancer Diagnostic), Wine, and Iris.
- [Regression](datasets/regression/README.md): Boston Housing, Auto MPG, and Tips.
- [Dataset manifest](datasets/manifest.json): names, task types, targets, source URLs, and local paths planned for dataset copies.

## Dataset availability

CSV snapshots are included in the classification and regression folders. The manifest records each dataset's source URL and target. Check each source's license and terms before use; upstream terms may differ from this repository.

This repository is intended to collect datasets for model-training workflows using BMC Integrator as the workflow controller. It does not contain model code or workflow definitions.