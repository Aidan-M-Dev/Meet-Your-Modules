CREATE TABLE IF NOT EXISTS departments (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS lecturers (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS modules (
  id SERIAL PRIMARY KEY,
  department_id INT REFERENCES departments(id) ON DELETE CASCADE,
  code VARCHAR(50) NOT NULL,
  name VARCHAR(255) NOT NULL,
  credits INT NOT NULL
);

CREATE TABLE IF NOT EXISTS courses (
  id SERIAL PRIMARY KEY,
  home_department_id INT REFERENCES departments(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS module_iterations (
  id SERIAL PRIMARY KEY,
  module_id INT REFERENCES modules(id) ON DELETE CASCADE,
  academic_year_start_year VARCHAR(20) NOT NULL,
  term INT NOT NULL
);

CREATE TABLE IF NOT EXISTS module_iterations_lecturers_links (
  id SERIAL PRIMARY KEY,
  module_iteration_id INT REFERENCES module_iterations(id) ON DELETE CASCADE,
  lecturer_id INT REFERENCES lecturers(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS module_iterations_courses_links (
  id SERIAL PRIMARY KEY,
  module_iteration_id INT REFERENCES module_iterations(id) ON DELETE CASCADE,
  course_id INT REFERENCES courses(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS reviews (
  id SERIAL PRIMARY KEY,
  module_iteration_id INT REFERENCES module_iterations(id) ON DELETE CASCADE,
  overall_rating INT CHECK (overall_rating >= 1 AND overall_rating <= 5),
  comment TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  moderation_status VARCHAR(50),
  report_tolerance INT DEFAULT 1,
  report_count INT DEFAULT 0,
  like_dislike INT DEFAULT 0
);
