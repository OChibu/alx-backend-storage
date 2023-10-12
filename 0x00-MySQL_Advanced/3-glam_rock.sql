-- lists all bands with Glam rock as their main style, ranked by their longevity
SELECT band_name,(YEAR('2022-01-01') - YEAR(formed)) + 1 AS lifespan
FROM bands
WHERE style = 'Glam rock'
ORDER BY lifespan DESC;
