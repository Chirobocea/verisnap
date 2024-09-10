import os
import shutil
import winshell
from datetime import datetime
import re
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DEFAULT_THRESHOLD = 50  # Default threshold size in bytes (50 MB)

def create_symlink_or_shortcut(src: str, dest: str) -> None:
    """Creates a symlink (or shortcut on Windows) for the given source."""
    
    def create_shortcut(src: str, dest: str) -> None:
        """Creates a shortcut at the given destination pointing to the source."""
        try:
            with winshell.shortcut(dest) as shortcut:
                shortcut.path = os.path.normpath(src)  # Normalize path to handle slashes correctly
                shortcut.description = f"Shortcut to {src}"
            logging.info(f"Created shortcut for {src} at {dest}")
        except Exception as e:
            logging.error(f"Failed to create shortcut: {e}")
    
    try:
        if os.name == 'nt':  # Windows
            create_shortcut(src, dest)
        else:
            os.symlink(src, dest)
            logging.info(f"Created symbolic link for '{src}' at '{dest}'")
    except OSError as e:
        logging.error(f"Error creating symlink or shortcut: {e}")
        if hasattr(e, 'winerror') and e.winerror == 1314:  # Privilege not held (Windows-specific)
            create_shortcut(src, dest)
        else:
            raise

def validate_threshold(threshold: any) -> int:
    """
    Validates and converts the threshold to bytes. If the input is invalid, it uses the default value.
    """
    try:
        # Try converting to float (to handle both int and float as input)
        threshold_value = float(threshold)
        
        # Check if the value is greater than 0
        if threshold_value <= 0:
            logging.warning(f"Invalid threshold value: {threshold}. Threshold must be greater than 0. Using default value: {DEFAULT_THRESHOLD} MB.")
            return DEFAULT_THRESHOLD
        elif threshold_value > 100:
            logging.warning(f"Threshold value {threshold_value} MB seems too high. Please provide a value in MB. Defaulting to {DEFAULT_THRESHOLD} MB.")
            return DEFAULT_THRESHOLD * 1024 * 1024
        else:
            # Convert to bytes (MB to bytes)
            return int(threshold_value * 1024 * 1024)
    except ValueError:
        # If conversion fails, use default threshold and inform the user
        logging.warning(f"Invalid threshold input: '{threshold}'. Using default value of {DEFAULT_THRESHOLD} MB.")
        return DEFAULT_THRESHOLD * 1024 * 1024

def format_size(bytes_size: int) -> str:
    """Converts bytes into a human-readable format (e.g., KB, MB, GB)."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0

def copy_directory(source_dir: str, output_dir: str, threshold: int = DEFAULT_THRESHOLD) -> int:
    """Copies files below the threshold size, creates symlinks/shortcuts for larger files or directories."""
    
    # Validate and convert the threshold
    threshold_bytes = validate_threshold(threshold)
    
    total_size_copied = 0  # To track the total size of copied files

    # Create the root directory as an empty structure
    try:
        root_dest_dir = os.path.normpath(os.path.join(output_dir, os.path.basename(source_dir)))
        os.makedirs(root_dest_dir, exist_ok=True)
        logging.info(f"Created root directory: {root_dest_dir}")
    except Exception as e:
        logging.error(f"Error creating directory {root_dest_dir}: {e}")
        return total_size_copied
    
    # Traverse the source directory and process files/subdirectories
    for dirpath, dirnames, filenames in os.walk(source_dir):
        relative_path = os.path.relpath(dirpath, source_dir)
        dest_dir = os.path.normpath(os.path.join(root_dest_dir, relative_path))

        # Ensure the directory structure is replicated but empty
        os.makedirs(dest_dir, exist_ok=True)
        
        # Handle subdirectories
        for dirname in dirnames:
            src_subdir = os.path.normpath(os.path.join(dirpath, dirname))
            dest_subdir = os.path.normpath(os.path.join(dest_dir, dirname))

            # Calculate the size of the directory
            dir_size = sum(os.path.getsize(os.path.join(src_subdir, f)) for f in os.listdir(src_subdir) if os.path.isfile(os.path.join(src_subdir, f)))
            
            if dir_size > threshold_bytes:
                # Create a link instead of copying the directory
                logging.info(f"Skipping directory '{src_subdir}' (size: {format_size(dir_size)}) exceeds threshold: {threshold} MB.")
                dest_shortcut = os.path.normpath(dest_subdir + '.lnk')
                create_symlink_or_shortcut(src_subdir, dest_shortcut)
                dirnames.remove(dirname)  # Prevent descending into this directory
            
        # Handle files
        for filename in filenames:
            src_file = os.path.normpath(os.path.join(dirpath, filename))
            dest_file = os.path.normpath(os.path.join(dest_dir, filename))
            file_size = os.path.getsize(src_file)
            
            if file_size <= threshold_bytes:
                try:
                    shutil.copy2(src_file, dest_file)
                    total_size_copied += file_size
                except Exception as e:
                    logging.error(f"Error copying file '{src_file}': {e}")
            else:
                # Create a link instead of copying the file
                logging.info(f"Skipping file '{src_file}' (size: {format_size(file_size)}) exceeds threshold: {threshold} MB.")
                dest_shortcut = os.path.normpath(dest_file + '.lnk')
                create_symlink_or_shortcut(src_file, dest_shortcut)

    return total_size_copied

def find_latest_version(snapshots_dir: str) -> int:
    """Finds the latest snapshot version by examining folder names that start with 'V' followed by a number."""
    version_pattern = re.compile(r'^V(\d+)_')
    latest_version = 0
    
    for folder_name in os.listdir(snapshots_dir):
        if os.path.isdir(os.path.join(snapshots_dir, folder_name)):
            match = version_pattern.match(folder_name)
            if match:
                version_num = int(match.group(1))
                latest_version = max(latest_version, version_num)
    
    return latest_version

def make_snapshot(source_dir: str, snapshots_dir: str, threshold: int = DEFAULT_THRESHOLD) -> int:
    """Creates a new snapshot by copying files from source_dir to a new versioned folder in snapshots_dir."""
    
    latest_version = find_latest_version(snapshots_dir)
    new_version = latest_version + 1
    current_time = datetime.now().strftime("%Y_%m_%d_%H_%M")
    
    output_dir = os.path.join(snapshots_dir, f"V{new_version}_{current_time}")
    
    total_size_copied = copy_directory(source_dir, output_dir, threshold)
    
    logging.info(f"Snapshot V{new_version} created with total size: {format_size(total_size_copied)}")

    return new_version