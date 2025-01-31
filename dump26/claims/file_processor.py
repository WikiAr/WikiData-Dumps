from pathlib import Path
from typing import Callable, Any
import time
import tqdm


class FileProcessor:
    def __init__(self, memory_check_interval: int = 500):
        self.memory_check_interval = memory_check_interval
        self.start_time = time.time()
        self.tt = time.time()

    def process_files(self, directory: Path, process_func: Callable[[Path], Any], pattern: str = "*.json"):
        """
        Process files in directory with progress tracking and memory monitoring.

        Args:
            directory: Directory containing files
            process_func: Function to process each file
            pattern: File pattern to match
        """
        files = list(directory.glob(pattern))
        print(f"Processing {len(files)} files")

        for current_count, file_path in enumerate(tqdm.tqdm(files), 1):
            process_func(file_path)

            if current_count % self.memory_check_interval == 0:
                self._print_progress(current_count)

        self._print_summary(len(files))

    def _print_progress(self, count: int):
        current_time = time.time()
        print(f"Processed {count} files, " f"elapsed: {current_time - self.tt:.2f}s")
        self.tt = current_time
        self.print_memory()
