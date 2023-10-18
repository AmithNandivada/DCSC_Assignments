--How many animals of each type have outcomes?
select a.animal_type, count(distinct a.animal_id) from animal_dim a
join outcome_fct o on o.animal_dim_key = a.animal_dim_key 
join outcome_dim od on o.outcome_dim_key = od.outcome_dim_key 
where od.outcome_type is not null
group by a.animal_type ;


--How many animals are there with more than 1 outcome?
select count(animal_id) animals
from(select a.animal_id from animal_dim a
join outcome_fct o on o.animal_dim_key = a.animal_dim_key 
join outcome_dim od on o.outcome_dim_key = od.outcome_dim_key 
where od.outcome_type is not null
group by a.animal_id having count(*)>1)as sub;


--What are the top 5 months for outcomes? 
select t.mnth,count(t.mnth) from timing_dim t 
join outcome_fct o on o.time_dim_key = t.time_dim_key 
join outcome_dim od on od.outcome_dim_key  = o.outcome_dim_key
where o.outcome_type is not null
group by t.mnth
order by 2 desc 
limit 5;


--What is the total number percentage of kittens, adults, and seniors, whose outcome is "Adopted"?
--Conversely, among all the cats who were "Adopted", what is the total number percentage of kittens, adults, and seniors?

WITH cat_age_groups AS (
  SELECT
    ad.animal_dim_key,
    CASE
      WHEN AGE(ad.dob) < INTERVAL '1 year' THEN 'Kittens'
      WHEN AGE(ad.dob) >= INTERVAL '1 year' AND AGE(ad.dob) <= INTERVAL '10 years' THEN 'Adults'
      WHEN AGE(ad.dob) > INTERVAL '10 years' THEN 'Seniors'
      ELSE 'Unknown'
    END AS cat_age_grp
  FROM animal_dim ad where ad.animal_type = 'Cat'
)

SELECT
  cat_age_grp,
  COUNT(*) totalcount
FROM outcome_fct o
JOIN cat_age_groups c ON o.animal_dim_key  = c.animal_dim_key
JOIN outcome_dim od ON o.outcome_dim_key  = od.outcome_dim_key 
WHERE od.outcome_type  = 'Adoption'
GROUP BY cat_age_grp;


--For each date, what is the cumulative total of outcomes up to and including this date?
SELECT 
    date(a.timestmp) "date",
    COUNT(a.animal_dim_key) ,
    SUM(COUNT(a.animal_dim_key)) OVER (ORDER BY date(a.timestmp) ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_total
FROM 
    animal_dim a 
    LEFT JOIN outcome_fct o2 ON a.animal_dim_key = o2.animal_dim_key
    LEFT JOIN outcome_dim o ON o2.outcome_dim_key = o.outcome_dim_key 
WHERE 
    o.outcome_type IS NOT NULL
GROUP BY 
    date(a.timestmp)
ORDER BY 
    date_only;