from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import mean_absolute_error, mean_squared_error
from torch.utils.data import DataLoader, TensorDataset


class VolatilityTransformer(nn.Module):
    def __init__(self, input_dim: int, d_model: int = 64, nhead: int = 4, num_layers: int = 2):
        super().__init__()
        self.input_projection = nn.Linear(input_dim, d_model)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=d_model * 2,
            dropout=0.1,
            batch_first=True,
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.head = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.ReLU(),
            nn.Linear(d_model // 2, 1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = self.input_projection(x)
        encoded = self.encoder(z)
        pooled = encoded[:, -1, :]
        return self.head(pooled).squeeze(-1)


@dataclass
class TrainConfig:
    epochs: int = 20
    batch_size: int = 64
    learning_rate: float = 1e-3


def train_model(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_val: np.ndarray,
    y_val: np.ndarray,
    config: TrainConfig,
) -> Tuple[VolatilityTransformer, Dict[str, float]]:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = VolatilityTransformer(input_dim=x_train.shape[-1]).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate)
    criterion = nn.MSELoss()

    train_loader = DataLoader(
        TensorDataset(torch.tensor(x_train), torch.tensor(y_train)),
        batch_size=config.batch_size,
        shuffle=True,
    )

    for _ in range(config.epochs):
        model.train()
        for xb, yb in train_loader:
            xb = xb.to(device)
            yb = yb.to(device)
            pred = model(xb)
            loss = criterion(pred, yb)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

    metrics = evaluate_model(model, x_val, y_val)
    return model, metrics


@torch.inference_mode()
def evaluate_model(model: VolatilityTransformer, x: np.ndarray, y: np.ndarray) -> Dict[str, float]:
    device = next(model.parameters()).device
    model.eval()

    xb = torch.tensor(x).to(device)
    pred = model(xb).detach().cpu().numpy()

    mae = mean_absolute_error(y, pred)
    rmse = mean_squared_error(y, pred) ** 0.5

    actual_direction = np.sign(np.diff(y))
    pred_direction = np.sign(np.diff(pred))
    directional_acc = float((actual_direction == pred_direction).mean()) if len(actual_direction) > 0 else 0.0

    return {
        "mae": float(mae),
        "rmse": float(rmse),
        "directional_accuracy": directional_acc,
    }


@torch.inference_mode()
def predict_next_volatility(model: VolatilityTransformer, x_latest: np.ndarray) -> float:
    device = next(model.parameters()).device
    model.eval()
    xb = torch.tensor(x_latest[None, ...], dtype=torch.float32).to(device)
    pred = model(xb).item()
    return float(pred)
