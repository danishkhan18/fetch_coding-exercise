-- Query 1: Top 5 brands by receipts scanned for the latest month
WITH LatestMonth AS (
    SELECT MAX(DATEPART(YEAR, purchaseDate)) AS LatestYear,
           MAX(DATEPART(MONTH, purchaseDate)) AS LatestMonth
    FROM Receipts
)
SELECT TOP 5 br.name AS Brand, COUNT(DISTINCT rc.receipt_id) AS TotalReceipts
FROM Receipts rc
JOIN ReceiptItems ri ON rc.receipt_id = ri.receipt_id
JOIN Brands br ON ri.barcode = br.barcode
CROSS JOIN LatestMonth lm
WHERE DATEPART(YEAR, rc.purchaseDate) = lm.LatestYear
  AND DATEPART(MONTH, rc.purchaseDate) = lm.LatestMonth
GROUP BY br.name
ORDER BY TotalReceipts DESC;

/* ------------------------------------------------------------ */

-- Query 2: Compare top 5 brands between the latest month and the previous month
WITH MonthlyData AS (
    SELECT br.name AS Brand,
           DATEPART(YEAR, rc.purchaseDate) AS YearVal,
           DATEPART(MONTH, rc.purchaseDate) AS MonthVal,
           COUNT(DISTINCT rc.receipt_id) AS TotalReceipts
    FROM Receipts rc
    JOIN ReceiptItems ri ON rc.receipt_id = ri.receipt_id
    JOIN Brands br ON ri.barcode = br.barcode
    GROUP BY br.name, DATEPART(YEAR, rc.purchaseDate), DATEPART(MONTH, rc.purchaseDate)
),
LatestMonth AS (
    SELECT MAX(YearVal) AS LatestYear, MAX(MonthVal) AS LatestMonth FROM MonthlyData
),
TopBrandData AS (
    SELECT Brand, TotalReceipts, YearVal, MonthVal
    FROM MonthlyData
    WHERE (YearVal = (SELECT LatestYear FROM LatestMonth) AND MonthVal = (SELECT LatestMonth FROM LatestMonth))
       OR (YearVal = (SELECT LatestYear FROM LatestMonth) AND MonthVal = (SELECT LatestMonth FROM LatestMonth) - 1)
)
SELECT Brand,
       SUM(CASE WHEN MonthVal = (SELECT LatestMonth FROM LatestMonth) THEN TotalReceipts ELSE 0 END) AS CurrentMonthReceipts,
       SUM(CASE WHEN MonthVal = (SELECT LatestMonth FROM LatestMonth) - 1 THEN TotalReceipts ELSE 0 END) AS PreviousMonthReceipts
FROM TopBrandData
GROUP BY Brand
ORDER BY CurrentMonthReceipts DESC, PreviousMonthReceipts DESC;

/* ------------------------------------------------------------ */

-- Query 3: Average spend comparison between 'Accepted' and 'Rejected' receipts
SELECT rewardsReceiptStatus,
       AVG(CAST(totalSpent AS DECIMAL(10,2))) AS AverageSpend
FROM Receipts
WHERE rewardsReceiptStatus IN ('Accepted', 'Rejected')
GROUP BY rewardsReceiptStatus;

/* ------------------------------------------------------------ */

-- Query 4: Total number of items purchased for 'Accepted' vs 'Rejected' receipts
SELECT rc.rewardsReceiptStatus,
       SUM(ri.quantityPurchased) AS TotalItems
FROM Receipts rc
JOIN ReceiptItems ri ON rc.receipt_id = ri.receipt_id
WHERE rc.rewardsReceiptStatus IN ('Accepted', 'Rejected')
GROUP BY rc.rewardsReceiptStatus;

/* ------------------------------------------------------------ */

-- Query 5: Brand with highest spend among users created in the last 6 months
WITH ActiveUsers AS (
    SELECT user_id
    FROM Users
    WHERE createdDate >= DATEADD(MONTH, -6, GETDATE())
)
SELECT TOP 1 br.name AS Brand, SUM(CAST(rc.totalSpent AS DECIMAL(10,2))) AS TotalExpenditure
FROM Receipts rc
JOIN ReceiptItems ri ON rc.receipt_id = ri.receipt_id
JOIN Brands br ON ri.barcode = br.barcode
JOIN ActiveUsers au ON rc.user_id = au.user_id
GROUP BY br.name
ORDER BY TotalExpenditure DESC;

/* ------------------------------------------------------------ */

-- Query 6: Brand with highest transactions among users created in the last 6 months
WITH ActiveUsers AS (
    SELECT user_id
    FROM Users
    WHERE createdDate >= DATEADD(MONTH, -6, GETDATE())
)
SELECT TOP 1 br.name AS Brand, COUNT(DISTINCT rc.receipt_id) AS TransactionCount
FROM Receipts rc
JOIN ReceiptItems ri ON rc.receipt_id = ri.receipt_id
JOIN Brands br ON ri.barcode = br.barcode
JOIN ActiveUsers au ON rc.user_id = au.user_id
GROUP BY br.name
ORDER BY TransactionCount DESC;
