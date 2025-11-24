// ============= SKILLS =============
MERGE (java:Skill {name: "Java", category: "Programming Language", popularity: 95})
MERGE (python:Skill {name: "Python", category: "Programming Language", popularity: 98})
MERGE (springboot:Skill {name: "Spring Boot", category: "Framework", popularity: 88})
MERGE (microservices:Skill {name: "Microservices", category: "Architecture", popularity: 85})
MERGE (restapi:Skill {name: "REST API", category: "Architecture", popularity: 90})
MERGE (kotlin:Skill {name: "Kotlin", category: "Programming Language", popularity: 75})
MERGE (scala:Skill {name: "Scala", category: "Programming Language", popularity: 60})
MERGE (aws:Skill {name: "AWS", category: "Cloud", popularity: 92})
MERGE (docker:Skill {name: "Docker", category: "DevOps", popularity: 88})
MERGE (kubernetes:Skill {name: "Kubernetes", category: "DevOps", popularity: 85})

// Skill relationships
MERGE (java)-[:RELATED_TO {strength: 0.9}]->(springboot)
MERGE (java)-[:RELATED_TO {strength: 0.8}]->(kotlin)
MERGE (java)-[:RELATED_TO {strength: 0.7}]->(scala)
MERGE (java)-[:RELATED_TO {strength: 0.85}]->(microservices)
MERGE (springboot)-[:REQUIRES]->(java)
MERGE (microservices)-[:COMMONLY_USES]->(restapi)
MERGE (microservices)-[:COMMONLY_USES]->(docker)
MERGE (docker)-[:RELATED_TO {strength: 0.9}]->(kubernetes)

// ============= JOB TITLES =============
MERGE (javaDev:JobTitle {name: "Java Developer", seniority: "Mid", category: "Backend"})
MERGE (softwareEng:JobTitle {name: "Software Engineer", seniority: "Mid", category: "General"})
MERGE (backendDev:JobTitle {name: "Backend Developer", seniority: "Mid", category: "Backend"})
MERGE (seniorJava:JobTitle {name: "Senior Java Developer", seniority: "Senior", category: "Backend"})
MERGE (javaArch:JobTitle {name: "Java Architect", seniority: "Lead", category: "Architecture"})

// Job title relationships
MERGE (javaDev)-[:SYNONYM_OF]->(softwareEng)
MERGE (javaDev)-[:SYNONYM_OF]->(backendDev)
MERGE (javaDev)-[:SENIOR_VERSION]->(seniorJava)
MERGE (seniorJava)-[:SENIOR_VERSION]->(javaArch)

// Job title skill requirements
MERGE (javaDev)-[:REQUIRES_SKILL {priority: "mandatory"}]->(java)
MERGE (javaDev)-[:REQUIRES_SKILL {priority: "preferred"}]->(springboot)
MERGE (javaDev)-[:REQUIRES_SKILL {priority: "preferred"}]->(microservices)

// ============= COMPANIES =============
MERGE (google:Company {id: "google", name: "Google", size: "Enterprise", industry: "Technology"})
MERGE (microsoft:Company {id: "microsoft", name: "Microsoft", size: "Enterprise", industry: "Technology"})
MERGE (amazon:Company {id: "amazon", name: "Amazon", size: "Enterprise", industry: "Technology"})
MERGE (meta:Company {id: "meta", name: "Meta", size: "Enterprise", industry: "Technology"})
MERGE (stripe:Company {id: "stripe", name: "Stripe", size: "Large", industry: "FinTech"})

// ============= VISA TYPES =============
MERGE (h1b:VisaType {type: "H1B", description: "Work visa for specialty occupations"})
MERGE (greenCard:VisaType {type: "Green Card", description: "Permanent residency"})
MERGE (opt:VisaType {type: "OPT", description: "Optional Practical Training"})

// Company visa sponsorship
MERGE (google)-[:SPONSORS_VISA]->(h1b)
MERGE (microsoft)-[:SPONSORS_VISA]->(h1b)
MERGE (amazon)-[:SPONSORS_VISA]->(h1b)
MERGE (meta)-[:SPONSORS_VISA]->(h1b)
MERGE (stripe)-[:SPONSORS_VISA]->(h1b)

// Company technologies
MERGE (google)-[:USES_TECHNOLOGY]->(java)
MERGE (google)-[:USES_TECHNOLOGY]->(python)
MERGE (google)-[:USES_TECHNOLOGY]->(kubernetes)
MERGE (amazon)-[:USES_TECHNOLOGY]->(java)
MERGE (amazon)-[:USES_TECHNOLOGY]->(aws)

// ============= EDUCATION LEVELS =============
MERGE (bachelor:EducationLevel {level: "Bachelor", degree: "BS"})
MERGE (master:EducationLevel {level: "Master", degree: "MS"})
MERGE (phd:EducationLevel {level: "Doctorate", degree: "PhD"})

// Job title education requirements
MERGE (javaDev)-[:REQUIRES_EDUCATION {minimum: true}]->(bachelor)
MERGE (javaArch)-[:REQUIRES_EDUCATION {minimum: true}]->(master)
