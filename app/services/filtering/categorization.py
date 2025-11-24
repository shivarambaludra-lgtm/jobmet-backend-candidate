from typing import List, Dict

class JobCategorizer:
    """Categorize jobs into 3 buckets"""
    
    JOB_BOARD_SOURCES = ["linkedin", "indeed", "glassdoor", "monster"]
    
    def categorize(self, jobs: List) -> Dict[str, List]:
        """
        Categorize jobs by source category
        
        Returns:
            {
                "job_boards": [...],
                "career_pages": [...],
                "hiring_posts": [...]
            }
        """
        
        categories = {
            "job_boards": [],
            "career_pages": [],
            "hiring_posts": []
        }
        
        for job in jobs:
            if job.source_category == "job_board":
                categories["job_boards"].append(job)
            elif job.source_category == "career_page":
                categories["career_pages"].append(job)
            elif job.source_category == "hiring_post":
                categories["hiring_posts"].append(job)
            else:
                # Fallback: categorize by source name
                if job.source in self.JOB_BOARD_SOURCES:
                    categories["job_boards"].append(job)
                else:
                    categories["career_pages"].append(job)
        
        return categories
