"""
Test dynamic filter generation
"""
from app.services.filter_generator import DynamicFilterGenerator

# Sample jobs data
sample_jobs = [
    {
        "location": "San Francisco, CA",
        "company": "Google",
        "skills": ["Python", "Django", "PostgreSQL", "Docker"],
        "years_experience_min": 3,
        "salary_min": 120000,
        "visa_sponsorship": True,
        "education_required": "Bachelor"
    },
    {
        "location": "Remote",
        "company": "Meta",
        "skills": ["Python", "React", "AWS", "Kubernetes"],
        "years_experience_min": 5,
        "salary_min": 150000,
        "visa_sponsorship": True,
        "education_required": "Master"
    },
    {
        "location": "New York, NY",
        "company": "Amazon",
        "skills": ["Java", "Spring Boot", "AWS"],
        "years_experience_min": 2,
        "salary_min": 110000,
        "visa_sponsorship": False,
        "education_required": "Bachelor"
    },
    {
        "location": "San Francisco, CA",
        "company": "Apple",
        "skills": ["Python", "Machine Learning", "TensorFlow"],
        "years_experience_min": 7,
        "salary_min": 180000,
        "visa_sponsorship": True,
        "education_required": "PhD"
    },
    {
        "location": "Remote",
        "company": "Stripe",
        "skills": ["Python", "Ruby", "PostgreSQL"],
        "years_experience_min": 4,
        "salary_min": 140000,
        "visa_sponsorship": True,
        "education_required": "Bachelor"
    }
]

def test_filter_generation():
    print("=" * 60)
    print("Testing Dynamic Filter Generation")
    print("=" * 60)
    
    generator = DynamicFilterGenerator()
    filters = generator.generate_filters(sample_jobs)
    
    print("\n📍 LOCATIONS:")
    for loc in filters['locations']:
        print(f"  - {loc['label']}: {loc['count']} jobs")
    
    print("\n🏢 COMPANIES:")
    for comp in filters['companies']:
        print(f"  - {comp['label']}: {comp['count']} jobs")
    
    print("\n💼 SKILLS:")
    for skill in filters['skills']:
        print(f"  - {skill['label']}: {skill['count']} jobs")
    
    print("\n📊 EXPERIENCE LEVELS:")
    for level in filters['experience_levels']:
        print(f"  - {level['label']}: {level['count']} jobs")
    
    print("\n💰 SALARY RANGES:")
    for salary in filters['salary_ranges']:
        print(f"  - {salary['label']}: {salary['count']} jobs")
    
    print("\n🌍 VISA SPONSORSHIP:")
    visa = filters['visa_sponsorship']
    print(f"  - Sponsors: {visa['sponsors']} jobs")
    print(f"  - No Sponsorship: {visa['no_sponsorship']} jobs")
    
    print("\n🎓 EDUCATION LEVELS:")
    for edu in filters['education_levels']:
        print(f"  - {edu['label']}: {edu['count']} jobs")
    
    print("\n" + "=" * 60)
    print("✅ Filter generation test complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_filter_generation()
