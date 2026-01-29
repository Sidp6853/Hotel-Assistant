"""
RAG Tool - Retrieves hotel policies using Chroma vector store
Uses Ollama embeddings for semantic search
"""
import json
import logging
from typing import List
from pathlib import Path

from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document

from config.settings import settings

logger = logging.getLogger(__name__)


class HotelPolicyRAG:
    """RAG system for retrieving relevant hotel policies"""
    
    def __init__(self):
        self.vectorstore = None
        self.initialized = False
        
    def initialize(self):
        """Initialize the vector store with hotel policies"""
        try:
            # Check if policies file exists
            if not Path(settings.POLICIES_PATH).exists():
                logger.warning(f"⚠️  Policies file not found: {settings.POLICIES_PATH}")
                logger.warning("⚠️  Using fallback mock policies")
                self._use_mock_policies()
                return
            
            # Load policies from JSON
            with open(settings.POLICIES_PATH, 'r') as f:
                policy_data = json.load(f)
            
            # Create documents
            documents = []
            for policy in policy_data.get('policies', []):
                doc = Document(
                    page_content=policy['content'],
                    metadata={
                        'id': policy.get('id', ''),
                        'title': policy.get('title', ''),
                        'category': policy.get('category', 'general')
                    }
                )
                documents.append(doc)
            
            if not documents:
                logger.warning("No policies found in file, using mock policies")
                self._use_mock_policies()
                return
            
            # Initialize embeddings and vector store
            logger.info("🔄 Creating embeddings (this may take a moment)...")
            embeddings = OllamaEmbeddings(model=settings.LLM_MODEL)
            
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=embeddings,
                collection_name=settings.RAG_COLLECTION_NAME,
                persist_directory="./chroma_db"
            )
            
            self.initialized = True
            logger.info(f"✅ RAG initialized with {len(documents)} policies")
            
        except Exception as e:
            logger.error(f"❌ RAG initialization failed: {e}")
            logger.warning("⚠️  Falling back to mock policies")
            self._use_mock_policies()
    
    def _use_mock_policies(self):
        """Fallback to simple mock policies"""
        self.mock_policies = {
            "maintenance": [
                "Standard Response Time: Maintenance requests must be acknowledged within 15 minutes and resolved within 2 hours for critical issues (AC, plumbing, heating).",
                "Compensation Policy: For AC/heating failures lasting more than 4 hours, offer room discount (25%) or relocation to comparable room.",
                "Escalation: All maintenance issues affecting guest safety must be escalated to Engineering Manager immediately."
            ],
            "cleanliness": [
                "Room Standards: All rooms must meet 5-star cleanliness standards. Any pest sightings require immediate room relocation and full inspection of floor.",
                "Compensation Policy: For cleanliness issues - minor: complimentary amenities, moderate: 50% room discount, severe: full refund + future stay credit.",
                "Health & Safety: Pest sightings or hygiene violations require mandatory incident report and notification to Quality Assurance team."
            ],
            "service": [
                "Service Recovery: For service failures, acknowledge within 10 minutes, resolve within 1 hour. Multiple failures require manager intervention.",
                "Compensation Guidelines: Delayed service - complimentary meal/drink, severe delays - room upgrade or percentage discount based on impact.",
                "Guest Satisfaction Priority: All guest complaints must receive personal manager follow-up within 24 hours."
            ],
            "positive_feedback": [
                "Recognition Policy: Positive feedback should be shared with mentioned staff members and their managers within 24 hours.",
                "Guest Relations: Thank guests for feedback, invite them back with loyalty program benefits or future stay discount.",
                "Team Morale: Outstanding feedback should be posted on staff recognition board and included in performance reviews."
            ],
            "general": [
                "Standard Complaint Handling: Acknowledge immediately, apologize sincerely, resolve within 2 hours, follow up within 24 hours.",
                "Compensation Authority: Front desk - up to $100, Duty Manager - up to $500, GM approval required for full refunds.",
                "Guest Relations: All complaints logged in CRM system, escalate high/critical severity to Guest Relations Manager."
            ]
        }
        self.initialized = True
        logger.info("✅ Using mock policy database")
    
    def retrieve(self, query: str, k: int = None) -> List[str]:
        """
        Retrieve relevant policies for a complaint
        
        Args:
            query: Complaint context (category, severity, issues)
            k: Number of policies to retrieve
            
        Returns:
            List of relevant policy texts
        """
        if not self.initialized:
            logger.warning("RAG not initialized, returning empty list")
            return []
        
        k = k or settings.RAG_TOP_K
        
        try:
            # If using vector store
            if self.vectorstore:
                docs = self.vectorstore.similarity_search(query, k=k)
                policies = [doc.page_content for doc in docs]
                logger.info(f"📚 Retrieved {len(policies)} policies via vector search")
                return policies
            
            # If using mock policies (fallback)
            else:
                query_lower = query.lower()
                
                # Simple keyword matching
                for category in self.mock_policies.keys():
                    if category in query_lower:
                        policies = self.mock_policies[category][:k]
                        logger.info(f"📚 Retrieved {len(policies)} mock policies for: {category}")
                        return policies
                
                # Default to general
                policies = self.mock_policies["general"][:k]
                logger.info(f"📚 Retrieved {len(policies)} general mock policies")
                return policies
                
        except Exception as e:
            logger.error(f"RAG retrieval failed: {e}")
            return []


# Global singleton
policy_rag = HotelPolicyRAG()