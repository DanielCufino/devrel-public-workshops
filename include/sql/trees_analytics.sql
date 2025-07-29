-- Simplified trees Analytics
-- Shows total users and top 5 tree recommendations

-- Total number of users
SELECT 
    'User Stats' as metric_category,
    'Total Users' as metric_name,
    COUNT(*) as metric_value,
    'users' as metric_unit
FROM users

UNION ALL

-- Top 5 most recommended tree species
SELECT 
    'Top Species' as metric_category,
    CONCAT('#', ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC), ' - ', tsc.common_name) as metric_name,
    COUNT(*) as metric_value,
    'recommendations' as metric_unit
FROM tree_recommendations tr
JOIN tree_species_catalog tsc ON tr.species_id = tsc.species_id
GROUP BY tsc.species_id, tsc.common_name
ORDER BY COUNT(*) DESC
LIMIT 5;
