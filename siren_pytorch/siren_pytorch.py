import torch
import math
from torch import nn
import torch.nn.functional as F

# siren initialization

def init_(weight, bias, c = 6., w0 = 1.):
    dim = weight.size(1)
    std = 1 / math.sqrt(dim)

    w_std = math.sqrt(c) * std / w0
    weight.uniform_(-w_std, w_std)

    if bias is not None:
        bias.uniform_(-std, std)

# sin activation

class Sine(nn.Module):
    def __init__(self, w0 = 1.):
        super().__init__()
        self.w0 = w0
    def forward(self, x):
        return torch.sin(self.w0 * x)

# siren layer

class Siren(nn.Module):
    def __init__(self, dim_in, dim_out, w0 = 1., c = 6., use_bias = True, activation = None):
        super().__init__()
        weight = torch.zeros(dim_out, dim_in)
        bias = torch.zeros(dim_out) if use_bias else None
        init_(weight, bias, c = c, w0 = w0)

        self.weight = nn.Parameter(weight)
        self.bias = nn.Parameter(bias) if use_bias else None
        self.activation = Sine(w0) if activation is None else activation

    def forward(self, x):
        out =  F.linear(x, self.weight, self.bias)
        out = self.activation(out)
        return out

# siren network

class SirenNet(nn.Module):
    def __init__(self, dim_in, dim_hidden, dim_out, num_layers, w0 = 1., w0_initial = 30., use_bias = True, final_activation = None):
        super().__init__()
        layers = []
        for ind in range(num_layers):
            layer_w0 = w0_initial if ind == 0 else w0
            layer_dim_in = dim_in if ind == 0 else dim_hidden

            layers.append(Siren(
                dim_in = layer_dim_in,
                dim_out = dim_hidden,
                w0 = layer_w0,
                use_bias = use_bias
            ))

        self.net = nn.Sequential(*layers)
        self.last_layer = Siren(dim_in = dim_hidden, dim_out = dim_out, w0 = w0, use_bias = use_bias, activation = final_activation)

    def forward(self, x):
        x = self.net(x)
        return self.last_layer(x)
