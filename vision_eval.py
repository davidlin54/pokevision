import os
import config
import sys
import torch
import time
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
from vision_model import PokemonClassifier
from vision_trainer import count_subfolders, load_state_dict
from safe_image_folder import SafeImageFolder
from PIL import Image

# === Config ===
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def main(image_path: str):
    num_classes = count_subfolders(config.training_dir)

    # === Data Loaders ===
    transform = transforms.Compose([
        transforms.Resize((config.image_size, config.image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225]),
    ])

    image = Image.open(image_path).convert('RGB')
    input_tensor = transform(image).unsqueeze(0).to(device)

    torch.set_float32_matmul_precision('high')

    # === Model ===
    model = PokemonClassifier(num_classes=num_classes).to(device)

    # === Load saved state and run inference ===
    model.load_state_dict(torch.load(config.model_checkpoint))

    model.eval()
    with torch.no_grad():
        start = time.perf_counter()
        output = model(input_tensor)
        end = time.perf_counter()
        total_time = (end - start)
        probabilities = torch.softmax(output, dim=1)
        top_k = torch.topk(probabilities, k=config.return_k_results, dim=1)

    train_dataset = SafeImageFolder(config.training_dir, allow_empty=True)
    class_names = train_dataset.classes

    for i in range(5):
        class_id = top_k.indices[0][i].item()
        prob = top_k.values[0][i].item()
        print(f"{i+1}: {class_names[class_id]} ({prob:.4f})")

if __name__ == "__main__":
    image_path = sys.argv[1]
    main(image_path)