# TweetStream2Story

 The rise of social media has brought a great transformation to the way news are discovered and shared. Unlike traditional news sources, social media allows anyone to cover a story. Therefore, sometimes an event is already discussed by people before a journalist turns it into a news article. Twitter is a particularly appealing social network for discussing events, since its posts are very compact and, therefore, contain colloquial language and abbreviations. However, its large volume of tweets also makes it impossible for a user to keep up with an event.

TweetStream2Story is a framework that allows the extraction of narratives from tweets posted in real time, about a topic of choice, by automatically collecting, cleaning and summarizing tweets. The user can visualize the evolution of the topic's narrative through time in different formats, such as a knowledge graph, a list of tweets or an annotation file.


## Setup repository

 1. Install [Docker](https://www.docker.com/get-started/) 
 2. Set a password for Elasticsearch in .env file
 3. Set the same password and Twitter API credentials in server/frontend/.env file
 4. Run ```docker-compose up``` to load the containers. The server container requires the elasticsearch container to be loaded first
 5. Open localhost:8000 on your browser