# Bug Log

## Bug #1: Vector Embedding Type Mismatch in PostgreSQL


### Description

When implementing semantic similarity using sentence-transformers and pgvector, embeddings failed to store in PostgreSQL due to type mismatch between NumPy arrays and pgvector's expected format.

**Error Message**:
```
sqlalchemy.exc.DataError: (psycopg2.errors.InvalidParameterValue) 
malformed array literal: "embedding" 
DETAIL: Expected array element type double precision, got list.
```

---

### Root Cause

The sentence-transformers `model.encode()` returns a NumPy ndarray, but PostgreSQL's pgvector extension expects a Python list. The code was passing the ndarray directly without conversion.

**Code Before Fix**:
```python
# ai/service.py
def generate_embedding(self, text: str) -> List[float]:
    embedding = self.model.encode(text, convert_to_numpy=True)
    return embedding  # ❌ Returns ndarray, not list
```

---

### Solution

Added `.tolist()` conversion to transform NumPy arrays into Python lists compatible with pgvector:

```python
# ai/service.py
def generate_embedding(self, text: str) -> List[float]:
    """
    Generate semantic embedding vector for text using sentence-transformers
    """
    if not self.model:
        raise RuntimeError("AI Service not initialized")
    
    try:
        # Generate embedding
        embedding = self.model.encode(text, convert_to_numpy=True)
        # ✅ Convert NumPy array to Python list for SQLAlchemy/pgvector
        return embedding.tolist()
        
    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}")
        raise
```

---

### Impact

**Before Fix**:
- ❌ All incident creation failed with 500 errors
- ❌ No embeddings stored in database
- ❌ Similarity search completely non-functional
- ❌ Duplicate detection unavailable

**After Fix**:
- ✅ Embeddings store correctly in PostgreSQL
- ✅ Similarity search fully operational
- ✅ Duplicate detection works during submission
- ✅ All AI features functional

---

## Bug #2: AI Model Dependency Version Conflict


### Description

Docker build and application startup failed due to incompatible versions between `sentence-transformers` and `huggingface_hub` packages, preventing the AI service from initializing.

**Error Message**:
```
ImportError: cannot import name 'cached_download' from 'huggingface_hub' 
(/usr/local/lib/python3.11/site-packages/huggingface_hub/__init__.py)
```

---

### Root Cause

The `sentence-transformers==2.2.2` (old version) depended on `huggingface_hub<0.20` which included the `cached_download` function. However, pip installed the latest `huggingface_hub` (0.23+) which removed this function in favor of `hf_hub_download`.

**Dependency Conflict**:
- Old sentence-transformers expected: `huggingface_hub<0.20`
- Pip automatically installed: `huggingface_hub==0.23+`
- Result: Import error when loading AI models

---

### Solution

**Updated requirements.txt with compatible versions**:
```python
# Before (causing conflict)
sentence-transformers==2.2.2

# After (compatible versions)
sentence-transformers==2.7.0
transformers==4.38.0
torch==2.2.0
huggingface_hub==0.21.0
scikit-learn==1.3.2
numpy==1.24.3
nltk==3.8.1
```

**Additional Optimization**:
- Removed model download from Dockerfile build (caused timeouts and large image size)
- Models now download on first application startup
- Cached in Docker volumes for persistence across container restarts

---

### Impact

**Before Fix**:
- ❌ Docker build failed
- ❌ Backend container couldn't start
- ❌ AI Service initialization failed
- ❌ All AI features unavailable

**After Fix**:
- ✅ Docker build succeeds
- ✅ All containers start successfully
- ✅ AI models load correctly on startup
- ✅ Full AI functionality operational


---

## Summary

Both bugs were critical blocking issues that prevented the AI features from functioning:

1. **Type Conversion Bug**: Prevented embedding storage, blocking similarity detection
2. **Dependency Bug**: Prevented AI service initialization, blocking all AI features

Both were resolved through careful investigation, proper type handling, and dependency version management. The fixes ensure all 4 AI features (waste classification, similarity detection, keyword extraction, and admin summary) work reliably in production.````
