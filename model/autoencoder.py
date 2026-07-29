# check 3, 5, 9, 10, 15, 16, 17, 18, 19, 20 only

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

SENSOR_COLS = [f"xmeas_{i}" for i in range(1, 42)] + [
    f"xmv_{i}" for i in range(1, 12)
]  # list[str], len 52

if torch.cuda.is_available():
    DEVICE = torch.device("cuda")
elif torch.backends.mps.is_available():
    DEVICE = torch.device("mps")
else:
    DEVICE = torch.device("cpu")


def load_csv(filename):
    return pd.read_csv(DATA_DIR / filename)  # pandas.DataFrame, shape (rows, 55)


class Autoencoder(nn.Module):
    def __init__(self, input_dim=52, bottleneck_dim=16):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 32),  # weight: (32, 52), bias: (32,)
            nn.ReLU(),
            nn.Linear(32, 16),  # weight: (16, 32), bias: (16,)
            nn.ReLU(),
            nn.Linear(
                16, bottleneck_dim
            ),  # weight: (bottleneck_dim, 16), bias: (bottleneck_dim,)
        )
        self.decoder = nn.Sequential(
            nn.Linear(bottleneck_dim, 16),  # weight: (16, bottleneck_dim), bias: (16,)
            nn.ReLU(),
            nn.Linear(16, 32),  # weight: (32, 16), bias: (32,)
            nn.ReLU(),
            nn.Linear(32, input_dim),  # weight: (52, 32), bias: (52,)
        )

    def forward(self, x):  # x: torch.Tensor, shape (batch_size, 52)
        z = self.encoder(x)  # torch.Tensor, shape (batch_size, bottleneck_dim)
        out = self.decoder(z)  # torch.Tensor, shape (batch_size, 52)
        return out


def train_autoencoder(
    train_df, epochs=50, batch_size=256, lr=1e-3, random_state=42, bottleneck_dim=16
):
    torch.manual_seed(random_state)

    scaler = StandardScaler()
    X_train = scaler.fit_transform(
        train_df[SENSOR_COLS]
    )  # numpy.ndarray, shape (n_rows, 52), dtype float64
    X_train_tensor = torch.tensor(
        X_train, dtype=torch.float32
    )  # torch.Tensor, shape (n_rows, 52), dtype float32

    dataset = TensorDataset(
        X_train_tensor, X_train_tensor
    )  # input == target for autoencoder
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    model = Autoencoder(input_dim=len(SENSOR_COLS), bottleneck_dim=bottleneck_dim).to(
        DEVICE
    )
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()

    model.train()
    for epoch in range(epochs):
        total_loss = 0.0  # python float
        for (
            X_batch,
            y_batch,
        ) in (
            loader
        ):  # X_batch, y_batch: torch.Tensor, shape (batch_size, 52), dtype float32 (last batch may be smaller)
            X_batch, y_batch = X_batch.to(DEVICE), y_batch.to(DEVICE)
            optimizer.zero_grad()
            output = model(X_batch)  # torch.Tensor, shape (batch_size, 52)
            loss = criterion(output, y_batch)  # torch.Tensor, shape () — scalar (0-dim)
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * X_batch.size(
                0
            )  # loss.item(): python float; X_batch.size(0): int (batch row count)
        avg_loss = total_loss / len(dataset)  # python float
        print(f"Epoch {epoch+1}/{epochs} - reconstruction loss: {avg_loss:.6f}")

    return model, scaler


def compute_reconstruction_error(model, scaler, df):
    X = scaler.transform(
        df[SENSOR_COLS]
    )  # numpy.ndarray, shape (n_rows, 52), dtype float64
    X_tensor = torch.tensor(X, dtype=torch.float32).to(
        DEVICE
    )  # torch.Tensor, shape (n_rows, 52), dtype float32

    model.eval()
    with torch.no_grad():
        reconstructed = model(X_tensor)  # torch.Tensor, shape (n_rows, 52)
        errors = torch.mean(
            (X_tensor - reconstructed) ** 2, dim=1
        )  # torch.Tensor, shape (n_rows,) — 1D vector

    return errors.cpu().numpy()  # numpy.ndarray, shape (n_rows,), dtype float32


