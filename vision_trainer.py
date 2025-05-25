import os
import config
import json
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms as transforms
from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader
from vision_model import PokemonClassifier
from safe_image_folder import SafeImageFolder
from tqdm import tqdm

# === Config ===
batch_size = 32
epochs = 20
learning_rate = 1e-4
num_workers = 1
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# === Early Stopping Setup ===
best_val_loss = float('inf')
patience = 5
no_improve_epochs=0

def count_subfolders(path) -> int:
    return sum(
        os.path.isdir(os.path.join(path, entry)) 
        for entry in os.listdir(path)
    )

def load_state_dict(model):
    saved_state_dict = torch.load(config.model_checkpoint)
    new_state_dict = model.state_dict()

    # Filter out only the matching keys
    matched_state_dict = {k: v for k, v in saved_state_dict.items() if k in new_state_dict and v.size() == new_state_dict[k].size()}

    # Update the new model's state_dict with matched keys
    new_state_dict.update(matched_state_dict)

    # Load the updated state_dict into the new model
    model.load_state_dict(new_state_dict)


def main():
    num_classes = count_subfolders(config.training_dir)

    # === Data Loaders ===
    transform = transforms.Compose([
        transforms.Resize((config.image_size, config.image_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225]),
    ])

    train_dataset = SafeImageFolder(config.training_dir, transform=transform, allow_empty=True)
    val_dataset = SafeImageFolder(config.val_dir, transform=transform, allow_empty=True)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers, pin_memory=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, num_workers=num_workers, pin_memory=True)

    torch.set_float32_matmul_precision('high')

    # === Model ===
    model = PokemonClassifier(num_classes=num_classes).to(device)

    # === Training Setup ===
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # === Load saved state and run validation for current loss ===
    try:
        load_state_dict(model)

        model.eval()
        val_loss, val_correct, val_total = 0, 0, 0
        with torch.no_grad():
            for imgs, labels in tqdm(val_loader, desc='running validation with saved state'):
                imgs, labels = imgs.to(device), labels.to(device)
                outputs = model(imgs)
                loss = criterion(outputs, labels)

                val_loss += loss.item()
                _, preds = torch.max(outputs, 1)
                val_correct += (preds == labels).sum().item()
                val_total += labels.size(0)

                wrong_indices = preds != labels
                wrong_labels = labels[wrong_indices]
                print(wrong_labels)

        best_val_loss = val_loss

        print(f'loaded saved state with val loss {best_val_loss: .4f}')
    except Exception as e:
        print('no saved model found. ' + str(e))
    # model = torch.compile(model)

    # === Training Loop ===
    for epoch in range(epochs):
        model.train()
        running_loss, correct, total = 0, 0, 0

        for imgs, labels in tqdm(train_loader, desc='training epoch' + str(epoch)):
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

        train_acc = 100 * correct / total

        model.eval()
        val_loss, val_correct, val_total = 0, 0, 0
        with torch.no_grad():
            for imgs, labels in tqdm(val_loader, desc='validation epoch' + str(epoch)):
                imgs, labels = imgs.to(device), labels.to(device)
                outputs = model(imgs)
                loss = criterion(outputs, labels)

                val_loss += loss.item()
                _, preds = torch.max(outputs, 1)
                val_correct += (preds == labels).sum().item()
                val_total += labels.size(0)

        val_acc = 100 * val_correct / val_total

        print(f"Epoch {epoch+1} - Train Loss: {running_loss:.4f} | Train Acc: {train_acc:.2f}% | Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.2f}%")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            no_improve_epochs = 0
            torch.save(model.state_dict(), config.model_checkpoint)

            # === Save model classes for validation matching ===
            if os.path.exists(config.model_classes):
                os.remove(config.model_classes)

            with open(config.model_classes, "w") as f:
                json.dump(train_dataset.classes, f)

            print(f"Saved new best model (val loss improved to {val_loss:.4f})")
        else:
            no_improve_epochs += 1
            if no_improve_epochs >= patience:
                print(f"Early stopping at epoch {epoch+1} (no improvement in {patience} epochs).")
                break

if __name__ == "__main__":
    main()