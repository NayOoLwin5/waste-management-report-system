"""
AI Service - Offline Machine Learning Features

This service implements multiple AI features using only offline/local models:
1. Waste Type Classification using TF-IDF and rule-based matching
2. Semantic Similarity Detection using sentence-transformers
3. Keyword Extraction using NLP
4. Duplicate/Similar Incident Detection using vector embeddings
"""
from typing import List, Dict, Any, Tuple, Optional
from uuid import UUID
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.config import settings
from app.core.logging import logger


class AIService:
    """
    AI Service for offline machine learning features
    No external API calls - all processing done locally
    """
    
    # Waste category definitions for semantic classification
    # Each category has a detailed description that captures its semantic meaning
    WASTE_CATEGORY_DESCRIPTIONS = {
        "plastic": "Plastic waste including bottles, bags, packaging, containers, wrappers, polythene, polyethylene, PET bottles, HDPE containers, PVC materials, straws, cups, lids, plastic film, and synthetic polymers",
        "organic": "Organic and biodegradable waste including food scraps, kitchen waste, vegetables, fruits, compostable materials, garden waste, plant matter, banana peels, apple cores, leftovers, spoiled food, rotten produce, and natural biodegradable matter",
        "paper": "Paper and cardboard waste including newspapers, magazines, cardboard boxes, cartons, tissue paper, documents, books, notebooks, envelopes, and paper packaging materials",
        "glass": "Glass waste including bottles, jars, broken glass, window glass, mirrors, wine bottles, beer bottles, glassware, and glass containers",
        "metal": "Metal waste including cans, aluminum, steel, tin, iron, copper, metal foil, wire, scrap metal, batteries with metal components, and metallic materials",
        "electronic": "Electronic waste and e-waste including computers, phones, mobile devices, laptops, televisions, monitors, cables, chargers, batteries, appliances, electronic devices, and gadgets",
        "hazardous": "Hazardous and toxic waste including chemicals, toxic substances, paint, oil, solvents, batteries, pesticides, medicines, pharmaceuticals, dangerous materials, flammable substances, and corrosive materials",
        "textile": "Textile and fabric waste including clothing, fabric scraps, cloth, clothes, shirts, pants, dresses, shoes, leather items, and rags",
        "construction": "Construction and demolition waste including concrete, bricks, wood, debris, rubble, tiles, drywall, lumber, and building materials",
        "mixed": "Mixed and general waste including household waste, municipal waste, various types of waste, assorted waste materials, multiple waste types, and diverse waste materials"
    }
    
    # Fallback keywords for edge cases (kept for backward compatibility)
    WASTE_CATEGORIES = {
        "plastic": [
            "plastic", "bottle", "bag", "packaging", "container", "wrapper",
            "polythene", "polyethylene", "pet", "hdpe", "pvc", "straw",
            "cup", "lid", "film"
        ],
        "organic": [
            "food", "organic", "kitchen", "vegetable", "fruit", "compost",
            "biodegradable", "garden", "plant", "waste", "banana", "apple",
            "leftover", "spoiled", "rotten"
        ],
        "paper": [
            "paper", "cardboard", "newspaper", "magazine", "box", "carton",
            "tissue", "document", "book", "notebook", "envelope"
        ],
        "glass": [
            "glass", "bottle", "jar", "window", "broken glass", "mirror",
            "wine bottle", "beer bottle", "glassware"
        ],
        "metal": [
            "metal", "can", "aluminum", "steel", "tin", "iron", "copper",
            "foil", "wire", "scrap metal", "battery"
        ],
        "electronic": [
            "electronic", "e-waste", "computer", "phone", "mobile", "laptop",
            "television", "tv", "monitor", "cable", "charger", "battery",
            "appliance", "device", "gadget"
        ],
        "hazardous": [
            "chemical", "hazardous", "toxic", "paint", "oil", "solvent",
            "battery", "pesticide", "medicine", "pharmaceutical", "dangerous",
            "flammable", "corrosive"
        ],
        "textile": [
            "clothing", "fabric", "textile", "cloth", "clothes", "shirt",
            "pants", "dress", "shoes", "leather", "rag"
        ],
        "construction": [
            "construction", "demolition", "concrete", "brick", "wood",
            "debris", "rubble", "tile", "drywall", "lumber"
        ],
        "mixed": [
            "mixed", "general", "household", "municipal", "various",
            "assorted", "multiple", "diverse"
        ]
    }
    
    _instance: Optional['AIService'] = None
    _initialized: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'model'):
            self.model: Optional[SentenceTransformer] = None
            self.tfidf_vectorizer: Optional[TfidfVectorizer] = None
            self.stopwords = set()
            self.category_embeddings: Dict[str, np.ndarray] = {}
        
    async def initialize(self):
        """Initialize AI models and NLP resources"""
        if AIService._initialized:
            logger.debug("AI Service already initialized, skipping")
            return
            
        logger.info("Initializing AI Service")
        
        try:
            # Download NLTK data
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt', quiet=True)
            
            try:
                nltk.data.find('corpora/stopwords')
            except LookupError:
                nltk.download('stopwords', quiet=True)
            
            self.stopwords = set(stopwords.words('english'))
            
            # Initialize sentence transformer model (offline, pre-trained)
            logger.info(f"Loading sentence transformer model: {settings.AI_MODEL_NAME}")
            self.model = SentenceTransformer(settings.AI_MODEL_NAME)
            
            # Initialize TF-IDF vectorizer
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            # Pre-compute embeddings for waste categories (for semantic classification)
            logger.info("Pre-computing waste category embeddings for semantic classification")
            for category, description in self.WASTE_CATEGORY_DESCRIPTIONS.items():
                self.category_embeddings[category] = self.model.encode(
                    description, 
                    convert_to_numpy=True
                )
            logger.info(f"Pre-computed embeddings for {len(self.category_embeddings)} waste categories")
            
            AIService._initialized = True
            logger.info("AI Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AI Service: {str(e)}", exc_info=True)
            raise
    
    def classify_waste_type(self, description: str) -> Tuple[str, float]:
        """
        Classify waste type using hybrid AI approach:
        1. Primary: Semantic similarity with category embeddings (AI-powered)
        2. Fallback: Keyword matching for edge cases
        
        Returns: (waste_type, confidence_score)
        """
        if not self.model or not self.category_embeddings:
            raise RuntimeError("AI Service not initialized")
        
        try:
            # Stage 1: Semantic Classification (AI-powered)
            # Generate embedding for the incident description
            description_embedding = self.model.encode(description, convert_to_numpy=True)
            
            # Calculate cosine similarity with each waste category
            semantic_scores = {}
            for category, category_embedding in self.category_embeddings.items():
                similarity = cosine_similarity(
                    description_embedding.reshape(1, -1),
                    category_embedding.reshape(1, -1)
                )[0][0]
                semantic_scores[category] = float(similarity)
            
            # Get best semantic match
            best_semantic_category = max(semantic_scores.items(), key=lambda x: x[1])
            semantic_category = best_semantic_category[0]
            semantic_confidence = best_semantic_category[1]
            
            # Stage 2: Keyword Matching (Fallback/Booster)
            description_lower = description.lower()
            keyword_scores = {}
            
            for category, keywords in self.WASTE_CATEGORIES.items():
                score = 0
                matches = 0
                
                for keyword in keywords:
                    if keyword in description_lower:
                        matches += 1
                        # Weight longer keywords more heavily
                        score += len(keyword.split())
                
                if matches > 0:
                    # Normalize score
                    keyword_scores[category] = score / len(keywords)
            
            # Decision Logic: Combine semantic and keyword approaches
            
            # Case 1: High semantic confidence (>= 0.50) - trust AI
            if semantic_confidence >= 0.50:
                # If keywords also match, boost confidence
                keyword_boost = keyword_scores.get(semantic_category, 0) * 0.2
                final_confidence = min(semantic_confidence + keyword_boost, 1.0)
                
                logger.debug(
                    "Classification (semantic primary)",
                    category=semantic_category,
                    semantic_conf=round(semantic_confidence, 3),
                    keyword_boost=round(keyword_boost, 3),
                    final_conf=round(final_confidence, 3)
                )
                
                return semantic_category, round(final_confidence, 2)
            
            # Case 2: Low semantic confidence but strong keyword match - use keywords
            if keyword_scores:
                best_keyword_match = max(keyword_scores.items(), key=lambda x: x[1])
                keyword_category = best_keyword_match[0]
                keyword_confidence = min(best_keyword_match[1] * 2, 1.0)
                
                # If semantic also weakly agrees, boost confidence
                if semantic_category == keyword_category:
                    semantic_boost = semantic_confidence * 0.3
                    final_confidence = min(keyword_confidence + semantic_boost, 1.0)
                else:
                    final_confidence = keyword_confidence
                
                logger.debug(
                    "Classification (keyword primary)",
                    category=keyword_category,
                    keyword_conf=round(keyword_confidence, 3),
                    semantic_conf=round(semantic_confidence, 3),
                    final_conf=round(final_confidence, 3)
                )
                
                return keyword_category, round(final_confidence, 2)
            
            # Case 3: No strong signals - return semantic with low confidence
            logger.debug(
                "Classification (low confidence)",
                category=semantic_category,
                semantic_conf=round(semantic_confidence, 3)
            )
            
            return semantic_category, round(semantic_confidence, 2)
            
        except Exception as e:
            logger.error(f"Error in semantic classification: {str(e)}", exc_info=True)
            # Fallback to keyword-only classification
            return self._classify_by_keywords_only(description)
    
    def _classify_by_keywords_only(self, description: str) -> Tuple[str, float]:
        """
        Fallback method: Classify using only keyword matching
        Used when semantic classification fails
        """
        description_lower = description.lower()
        
        scores = {}
        for category, keywords in self.WASTE_CATEGORIES.items():
            score = 0
            matches = 0
            
            for keyword in keywords:
                if keyword in description_lower:
                    matches += 1
                    score += len(keyword.split())
            
            if matches > 0:
                scores[category] = score / len(keywords)
        
        if not scores:
            return "unclassified", 0.0
        
        best_category = max(scores.items(), key=lambda x: x[1])
        max_score = best_category[1]
        confidence = min(max_score * 2, 1.0)
        
        logger.warning(
            "Using fallback keyword classification",
            category=best_category[0],
            confidence=round(confidence, 2)
        )
        
        return best_category[0], round(confidence, 2)
    
    def extract_keywords(self, description: str, top_n: int = 5) -> List[str]:
        """
        Extract important keywords from description using NLP
        """
        try:
            # Tokenize and clean
            tokens = word_tokenize(description.lower())
            
            # Remove stopwords and non-alphabetic tokens
            keywords = [
                word for word in tokens 
                if word.isalpha() 
                and word not in self.stopwords 
                and len(word) > 2
            ]
            
            # Get frequency
            word_freq = {}
            for word in keywords:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Sort by frequency and return top N
            sorted_keywords = sorted(
                word_freq.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            return [word for word, freq in sorted_keywords[:top_n]]
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {str(e)}")
            return []
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate semantic embedding vector for text using sentence-transformers
        """
        if not self.model:
            raise RuntimeError("AI Service not initialized")
        
        try:
            # Generate embedding
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    async def process_incident(
        self,
        description: str,
        location: str
    ) -> Dict[str, Any]:
        """
        Process incident with all AI features
        Returns dict with waste_type, confidence, embedding, keywords
        """
        try:
            # Classify waste type
            waste_type, confidence = self.classify_waste_type(description)
            
            # Extract keywords
            keywords = self.extract_keywords(description)
            
            # Generate embedding for similarity search
            combined_text = f"{description} {location}"
            embedding = self.generate_embedding(combined_text)
            
            result = {
                "waste_type": waste_type,
                "confidence": confidence,
                "keywords": keywords,
                "embedding": embedding
            }
            
            logger.info(
                "Incident processed",
                waste_type=waste_type,
                confidence=confidence,
                keywords=keywords[:3]
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing incident: {str(e)}", exc_info=True)
            raise
    
    async def find_similar_incidents(
        self,
        db: AsyncSession,
        current_incident_id: UUID,
        embedding: List[float],
        threshold: float = None,
        limit: int = 5
    ) -> List[Any]:
        """
        Find similar incidents using vector similarity search
        """
        if threshold is None:
            threshold = settings.SIMILARITY_THRESHOLD
        
        try:
            from app.modules.incidents.models import Incident
            
            # Get all incidents with embeddings (excluding current)
            query = select(Incident).where(
                Incident.id != current_incident_id,
                Incident.embedding.isnot(None)
            )
            
            result = await db.execute(query)
            all_incidents = result.scalars().all()
            
            if not all_incidents:
                return []
            
            # Calculate cosine similarity
            current_embedding = np.array(embedding).reshape(1, -1)
            similarities = []
            
            for incident in all_incidents:
                if incident.embedding is not None and len(incident.embedding) > 0:
                    incident_embedding = np.array(incident.embedding).reshape(1, -1)
                    similarity = cosine_similarity(current_embedding, incident_embedding)[0][0]
                    
                    if similarity >= threshold:
                        similarities.append((incident, float(similarity)))
            
            # Sort by similarity (descending) and return top N
            similarities.sort(key=lambda x: x[1], reverse=True)
            similar_incidents = [inc for inc, sim in similarities[:limit]]
            
            logger.info(
                "Similar incidents found",
                count=len(similar_incidents),
                threshold=threshold
            )
            
            return similar_incidents
            
        except Exception as e:
            logger.error(f"Error finding similar incidents: {str(e)}", exc_info=True)
            return []
