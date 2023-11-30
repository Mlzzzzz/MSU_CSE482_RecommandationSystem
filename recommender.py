import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import json

class Recommender(object):
    def __init__(self):         
        self.movies_info = {}
        self.ratings = pd.read_csv('ratings.csv')
        self.users_avg_rating = pd.read_csv('users_avg_rating.csv')
        self.movie_info = pd.read_json('metadata.json', lines=True)

        # Load item-based similarity data from JSON files
        with open('similarity_data_tags.json', 'r') as file:
            self.similarity_data_tags = json.load(file)
            self.similarity_data_tags = {
                int(float(key)): {int(float(nested_key)): value for nested_key, value in nested_dict.items()}
                for key, nested_dict in self.similarity_data_tags.items()
            }
        with open('similarity_data_actors.json', 'r') as file:
            self.similarity_data_actors = json.load(file)
            self.similarity_data_actors = {
                int(float(key)): {int(float(nested_key)): value for nested_key, value in nested_dict.items()}
                for key, nested_dict in self.similarity_data_actors.items()
            }
        with open('similarity_data_director.json', 'r') as file:
            self.similarity_data_director = json.load(file)
            self.similarity_data_director = {int(key): value for key, value in self.similarity_data_director.items()}


    def get_movieinfo(self):
        for _, row in self.movie_info.iterrows():
            self.movies_info[row['item_id']] = row['title']


    # user-based
    def recommender_user_based(self, input_data, n=20):
        """
        Recommend movies to a user by combining nearest neighbor finding, rating prediction, 
        and sorting by predicted ratings, with a limit of top 10 movies per neighbor.

        Parameters:
        input_data (list of dicts): A list where each dict contains 'item_id' and 'rating' keys, 
        representing movies rated by the user.

        Returns:
        list of dicts: A list of dictionaries sorted by their predicted ratings. Each dictionary contains 
        'rank' and 'movie name', where 'rank' is the order to recommend movies and 'movie name' is the 
        movie's name retrieved from self.movies_info.
        """
        input_df = pd.DataFrame(input_data)
        # Find Nearest Neighbours
        watched_movies = input_df['item_id'].unique()
        relevant_ratings = self.ratings[self.ratings['item_id'].isin(watched_movies)]
        user_item_matrix = relevant_ratings.pivot_table(index='user_id', columns='item_id', values='rating').fillna(0)
        user_profile = input_df.set_index('item_id').reindex(user_item_matrix.columns).fillna(0).T
        similarity = cosine_similarity(user_profile, user_item_matrix)
        similarity_df = pd.DataFrame(similarity.T, index=user_item_matrix.index, columns=['cos_sim'])
        top_neighbours = similarity_df.sort_values(by='cos_sim', ascending=False).head(n).reset_index()
        

        # Limit to Top N Movies for Each Neighbor
        top_movies_by_neighbour = {}
        for neighbor_id in top_neighbours['user_id']:
            top_movies = self.ratings[self.ratings['user_id'] == neighbor_id].sort_values(by='rating', ascending=False).head(10)['item_id'].tolist()
            top_movies_by_neighbour[neighbor_id] = top_movies

        # Aggregate Movies to Predict
        movies_to_predict = set()
        for movies in top_movies_by_neighbour.values():
            movies_to_predict.update(movies)
        movies_to_predict -= set(input_df['item_id'])

        # Predict Ratings
        users_avg_ratings_dict = self.users_avg_rating.set_index('user_id')['rating'].to_dict()
        
        predictions = []
        useravg_rating = input_df['rating'].mean()  
        for movie_id in movies_to_predict:
            numerator, denominator = 0, 0
            for _, row in top_neighbours.iterrows():
                neighbor_id = row['user_id']
                if movie_id in top_movies_by_neighbour[neighbor_id]:
                    cos_sim = row['cos_sim']
                    neighbor_ratings = self.ratings.loc[(self.ratings['user_id'] == neighbor_id) & (self.ratings['item_id'] == movie_id), 'rating']
                    if not neighbor_ratings.empty:
                        neighbor_rating = neighbor_ratings.iloc[0]
                        neighbor_avg_rating = users_avg_ratings_dict.get(neighbor_id, 0) 
                        numerator += cos_sim * (neighbor_rating - neighbor_avg_rating)
                        denominator += abs(cos_sim)

            # Calculate Predicted Rating
            pred_rating = useravg_rating if denominator == 0 else useravg_rating + (numerator / denominator)
            predictions.append((movie_id, pred_rating))

        # Sort and Return Recommendations
        recommended_movies_list = sorted(predictions, key=lambda x: x[1], reverse=True)
        recommended_movies_with_names = []
        for i, (movie_id, _) in enumerate(recommended_movies_list):
            movie_name = self.movies_info.get(movie_id, "Unknown Movie")
            recommended_movies_with_names.append({'rank': i+1, 'movie name': movie_name})

        return recommended_movies_with_names


    # item-based
    def recommender_item_based(self, input_data, weights=[0.77186, 1.80313, 0.25901],):
        """
        Recommend movies to a user based on item-based collaborative filtering. 
        This function uses director, actor, and tag similarities to find movies similar to those rated by the user. 
        It combines these similarities using a weighted approach to predict ratings for potential recommendations.

        Parameters:
        input_data (list of dicts): A list where each dict contains 'item_id' and 'rating' keys, 
        representing movies rated by the user.
        weights (list of floats): A list of three weights [w1, w2, w3] used to combine similarities based on 
        tags, actors, and directors, respectively.

        Returns:
        list of dicts: A list of dictionaries sorted by their predicted ratings. Each dictionary contains 
        'rank' and 'movie name', where 'rank' is the order to recommend movies and 'movie name' is the 
        movie's name retrieved from self.movies_info.
        """

        input_df = pd.DataFrame(input_data)
        COSINE_SIMILARITY_THRESHOLD = 0.35
        JACCARD_SIMILARITY_THRESHOLD = 0.15
        
        # Determine the set of movies rated by the user
        rated_movies = set(input_df["item_id"])
        
        # Initialize a set for potential recommended movies
        possible_recommended_movies = set()
        
        # Iterate through each movie rated by the user
        for movie_id in rated_movies:
            # Filter out movies sharing the same director, actors, and tags
            movies_with_same_director = set(self.similarity_data_director.get(movie_id, []))
            movies_with_similar_actors = {other_movie_id for other_movie_id, jac_sim in self.similarity_data_actors.get(movie_id, {}).items() if jac_sim > JACCARD_SIMILARITY_THRESHOLD}
            movies_with_similar_tags = {other_movie_id for other_movie_id, cos_sim in self.similarity_data_tags.get(movie_id, {}).items() if cos_sim > COSINE_SIMILARITY_THRESHOLD}
            
            # Combine all filtered movies
            possible_recommended_movies.update(movies_with_same_director, movies_with_similar_actors, movies_with_similar_tags)
        
        # Remove movies already rated by the user
        possible_recommended_movies.difference_update(rated_movies)
        
        # Calculate the weighted rating for each potentially recommended movie
        movie_scores = {}
        for movie_id in possible_recommended_movies:
            total_similarity = 0
            weighted_ratings_sum = 0
            
            # Iterate through each movie in the baseline set (input_df)
            for _, row in input_df.iterrows():
                baseline_movie_id = row['item_id']
                user_rating = row['rating']
                
                # Calculate similarities
                sim_tags = self.similarity_data_tags.get(baseline_movie_id, {}).get(movie_id, 0)
                sim_actors = self.similarity_data_actors.get(baseline_movie_id, {}).get(movie_id, 0)
                sim_director = 1 if baseline_movie_id in self.similarity_data_director.get(movie_id, []) else 0
                
                # Conditional restrict for sim_actors
                if sim_tags == 0 and sim_director == 0 and sim_actors <= 0.3:
                    continue
                
                # Combine similarities
                sim_combine = (weights[0] * sim_tags + weights[1] * sim_actors + weights[2] * sim_director)
                
                # Calculate weighted sum
                weighted_ratings_sum += sim_combine * user_rating
                total_similarity += sim_combine
            
            # Calculate predicted rating
            predicted_score = weighted_ratings_sum / total_similarity if total_similarity != 0 else 0
            movie_scores[movie_id] = predicted_score
        
        # Create a DataFrame for recommended movies
        recommended_movies_list = sorted(movie_scores.items(), key=lambda x: x[1], reverse=True)
        recommended_movies_with_names = []
        for i, (movie_id, _) in enumerate(recommended_movies_list):
            movie_name = self.movies_info.get(movie_id, "Unknown Movie")
            recommended_movies_with_names.append({'rank': i+1, 'movie name': movie_name})

        return recommended_movies_with_names