def set_threshold(model, scaler, faultfree_testing_df, target_fpr=0.05):
    normal_df = faultfree_testing_df[faultfree_testing_df["faultNumber"] == 0]
    errors = compute_reconstruction_error(model, scaler, normal_df)

    threshold = np.percentile(errors, (1 - target_fpr) * 100)

    predicted_anomaly = errors > threshold
    actual_fpr = predicted_anomaly.mean()
    print(f"Target FPR: {target_fpr}, Actual FPR: {actual_fpr:.4f}")
    print(
        f"Target FPR: {target_fpr}, Actual FPR: {actual_fpr:.4f}, Threshold: {threshold:.6f}"
    )  # Threshold
    print(
        f"  Normal errors -> mean: {errors.mean():.6f}, std: {errors.std():.6f}"
    )  # distribution
    return threshold


def evaluate_on_faulty(model, scaler, threshold, faulty_testing_df, sample_cutoff=160):
    df = faulty_testing_df.copy()
    df["true_label"] = (df["sample"] >= sample_cutoff).astype(int)

    errors = compute_reconstruction_error(model, scaler, df)

    fault_errors = errors[df["true_label"] == 1]
    print(
        f"  Fault errors -> mean: {fault_errors.mean():.6f}, std: {fault_errors.std():.6f}"
    )

    df["predicted_label"] = (errors > threshold).astype(int)

    precision = precision_score(df["true_label"], df["predicted_label"])
    recall = recall_score(df["true_label"], df["predicted_label"])
    f1 = f1_score(df["true_label"], df["predicted_label"])
    cm = confusion_matrix(df["true_label"], df["predicted_label"])

    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1: {f1:.4f}")
    print("Confusion Matrix:\n", cm)

    return {"precision": precision, "recall": recall, "f1": f1, "confusion_matrix": cm}


def evaluate_by_fault(
    model, scaler, threshold, faulty_testing_df, sample_cutoff=160, late_start=None
):
    df = faulty_testing_df.copy()
    df["true_label"] = (df["sample"] >= sample_cutoff).astype(int)

    errors = compute_reconstruction_error(model, scaler, df)
    df["predicted_label"] = (errors > threshold).astype(int)

    anomaly_only = df[df["true_label"] == 1]
    if late_start is not None:
        anomaly_only = anomaly_only[anomaly_only["sample"] >= late_start]

    label = f"Recall (sample>={late_start})" if late_start else "Recall (full)"
    print(f"{'Fault':<8}{label:<20}{'Caught':<12}{'Missed'}")
    for fault_num in sorted(anomaly_only["faultNumber"].unique()):
        subset = anomaly_only[anomaly_only["faultNumber"] == fault_num]
        caught = subset["predicted_label"].sum()
        total = len(subset)
        recall = caught / total
        print(f"{fault_num:<8}{recall:<20.4f}{caught:<12}{total - caught}")


if __name__ == "__main__":
    print("1. Load & split (FaultFree Training)")
    train_df, val_df = load_and_split(
        "TEP_FaultFree_Training.csv"
    )  # train_df: DataFrame (400 runs), val_df: DataFrame (100 runs)
    print("Train shape:", train_df.shape)  # (200000, 55)
    print("Val shape:", val_df.shape)  # (50000, 55)

    print("\n2. Train Autoencoder (train split only)")
    model, scaler = train_autoencoder(
        train_df, bottleneck_dim=16, epochs=50
    )  # model: Autoencoder, scaler: StandardScaler

    print("\n3. Sanity check on validation split")
    val_errors = compute_reconstruction_error(
        model, scaler, val_df
    )  # numpy.ndarray, shape (50000,)
    print(
        f"Validation reconstruction error -> mean: {val_errors.mean():.4f}, std: {val_errors.std():.4f}"
    )

    print("\n4. Set threshold (FaultFree Testing)")
    faultfree_testing_df = load_csv("TEP_FaultFree_Testing.csv")
    threshold = set_threshold(model, scaler, faultfree_testing_df, target_fpr=0.05)

    print("\n5. Final evaluation (Faulty Testing)")
    faulty_testing_df = load_csv("TEP_Faulty_Testing.csv")
    results = evaluate_on_faulty(model, scaler, threshold, faulty_testing_df)

    print("\n6. Recall by fault number (full anomaly window)")
    evaluate_by_fault(model, scaler, threshold, faulty_testing_df)

    print("\n7. Recall by fault number (late window only)")
    evaluate_by_fault(model, scaler, threshold, faulty_testing_df, late_start=300)
