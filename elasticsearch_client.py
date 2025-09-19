import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from elasticsearch import AsyncElasticsearch
import logging
from config import ES_HOST, ES_PORT, ES_USERNAME, ES_PASSWORD, ES_USE_SSL

class ElasticsearchClient:
    """Elasticsearch client for storing crawler data"""
    
    def __init__(self):
        self.client = None
        self.logger = logging.getLogger(__name__)
        self.index_prefix = "telegram_crawler"
        
    async def connect(self) -> bool:
        """Connect to Elasticsearch"""
        try:
            self.client = AsyncElasticsearch(
                hosts=[f"{ES_HOST}:{ES_PORT}"],
                http_auth=(ES_USERNAME, ES_PASSWORD) if ES_USERNAME else None,
                use_ssl=ES_USE_SSL,
                verify_certs=False,
                timeout=30
            )
            
            # Test connection
            await self.client.ping()
            self.logger.info("Connected to Elasticsearch successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Elasticsearch: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from Elasticsearch"""
        if self.client:
            await self.client.close()
    
    def _get_index_name(self, data_type: str, date: Optional[str] = None) -> str:
        """Generate index name with date suffix for rotation"""
        if date:
            return f"{self.index_prefix}_{data_type}_{date}"
        return f"{self.index_prefix}_{data_type}"
    
    async def create_indices(self) -> None:
        """Create necessary indices with proper mappings"""
        indices = [
            ("groups", self._get_groups_mapping()),
            ("messages", self._get_messages_mapping()),
            ("phones", self._get_phones_mapping()),
            ("jobs", self._get_jobs_mapping())
        ]
        
        for index_name, mapping in indices:
            full_index_name = self._get_index_name(index_name)
            try:
                if not await self.client.indices.exists(index=full_index_name):
                    await self.client.indices.create(
                        index=full_index_name,
                        body=mapping
                    )
                    self.logger.info(f"Created index: {full_index_name}")
            except Exception as e:
                self.logger.error(f"Failed to create index {full_index_name}: {e}")
    
    def _get_groups_mapping(self) -> Dict:
        """Mapping for groups index"""
        return {
            "mappings": {
                "properties": {
                    "link": {"type": "keyword"},
                    "joined_at": {"type": "date"},
                    "account_phone": {"type": "keyword"},
                    "messages_read": {"type": "integer"},
                    "job_score": {"type": "float"},
                    "status": {"type": "keyword"},
                    "created_at": {"type": "date"}
                }
            }
        }
    
    def _get_messages_mapping(self) -> Dict:
        """Mapping for messages index"""
        return {
            "mappings": {
                "properties": {
                    "message_id": {"type": "long"},
                    "group_link": {"type": "keyword"},
                    "sender_id": {"type": "long"},
                    "text": {"type": "text", "analyzer": "standard"},
                    "date": {"type": "date"},
                    "job_score": {"type": "float"},
                    "processed": {"type": "boolean"},
                    "created_at": {"type": "date"}
                }
            }
        }
    
    def _get_phones_mapping(self) -> Dict:
        """Mapping for phones index"""
        return {
            "mappings": {
                "properties": {
                    "phone_number": {"type": "keyword"},
                    "job_posts_count": {"type": "integer"},
                    "high_score_posts": {"type": "integer"},
                    "last_seen": {"type": "date"},
                    "created_at": {"type": "date"}
                }
            }
        }
    
    def _get_jobs_mapping(self) -> Dict:
        """Mapping for jobs index"""
        return {
            "mappings": {
                "properties": {
                    "title": {"type": "text", "analyzer": "standard"},
                    "description": {"type": "text", "analyzer": "standard"},
                    "company": {"type": "text"},
                    "location": {"type": "keyword"},
                    "remote": {"type": "boolean"},
                    "fresher_friendly": {"type": "boolean"},
                    "technologies": {"type": "keyword"},
                    "job_score": {"type": "float"},
                    "source_group": {"type": "keyword"},
                    "source_message_id": {"type": "long"},
                    "contact_phones": {"type": "keyword"},
                    "created_at": {"type": "date"}
                }
            }
        }
    
    async def index_group(self, group_data: Dict) -> bool:
        """Index a group document"""
        try:
            group_data["created_at"] = datetime.now().isoformat()
            await self.client.index(
                index=self._get_index_name("groups"),
                body=group_data,
                id=group_data["link"]
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to index group {group_data.get('link')}: {e}")
            return False
    
    async def index_message(self, message_data: Dict, date_suffix: Optional[str] = None) -> bool:
        """Index a message document with optional date rotation"""
        try:
            message_data["created_at"] = datetime.now().isoformat()
            index_name = self._get_index_name("messages", date_suffix)
            doc_id = f"{message_data['group_link']}:{message_data['message_id']}"
            
            await self.client.index(
                index=index_name,
                body=message_data,
                id=doc_id
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to index message {doc_id}: {e}")
            return False
    
    async def index_phone(self, phone_data: Dict) -> bool:
        """Index a phone document"""
        try:
            phone_data["created_at"] = datetime.now().isoformat()
            await self.client.index(
                index=self._get_index_name("phones"),
                body=phone_data,
                id=phone_data["phone_number"]
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to index phone {phone_data.get('phone_number')}: {e}")
            return False
    
    async def index_job(self, job_data: Dict) -> bool:
        """Index a job document"""
        try:
            job_data["created_at"] = datetime.now().isoformat()
            await self.client.index(
                index=self._get_index_name("jobs"),
                body=job_data
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to index job: {e}")
            return False
    
    async def search_jobs(self, filters: Dict) -> List[Dict]:
        """Search for jobs with filters"""
        try:
            query = {
                "bool": {
                    "must": []
                }
            }
            
            # Add filters
            if filters.get("technologies"):
                query["bool"]["must"].append({
                    "terms": {"technologies": filters["technologies"]}
                })
            
            if filters.get("location"):
                if filters["location"] == "remote":
                    query["bool"]["must"].append({"term": {"remote": True}})
                else:
                    query["bool"]["must"].append({"term": {"location": filters["location"]}})
            
            if filters.get("fresher_friendly"):
                query["bool"]["must"].append({"term": {"fresher_friendly": True}})
            
            if filters.get("min_job_score"):
                query["bool"]["must"].append({
                    "range": {"job_score": {"gte": filters["min_job_score"]}}
                })
            
            response = await self.client.search(
                index=self._get_index_name("jobs"),
                body={
                    "query": query,
                    "sort": [{"job_score": {"order": "desc"}}],
                    "size": filters.get("size", 50)
                }
            )
            
            return [hit["_source"] for hit in response["hits"]["hits"]]
            
        except Exception as e:
            self.logger.error(f"Failed to search jobs: {e}")
            return []

# Global Elasticsearch client instance
es_client = ElasticsearchClient()
