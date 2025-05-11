from torchvision.datasets import ImageFolder
from PIL import Image
import os

class SafeImageFolder(ImageFolder):
    def __getitem__(self, index):
        while True:
            try:
                path, target = self.samples[index]
                sample = self.loader(path)
                if self.transform is not None:
                    sample = self.transform(sample)
                if self.target_transform is not None:
                    target = self.target_transform(target)
                return sample, target
            except Exception as e:
                # print(f"Skipping corrupted image: {self.samples[index][0]} ({e})")
                index = (index + 1) % len(self.samples)  # Try next image