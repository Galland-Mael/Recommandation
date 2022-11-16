.open 
.headers on 
.mode csv
.output ratings.csv
.open db.sqlite3
SELECT restaurant_id,user_id,note from appsae_avis;

