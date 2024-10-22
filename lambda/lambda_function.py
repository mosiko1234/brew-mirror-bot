import boto3
import subprocess
from pathlib import Path
import datetime
import hashlib
import requests

s3 = boto3.client('s3')
bucket_name = "brew-mirror-bucket"

def calculate_sha256(file_path: Path):
    sha256_hash = hashlib.sha256()
    with file_path.open("rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def freeze_tap(tap: str, output_dir: Path):
    """ Executes `brew_mirror freeze` to freeze the current state of a tap. """
    subprocess.run(["python3", "-m", "brew_mirror", "freeze", tap, str(output_dir)], check=True)
    print(f"Tap {tap} has been frozen.")

def download_and_zip_repo(repo_url: str, repo_name: str, output_dir: Path):
    subprocess.run(["git", "clone", repo_url], check=True)
    subprocess.run(["zip", "-r", f"{repo_name}.zip", repo_name], check=True)
    output_zip = output_dir / f"{repo_name}.zip"
    return output_zip

def download_bottle(bottle_url: str, output_dir: Path):
    bottle_name = bottle_url.split("/")[-1]
    output_file = output_dir / bottle_name
    subprocess.run(["curl", "-L", bottle_url, "-o", str(output_file)], check=True)
    return output_file

def download_portable_ruby_assets(output_dir: Path):
    api_url = "https://api.github.com/repos/Homebrew/homebrew-portable-ruby/releases/latest"
    response = requests.get(api_url)
    if response.status_code == 200:
        release_data = response.json()
        assets = release_data.get("assets", [])
        for asset in assets:
            asset_name = asset["name"]
            download_url = asset["browser_download_url"]
            output_file = output_dir / asset_name
            print(f"Downloading {asset_name} from {download_url}")
            subprocess.run(["curl", "-L", download_url, "-o", str(output_file)], check=True)
        return assets
    else:
        print("Failed to fetch the latest release of homebrew-portable-ruby.")
        return None

def upload_to_s3(local_path: Path, s3_path: str):
    s3.upload_file(str(local_path), bucket_name, s3_path)
    print(f"Uploaded {local_path} to s3://{bucket_name}/{s3_path}")

def lambda_handler(event, context):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    output_folder = Path("/tmp/output")
    bottles_folder = output_folder / "bottles"
    ruby_folder = output_folder / "portable-ruby"
    output_folder.mkdir(parents=True, exist_ok=True)
    bottles_folder.mkdir(parents=True, exist_ok=True)
    ruby_folder.mkdir(parents=True, exist_ok=True)

    freeze_tap("homebrew/core", output_folder)

    brew_zip = download_and_zip_repo("git@github.com:Homebrew/brew.git", "brew", output_folder)
    install_zip = download_and_zip_repo("git@github.com:Homebrew/install.git", "install", output_folder)
    services_zip = download_and_zip_repo("git@github.com:Homebrew/homebrew-services.git", "homebrew-services", output_folder)

    bottles = [
        "https://homebrew.bintray.com/bottles/bottle1.tar.gz",
        "https://homebrew.bintray.com/bottles/bottle2.tar.gz"
    ]
    
    for bottle_url in bottles:
        bottle = download_bottle(bottle_url, bottles_folder)
        
        bottle_hash = calculate_sha256(bottle)

        upload_to_s3(bottle, f"mirrors/{timestamp}/bottles/{bottle.name}")

    ruby_assets = download_portable_ruby_assets(ruby_folder)

    upload_to_s3(brew_zip, f"mirrors/{timestamp}/brew.zip")
    upload_to_s3(install_zip, f"mirrors/{timestamp}/install.zip")
    upload_to_s3(services_zip, f"mirrors/{timestamp}/homebrew-services.zip")

    if ruby_assets:
        for asset in ruby_assets:
            asset_name = asset["name"]
            asset_file = ruby_folder / asset_name
            upload_to_s3(asset_file, f"mirrors/{timestamp}/portable-ruby/{asset_name}")
