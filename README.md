# Simple Generator Script for Making Synthetic Elastic Tasksets

## Overview
A Python script for generating synthetic elastic tasksets with configurable parameters for testing and simulation purposes.

## Usage
```bash
python gen.py <num_tasks> <discrete_ratio> <skewness_ratio> [yaml_file]
```

## Parameters

| Parameter | Description |
|-----------|-------------|
| `num_tasks` | Number of tasks to generate |
| `discrete_ratio` | Stepping ratio for converting continuous elasticity into discrete modes |
| `skewness_ratio` | Ratio determining workload distribution between core A and core B |
| `yaml_file` | *(Optional)* Output file name for YAML format compatible with scheduler |
