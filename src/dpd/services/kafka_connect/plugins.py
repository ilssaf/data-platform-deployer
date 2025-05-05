import os
import requests
import zipfile
import tarfile
import shutil



def download_and_extract_archive(url, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_name = os.path.basename(url)
    output_file_path = os.path.join(output_dir, file_name)

    response = requests.get(url)
    response.raise_for_status()

    with open(output_file_path, "wb") as file:
        file.write(response.content)
    if zipfile.is_zipfile(output_file_path):
        with zipfile.ZipFile(output_file_path, "r") as zip_ref:
            zip_ref.extractall(output_dir)

    elif tarfile.is_tarfile(output_file_path):
        with tarfile.open(output_file_path, "r") as tar_ref:
            tar_ref.extractall(output_dir)
    else:
        raise Exception(f"Файл {file_name} не является архивом ZIP или TAR.")
    
    os.remove(output_file_path)


def move_file(source_file_path, destination_dir):

    if not os.path.isfile(source_file_path):
        raise FileNotFoundError(f"Файл {source_file_path} не существует или не является файлом.")
        
    os.makedirs(destination_dir, exist_ok=True)
    file_name = os.path.basename(source_file_path)
    destination_file_path = os.path.join(destination_dir, file_name)
    shutil.copy(source_file_path, destination_file_path)
