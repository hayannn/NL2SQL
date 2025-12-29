SELECT
  c.id,
  c.name,
  SUM(o.amount) AS total_amount
FROM customers c
JOIN orders o ON o.customer_id = c.id
GROUP BY c.id, c.name
ORDER BY total_amount DESC
LIMIT 5;

SELECT
  o.id,
  o.customer_id,
  o.amount
FROM orders o
WHERE o.status = 'COMPLETED'
ORDER BY o.created_at DESC
LIMIT 20;