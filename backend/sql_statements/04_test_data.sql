-- Test data for module review system
-- This file populates the database with sample data for testing

-- Clear existing data (in reverse order of dependencies)
DELETE FROM reviews;
DELETE FROM module_iterations_courses_links;
DELETE FROM module_iterations_lecturers_links;
DELETE FROM module_iterations;
DELETE FROM modules;
DELETE FROM courses;
DELETE FROM lecturers;
DELETE FROM departments;

-- Reset sequences (for PostgreSQL)
ALTER SEQUENCE IF EXISTS departments_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS lecturers_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS modules_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS courses_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS module_iterations_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS module_iterations_lecturers_links_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS module_iterations_courses_links_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS reviews_id_seq RESTART WITH 1;

-- Insert Departments
INSERT INTO departments (name) VALUES
  ('Computer Science'),
  ('Mathematics'),
  ('Physics'),
  ('Engineering'),
  ('Business');

-- Insert Lecturers
INSERT INTO lecturers (name) VALUES
  ('Dr. Sarah Johnson'),
  ('Prof. Michael Chen'),
  ('Dr. Emily Rodriguez'),
  ('Prof. James Wilson'),
  ('Dr. Aisha Patel'),
  ('Dr. Robert Taylor'),
  ('Prof. Lisa Anderson'),
  ('Dr. David Kim'),
  ('Prof. Maria Garcia'),
  ('Dr. Thomas Brown');

-- Insert Modules (including some duplicate codes to test duplicate handling)
INSERT INTO modules (department_id, code, name, credits) VALUES
  -- Computer Science modules
  (1, 'CS101', 'Introduction to Programming', 20),
  (1, 'CS102', 'Data Structures and Algorithms', 20),
  (1, 'CS201', 'Database Systems', 20),
  (1, 'CS202', 'Web Development', 20),
  (1, 'CS301', 'Machine Learning', 20),
  (1, 'CS302', 'Software Engineering', 20),

  -- Duplicate module code (same code, different offering/department)
  (1, 'CS101', 'Introduction to Programming (Evening)', 20),

  -- Mathematics modules
  (2, 'MATH101', 'Calculus I', 20),
  (2, 'MATH102', 'Linear Algebra', 20),
  (2, 'MATH201', 'Discrete Mathematics', 20),

  -- Physics modules
  (3, 'PHYS101', 'Physics I: Mechanics', 20),
  (3, 'PHYS102', 'Physics II: Electromagnetism', 20),

  -- Engineering modules
  (4, 'ENG101', 'Engineering Design', 20),
  (4, 'ENG201', 'Systems Analysis', 20),

  -- Business modules
  (5, 'BUS101', 'Introduction to Business', 20);

-- Insert Courses (degree programs)
INSERT INTO courses (home_department_id, title) VALUES
  (1, 'BSc Computer Science'),
  (1, 'BSc Software Engineering'),
  (2, 'BSc Mathematics'),
  (2, 'BSc Mathematics and Computer Science'),
  (3, 'BSc Physics'),
  (4, 'BEng Computer Engineering'),
  (5, 'BSc Business Information Systems');

-- Insert Module Iterations (multiple years and terms)
-- CS101 (regular) - module_id 1
INSERT INTO module_iterations (module_id, academic_year_start_year, term) VALUES
  (1, '2022', 1),
  (1, '2023', 1),
  (1, '2024', 1);

-- CS102 - module_id 2
INSERT INTO module_iterations (module_id, academic_year_start_year, term) VALUES
  (2, '2022', 2),
  (2, '2023', 2),
  (2, '2024', 2);

-- CS201 - module_id 3
INSERT INTO module_iterations (module_id, academic_year_start_year, term) VALUES
  (3, '2023', 1),
  (3, '2024', 1);

-- CS202 - module_id 4
INSERT INTO module_iterations (module_id, academic_year_start_year, term) VALUES
  (4, '2023', 2),
  (4, '2024', 2);

-- CS301 - module_id 5
INSERT INTO module_iterations (module_id, academic_year_start_year, term) VALUES
  (5, '2024', 1);

-- CS302 - module_id 6
INSERT INTO module_iterations (module_id, academic_year_start_year, term) VALUES
  (6, '2024', 2);

-- CS101 Evening (duplicate code) - module_id 7
INSERT INTO module_iterations (module_id, academic_year_start_year, term) VALUES
  (7, '2023', 1),
  (7, '2024', 1);

-- MATH101 - module_id 8
INSERT INTO module_iterations (module_id, academic_year_start_year, term) VALUES
  (8, '2023', 1),
  (8, '2024', 1);

-- MATH102 - module_id 9
INSERT INTO module_iterations (module_id, academic_year_start_year, term) VALUES
  (9, '2023', 2),
  (9, '2024', 2);

-- MATH201 - module_id 10
INSERT INTO module_iterations (module_id, academic_year_start_year, term) VALUES
  (10, '2024', 1);

-- Link Module Iterations to Lecturers
INSERT INTO module_iterations_lecturers_links (module_iteration_id, lecturer_id) VALUES
  -- CS101 2022 taught by Dr. Sarah Johnson
  (1, 1),
  -- CS101 2023 taught by Dr. Sarah Johnson and Dr. David Kim
  (2, 1),
  (2, 8),
  -- CS101 2024 taught by Dr. David Kim
  (3, 8),

  -- CS102 taught by Prof. Michael Chen
  (4, 2),
  (5, 2),
  (6, 2),

  -- CS201 taught by Dr. Emily Rodriguez
  (7, 3),
  (8, 3),

  -- CS202 taught by Prof. James Wilson
  (9, 4),
  (10, 4),

  -- CS301 taught by Dr. Aisha Patel
  (11, 5),

  -- CS302 taught by Dr. Robert Taylor
  (12, 6),

  -- CS101 Evening taught by Prof. Lisa Anderson
  (13, 7),
  (14, 7),

  -- MATH modules
  (15, 9),
  (16, 9),
  (17, 10),
  (18, 10),
  (19, 9);

