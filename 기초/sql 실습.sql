SELECT * FROM north_wind.customers;


SELECT*,
CASE
	WHEN UNITPRICE <30 THEN '저'
    WHEN UNITPRICE <50 THEN '중'
    ELSE '고'
END AS '가격' -- AS는 생략 가능...
-- 모든 컬럼의 별칭을 다 지을 수 있다!
FROM products;

-- COLUM에 별칭 정하기
SELECT PRODUCTID AS 'ID', PRODUCTNAME AS '이름', UNITPRICE AS'가격'
FROM PRODUCTS;

-- COUNT
SELECT COUNT(*)
FROM PRODUCTS
WHERE UNITPRICE>30; -- 여기서 집계할 때 NULL값은 없는 것으로 친다.
--
SELECT COUNT(*)
FROM CUSTOMERS;
--
SELECT COUNT(REGION) -- 여기서 집계할 때 NULL값은 없는 것으로 친다.
FROM CUSTOMERS;
--
SELECT COUNT(REGION)
FROM CUSTOMERS;
-- AVG
SELECT AVG(UNITPRICE) 'AVG_PRICE'
FROM PRODUCTS
WHERE UNITPRICE >30;

-- SUM
SELECT SUM(UNITPRICE)
FROM PRODUCTS;

-- MAX
SELECT MAX(UNITPRICE)
FROM products;
-- MIN
SELECT MIN(UNITPRICE)
FROM PRODUCTS;
-- GROUP BY
SELECT COUNTRY, COUNT(*)
FROM CUSTOMERS -- HAVING은 GROUP BY 된 것에서 사용
-- (WHERE)
GROUP BY COUNTRY
HAVING COUNT(CONTACTNAME) <9
ORDER BY COUNT(CONTACTNAME) DESC;
-- LIMIT
-- OFFSET
-- 각 항목의 순서를 잘 지켜 주어야 한다.

-- '같지 않다': <>

--
SELECT * 
FROM PRODUCTS
WHERE UNITPRICE BETWEEN 15 AND 20;
-- 가격이 15에서 20사이인 상품
-- 의 생산자 목록 조회
-- 서브 쿼리
SELECT *
FROM SUPPLIERS
WHERE SUPPLIERS.SUPPLIERID IN (
	SELECT SUPPLIERID
    FROM PRODUCTS
    WHERE UNITPRICE BETWEEN 15 AND 20
);
-- DESC suppliers;
DESCRIBE suppliers;
--
-- CASE END
SELECT SupplierID,
CASE SupplierID
	when 1 then 'A'
    when 2 then 'B'
    when 3 then 'C'
    else 'D'
END as 'pr'
FROM PRODUCTS;

-- Column 만들기
Select UnitPrice, UnitPrice*2 -- 연산까지 반영해서 칼럼을 뽑아낼 수 있다규
from products;

-- limit : 개수
-- offset : 페이지네이션

-- ALIAS
DESC customers;
select country, count(*)
from customers
group by country
order by count(*) DESC;

-- ALIAS
Select customerID, city, address, country
from customers as c
where country = 'USA';

-- ALIAS
DESC products;
DESC suppliers;

Select products.productID, products.ProductName, suppliers.supplierID, suppliers.CompanyName
from products, suppliers
where products.supplierID= suppliers.supplierID;

select p.*, s.*
from products as p, suppliers as s -- 별칭!!
where p.supplierID=s.supplierID;

-- INNER JOIN : 교집합

-- union -> 중복이 없다 파이썬의 dataframe에서 extend와 비슷
-- 같은 의미에 있는 것을 한번에 저장하자는 의미!

-- Join
Select ProductID, ProductName, products.SupplierID, Suppliers.CompanyName
From products
Join Suppliers
ON products.SupplierID = Suppliers.SupplierID
Order By Suppliers.supplierID
LIMIT 10;

-- Outer Join
Select ProductID, ProductName, products.SupplierID, Suppliers.CompanyName
From products
left Join Suppliers
ON products.SupplierID = Suppliers.SupplierID
Order By Suppliers.supplierID
LIMIT 10;



-- Outer Join
Select ProductID, ProductName, products.SupplierID, Suppliers.CompanyName
From products
right Join Suppliers
ON products.SupplierID = Suppliers.SupplierID
Order By Suppliers.supplierID
LIMIT 10;
