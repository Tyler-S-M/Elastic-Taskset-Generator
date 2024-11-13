import re
import sys
from pathlib import Path

def parse_loss_values(file_path):
    """
    Parse log files to extract total loss values and convert error messages to -1.
    
    Args:
        file_path (str): Path to the log file
        
    Returns:
        list: List of numbers representing loss values or -1 for errors
    """
    loss_pattern = r"Total Loss from Mode Change: ([-+]?\d*\.?\d+)"
    error_message = "Error: System is not schedulable in any configuration with specified constraints. Not updating modes."
    
    results = []
    
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if error_message in line:
                    results.append(-1)
                    continue
                
                match = re.search(loss_pattern, line)
                if match:
                    value = float(match.group(1))
                    results.append(value)
    
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
        return []
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return []
        
    return results

def process_directory(input_dir, output_dir=None):
    """
    Process all files in directory containing 'stderr' in their name
    and write results to new files with 'stderr' removed from name.
    
    Args:
        input_dir (str): Path to directory containing stderr files
        output_dir (str, optional): Path to directory for output files
    """
    input_path = Path(input_dir)
    if not input_path.is_dir():
        print(f"Error: {input_dir} is not a directory")
        return

    # Set up output directory
    if output_dir:
        output_path = Path(output_dir)
        # Create output directory if it doesn't exist
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = input_path

    # Find all files with 'stderr' in the name
    stderr_files = list(input_path.glob('*stderr*'))
    if not stderr_files:
        print(f"No files containing 'stderr' found in {input_dir}")
        return

    print(f"\nProcessing files from: {input_path}")
    print(f"Writing output to: {output_path}")

    for stderr_file in stderr_files:
        print(f"\nProcessing {stderr_file.name}...")
        
        # Create output filename by removing 'stderr'
        output_name = stderr_file.name.replace('stderr', '')
        if output_name == stderr_file.name:  # If 'stderr' wasn't found or removed
            output_name = f"processed_{stderr_file.name}"
        output_file = output_path / output_name
        
        # Process the file
        values = parse_loss_values(stderr_file)
        
        if values:  # Only write if we got some values
            try:
                with open(output_file, 'w') as f:
                    for value in values:
                        f.write(f"{value}\n")
                print(f"Wrote {len(values)} values to {output_file}")
            except Exception as e:
                print(f"Error writing to {output_file}: {str(e)}")
        else:
            print(f"No values found in {stderr_file.name}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Process stderr files and extract loss values")
    parser.add_argument("input_dir", help="Directory containing stderr files to process")
    parser.add_argument("-o", "--output-dir", help="Directory for output files (optional)")
    
    args = parser.parse_args()
    
    process_directory(args.input_dir, args.output_dir)