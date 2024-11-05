import numpy as np
import math
import sys

# Global system CPU constraints
TOTAL_CPUS_A = 16  # Total type A CPUs available in system
TOTAL_CPUS_B = 32  # Total type B CPUs available in system

MAX_ALLOWED_CPUS = 16
MIN_ALLOWED_CPUS = 2

def generate_discrete_modes(min_val, max_val, mode_ratio):

    num_modes = round(1 / mode_ratio)
    step = (max_val - min_val) / (num_modes - 1)
    return [min_val + i * step for i in range(num_modes)]

def calculate_cpus(work, span, period, skewness_ratio):

    adjusted_period = period if skewness_ratio == 1.0 else period / 2

    try:
        denominator = (adjusted_period) - span
        if denominator <= 0:
            return None
        
        numerator = work - span
        if numerator < 0:
            return None
            
        cpus = math.ceil(numerator / denominator)
        return cpus if cpus >= 0 else None
        
    except (ValueError, ZeroDivisionError):
        return None

def is_valid_cpus(cpus_a, cpus_b, skewness_ratio):

    if skewness_ratio != 1.0:

        if (cpus_a is None or cpus_b is None):
            return False

        if (cpus_a > TOTAL_CPUS_A or cpus_b > TOTAL_CPUS_B):
            return False

        if ((cpus_a + cpus_b) > MAX_ALLOWED_CPUS):
            return False

        if (cpus_a < MIN_ALLOWED_CPUS) or (cpus_b < MIN_ALLOWED_CPUS):
            return False
        
    else:

        if (cpus_a is None):
            return False

        if (cpus_a > TOTAL_CPUS_A):
            return False

        if (cpus_a > MAX_ALLOWED_CPUS):
            return False

        if (cpus_a < MIN_ALLOWED_CPUS):
            return False
        
    return True

def generate_task(mode_ratio=0.25, skewness_ratio=None):
    # Constants
    pmax = 1 / (2 * (2 + math.sqrt(2)))
    
    # Generate ratio of span to minimum period
    ratios = [0.4, 0.5, 0.7, 1.0]
    probabilities = [0.4, 0.3, 0.2, 0.1]
    chosen_ratio = np.random.choice(ratios, p=probabilities) * pmax
    
    # Generate skewness ratio (random between 0.2 and 0.8)
    if skewness_ratio is None:
        skewness_ratio = np.random.uniform(0.2, 0.8)
    
    # Generate segments until we reach the target span
    total_span = 0
    segments = []
    segment_strands = []
    segment_types = []  # 'a' or 'b'
    
    target_span = chosen_ratio * 1000  # Converting to milliseconds
    target_span_a = target_span * skewness_ratio
    current_span_a = 0
    
    while total_span < target_span:
        # Generate segment length from log normal distribution with mean 5ms
        segment_length = np.random.lognormal(mean=np.log(5), sigma=0.5)
        
        # Determine if this segment should be type 'a' or 'b'
        if current_span_a < target_span_a:
            segment_type = 'a'
            current_span_a += segment_length
        else:
            segment_type = 'b'
            
        # Generate number of strands for min and max work
        m = len(segments) + 1  # Current number of segments
        mean_strands = 1 + math.sqrt(m)/3
        min_strands = max(1, round(np.random.lognormal(mean=np.log(mean_strands), sigma=0.3)))
        max_strands = max(min_strands + 1, round(np.random.lognormal(mean=np.log(mean_strands * 1.5), sigma=0.3)))
        
        segments.append(segment_length)
        segment_strands.append((min_strands, max_strands))
        segment_types.append(segment_type)
        total_span += segment_length

    # Calculate spans for both types
    span_a = sum(length for length, type_ in zip(segments, segment_types) if type_ == 'a')
    span_b = sum(length for length, type_ in zip(segments, segment_types) if type_ == 'b')

    # Calculate minimum and maximum work for both types
    min_work_a = sum(length * strands[0] for length, strands, type_ 
                    in zip(segments, segment_strands, segment_types) if type_ == 'a')
    max_work_a = sum(length * strands[1] for length, strands, type_ 
                    in zip(segments, segment_strands, segment_types) if type_ == 'a')
    min_work_b = sum(length * strands[0] for length, strands, type_ 
                    in zip(segments, segment_strands, segment_types) if type_ == 'b')
    max_work_b = sum(length * strands[1] for length, strands, type_ 
                    in zip(segments, segment_strands, segment_types) if type_ == 'b')
    
    # Generate period uniformly between 50ms and 1s
    period = np.random.uniform(50, 1000)
    
    # Generate elasticity value
    elasticity = np.random.uniform(0, 1)
    
    # Calculate minimum and maximum CPUs needed for both types
    min_cpus_a = calculate_cpus(min_work_a, span_a, period, skewness_ratio)
    max_cpus_a = calculate_cpus(max_work_a, span_a, period, skewness_ratio)
    min_cpus_b = calculate_cpus(min_work_b, span_b, period, skewness_ratio)
    max_cpus_b = calculate_cpus(max_work_b, span_b, period, skewness_ratio)
    
    # Validate all CPU calculations and system constraints
    if not all([is_valid_cpus(min_cpus_a, min_cpus_b, skewness_ratio),
                is_valid_cpus(max_cpus_a, max_cpus_b, skewness_ratio)]):
        return None
    
    # Generate modes and validate their CPU requirements
    modes_a = generate_discrete_modes(min_work_a, max_work_a, mode_ratio)
    modes_b = generate_discrete_modes(min_work_b, max_work_b, mode_ratio)
    
    # Create combined mode information
    mode_info = []
    for mode_a, mode_b in zip(modes_a, modes_b):
        cpus_a = calculate_cpus(mode_a, span_a, period, skewness_ratio)
        cpus_b = calculate_cpus(mode_b, span_b, period, skewness_ratio)
            
        mode_info.append({
            'period': period,
            'total_work': mode_a + mode_b,
            'work_a': mode_a,
            'work_b': mode_b,
            'total_cpus': cpus_a + cpus_b,
            'cpus_a': cpus_a,
            'cpus_b': cpus_b
        })
    
    return {
        'span_a': span_a,
        'span_b': span_b,
        'period': period,
        'min_work_a': min_work_a,
        'max_work_a': max_work_a,
        'min_work_b': min_work_b,
        'max_work_b': max_work_b,
        'mode_info': mode_info,
        'min_cpus_a': min_cpus_a,
        'max_cpus_a': max_cpus_a,
        'min_cpus_b': min_cpus_b,
        'max_cpus_b': max_cpus_b,
        'elasticity': elasticity,
        'skewness_ratio': skewness_ratio,
        'segments': list(zip(segments, segment_strands, segment_types))
    }

