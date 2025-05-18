import numpy as np
import os
from sentence_transformers import SentenceTransformer
text = np.array([])
model = SentenceTransformer("intfloat/multilingual-e5-large") #  We could use different models here
for filename in os.listdir('Documents_TXT/'):
    with open(os.path.join('Documents_TXT/',filename),"r") as file:
        for line in file:
            text = np.append(text,{'text':line,'filename':filename})

from sklearn.metrics.pairwise import cosine_similarity
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain.vectorstores import FAISS
from tqdm import tqdm  # For progress bar

# Function to encode a batch of sentences along with their indices
def encode_batch(batch):
    indices, sentences = zip(*batch)
    embeddings = model.encode(sentences)
    return list(zip(indices, embeddings))

# The sentences to encode
sentences = [(i, textlines['text']) for i, textlines in enumerate(text)]  # List of (index, sentence) tuples

# Batch processing
batch_size = 20  # Adjust based on your memory and model capacity
sentence_embeddings = []

# Use ThreadPoolExecutor to parallelize the batch processing
with ThreadPoolExecutor() as executor:
    futures = []
    for i in range(0, len(sentences), batch_size):
        batch = sentences[i:i + batch_size]
        futures.append(executor.submit(encode_batch, batch))
    
    for future in tqdm(as_completed(futures), total=len(futures)):
        batch_embeddings = future.result()
        sentence_embeddings.extend(batch_embeddings)

# Add embeddings to the text array
for index, embedding in sentence_embeddings:
    text[index]['embedding'] = embedding

# Now the text array has embeddings added to each entry

np.save('Documents/text.npy', text) #save the text array to a file

# Load the text array with embeddings
text = np.load('Documents/text.npy', allow_pickle=True)

# Extract embeddings and convert to float32 numpy array
embeddings = np.stack([entry['embedding'] for entry in text]).astype('float32')

# Build FAISS index
dimension = embeddings.shape[1]

index.add(embeddings)

# Save the FAISS index
FAISS.write_index(index, 'Documents/faiss.index')