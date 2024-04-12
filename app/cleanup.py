# cleanup.py

# Importing necessary modules
import os
import time

# Function to delete old PDFs
def delete_old_pdfs(directory='/app/downloads', max_age_days=3):
    # Get the current time
    now = time.time()

    # Iterate through all files in the specified directory
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        # If the file is older than max_age_days, remove it
        if os.stat(file_path).st_mtime < now - max_age_days * 86400:
            os.remove(file_path)
            print(f"Deleted: {file_path}")

# Main execution
if __name__ == "__main__":
    delete_old_pdfs()
