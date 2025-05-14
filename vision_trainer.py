import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms as transforms
from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader, random_split
from vision_model import PokemonClassifier
from safe_image_folder import SafeImageFolder
from tqdm import tqdm

# === Config ===
num_classes = 55865
image_size = 224
batch_size = 32
epochs = 10
learning_rate = 1e-4
eval_percentage = 0.1
num_workers = 4
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def main():
    # === Data Loaders ===
    transform = transforms.Compose([
        transforms.Resize((image_size, image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225]),
    ])

    full_dataset = SafeImageFolder("training", transform=transform, allow_empty=True)
    # === Calculate the split sizes ===
    total_size = len(full_dataset)
    eval_size = int(total_size * eval_percentage)
    train_size = total_size - eval_size

    # === Split the dataset into training and validation ===
    train_dataset, val_dataset = random_split(full_dataset, [train_size, eval_size])

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers, pin_memory=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, num_workers=num_workers, pin_memory=True)

    torch.set_float32_matmul_precision('high')

    # === Model ===
    model = PokemonClassifier(num_classes=num_classes).to(device)
    # model = torch.compile(model)

    # === Training Setup ===
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # === Training Loop ===
    for epoch in range(epochs):
        model.train()
        running_loss, correct, total = 0, 0, 0

        for imgs, labels in tqdm(train_loader):
            imgs, labels = imgs.to(device), labels.to(device)
            outputs = model(imgs)
            loss = criterion(outputs, labels)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            _, preds = torch.max(outputs, 1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

        acc = 100 * correct / total
        print(f"Epoch {epoch+1} - Loss: {running_loss:.4f} - Accuracy: {acc:.2f}%")

        # torch.save(model.state_dict(), 'trained_model.pth')

    # === Validation Accuracy ===
    model.eval()
    val_correct, val_total = 0, 0
    with torch.no_grad():
        for imgs, labels in val_loader:
            imgs, labels = imgs.to(device), labels.to(device)
            outputs = model(imgs)
            _, preds = torch.max(outputs, 1)
            val_correct += (preds == labels).sum().item()
            val_total += labels.size(0)

    print(f"Validation Accuracy: {100 * val_correct / val_total:.2f}%")

if __name__ == "__main__":
    main()