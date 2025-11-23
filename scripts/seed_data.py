import sys
import os

# Add the project root to the python path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.candidate import Candidate
from app.models.job import Job

def seed_data():
    db = SessionLocal()
    try:
        print("Seeding data...")
        
        # Check if data already exists
        if db.query(Candidate).count() > 0:
            print("Candidates already exist. Skipping candidate seeding.")
        else:
            # Create Candidates
            candidates = [
                Candidate(
                    first_name="John",
                    last_name="Doe",
                    email="john@example.com",
                    resume_text="Senior Backend Engineer with 7+ years experience. Expert in Python, FastAPI, PostgreSQL, Docker, AWS. Led teams building scalable systems handling 1M+ requests/day. Strong database optimization skills."
                ),
                Candidate(
                    first_name="Jane",
                    last_name="Smith",
                    email="jane@example.com",
                    resume_text="Full Stack Developer, 5 years experience. JavaScript, React, Node.js, MongoDB. Built e-commerce platforms. Some Python experience but limited backend expertise."
                ),
                Candidate(
                    first_name="Mike",
                    last_name="Johnson",
                    email="mike@example.com",
                    resume_text="Junior Developer, 2 years experience. Knows Java and Spring Boot. Learning Python. Minimal database experience. Enthusiastic about backend development."
                )
            ]
            db.add_all(candidates)
            print(f"Added {len(candidates)} candidates.")

        if db.query(Job).count() > 0:
            print("Jobs already exist. Skipping job seeding.")
        else:
            # Create Jobs
            jobs = [
                Job(
                    title="Senior Backend Engineer",
                    description="Build scalable backend systems for our fintech platform. Work with Python, FastAPI, PostgreSQL. Lead small team.",
                    requirements="7+ years backend experience, Python expert, FastAPI knowledge, PostgreSQL, Docker, AWS, system design skills"
                ),
                Job(
                    title="Full Stack Developer",
                    description="Develop web applications using modern tech stack. Both frontend and backend work.",
                    requirements="5+ years experience, JavaScript/React, Node.js or Python, MongoDB or SQL, web development"
                ),
                Job(
                    title="Junior Developer Program",
                    description="Entry level position for new graduates. Training provided.",
                    requirements="Basic programming knowledge, willingness to learn, problem solving skills, communication"
                )
            ]
            db.add_all(jobs)
            print(f"Added {len(jobs)} jobs.")

        db.commit()
        print("Seeding complete!")
        
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
