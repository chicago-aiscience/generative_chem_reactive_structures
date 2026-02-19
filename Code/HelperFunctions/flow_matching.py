import torch
from torch import nn


class FlowMatchingModel(nn.Module):
    def __init__(self, node_dim: int, hidden_dim: int = 64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(node_dim * 2 + 1, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, node_dim),
        )

    def forward(self, x_t: torch.Tensor, t: torch.Tensor, h: torch.Tensor):
        # x_t: [N, 3], h: [N, node_dim], t: [1] or [N, 1]
        if t.ndim == 0:
            t = t.view(1, 1).expand(x_t.shape[0], 1)
        if t.ndim == 1:
            t = t.view(-1, 1)
        t = t.expand(x_t.shape[0], 1)
        inp = torch.cat([x_t, h, t], dim=-1)
        return self.net(inp)


def sample_flow_targets(x0: torch.Tensor, x1: torch.Tensor, t: torch.Tensor):
    x_t = (1.0 - t) * x0 + t * x1
    v_target = x1 - x0
    return x_t, v_target
