import torch
import torch.nn as nn
import math

class MultiHeadAttention(nn.Module):
    def __init__(self, embed_size, heads):
        super(MultiHeadAttention, self).__init__()
        self.embed_size = embed_size
        self.heads = heads
        self.head_dim = embed_size // heads

        assert (
            self.head_dim * heads == embed_size
        ), "Embedding dimension needs to be divisible by heads"

        self.values = nn.Linear(self.head_dim, self.head_dim, bias=False)
        self.keys = nn.Linear(self.head_dim, self.head_dim, bias=False)
        self.queries = nn.Linear(self.head_dim, self.head_dim, bias=False)
        self.fc_out = nn.Linear(heads * self.head_dim, embed_size)

    def forward(self, values, keys, query, mask=None):
        N = query.shape[0]
        value_len, key_len, query_len = values.shape[1], keys.shape[1], query.shape[1]

        # Split embedding into self.heads pieces
        values = values.reshape(N, value_len, self.heads, self.head_dim)
        keys = keys.reshape(N, key_len, self.heads, self.head_dim)
        queries = query.reshape(N, query_len, self.heads, self.head_dim)

        values = self.values(values)
        keys = self.keys(keys)
        queries = self.queries(queries)

        # Calculate attention scores
        energy = torch.einsum("nqhd,nkhd->nhqk", [queries, keys])

        # Mask out the padding values
        if mask is not None:
            energy = energy.masked_fill(mask == 0, float("-1e20"))

        # Normalize the energy values
        attention = torch.softmax(energy / (self.embed_size ** (1 / 2)), dim=3)

        out = torch.einsum("nhql,nlhd->nqhd", [attention, values]).reshape(
            N, query_len, self.heads * self.head_dim
        )

        out = self.fc_out(out)
        return out, attention

# 测试
if __name__ == "__main__":
    # 创建一个随机矩阵作为输入
    embed_size = 512
    heads = 8
    seq_length = 10
    batch_size = 32
    x = torch.randn((batch_size, seq_length, embed_size))

    # 创建多头注意力机制实例
    attention = MultiHeadAttention(embed_size, heads)

    # 计算注意力权重
    out, att = attention(x, x, x)
    print("Attention weights shape:", att.shape)
    print("Output shape:", out.shape)