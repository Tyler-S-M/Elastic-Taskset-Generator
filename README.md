Simple Generator Script for Making Synthetic Elastic Tasksets

Usage: python gen.py <num_tasks> <discrete_ratio> <skewness_ratio> <(optional) Yaml File Name>

num_tasks = number of tasks to generate
discrete_ratio = stepping at which to turn continuous elasticity into discrete modes
skewness_ratio = how much of the dag should be attributed to core A vs core B
Yaml File Name = if provided, what file to output YAML to for use with scheduler
