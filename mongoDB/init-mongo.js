// Initialize MongoDB database and collections
db = db.getSiblingDB('eNews');

// Create x_account collection
db.createCollection('x_account');

// Create indexes
db.x_account.createIndex({ "x_account": 1 }, { unique: true });
db.x_account.createIndex({ "x_account_id": 1 });
db.x_account.createIndex({ "is_active": 1 });

// Create source-twitter collection for storing tweets
db.createCollection('source-twitter');
db['source-twitter'].createIndex({ "tweet_id": 1 }, { unique: true });
db['source-twitter'].createIndex({ "x_account_id": 1 });
db['source-twitter'].createIndex({ "created_at": -1 });

print('Database initialized successfully');
