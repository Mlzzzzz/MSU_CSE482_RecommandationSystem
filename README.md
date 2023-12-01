## MSU CSE482 Movie Recommandation System Website - Linqing Mo, Jingqiao Li

This is a course project for MSU CSE482 Big Data Analysis: Development of a recommender system Web site.

In this project, our recommendation system employs two main methodologies: User-Based and Item-Based Collaborative Filtering. These methods rely on the analysis of historical user behavior to predict future preferences.

We'd absolutely love to hear from you! If you have any thoughts, ideas, or questions about our project, please know that we're more than happy to engage. Don't hesitate to reach out to us at: molinqin@msu.edu.

The demonstration of our website can be accessed at the following URLs: http://13.58.31.191 and http://18.223.20.111 (as an alternative). Please note that our website is hosted on free servers, which may occasionally enter a sleep mode after periods of inactivity. If you experience any difficulty accessing the website, we recommend trying again after a few minutes. This should allow the servers to reactivate. For immediate assistance or if the issue persists, please feel free to contact us via email.

### Dataset Overview ###

This project utilizes the MovieLens Tag Genome Dataset 2021, available at GroupLens. This dataset comprises 10.5 million computed tag-movie relevance scores from a pool of 1,084 tags applied to 9,734 movies, released in December 2021.

The collection and generation of this dataset followed the methods described in:

Kotkov et al., 2021: Kotkov, D., Maslov, A., and Neovius, M. 2021. Revisiting the tag relevance prediction problem. In Proceedings of the 44th. International ACM SIGIR conference on Research and Development in Information Retrieval.
Vig et al., 2012: Vig, J., Sen, S., and Riedl, J. 2012. The tag genome: Encoding community knowledge to support novel interaction. ACM Trans. Interact. Intell. Syst. 2, 1-44.

### Dataset Usage and Permissions ###

The original datasets are not provided on Github. 

The dataset utilized in this project is not available for public distribution. Permission for its use has been granted by GroupLens, a research laboratory affiliated with the University of Minnesota, Twin Cities. Individuals or entities seeking access to the original dataset should direct their inquiries to GroupLens.

### Data Files Used ###

"metadata.json": 84,661 lines of movie information from MovieLens including movie title, directors, actors, date that the movie was added to MovieLens, average rating, movie id on IMDB, movie identification id.

"tags.json": 1094 lines of information about movie tags including movie tag and tag id.

"tag_count.json": 212,704 lines of numbers of times MovieLens users attached tags to movies including movie identification id, tag id and number of times users have attached the tag to the movie.

"ratings.json": 28,490,116 lines of user ratings on MovieLens - movie identification id, user id and rating. Each rating corresponds to several stars from 0.5 till 5 with the granularity of 0.5 star.

"survey_answers.json": 58,903 lines of ratings that MovieLens users gave to movie-tag pairs in the survey including user id, movie identification id, tag id and movie-tag rating. The users were asked to indicate the degree, to which a tag applies to a movie on a 5-point scale from the tag not applying at all (1 point) to applying very strongly (5 points).

### Restrictions on Commercial Utilization ###

It is important to emphasize that the development and deployment of this program have been carried out solely for academic and educational objectives. The program is not designed or permitted for use in any commercial capacity.
