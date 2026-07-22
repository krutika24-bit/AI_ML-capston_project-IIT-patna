-- Google Play Store Analysis SQL Queries
-- ======================================


-- Query 1: WHERE filter - Apps with price between $1 and $10
SELECT App, Category, Price, Installs
FROM apps
WHERE Price BETWEEN 1.0 AND 10.0
ORDER BY Price;


-- Query 2: Aggregate with GROUP BY - Average price and total installs per category
SELECT Category,
       COUNT(*) AS app_count,
       ROUND(AVG(Price), 2) AS avg_price,
       SUM(Installs) AS total_installs
FROM apps
GROUP BY Category
ORDER BY total_installs DESC;


-- Query 3: HAVING clause - Categories with average price > $1
SELECT Category,
       COUNT(*) AS app_count,
       ROUND(AVG(Price), 2) AS avg_price
FROM apps
GROUP BY Category
HAVING AVG(Price) > 1.0
ORDER BY avg_price DESC;


-- Query 4: ORDER BY with LIMIT - Top 10 most installed free apps
SELECT App, Category, Installs, Reviews
FROM apps
WHERE Type = 'Free'
ORDER BY Installs DESC
LIMIT 10;


-- Query 5: JOIN - App reviews sentiment analysis
SELECT a.App,
       a.Category,
       a.Installs,
       ROUND(AVG(ur.Sentiment_Polarity), 3) AS avg_sentiment_polarity,
       COUNT(ur.Translated_Review) AS review_count
FROM apps a
JOIN user_reviews ur ON a.App = ur.App
WHERE ur.Sentiment IS NOT NULL
GROUP BY a.App
ORDER BY avg_sentiment_polarity DESC
LIMIT 15;


-- Query 6: Complex query - Paid apps with high installs in specific categories
SELECT App, Category, Price, Installs, Reviews
FROM apps
WHERE Type = 'Paid'
  AND Installs > 10000
  AND Category IN ('GAME', 'FAMILY', 'TOOLS', 'PRODUCTIVITY')
ORDER BY Installs DESC
LIMIT 20;

