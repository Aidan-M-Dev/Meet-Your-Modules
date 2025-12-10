CREATE OR REPLACE FUNCTION lecturers_from_module_iteration(p_module_iteration_id INT)
RETURNS TABLE (id INT, name VARCHAR)
LANGUAGE sql
AS $$
  SELECT DISTINCT
    l.id,
    l.name
  FROM lecturers l
  INNER JOIN module_iterations_lecturers_links mil
    ON l.id = mil.lecturer_id
  WHERE mil.module_iteration_id = p_module_iteration_id
  ORDER BY l.name;
$$;
