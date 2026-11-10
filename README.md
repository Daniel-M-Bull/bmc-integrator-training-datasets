# BMC Integrator training datasets

A small collection of public datasets for experimenting with model training workflows orchestrated by **BMC Integrator**. Datasets are organized by the common supervised-learning task they can support.

## Dataset collections

- [Classification](datasets/classification/README.md): WBCD (Wisconsin Breast Cancer Diagnostic), Wine, and Iris.
- [Regression](datasets/regression/README.md): Boston Housing, Auto MPG, and Tips.
- [Dataset manifest](datasets/manifest.json): names, task types, targets, source URLs, and local paths planned for dataset copies.

## Dataset availability

The collection currently catalogs public source files by URL; the CSV copies are **not yet present** in this repository. Use the source URLs in the category READMEs and manifest to fetch data, and update the manifest status when reviewed snapshots are added. Check each source's license and terms before use. Some upstream datasets may have terms that differ from this repository.

This repository is intended to collect datasets for model-training workflows using BMC Integrator as the workflow controller. It does not contain model code or workflow definitions.