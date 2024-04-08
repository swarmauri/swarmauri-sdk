import dgl
import torch
import torch.nn.functional as F
import numpy as np
from dgl.nn import GraphConv
from typing import List, Union, Any
from swarmauri.core.vectorizers.IVectorize import IVectorize
from swarmauri.core.vectors.IVector import IVector
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector

class DGLGraphConv(torch.nn.Module):
    def __init__(self, in_feats, out_feats, activation=F.relu):
        super(DGLGraphConv, self).__init__()
        self.conv1 = GraphConv(in_feats, 128)
        self.conv2 = GraphConv(128, out_feats)
        self.activation = activation

    def forward(self, g, inputs):
        # Apply graph convolution and activation.
        h = self.conv1(g, inputs)
        h = self.activation(h)
        h = self.conv2(g, h)
        return h

class DGLVectorizer(IVectorize):
    def __init__(self, in_feats, out_feats, model=None):
        self.in_feats = in_feats
        self.out_feats = out_feats
        self.model = model or DGLGraphConv(in_feats, out_feats)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
    def fit(self, graphs, features, epochs=10, learning_rate=0.01):
        self.model.to(self.device)
        optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        for epoch in range(epochs):
            for g, feat in zip(graphs, features):
                g = g.to(self.device)
                feat = feat.to(self.device)
                outputs = self.model(g, feat)
                loss = F.mse_loss(outputs, feat)  # Example loss; adjust as needed
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
            print(f'Epoch {epoch + 1}, Loss: {loss.item()}')
    
    def infer_vector(self, graph, features):
        graph = graph.to(self.device)
        features = features.to(self.device)
        with torch.no_grad():
            embeddings = self.model(graph, features)
        return SimpleVector(embeddings.cpu().numpy())