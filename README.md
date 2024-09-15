### VeriSnap

VeriSnap is a Python tool designed to facilitate tracking and managing multiple experiment runs. It creates snapshots of directories, selectively copying or symbolically linking files based on a specified size threshold. This is especially useful in research environments where experiments might contain bugs or need to be rerun, as it provides an easy way to version and manage experiment results without risk of overwriting previous snapshots.

## Key Features
- **Automatic Versioning**: VeriSnap automatically checks the snapshot directory and increments the version number, so you don’t need to worry about overwriting previous experiments.
- **Integration with Experiment Tracking**: The generated version number can be used within your code to label saved models, and it can be integrated with tools like TensorBoard for logging metrics and results.
- **Efficient File Management**: Files are either copied or symbolically linked based on a size threshold, optimizing storage space.

## Installation

To install VeriSnap, use pip:

```bash
pip install verisnap
```

## Usage 
```
from verisnap import make_snapshot

source_dir = '/path/to/source'  # Directory containing the experiment results
snapshots_dir = '/path/to/snapshots'  # Directory where snapshots will be stored
threshold = 50  # MB, files larger than this will be symbolically linked

version = make_snapshot(source_dir, snapshots_dir, threshold)

# Proceed with your training code...

# You can use the `version` in your code to label saved models or logs.
```
