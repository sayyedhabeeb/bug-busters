import os
import logging
import json
import numpy as np
import pymysql
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Load env variables
load_dotenv()

logger = logging.getLogger(__name__)

class MySQLConnector:
    """
    Handles connection to MySQL and similarity search operations.
    """
    
    def __init__(self):
        self.host = os.getenv("MYSQL_HOST", "localhost")
        self.port = int(os.getenv("MYSQL_PORT", "3306"))
        self.db_name = os.getenv("MYSQL_DB", "job_recommendation")
        self.user = os.getenv("MYSQL_USER", "root")
        self.password = os.getenv("MYSQL_PASSWORD", "root")
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Establish database connection."""
        try:
            self.conn = pymysql.connect(
                host=self.host,
                port=self.port,
                database=self.db_name,
                user=self.user,
                password=self.password,
                cursorclass=pymysql.cursors.DictCursor
            )
            self.cursor = self.conn.cursor()
            logger.info("Connected to MySQL.")
        except Exception as e:
            logger.error(f"Failed to connect to MySQL: {e}")
            raise
    
    def close(self):
        """Close connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("MySQL connection closed.")

    def setup_tables(self):
        """Create tables for MySQL."""
        try:
            self.connect()
            
            # Create jobs table (using JSON for embedding)
            create_jobs_tbl = """
            CREATE TABLE IF NOT EXISTS jobs (
                id VARCHAR(255) PRIMARY KEY,
                title TEXT,
                description TEXT,
                skills JSON,
                embedding JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            self.cursor.execute(create_jobs_tbl)
            
            # Create candidates table
            create_candidates_tbl = """
            CREATE TABLE IF NOT EXISTS candidates (
                id VARCHAR(255) PRIMARY KEY,
                resume_text TEXT,
                skills JSON,
                experience_years INT,
                embedding JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            self.cursor.execute(create_candidates_tbl)
            
            self.conn.commit()
            logger.info("MySQL tables (jobs & candidates) setup complete.")
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            logger.error(f"Setup failed: {e}")
            raise
        finally:
            self.close()

    def insert_jobs(self, jobs_data: List[Dict[str, Any]]):
        """Bulk insert jobs with embeddings."""
        try:
            self.connect()
            insert_query = """
            INSERT INTO jobs (id, title, description, skills, embedding)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                title = VALUES(title),
                description = VALUES(description),
                skills = VALUES(skills),
                embedding = VALUES(embedding);
            """
            
            # Prepare data: convert lists to JSON strings
            values = [
                (
                    j['id'], 
                    j['title'], 
                    j['description'], 
                    json.dumps(j['skills']), 
                    json.dumps(j['embedding']) 
                )
                for j in jobs_data
            ]
            
            self.cursor.executemany(insert_query, values)
            self.conn.commit()
            logger.info(f"Inserted {len(jobs_data)} jobs into MySQL.")
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            logger.error(f"Insert failed: {e}")
    def insert_candidate(self, cand_data: Dict[str, Any]):
        """Insert a single candidate."""
        try:
            self.connect()
            insert_query = """
            INSERT INTO candidates (id, resume_text, skills, experience_years, embedding)
            VALUES (%s, %s, %s, %s, %s)
            """
            self.cursor.execute(insert_query, (
                cand_data['id'],
                cand_data['resume_text'],
                json.dumps(cand_data['skills']),
                cand_data.get('experience_years', 0),
                json.dumps(cand_data.get('embedding', []))
            ))
            self.conn.commit()
            logger.info(f"Inserted candidate {cand_data['id']} into MySQL.")
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            logger.error(f"Candidate insert failed: {e}")
            raise
        finally:
            self.close()

    def insert_job(self, job_data: Dict[str, Any]):
        """Insert a single job."""
        try:
            self.connect()
            insert_query = """
            INSERT INTO jobs (id, title, description, skills, embedding)
            VALUES (%s, %s, %s, %s, %s)
            """
            self.cursor.execute(insert_query, (
                job_data['id'],
                job_data['title'],
                job_data['description'],
                json.dumps(job_data['skills']),
                json.dumps(job_data.get('embedding', []))
            ))
            self.conn.commit()
            logger.info(f"Inserted job {job_data['id']} into MySQL.")
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            logger.error(f"Job insert failed: {e}")
            raise
        finally:
            self.close()

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Calculate cosine similarity in Python."""
        v1 = np.array(v1)
        v2 = np.array(v2)
        if np.all(v1 == 0) or np.all(v2 == 0):
            return 0.0
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

    def search_similar_jobs(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar jobs. 
        Note: Since MySQL doesn't have vector search, we fetch all and calculate in Python.
        In a real production environment with 1M+ rows, you'd use a dedicated vector DB.
        """
        try:
            self.connect()
            # Fetch all jobs with embeddings
            self.cursor.execute("SELECT id, title, skills, embedding FROM jobs")
            rows = self.cursor.fetchall()
            
            results = []
            for row in rows:
                if row['embedding']:
                    job_emb = json.loads(row['embedding']) if isinstance(row['embedding'], str) else row['embedding']
                    similarity = self._cosine_similarity(query_embedding, job_emb)
                    results.append({
                        "id": row['id'],
                        "title": row['title'],
                        "skills": row['skills'],
                        "score": float(similarity)
                    })
            
            # Sort by score DESC
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:top_k]
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
        finally:
            self.close()

if __name__ == "__main__":
    db = MySQLConnector()
    try:
        db.setup_tables()
    except:
        logger.warning("Could not setup MySQL (is it running?)")
