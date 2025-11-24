from typing import List, Dict, Any
from collections import Counter
import statistics
import logging

logger = logging.getLogger(__name__)

class DynamicFilterGenerator:
    """Generate filters dynamically from search results"""
    
    def generate_filters(self, jobs: List) -> Dict[str, Any]:
        """
        Generate filter options from job list
        
        Args:
            jobs: List of job objects (JobPosting or dict)
            
        Returns:
            {
                "locations": [...],
                "companies": [...],
                "skills": [...],
                "experience_levels": [...],
                "salary_ranges": [...],
                "visa_sponsorship": {...},
                "education_levels": [...]
            }
        """
        if not jobs:
            return self._empty_filters()
        
        # Extract unique values
        locations = self._extract_locations(jobs)
        companies = self._extract_companies(jobs)
        skills = self._extract_skills(jobs)
        experience_levels = self._extract_experience_levels(jobs)
        salary_ranges = self._generate_salary_ranges(jobs)
        visa_counts = self._count_visa_sponsorship(jobs)
        education_levels = self._extract_education_levels(jobs)
        
        return {
            "locations": locations,
            "companies": companies,
            "skills": skills,
            "experience_levels": experience_levels,
            "salary_ranges": salary_ranges,
            "visa_sponsorship": visa_counts,
            "education_levels": education_levels
        }
    
    def _extract_locations(self, jobs: List) -> List[Dict]:
        """Extract location filters with counts"""
        locations = []
        for job in jobs:
            loc = getattr(job, 'location', None) if hasattr(job, 'location') else job.get('location')
            if loc:
                locations.append(loc)
        
        location_counter = Counter(locations)
        return [
            {"value": loc, "label": loc, "count": count}
            for loc, count in location_counter.most_common(20)
        ]
    
    def _extract_companies(self, jobs: List) -> List[Dict]:
        """Extract company filters with counts"""
        companies = []
        for job in jobs:
            comp = getattr(job, 'company', None) if hasattr(job, 'company') else job.get('company')
            if comp:
                companies.append(comp)
        
        company_counter = Counter(companies)
        return [
            {"value": comp, "label": comp, "count": count}
            for comp, count in company_counter.most_common(20)
        ]
    
    def _extract_skills(self, jobs: List) -> List[Dict]:
        """Extract skill filters with counts"""
        all_skills = []
        for job in jobs:
            skills = getattr(job, 'skills', None) if hasattr(job, 'skills') else job.get('skills')
            if skills:
                all_skills.extend(skills)
        
        skill_counter = Counter(all_skills)
        return [
            {"value": skill, "label": skill, "count": count}
            for skill, count in skill_counter.most_common(30)
        ]
    
    def _extract_experience_levels(self, jobs: List) -> List[Dict]:
        """Categorize experience levels"""
        level_counter = Counter()
        
        for job in jobs:
            exp_min = getattr(job, 'years_experience_min', None) if hasattr(job, 'years_experience_min') else job.get('years_experience_min')
            
            if exp_min is not None:
                if exp_min == 0:
                    level_counter["Entry Level (0-2 years)"] += 1
                elif exp_min <= 3:
                    level_counter["Mid Level (3-5 years)"] += 1
                elif exp_min <= 7:
                    level_counter["Senior (5-7 years)"] += 1
                else:
                    level_counter["Lead/Principal (7+ years)"] += 1
        
        return [
            {"value": level, "label": level, "count": count}
            for level, count in level_counter.items()
        ]
    
    def _generate_salary_ranges(self, jobs: List) -> List[Dict]:
        """Generate salary range buckets"""
        salaries = []
        for job in jobs:
            sal = getattr(job, 'salary_min', None) if hasattr(job, 'salary_min') else job.get('salary_min')
            if sal:
                salaries.append(sal)
        
        if not salaries:
            return []
        
        # Define ranges
        ranges = [
            (0, 60000, "$0-$60k"),
            (60000, 80000, "$60k-$80k"),
            (80000, 100000, "$80k-$100k"),
            (100000, 120000, "$100k-$120k"),
            (120000, 150000, "$120k-$150k"),
            (150000, 200000, "$150k-$200k"),
            (200000, float('inf'), "$200k+")
        ]
        
        range_counter = Counter()
        for salary in salaries:
            for min_sal, max_sal, label in ranges:
                if min_sal <= salary < max_sal:
                    range_counter[label] += 1
                    break
        
        return [
            {"value": label, "label": label, "count": count}
            for label, count in range_counter.items()
        ]
    
    def _count_visa_sponsorship(self, jobs: List) -> Dict:
        """Count visa sponsorship availability"""
        visa_yes = 0
        for job in jobs:
            visa = getattr(job, 'visa_sponsorship', None) if hasattr(job, 'visa_sponsorship') else job.get('visa_sponsorship')
            if visa:
                visa_yes += 1
        
        visa_no = len(jobs) - visa_yes
        
        return {
            "sponsors": visa_yes,
            "no_sponsorship": visa_no
        }
    
    def _extract_education_levels(self, jobs: List) -> List[Dict]:
        """Extract education requirements"""
        education = []
        for job in jobs:
            edu = getattr(job, 'education_required', None) if hasattr(job, 'education_required') else job.get('education_required')
            if edu:
                education.append(edu)
        
        edu_counter = Counter(education)
        return [
            {"value": edu, "label": edu, "count": count}
            for edu, count in edu_counter.items()
        ]
    
    def _empty_filters(self) -> Dict:
        """Return empty filter structure"""
        return {
            "locations": [],
            "companies": [],
            "skills": [],
            "experience_levels": [],
            "salary_ranges": [],
            "visa_sponsorship": {"sponsors": 0, "no_sponsorship": 0},
            "education_levels": []
        }
