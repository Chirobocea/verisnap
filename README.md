# VeriSnap

A Python tool to create snapshots of directories with selective file copying or symbolic linking based on size thresholds.

## Installation

```bash
pip install verisnap
```

## Usage
```
from verisnap import make_snapshot

source_dir = '/path/to/source'
snapshots_dir = '/path/to/snapshots'
threshold = 50  # MB

make_snapshot(source_dir, snapshots_dir, threshold)
```
