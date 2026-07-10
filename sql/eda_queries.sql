-- Optional SQL checks for cleaned customer support ticket data.
-- Import data/processed/tickets_cleaned.csv into your SQL tool first.

-- Ticket volume by category
SELECT
  actual_category,
  COUNT(*) AS ticket_count
FROM tickets_cleaned
GROUP BY actual_category
ORDER BY ticket_count DESC;

-- Ticket volume by priority
SELECT
  actual_priority,
  COUNT(*) AS ticket_count
FROM tickets_cleaned
GROUP BY actual_priority
ORDER BY ticket_count DESC;

-- Ticket volume by department
SELECT
  actual_department,
  COUNT(*) AS ticket_count
FROM tickets_cleaned
GROUP BY actual_department
ORDER BY ticket_count DESC;

-- Category and priority mix for triage planning
SELECT
  actual_category,
  actual_priority,
  COUNT(*) AS ticket_count
FROM tickets_cleaned
GROUP BY actual_category, actual_priority
ORDER BY ticket_count DESC;
