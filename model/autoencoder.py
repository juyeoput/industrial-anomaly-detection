from pathlib import Path
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix

from data_split import load_and_split

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

SENSOR_COLS = [f"xmeas_{i}" for i in range(1, 42)] + [f"xmv_{i}" for i in range(1, 12)]

if torch.cuda.is_available():
    DEVICE = torch.device("cuda")
elif torch.backends.mps.is_available():
    DEVICE = torch.device("mps")
else:
    DEVICE = torch.device("cpu")


def load_csv(filename):
    return pd.read_csv(DATA_DIR / filename)


class Autoencoder(nn.Module):
    def __init__(self, input_dim=52, bottleneck_dim=16):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, bottleneck_dim),
        )
        self.decoder = nn.Sequential(
            nn.Linear(bottleneck_dim, 16),
            nn.ReLU(),
            nn.Linear(16, 32),
            nn.ReLU(),
            nn.Linear(32, input_dim),
        )

    def forward(self, x):
        z = self.encoder(x)
        out = self.decoder(z)
        return out


def train_autoencoder(train_df, epochs=50, batch_size=256, lr=1e-3, random_state=42, bottleneck_dim=16):
    torch.manual_seed(random_state)

    scaler = StandardScaler()
    X_train = scaler.fit_transform(train_df[SENSOR_COLS])
    X_train_tensor = torch.tensor(X_train, dtype=torch.float32)

    dataset = TensorDataset(X_train_tensor, X_train_tensor)  # input == target for autoencoder
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    model = Autoencoder(input_dim=len(SENSOR_COLS), bottleneck_dim=bottleneck_dim).to(DEVICE)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()

    model.train()
    for epoch in range(epochs):
        total_loss = 0.0
        for X_batch, y_batch in loader:
            X_batch, y_batch = X_batch.to(DEVICE), y_batch.to(DEVICE)
            optimizer.zero_grad()
            output = model(X_batch)
            loss = criterion(output, y_batch)
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * X_batch.size(0)
        avg_loss = total_loss / len(dataset)
        print(f"Epoch {epoch+1}/{epochs} - reconstruction loss: {avg_loss:.6f}")

    return model, scaler


def compute_reconstruction_error(model, scaler, df):
    X = scaler.transform(df[SENSOR_COLS])
    X_tensor = torch.tensor(X, dtype=torch.float32).to(DEVICE)

    model.eval()
    with torch.no_grad():
        reconstructed = model(X_tensor)
        errors = torch.mean((X_tensor - reconstructed) ** 2, dim=1)

    return errors.cpu().numpy()


if __name__ == "__main__":
    print("1. Load & split (FaultFree Training)")
    train_df, val_df = load_and_split('TEP_FaultFree_Training.csv')
    print("Train shape:", train_df.shape)
    print("Val shape:", val_df.shape)

    print("\n2. Train Autoencoder (train split only)")
    model, scaler = train_autoencoder(train_df, bottleneck_dim=16, epochs=50)

    print("\n3. Sanity check on validation split")
    val_errors = compute_reconstruction_error(model, scaler, val_df)
    print(f"Validation reconstruction error -> mean: {val_errors.mean():.4f}, std: {val_errors.std():.4f}")