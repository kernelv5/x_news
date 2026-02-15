
# Twitter Token 

Bearer Token AAAAAAAAAAAAAAAAAAAAAE9F7gEAAAAA%2Fq2DeNWTyeeqUhriXmU%2BSD2DOLY%3DYObtPfwmmR5xnsBLFXcnCMhQKOtlna3vLgkkCD4TKvEl2C81tg



# MongoDB Connection String
mongodb://localhost:27017
Database : eNews
Collection : source-twitter

docker-compose build --no-cache backend

docker-compose build --no-cache frontend
docker-compose up -d backend
docker-compose up -d --remove-orphans
docker-compose down 

docker-compose restart backend

docker-compose down
docker-compose build
docker-compose up -d