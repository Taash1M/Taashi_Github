import os
import shutil

def cleanup_repository():
    # 1. Define the destination folder name
    dest_folder_name = "Implementation Code"
    
    # 2. Define the allow-list (Files/Folders to KEEP in the root)
    # We must include the script itself so it doesn't try to move itself while running
    keep_files = {
        "README.md", 
        ".gitignore", 
        "LICENSE", 
        ".git",              # CRITICAL: Never move the .git folder
        dest_folder_name,    # Don't move the destination folder
        "cleanup_root.py"    # Don't move this script while it's running
    }

    # Get the current working directory (should be the repo root)
    root_dir = os.getcwd()
    dest_path = os.path.join(root_dir, dest_folder_name)

    # 3. Create the destination folder if it doesn't exist
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)
        print(f"Created directory: {dest_folder_name}")
    else:
        print(f"Directory already exists: {dest_folder_name}")

    # 4. Iterate through files and move them
    print("-" * 30)
    print("Starting cleanup process...")
    
    items_moved = 0
    
    # List all files and directories in the root
    for item in os.listdir(root_dir):
        # Skip items in the keep_list
        if item in keep_files:
            continue
            
        source_item = os.path.join(root_dir, item)
        destination_item = os.path.join(dest_path, item)

        try:
            # Move file or directory
            print(f"Moving: {item} -> {dest_folder_name}/{item}")
            shutil.move(source_item, destination_item)
            items_moved += 1
        except Exception as e:
            print(f"ERROR moving {item}: {e}")

    print("-" * 30)
    print(f"Cleanup complete. {items_moved} items moved to '{dest_folder_name}'.")
    print("Remember to update the links in your README.md!")

if __name__ == "__main__":
    # verification prompt
    confirm = input("This will move ALL files (except README, LICENSE, .gitignore) to 'Implementation Code'.\nAre you sure? (y/n): ")
    if confirm.lower() == 'y':
        cleanup_repository()
    else:
        print("Operation cancelled.")
