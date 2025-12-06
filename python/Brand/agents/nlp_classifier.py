from sentence_transformers import SentenceTransformer, util

class SemanticBrandClassifier:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.brand_labels = ["Atomberg", "Havells", "Crompton", "Usha", "Orient", "Bajaj", "Luminous", "Superfan"]

        self.brand_embeddings = self.model.encode(self.brand_labels)

    def predict(self, text):
        query_emb = self.model.encode(text)
        scores = util.cos_sim(query_emb, self.brand_embeddings)[0]

        best_idx = int(scores.argmax().item())
        confidence = float(scores[best_idx].item())

        return self.brand_labels[best_idx], confidence
