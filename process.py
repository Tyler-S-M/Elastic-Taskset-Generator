import sys
from pathlib import Path
from collections import defaultdict
import re

class FileStats:
    def __init__(self):
        self.positive_sum = 0.0
        self.positive_count = 0
        self.negative_one_count = 0

    def add_value(self, value):
        if value > 0:
            self.positive_sum += value
            self.positive_count += 1
        elif value == -1:
            self.negative_one_count += 1

    @property
    def average_positive(self):
        return self.positive_sum / self.positive_count if self.positive_count > 0 else 0

def get_base_name(filename):
    """Extract base name from file by removing _i_.log or _e_.log"""
    return re.sub(r'_[ie]_\.log$', '', filename)

def process_directory(directory):
    """
    Process all matching pairs of _i_.log and _e_.log files in directory
    and calculate statistics for each type
    """
    dir_path = Path(directory)
    if not dir_path.is_dir():
        print(f"Error: {directory} is not a directory")
        return

    # Group files by their base name
    file_groups = defaultdict(dict)
    for file_path in dir_path.glob('*_[ie]_.log'):
        base_name = get_base_name(file_path.name)
        suffix = '_i_' if '_i_' in file_path.name else '_e_'
        file_groups[base_name][suffix] = file_path

    # Initialize statistics for each type
    i_stats = FileStats()
    e_stats = FileStats()

    # Process each group of files
    for base_name, files in file_groups.items():
        print(f"\nProcessing files for base name: {base_name}")

        # Process _i_.log file
        if '_i_' in files:
            try:
                with open(files['_i_'], 'r') as f:
                    for line in f:
                        try:
                            value = float(line.strip())
                            i_stats.add_value(value)
                        except ValueError:
                            print(f"Warning: Invalid number in {files['_i_'].name}: {line.strip()}")
            except Exception as e:
                print(f"Error processing {files['_i_'].name}: {str(e)}")

        # Process _e_.log file
        if '_e_' in files:
            try:
                with open(files['_e_'], 'r') as f:
                    for line in f:
                        try:
                            value = float(line.strip())
                            e_stats.add_value(value)
                        except ValueError:
                            print(f"Warning: Invalid number in {files['_e_'].name}: {line.strip()}")
            except Exception as e:
                print(f"Error processing {files['_e_'].name}: {str(e)}")

    # Print results
    print("\nResults:")
    print("\n_i_.log files:")
    print(f"Average of positive numbers: {i_stats.average_positive:.4f}")
    print(f"Count of -1s: {i_stats.negative_one_count}")
    
    print("\n_e_.log files:")
    print(f"Average of positive numbers: {e_stats.average_positive:.4f}")
    print(f"Count of -1s: {e_stats.negative_one_count}")

    # Return the statistics in case needed for further processing
    return {
        'i_stats': {
            'average_positive': i_stats.average_positive,
            'negative_one_count': i_stats.negative_one_count,
            'total_positive_count': i_stats.positive_count
        },
        'e_stats': {
            'average_positive': e_stats.average_positive,
            'negative_one_count': e_stats.negative_one_count,
            'total_positive_count': e_stats.positive_count
        }
    }

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <directory_path>")
        sys.exit(1)
    
    directory_path = sys.argv[1]
    process_directory(directory_path)