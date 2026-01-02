
"""Lightweight EDI minimal LLM module with lazy imports to avoid heavy
import-time overhead.

This file historically imported PyTorch and transformers at module import
time which forces GPU/CPU initialization when other parts of the project
import EDI. To reduce overhead we lazily import heavy libraries and expose
informative errors when the ML stack is not available.
"""

import math
import os
from typing import Optional

# Lazy import helper: attempt to import heavy ML libs but don't fail on import
HAS_TORCH = False
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch.utils.data import Dataset, DataLoader
    from transformers import GPT2Tokenizer
    import requests
    HAS_TORCH = True
except Exception:
    # If imports fail, keep module importable; functions will raise if used.
    torch = None  # type: ignore
    nn = None  # type: ignore
    F = None  # type: ignore
    Dataset = object  # type: ignore
    DataLoader = object  # type: ignore
    GPT2Tokenizer = None  # type: ignore
    requests = None  # type: ignore


# Configuration for the model. Safe to create even without torch installed.
class Config:
    vocab_size = 50257
    block_size = 256
    n_layer = 12
    n_head = 12
    n_embd = 768
    dropout = 0.15
    batch_size = 16
    lr = 1e-4
    epochs = 4
    device = None


config = Config()
if HAS_TORCH:
    config.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


if HAS_TORCH:
    # Define model classes only when torch is available to avoid import-time cost.
    class SelfAttention(nn.Module):
        def __init__(self, config):
            super().__init__()
            self.n_head = config.n_head
            self.key = nn.Linear(config.n_embd, config.n_embd)
            self.query = nn.Linear(config.n_embd, config.n_embd)
            self.value = nn.Linear(config.n_embd, config.n_embd)
            self.proj = nn.Linear(config.n_embd, config.n_embd)
            self.dropout = nn.Dropout(config.dropout)

        def forward(self, x):
            B, T, C = x.size()
            k = self.key(x).view(B, T, self.n_head, C // self.n_head).transpose(1, 2)
            q = self.query(x).view(B, T, self.n_head, C // self.n_head).transpose(1, 2)
            v = self.value(x).view(B, T, self.n_head, C // self.n_head).transpose(1, 2)
            att = (q @ k.transpose(-2, -1)) / math.sqrt(C // self.n_head)
            att = F.softmax(att, dim=-1)
            att = self.dropout(att)
            y = att @ v
            y = y.transpose(1, 2).contiguous().view(B, T, C)
            return self.proj(y)


    class TransformerBlock(nn.Module):
        def __init__(self, config):
            super().__init__()
            self.ln1 = nn.LayerNorm(config.n_embd)
            self.attn = SelfAttention(config)
            self.ln2 = nn.LayerNorm(config.n_embd)
            self.mlp = nn.Sequential(
                nn.Linear(config.n_embd, 4 * config.n_embd),
                nn.GELU(),
                nn.Linear(4 * config.n_embd, config.n_embd),
                nn.Dropout(config.dropout),
            )

        def forward(self, x):
            x = x + self.attn(self.ln1(x))
            x = x + self.mlp(self.ln2(x))
            return x


    class MiniGPT(nn.Module):
        def __init__(self, config):
            super().__init__()
            self.token_emb = nn.Embedding(config.vocab_size, config.n_embd)
            self.pos_emb = nn.Embedding(config.block_size, config.n_embd)
            self.blocks = nn.ModuleList([TransformerBlock(config) for _ in range(config.n_layer)])
            self.ln_f = nn.LayerNorm(config.n_embd)
            self.head = nn.Linear(config.n_embd, config.vocab_size, bias=False)
            self.dropout = nn.Dropout(config.dropout)

        def forward(self, idx):
            B, T = idx.size()
            tok = self.token_emb(idx)
            pos = self.pos_emb(torch.arange(T, device=idx.device))[None, :, :]
            x = tok + pos
            for block in self.blocks:
                x = block(x)
            x = self.ln_f(x)
            x = self.dropout(x)
            logits = self.head(x)
            return logits


    # Tokenizer is loaded lazily when needed to avoid network/disk cost at import time.
    _tokenizer: Optional[GPT2Tokenizer] = None

    def _get_tokenizer() -> GPT2Tokenizer:
        global _tokenizer
        if _tokenizer is None:
            _tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
        return _tokenizer


    class WikiTextDataset(Dataset):
        def __init__(self, split='train', config=config):
            url = f'https://raw.githubusercontent.com/pytorch/examples/master/word_language_model/data/wikitext-2/{split}.txt'
            text = requests.get(url).text
            # Use more data for training
            tokens = _get_tokenizer()(text, return_tensors='pt', truncation=True, max_length=config.block_size * 2000)
            self.input_ids = tokens['input_ids'].view(-1, config.block_size)

        def __len__(self):
            return self.input_ids.size(0)

        def __getitem__(self, idx):
            return self.input_ids[idx]


    def train():
        model = MiniGPT(config).to(config.device)
        dataset = WikiTextDataset('train', config)
        loader = DataLoader(dataset, batch_size=config.batch_size, shuffle=True)
        optimizer = torch.optim.AdamW(model.parameters(), lr=config.lr)
        for epoch in range(config.epochs):
            print(f"Epoch {epoch+1}/{config.epochs}")
            for i, batch in enumerate(loader):
                batch = batch.to(config.device)
                logits = model(batch)
                loss = F.cross_entropy(logits.view(-1, config.vocab_size), batch.view(-1))
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                if i % 10 == 0:
                    print(f"Step {i}, Loss: {loss.item():.4f}")
                    # Generate sample output for quality check
                    sample_prompt = "EDI is an AI that "
                    print("Sample output:", generate(sample_prompt, model_path=None, model=model))
            torch.save(model.state_dict(), f'edi_minigpt_epoch{epoch+1}.pth')
            print(f"Checkpoint saved: edi_minigpt_epoch{epoch+1}.pth")


    def generate(prompt: str, model_path: str = 'edi_minigpt_epoch1.pth', max_new_tokens: int = 50, model: Optional[MiniGPT] = None) -> str:
        if model is None:
            model = MiniGPT(config).to(config.device)
            model.load_state_dict(torch.load(model_path, map_location=config.device))
        model.eval()
        tokenizer = _get_tokenizer()
        input_ids = tokenizer(prompt, return_tensors='pt').input_ids[:, :config.block_size].to(config.device)
        for _ in range(max_new_tokens):
            logits = model(input_ids)
            probs = torch.softmax(logits[:, -1, :], dim=-1)
            top_k = 10
            top_k_probs, top_k_indices = torch.topk(probs, top_k)
            next_token = top_k_indices[0, torch.multinomial(top_k_probs, 1)]
            next_token = next_token.unsqueeze(0).unsqueeze(0)
            input_ids = torch.cat([input_ids, next_token], dim=1)
            if input_ids.size(1) > config.block_size:
                input_ids = input_ids[:, -config.block_size:]
        return tokenizer.decode(input_ids[0])


else:
    # Lightweight stubs when heavy ML stack isn't available. These raise helpful
    # errors if called, avoiding silent failures.
    def train():
        raise RuntimeError("PyTorch not available: install torch and transformers to train EDI")


    def generate(*args, **kwargs):
        raise RuntimeError("PyTorch not available: install torch and transformers to run generation")


if __name__ == "__main__":
    # No-op main. Keep commands explicit to avoid accidental heavy operations on import.
    pass
