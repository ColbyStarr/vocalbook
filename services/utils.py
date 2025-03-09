import os
import requests
import zipfile
import shutil
from io import BytesIO

def unpack_model_from_link(url: str, model_name: str, output_folder: str = "voice_models"):
    """
    Downloads a ZIP file from the given URL and extracts its contents into the specified folder.
    The extracted .pth and .index files are renamed to match the given model_name.
    """
    model_path = os.path.join(output_folder, model_name)
    os.makedirs(model_path, exist_ok=True)
    
    print(f"Downloading model from {url}...")
    response = requests.get(url, stream=True)
    
    if response.status_code == 200:
        with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
            extract_path = os.path.join(output_folder, f"{model_name}_temp")
            os.makedirs(extract_path, exist_ok=True)
            zip_ref.extractall(extract_path)
        
        # Search for .pth and .index files inside extracted contents
        for root, _, files in os.walk(extract_path):
            for file in files:
                if file.endswith(".pth"):
                    os.rename(os.path.join(root, file), os.path.join(model_path, f"{model_name}.pth"))
                elif file.endswith(".index"):
                    os.rename(os.path.join(root, file), os.path.join(model_path, f"{model_name}.index"))
        
        # Clean up temp extraction folder
        shutil.rmtree(extract_path, ignore_errors=True)
        
        print(f"Model extracted successfully to '{model_path}'")
    else:
        print(f"Failed to download model. HTTP Status: {response.status_code}")



def get_model_file_paths(model_name: str, output_folder: str = "models"):
    """
    Given the model name, returns the paths to the .pth and .index files.
    """
    model_path = os.path.join(output_folder, model_name)
    pth_path = os.path.join(model_path, f"{model_name}.pth")
    index_path = os.path.join(model_path, f"{model_name}.index")
    # print(f"PTH path: {pth_path}")
    # print(f"INDEX path: {index_path}")
    
    return pth_path, index_path



def list_model_directories(output_folder: str = "voice_models"):
    """
    Prints all directories inside the output folder.
    """
    if os.path.exists(output_folder):
        directories = [d for d in os.listdir(output_folder) if os.path.isdir(os.path.join(output_folder, d))]
        print("Model Directories:")
        for directory in directories:
            print(directory)
    else:
        print(f"The folder '{output_folder}' does not exist.")


#  https://huggingface.co/DeputyRipper/Morgan_Freeman_RVCV2/resolve/main/Morgan%20Freeman.zip?download=true 


get_model_file_paths("michael_caine")