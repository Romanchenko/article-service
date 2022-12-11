#!/usr/bin/env bash

mongo admin -u made -p password --eval "db.createUser({user: 'made_user', pwd: 'password2', roles: [{role: 'readWrite', db: 'main'}]});"

echo "start importing data"
# db_to_feed needs to be defined
# mongorestore -u mongoadmin -p mypass --authenticationDatabase admin -d db_to_feed ./mongo-seed-data
# e.g.
mongoimport --host 127.0.0.1:27017 --db main --collection articles --type json --file /articles2.json --jsonArray --mode=upsert -u made_user -p password2 --authenticationDatabase=admin
mongoimport --host 127.0.0.1:27017 --db main --collection authors --type json --file /mongo_seed/mongo_seed/data/authors.json --jsonArray -u made_user -p password2 --authenticationDatabase=admin
echo "data imported"


echo "Doing other useful mongodb database stuff, e.g creating additional mongo users..."

echo "Mongo users created."

mongosh mongodb://made_user:password2@127.0.0.1:27017
db.articles.find().forEach( function(myDoc) {
  const newRefs = [];
  if (myDoc.references !== undefined) {
    myDoc.references.forEach(r => newRefs.push(ObjectId(r)));
    db.articles.updateOne({_id: myDoc._id}, {$set:{"references": newRefs}})
  }
});

