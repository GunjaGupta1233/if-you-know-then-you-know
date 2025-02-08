import os
try:
    import requests
except ImportError:
    print("Please install the 'requests' library using 'pip install requests' and try again.")
    exit()

def download_folder(owner, repo, branch, path, local_dir):
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}"
    headers = {'Accept': 'application/vnd.github.v3+json'}
    response = requests.get(api_url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to download {path}. Status code: {response.status_code}")
        return
    
    try:
        contents = response.json()
    except:
        print(f"Invalid response from GitHub API for path: {path}")
        return

    for item in contents:
        item_type = item.get('type', '')
        if item_type == 'file':
            file_url = item.get('download_url')
            file_name = item.get('name')
            if not file_url or not file_name:
                continue
            
            file_path = os.path.join(local_dir, file_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            try:
                with requests.get(file_url, stream=True) as r:
                    r.raise_for_status()
                    with open(file_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                print(f"Downloaded: {file_name}")
            except Exception as e:
                print(f"Failed to download {file_name}: {e}")
        
        elif item_type == 'dir':
            dir_name = item.get('name')
            if not dir_name:
                continue
            
            dir_path = os.path.join(local_dir, dir_name)
            os.makedirs(dir_path, exist_ok=True)
            new_path = os.path.join(path, dir_name).replace('\\', '/')
            download_folder(owner, repo, branch, new_path, dir_path)
        
        else:
            print(f"Skipping unsupported item type: {item_type} for {item.get('name', 'unknown')}")

def main():
    url = input("Enter the GitHub folder URL: ").strip()
    
    if not url.startswith("https://github.com/"):
        print("Error: Invalid GitHub URL.")
        return
    
    parts = url.split("github.com/")[1].split("/")
    
    if len(parts) < 4 or parts[2] != 'tree':
        print("Error: The URL must be a direct link to a folder (tree), not a file (blob).")
        return
    
    owner = parts[0]
    repo = parts[1]
    branch = parts[3]
    folder_path = "/".join(parts[4:]) if len(parts) > 4 else ''
    folder_name = os.path.basename(folder_path) if folder_path else repo
    local_dir = os.path.join(os.getcwd(), folder_name)
    
    os.makedirs(local_dir, exist_ok=True)
    print(f"Downloading to: {local_dir}")
    
    download_folder(owner, repo, branch, folder_path, local_dir)
    print("Download completed!")

if __name__ == "__main__":
    main()
