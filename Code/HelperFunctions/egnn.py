import torch
from torch import nn


class EGNN(nn.Module):
    def __init__(self, node_dim: int, hidden_dim: int = 64):
        super().__init__()
        self.edge_mlp = nn.Sequential(
            nn.Linear(node_dim * 2 + 1, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.SiLU(),
        )
        self.node_mlp = nn.Sequential(
            nn.Linear(node_dim + hidden_dim, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, node_dim),
        )
        self.coord_mlp = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, 1),
        )

    def forward(self, x: torch.Tensor, h: torch.Tensor):
        n = x.shape[0]
        xi = x.unsqueeze(1).expand(n, n, 3)
        xj = x.unsqueeze(0).expand(n, n, 3)
        hi = h.unsqueeze(1).expand(n, n, h.shape[-1])
        hj = h.unsqueeze(0).expand(n, n, h.shape[-1])

        rel = xi - xj
        dist2 = torch.sum(rel * rel, dim=-1, keepdim=True)
        edge_in = torch.cat([hi, hj, dist2], dim=-1)
        e = self.edge_mlp(edge_in)

        h_update = self.node_mlp(torch.cat([h, e.mean(dim=1)], dim=-1))
        h = h + h_update

        coord_coef = self.coord_mlp(e).squeeze(-1)
        coord_update = (coord_coef.unsqueeze(-1) * rel).mean(dim=1)
        x = x + coord_update

        return x, h
