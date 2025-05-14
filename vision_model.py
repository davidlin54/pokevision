import torch
import torch.nn as nn
import torchvision.models as models

class PokemonClassifier(nn.Module):
    def __init__(self, num_classes):
        super(PokemonClassifier, self).__init__()

        # Pre-trained ResNet18 model
        self.model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)

        # Replace the final fully connected layer to match the number of classes
        self.model.fc = nn.Linear(self.model.fc.in_features, num_classes)

    def forward(self, x):
        return self.model(x)