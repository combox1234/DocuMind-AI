"""LLM service using Ollama for response generation and semantic operations"""
import ollama
import logging
import re
from typing import Tuple, List, Dict, Optional
from sentence_transformers import CrossEncoder
from core.classifier import DocumentClassifier

logger = logging.getLogger(__name__)


class LLMService:
    """Handles LLM operations for query generation, response generation, and semantic operations"""
    
    def __init__(self, model: str = "llama3.2"):
        self.model = model
        self.classifier = DocumentClassifier()
        try:
            logger.info("Loading CrossEncoder model for re-ranking...")
            self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', max_length=512)
            logger.info("CrossEncoder loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load CrossEncoder: {e}")
            self.reranker = None
        logger.info(f"LLM Service initialized with model: {model}")
    
    def classify_hierarchical(self, text: str, filename: str = "") -> Dict:
        """Classify content into hierarchical structure: Domain > Category > FileType
        
        Delegates to DocumentClassifier for optimized classification.
        """
        return self.classifier.classify_hierarchical(text, filename)
    
    def _calculate_confidence(self, query: str, chunks: List[dict]) -> float:
        """Calculate confidence score (0-100) for the answer"""
        if not chunks:
            return 0.0
        
        avg_similarity = sum(chunk.get('similarity', 0) for chunk in chunks) / len(chunks)
        chunk_bonus = min(len(chunks) / 5.0, 1.0)
        avg_distance = sum(chunk.get('distance', 2.0) for chunk in chunks) / len(chunks)
        distance_confidence = max(0, 1.0 - (avg_distance / 2.0))
        
        confidence = (avg_similarity * 0.4 + chunk_bonus * 0.3 + distance_confidence * 0.3)
        confidence_score = int(confidence * 100)
        return max(0, min(100, confidence_score))
    
    def _get_confidence_level(self, score: int) -> str:
        """Get confidence level label"""
        if score >= 75:
            return "🟢 HIGH"
        elif score >= 40:
            return "🟡 MEDIUM"
        else:
            return "🔴 LOW"

    def _rerank_chunks(self, query: str, chunks: List[dict], top_k: int = 5) -> List[dict]:
        """Re-rank chunks using Cross-Encoder"""
        if not self.reranker or not chunks:
            return chunks[:top_k]
            
        try:
            # Create pairs of (query, document_text)
            pairs = [[query, chunk['text']] for chunk in chunks]
            
            # Predict scores
            scores = self.reranker.predict(pairs)
            
            # Attach scores to chunks
            for i, chunk in enumerate(chunks):
                chunk['relevance_score'] = float(scores[i])
                
            # Sort by new relevance score
            reranked = sorted(chunks, key=lambda x: x['relevance_score'], reverse=True)
            
            logger.info(f"Re-ranking complete. Top chunk: {reranked[0].get('filename')} (Score: {reranked[0].get('relevance_score'):.4f})")
            return reranked[:top_k]
            
        except Exception as e:
            logger.error(f"Re-ranking failed: {e}")
            return chunks[:top_k]
    
    def generate_response(self, query: str, context_chunks: List[dict]) -> Tuple[str, List[str], float, List[dict]]:
        """Generate response STRICTLY from documents only - no external knowledge"""
        
        if not context_chunks:
            # No documents found - cannot answer
            return "I don't have this information in your documents. Please upload relevant documents or ask questions about the documents you've provided.", [], 0, []
        
        # Relevance filter: prefer chunks containing query keywords
        keywords = [w.strip().lower() for w in re.split(r"[^A-Za-z0-9]+", query) if len(w.strip()) > 2]
        def relevance(c):
            text = c.get('text', '').lower()
            hits = sum(1 for k in keywords if k and k in text)
            sim = float(c.get('similarity', 0) or 0)
            return hits * 2 + sim
        
        # Re-rank deeper pool of chunks (using CrossEncoder)
        context_chunks = self._rerank_chunks(query, context_chunks, top_k=5)
        
        logger.info(f"LLM Processing: {len(context_chunks)} chunks for query: '{query}'")
        if context_chunks:
            # Noise Filter: Remove chunks with very low scores (likely irrelevant)
            # Valid matches usually score > 0. Ambiguous match ~ -2 to 0. Irrelevant < -5.
            # We use a threshold of -3.0 to keep "maybe" relevant but strict enough to hide noise.
            context_chunks = [c for c in context_chunks if c.get('relevance_score', 0) > -3.0]
            
            if not context_chunks:
                 logger.warning("All chunks filtered out by Noise Filter. Returning top 1 fallback.")
                 # Fallback: if everything is filtered, return at least one
                 # (But ideally we should return "I don't know")
                
            logger.info(f"Top 5 Filenames (Filtered): {[c.get('filename') for c in context_chunks]}")
            for i, c in enumerate(context_chunks):
                logger.info(f"Chunk {i+1} ({c['filename']}): {c['text'][:100]}...")
            
        confidence_score = self._calculate_confidence(query, context_chunks)
        confidence_level = self._get_confidence_level(confidence_score)
        
        source_snippets = []
        for i, chunk in enumerate(context_chunks, 1):
            snippet = {
                'id': i,
                'filename': chunk['filename'],
                'category': chunk.get('category', 'Unknown'),
                'text': chunk['text'][:300] + '...' if len(chunk['text']) > 300 else chunk['text'],
                'similarity': chunk.get('similarity', 0),
                'relevance_pct': int(chunk.get('similarity', 0) * 100)
            }
            source_snippets.append(snippet)
        
        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            source_info = f"[Source {i}: {chunk['filename']}]"
            context_parts.append(f"{source_info}\n{chunk['text']}\n")
        
        context_text = "\n".join(context_parts)
        
        # STRICT DOCUMENT-ONLY PROMPT - No external knowledge allowed
        # If query asks for definition, require a direct definition first
        needs_definition = any(x in query.lower() for x in ["what is", "define", "definition of", "meaning of"]) 
        definition_preamble = "" if not needs_definition else "Provide a concise 1-2 line definition FIRST, then details."

        full_prompt = f"""You are a helpful AI assistant that answers questions EXCLUSIVELY and STRICTLY based on the provided documents.

CRITICAL RULES:
1. ONLY answer using information from the documents below
2. Do NOT use any external knowledge, general knowledge, or information from training data
3. If the answer is NOT in the documents, respond: "I don't have this information in the provided documents."
4. Do NOT make up, infer, or assume information
5. Always cite which document the information comes from
6. Provide detailed, comprehensive answers using ALL relevant information from the documents
7. Include all types, categories, characteristics, and details mentioned in the documents
8. Use bullet points, numbering, or clear formatting when listing multiple items
9. {definition_preamble}

Documents:
{context_text}

Question: {query}

Answer ONLY based on the documents above. Provide a comprehensive, detailed answer with all relevant information. If information is not in documents, say so clearly:"""
        
        try:
            response = ollama.generate(
                model=self.model,
                prompt=full_prompt,
                stream=False,
                options={
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "top_k": 40,
                    "num_predict": 1024,
                    "num_ctx": 4096,
                    "repeat_penalty": 1.1,
                    "num_thread": 8,
                }
            )
            
            answer = response['response'].strip()
            
            # Check if LLM says information is not in documents
            no_info_phrases = [
                "don't have this information",
                "not in the provided documents",
                "not in the documents",
                "cannot find this information",
                "no information about",
                "not mentioned in the documents",
                "not available in the documents"
            ]
            
            is_no_info = any(phrase in answer.lower() for phrase in no_info_phrases)
            
            # FIX: If answer is long (>100 chars) and contains "no info" phrase, it's likely a hallucinated suffix.
            # We should valid the answer if it has substance.
            if is_no_info and len(answer) > 100:
                logger.warning(f"Detected 'no info' phrase but answer length is {len(answer)}. Treating as valid.")
                is_no_info = False
            
            if is_no_info:
                # Don't add sources/confidence if information not found
                return answer, [], 0, []
            
            cited_files = list(set([chunk['filename'] for chunk in context_chunks]))
            
            if cited_files:
                answer += f"\n\n📊 Confidence: {confidence_level} ({confidence_score}%)"
                answer += f"\n📄 Sources: {', '.join(cited_files)}"
            
            return answer, cited_files, confidence_score, source_snippets
            
        except Exception as e:
            error_msg = str(e).lower()
            
            # Check if it's an Ollama connection error
            if "connection" in error_msg or "ollama" in error_msg or "failed" in error_msg:
                logger.warning(f"Ollama unavailable: {e}")
                # Return message asking to start Ollama
                return "I cannot answer right now because Ollama is not running. Please start Ollama to get AI-powered answers from your documents.", [], 0, []
            
            else:
                logger.error(f"Error generating response: {e}")
                return f"Error: Unable to generate response. {str(e)}", [], 0, []
    
    def check_availability(self) -> bool:
        """Check if Ollama is available"""
        try:
            ollama.list()
            return True
        except:
            return False
