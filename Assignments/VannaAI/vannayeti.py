import vanna
from vanna.remote import VannaDefault
# vn = VannaDefault(model='chinook', api_key=vanna.get_api_key('susanths@gmail.com'))
vn = VannaDefault(model='chinook', api_key='e2d5934bd041425b818848ba7c4f6111')
vn.connect_to_sqlite('Chinook.sqlite')
# vn.ask("What are the top 10 albums by sales?")
# vn.ask("What is the total sales by genre?")
# vn.ask("How many tracks are there in each genre?")
# vn.ask("What is the cricket score?")
vn.ask("How many artists are there in each genre?")
# vn.generate_question("SELECT g.Name AS Genre, SUM(il.Quantity) AS TotalSales \
# FROM Genre g \
# JOIN Track t ON g.GenreId = t.GenreId \
# JOIN InvoiceLine il ON t.TrackId = il.TrackId \
# GROUP BY g.GenreId, g.Name")
# SELECT g.Name AS Genre, SUM(il.Quantity) AS TotalSales
# FROM Genre g
# JOIN Track t ON g.GenreId = t.GenreId
# JOIN InvoiceLine il ON t.TrackId = il.TrackId
# GROUP BY g.GenreId, g.Name;
# SELECT g.Name AS Genre, SUM(il.Quantity) AS TotalSales
# FROM Genre g
# JOIN Track t ON g.GenreId = t.GenreId
# JOIN InvoiceLine il ON t.TrackId = il.TrackId
# GROUP BY g.GenreId, g.Name;")