def generate_task_set(num_tasks, mode_ratio=0.25, skewness_ratio=None):
    tasks = []
    task_num = 1
    attempts = 0
    max_attempts = 100000  # Prevent infinite loops
    
    while len(tasks) < num_tasks and attempts < max_attempts:
        task = generate_task(mode_ratio, skewness_ratio)
        attempts += 1
        
        if task is not None:
            print(f"\nTask {task_num}:")
            print(f"Skewness Ratio: {task['skewness_ratio']:.2f}")
            print(f"Span A: {task['span_a']:.2f}ms")
            print(f"Span B: {task['span_b']:.2f}ms")
            print(f"Period: {task['period']:.2f}ms")
            
            print("\nWork Type A:")
            print(f"  Min Work: {task['min_work_a']:.2f}ms")
            print(f"  Max Work: {task['max_work_a']:.2f}ms")
            print(f"  Min CPUs: {task['min_cpus_a']}")
            print(f"  Max CPUs: {task['max_cpus_a']}")
            
            print("\nWork Type B:")
            print(f"  Min Work: {task['min_work_b']:.2f}ms")
            print(f"  Max Work: {task['max_work_b']:.2f}ms")
            print(f"  Min CPUs: {task['min_cpus_b']}")
            print(f"  Max CPUs: {task['max_cpus_b']}")
            
            print(f"\nElasticity: {task['elasticity']:.3f}")
            
            print(f"\nSystem Constraints:")
            print(f"  Total System CPUs Type A: {TOTAL_CPUS_A}")
            print(f"  Total System CPUs Type B: {TOTAL_CPUS_B}")
            
            print("\nSegments (length, (min_strands, max_strands), type):")
            for idx, (length, strands, type_) in enumerate(task['segments'], 1):
                print(f"  Segment {idx}: {length:.2f}ms, {strands}, Type {type_}")
            
            print("\nModes:")
            for idx, mode in enumerate(task['mode_info'], 1):
                print(f"  Mode {idx}:")
                print(f"    Period: {mode['period']:.2f}ms")
                print(f"    Total Work: {mode['total_work']:.2f}ms")
                print(f"    Work Type A: {mode['work_a']:.2f}ms")
                print(f"    Work Type B: {mode['work_b']:.2f}ms")
                print(f"    Total CPUs: {mode['total_cpus']}")
                print(f"    CPUs Type A: {mode['cpus_a']}")
                print(f"    CPUs Type B: {mode['cpus_b']}")
            
            tasks.append(task)
            task_num += 1
    
    if attempts >= max_attempts:
        print("\nWarning: Reached maximum attempts to generate valid tasks. Some tasks may be missing.")
    
    return tasks

if __name__ == "__main__":
    if len(sys.argv) == 3:
        tasks = generate_task_set(int(sys.argv[1]), float(sys.argv[2]))
    else:
        tasks = generate_task_set(int(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]))
