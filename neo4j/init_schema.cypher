// Create constraints for unique nodes
CREATE CONSTRAINT skill_name IF NOT EXISTS FOR (s:Skill) REQUIRE s.name IS UNIQUE;
CREATE CONSTRAINT job_title_name IF NOT EXISTS FOR (jt:JobTitle) REQUIRE jt.name IS UNIQUE;
CREATE CONSTRAINT company_id IF NOT EXISTS FOR (c:Company) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT visa_type IF NOT EXISTS FOR (v:VisaType) REQUIRE v.type IS UNIQUE;
CREATE CONSTRAINT education_level IF NOT EXISTS FOR (e:EducationLevel) REQUIRE e.level IS UNIQUE;

// Create indexes for performance
CREATE INDEX skill_category IF NOT EXISTS FOR (s:Skill) ON (s.category);
CREATE INDEX company_size IF NOT EXISTS FOR (c:Company) ON (c.size);
CREATE INDEX job_title_seniority IF NOT EXISTS FOR (jt:JobTitle) ON (jt.seniority);
