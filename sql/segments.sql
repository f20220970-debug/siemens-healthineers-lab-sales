-- name: by_segment
SELECT territory, type, COUNT(*) accounts, ROUND(AVG(tests_per_day)) avg_tests_per_day,
       ROUND(SUM(value_lakh) / 100, 1) total_value_cr,
       SUM(CASE WHEN tier = 'A' THEN 1 ELSE 0 END) tier_a
FROM scored GROUP BY 1, 2 ORDER BY total_value_cr DESC;

-- name: by_vendor
SELECT current_vendor, COUNT(*) accounts, ROUND(AVG(analyser_age_yrs), 1) avg_age,
       SUM(CASE WHEN analyser_age_yrs >= 7 THEN 1 ELSE 0 END) due_for_replacement,
       ROUND(AVG(fit_score), 1) avg_fit
FROM scored GROUP BY 1 ORDER BY avg_fit DESC;

-- name: budget_calendar
-- Tier A accounts by budget month: when to time demos (3 months before budget)
SELECT budget_month, COUNT(*) tier_a_accounts, ROUND(SUM(value_lakh) / 100, 1) value_cr
FROM scored WHERE tier = 'A' GROUP BY 1 ORDER BY 1;