-- Link Module Iterations to Courses
INSERT INTO module_iterations_courses_links (module_iteration_id, course_id) VALUES
  -- CS101 is part of CS, SE, and Math+CS programs
  (1, 1), (1, 2), (1, 4),
  (2, 1), (2, 2), (2, 4),
  (3, 1), (3, 2), (3, 4),

  -- CS102 is part of CS and SE programs
  (4, 1), (4, 2),
  (5, 1), (5, 2),
  (6, 1), (6, 2),

  -- CS201 is part of CS and SE programs
  (7, 1), (7, 2),
  (8, 1), (8, 2),

  -- CS202 is part of CS and SE programs
  (9, 1), (9, 2),
  (10, 1), (10, 2),

  -- CS301 is part of CS program
  (11, 1),

  -- CS302 is part of SE program
  (12, 2),

  -- CS101 Evening is part of CS and Business IS programs
  (13, 1), (13, 7),
  (14, 1), (14, 7),

  -- MATH modules are part of Math and Math+CS programs
  (15, 3), (15, 4),
  (16, 3), (16, 4),
  (17, 3), (17, 4),
  (18, 3), (18, 4),
  (19, 3), (19, 4);

-- Insert Reviews (with various ratings and statuses)
INSERT INTO reviews (module_iteration_id, overall_rating, comment, moderation_status, like_dislike) VALUES
  -- CS101 2022 reviews
  (1, 5, 'Excellent introduction to programming! Dr. Johnson explains concepts very clearly.', 'published', 15),
  (1, 4, 'Great module, very well structured. The assignments were challenging but fair.', 'published', 8),
  (1, 5, 'Best module I have taken. Really builds a strong foundation in programming.', 'published', 12),

  -- CS101 2023 reviews
  (2, 4, 'Good module overall. Having two lecturers brought different perspectives.', 'published', 6),
  (2, 5, 'Absolutely loved this module! The practical exercises were very helpful.', 'published', 10),
  (2, 3, 'Decent module but the pace was sometimes too fast.', 'published', 2),

  -- CS101 2024 reviews
  (3, 5, 'Dr. Kim is an amazing lecturer. Makes programming fun and accessible.', 'published', 20),
  (3, 4, 'Very engaging module with lots of hands-on coding practice.', 'published', 7),

  -- CS102 2022 reviews
  (4, 5, 'Prof. Chen is brilliant! Data structures finally make sense.', 'published', 18),
  (4, 4, 'Challenging but rewarding. The algorithmic thinking skills are invaluable.', 'published', 9),

  -- CS102 2023 reviews
  (5, 5, 'Excellent module. The content is well-paced and the examples are practical.', 'published', 14),
  (5, 3, 'Good content but very heavy workload.', 'published', 3),

  -- CS201 2023 reviews
  (7, 4, 'Really useful module. SQL and database design skills are so practical.', 'published', 11),
  (7, 5, 'Dr. Rodriguez is fantastic! The project was challenging but educational.', 'published', 16),

  -- CS201 2024 reviews
  (8, 5, 'One of the most useful modules for real-world applications.', 'published', 13),
  (8, 4, 'Great introduction to databases. The assignments were very practical.', 'published', 8),

  -- CS202 2024 reviews
  (10, 5, 'Amazing module! Building actual websites was so satisfying.', 'published', 19),
  (10, 4, 'Very hands-on and practical. Learned a lot about modern web development.', 'published', 10),

  -- CS301 2024 reviews
  (11, 5, 'Fascinating introduction to ML. Dr. Patel explains complex topics clearly.', 'published', 17),
  (11, 4, 'Very interesting module but quite mathematically intensive.', 'published', 7),

  -- CS101 Evening 2023 reviews
  (13, 5, 'Perfect for mature students. Prof. Anderson is very supportive.', 'published', 9),
  (13, 4, 'Great evening option for those working during the day.', 'published', 6),

  -- CS101 Evening 2024 reviews
  (14, 5, 'Excellent module with a supportive learning environment.', 'published', 11),

  -- Some pending/rejected reviews (not published)
  (3, 2, 'This review is pending moderation.', 'reported', 0),
  (5, 1, 'Inappropriate content - rejected.', 'automatic_review', 0),

  -- MATH101 reviews
  (15, 4, 'Solid calculus course. Prof. Garcia explains concepts well.', 'published', 8),
  (16, 5, 'Excellent teaching and well-organized lectures.', 'published', 12);

-- Display summary of inserted data
SELECT 'Data insertion complete!' as status;
SELECT 'Departments:', COUNT(*) FROM departments;
SELECT 'Lecturers:', COUNT(*) FROM lecturers;
SELECT 'Modules:', COUNT(*) FROM modules;
SELECT 'Courses:', COUNT(*) FROM courses;
SELECT 'Module Iterations:', COUNT(*) FROM module_iterations;
SELECT 'Reviews (published):', COUNT(*) FROM reviews WHERE moderation_status = 'published';
