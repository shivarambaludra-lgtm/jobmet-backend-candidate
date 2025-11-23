-- Test data for JobMet.AI
-- Run this after initial migrations to populate database with sample data

-- ============================================
-- 1. INSERT TEST CANDIDATES
-- ============================================

INSERT INTO candidates (first_name, last_name, email, resume_text) VALUES
('John', 'Doe', 'john.doe@example.com', 
'JOHN DOE
Senior Software Engineer
Email: john.doe@example.com | Phone: (555) 123-4567

SUMMARY
Experienced software engineer with 7+ years building scalable backend systems. Expert in Python, FastAPI, and cloud architecture. Led teams of 5+ engineers and shipped products serving millions of users.

TECHNICAL SKILLS
Languages: Python, JavaScript, SQL, Go
Frameworks: FastAPI, Django, React, Node.js
Databases: PostgreSQL, MongoDB, Redis
Cloud: AWS (EC2, S3, Lambda, RDS), Docker, Kubernetes
Tools: Git, CI/CD, Terraform, Prometheus

EXPERIENCE

Senior Backend Engineer | TechCorp Inc. | 2021-Present
- Architected and deployed microservices handling 10M+ API requests/day
- Built REST APIs using FastAPI with 99.9% uptime SLA
- Optimized PostgreSQL queries reducing response time by 60%
- Mentored junior engineers and conducted code reviews
- Technologies: Python, FastAPI, PostgreSQL, Docker, AWS

Software Engineer | StartupXYZ | 2018-2021
- Developed e-commerce platform processing $5M+ in transactions
- Implemented OAuth2 authentication and RBAC authorization
- Created automated testing suite with 85% code coverage
- Technologies: Django, PostgreSQL, Redis, Celery

EDUCATION
B.S. Computer Science | University of Technology | 2018
GPA: 3.8/4.0

CERTIFICATIONS
- AWS Certified Solutions Architect
- Google Cloud Professional Developer'),

('Sarah', 'Johnson', 'sarah.j@example.com',
'SARAH JOHNSON
Full Stack Developer
sarah.j@example.com | LinkedIn: /in/sarahjohnson

PROFESSIONAL SUMMARY
Full-stack developer with 4 years experience building modern web applications. Proficient in React, Node.js, and cloud deployment. Passionate about clean code and user experience.

SKILLS
Frontend: React, TypeScript, Next.js, Tailwind CSS
Backend: Node.js, Express, Python, REST APIs
Databases: PostgreSQL, MySQL, MongoDB
DevOps: Docker, GitHub Actions, Vercel, Heroku

WORK HISTORY

Full Stack Developer | WebSolutions Co | 2022-Present
- Built customer-facing dashboards using React and TypeScript
- Developed RESTful APIs with Node.js and Express
- Integrated Stripe payment processing
- Implemented responsive designs with Tailwind CSS

Junior Developer | DigitalAgency | 2020-2022
- Created landing pages and marketing sites
- Collaborated with designers using Figma
- Fixed bugs and added features to client projects

EDUCATION
B.A. Information Systems | State University | 2020'),

('Michael', 'Chen', 'mchen@example.com',
'MICHAEL CHEN
Data Engineer
mchen@example.com | GitHub: github.com/mchen

ABOUT
Data engineer specializing in ETL pipelines and data warehousing. 5 years experience with big data technologies and analytics infrastructure.

CORE COMPETENCIES
- Python (Pandas, NumPy, PySpark)
- SQL (PostgreSQL, MySQL, Snowflake)
- ETL Tools (Airflow, dbt, Fivetran)
- Data Warehousing (Snowflake, Redshift)
- Cloud Platforms (AWS, GCP)

PROFESSIONAL EXPERIENCE

Data Engineer | DataCorp | 2021-Present
- Built ETL pipelines processing 500GB+ daily data
- Designed data warehouse schema in Snowflake
- Created dbt models for analytics transformations
- Automated data quality checks using Great Expectations
- Reduced data pipeline runtime by 40%

Analytics Engineer | FinTech Startup | 2019-2021
- Developed Python scripts for data ingestion
- Created SQL queries for business intelligence
- Maintained PostgreSQL databases
- Built Tableau dashboards for executives

EDUCATION
M.S. Data Science | Tech Institute | 2019
B.S. Mathematics | University | 2017');

-- ============================================
-- 2. INSERT TEST JOBS
-- ============================================

INSERT INTO jobs (title, description, requirements) VALUES
('Senior Backend Engineer', 
'We are seeking an experienced backend engineer to join our platform team. You will architect and build scalable APIs that power our core product used by millions of users worldwide. This role involves working with modern Python frameworks, cloud infrastructure, and distributed systems.

Our tech stack includes FastAPI, PostgreSQL, Redis, and AWS. You will collaborate with product managers, frontend engineers, and data scientists to deliver features that delight our customers.

This is a high-impact role where your work will directly influence the reliability and performance of our platform.',

'REQUIRED QUALIFICATIONS:
- 5+ years professional software development experience
- Expert-level Python programming skills
- Production experience with FastAPI or Django
- Deep understanding of PostgreSQL and database optimization
- Experience with Docker and container orchestration
- Strong knowledge of REST API design principles
- Experience with AWS cloud services (EC2, RDS, Lambda)
- Proven track record of building scalable systems

PREFERRED QUALIFICATIONS:
- Experience with Redis or other caching solutions
- Knowledge of microservices architecture
- Familiarity with CI/CD pipelines
- Experience mentoring junior engineers
- AWS certifications
- Open source contributions'),

('Full Stack Developer',
'Join our fast-growing startup as a full-stack developer! We are building a modern SaaS platform that helps small businesses manage their operations. You will work across the entire stack, from React frontends to Node.js backends.

We value engineers who are product-minded, write clean code, and care about user experience. You will have significant autonomy and ownership over features from conception to deployment.

Our stack: React, TypeScript, Node.js, PostgreSQL, Docker, deployed on AWS.',

'REQUIREMENTS:
- 3+ years experience in full-stack web development
- Proficiency with React and modern JavaScript/TypeScript
- Experience building REST APIs with Node.js or Python
- Solid understanding of PostgreSQL or similar relational databases
- Familiarity with Git version control
- Experience with responsive web design
- Strong communication skills

NICE TO HAVE:
- Next.js experience
- GraphQL knowledge
- Experience with payment integration (Stripe, etc.)
- Docker containerization experience
- Startup experience'),

('Data Engineer',
'Our data team is looking for a talented data engineer to build and maintain our analytics infrastructure. You will design ETL pipelines, optimize data warehouses, and enable data-driven decision making across the organization.

We process terabytes of data daily and you will ensure this data is reliable, accessible, and actionable for our analytics and ML teams.

Technology: Python, SQL, Apache Airflow, dbt, Snowflake, AWS',

'REQUIRED SKILLS:
- 4+ years experience in data engineering or related field
- Advanced SQL skills (PostgreSQL, MySQL, or Snowflake)
- Proficiency in Python for data processing (Pandas, PySpark)
- Experience building ETL pipelines with Airflow or similar tools
- Understanding of data modeling and warehouse design
- Experience with cloud platforms (AWS or GCP)
- Strong problem-solving abilities

PREFERRED SKILLS:
- Experience with dbt (data build tool)
- Knowledge of Snowflake data warehouse
- Familiarity with data quality frameworks
- Understanding of data governance
- Experience with real-time streaming data (Kafka, Kinesis)'),

('Junior Python Developer',
'Are you a recent graduate or early-career developer passionate about Python? We are looking for a junior developer to join our backend team and grow your skills in a supportive environment.

You will work on real features, participate in code reviews, and learn from senior engineers. We value curiosity, eagerness to learn, and attention to detail.

This role is perfect for someone who wants to build a strong foundation in backend development and cloud technologies.',

'REQUIREMENTS:
- 1-2 years programming experience (including internships/projects)
- Solid understanding of Python fundamentals
- Basic knowledge of SQL and databases
- Familiarity with Git and version control
- Understanding of REST APIs
- Bachelor degree in Computer Science or related field (or equivalent experience)
- Strong willingness to learn

BONUS POINTS:
- Personal projects or GitHub portfolio
- Any experience with FastAPI, Django, or Flask
- Basic understanding of Docker
- Contributions to open source
- Coursework or projects involving databases'),

('Frontend Engineer - React',
'We need a skilled frontend engineer to build beautiful, performant user interfaces for our web application. You will work closely with designers to implement pixel-perfect UIs and collaborate with backend engineers to integrate APIs.

You should be passionate about modern JavaScript, component-based architecture, and creating delightful user experiences. Performance optimization and accessibility are key focuses.

Tech stack: React, TypeScript, Next.js, Tailwind CSS, deployed on Vercel.',

'MUST HAVE:
- 4+ years frontend development experience
- Expert knowledge of React and React hooks
- Strong TypeScript skills
- Experience with modern CSS (Flexbox, Grid, Tailwind or similar)
- Understanding of responsive and mobile-first design
- Proficiency with REST API integration
- Experience with state management (Redux, Zustand, Context)
- Strong eye for design and UX

PREFERRED:
- Next.js experience
- Experience with design systems
- Knowledge of web accessibility (WCAG)
- Performance optimization experience
- Experience with testing (Jest, React Testing Library)
- Familiarity with Figma or similar design tools');

-- ============================================
-- 3. VERIFY DATA INSERTION
-- ============================================

-- Count records
SELECT 'Candidates inserted:', COUNT(*) FROM candidates;
SELECT 'Jobs inserted:', COUNT(*) FROM jobs;

-- Display sample data
SELECT id, first_name, last_name, email FROM candidates;
SELECT id, title FROM jobs;

-- ============================================
-- 4. USEFUL QUERIES FOR TESTING
-- ============================================

-- Get candidate IDs for testing API calls
SELECT id, first_name, last_name, email FROM candidates ORDER BY id;

-- Get job IDs for testing API calls
SELECT id, title FROM jobs ORDER BY id;

-- Check applications after running tests
-- SELECT 
--     a.id,
--     c.first_name || ' ' || c.last_name as candidate_name,
--     j.title as job_title,
--     a.status,
--     a.match_score,
--     a.ai_reasoning
-- FROM applications a
-- JOIN candidates c ON a.candidate_id = c.id
-- JOIN jobs j ON a.job_id = j.id
-- ORDER BY a.applied_at DESC;
