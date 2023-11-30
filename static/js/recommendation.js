// Initialize global variables
var ratedMovies = {}; // Stores user-rated movies
var currentPage = 1; // Current page for pagination
var itemsPerPage = 20; // Number of items per page
var currentRecommendations = {}; // Stores current recommendations

// Event listener for DOM content loaded
document.addEventListener('DOMContentLoaded', function () {
    // Initialize search input, rating submission, and delete functionality
    var searchInput = document.getElementById('movie-search');
    var searchResults = document.getElementById('search-results');
    var selectedMovie = document.getElementById('selected-movie');
    var movieRating = document.getElementById('movie-rating');
    var ratingContainer = document.getElementById('rating-container');

    // Hide table headers initially
    document.getElementById('rated-movies-table').querySelector('thead').style.display = 'none';
    document.getElementById('user-recommendations-table').querySelector('thead').style.display = 'none';
    document.getElementById('item-recommendations-table').querySelector('thead').style.display = 'none';

    // Hide rating section initially
    document.getElementById('rating-container').style.display = 'none';

// Event listener for search input
searchInput.addEventListener('input', function () {
    var searchText = searchInput.value.toLowerCase();
    searchResults.innerHTML = ''; 
    if (searchText.length > 2) {
        for (var movieId in moviesInfo) {
            if (moviesInfo[movieId].toLowerCase().includes(searchText)) {
                // Create an anchor element instead of a list item
                var listItem = document.createElement('a');
                listItem.textContent = moviesInfo[movieId];
                listItem.setAttribute('href', '#'); 
                listItem.setAttribute('data-movie-id', movieId);
                
                // Add Bootstrap list group classes
                listItem.classList.add('list-group-item', 'list-group-item-action');
                
                // Add event listener for click 
                listItem.addEventListener('click', function (e) {
                    e.preventDefault();
                    selectedMovie.textContent = 'Selected Movie: ' + this.textContent;
                    selectedMovie.setAttribute('data-movie-id', this.getAttribute('data-movie-id'));
                    movieRating.value = '';
                    ratingContainer.style.display = 'block';
                });
                
                listItem.addEventListener('click', onSearchResultClick);

                // Append the anchor element to the search results container
                searchResults.appendChild(listItem);
            }
        }
    }
});

// Handle clicks of search results: visualiza the rating box
function onSearchResultClick(e) {
    e.preventDefault(); 
    var ratingContainer = document.getElementById('rating-container');
    var userBasedRecommendations = document.querySelector('.user-based-recommendations');
    var itemBasedRecommendations = document.querySelector('.item-based-recommendations');
    var selectedMovie = document.getElementById('selected-movie');
    var movieRating = document.getElementById('movie-rating');

    selectedMovie.textContent = 'Selected Movie: ' + this.textContent;
    selectedMovie.setAttribute('data-movie-id', this.getAttribute('data-movie-id'));
    movieRating.value = '';
    
    // Make the containers visible
    ratingContainer.style.display = 'block';
    userBasedRecommendations.style.display = 'block';
    itemBasedRecommendations.style.display = 'block';
}

    // Event listener for submit rating button
    document.getElementById('submit-rating').addEventListener('click', function () {
        var movieId = selectedMovie.getAttribute('data-movie-id');
        var movieName = selectedMovie.textContent.replace('Selected Movie: ', '');
        var rating = movieRating.value;
        var ratingReminder = document.getElementById('rating-reminder');

        if (!rating) {
            // Show a reminder message if no rating is selected
            document.getElementById('rating-reminder').textContent = 'Please select a rating before submitting.';
            ratingReminder.style.display = 'block';
            return;
        } else {
            // Clear the reminder message if there is one
            document.getElementById('rating-reminder').textContent = '';
            ratingReminder.style.display = 'none';
        }

        ratedMovies[movieId] = {
            name: movieName,
            rating: rating
        };

        updateRatedMoviesDisplay();
    });

    // Function to update rated movies display
    function updateRatedMoviesDisplay() {
        var ratedMoviesList = document.getElementById('rated-movies-list');
        var tableHeader = document.getElementById('rated-movies-table').querySelector('thead');
        ratedMoviesList.innerHTML = '';

        var hasData = false;
        for (var id in ratedMovies) {
            var movie = ratedMovies[id];
            var row = document.createElement('tr');

            var cellId = document.createElement('td');
            cellId.textContent = id;
            row.appendChild(cellId);

            var cellName = document.createElement('td');
            cellName.textContent = movie.name;
            row.appendChild(cellName);

            var cellRating = document.createElement('td');
            cellRating.textContent = movie.rating;
            row.appendChild(cellRating);

            var deleteCell = document.createElement('td');
            var deleteButton = document.createElement('button');
            deleteButton.textContent = 'Delete';
            deleteButton.className = 'btn btn-outline-danger';
            deleteButton.onclick = function () {
                deleteRatedMovie(id);
            };
            deleteCell.appendChild(deleteButton);
            row.appendChild(deleteCell);

            ratedMoviesList.appendChild(row);
            hasData = true;
        }

        tableHeader.style.display = hasData ? '' : 'none';
    }

    // Function to delete a rated movie
    function deleteRatedMovie(movieId) {
        delete ratedMovies[movieId];
        updateRatedMoviesDisplay();
    }

    document.getElementById('generate-user-based').addEventListener('click', function () {
        if (Object.keys(ratedMovies).length === 0) {
            // Show reminder message if no movies are rated
            document.getElementById('generate-reminder').textContent = 'Please rate some movies before generating recommendations.';
            return;
        } else {
            document.getElementById('generate-reminder').textContent = '';
            fetchRecommendations('/recommend/user-based', 'user-recommendations');
        }
    });
    
    document.getElementById('generate-item-based').addEventListener('click', function () {
        if (Object.keys(ratedMovies).length === 0) {
            // Show reminder message if no movies are rated
            document.getElementById('generate-reminder').textContent = 'Please rate some movies before generating recommendations.';
            return;
        } else {
            document.getElementById('generate-reminder').textContent = '';
            fetchRecommendations('/recommend/item-based', 'item-recommendations');
        }
    });
});

// Fetches recommendations from the server and handles pagination
function fetchRecommendations(endpoint, containerId) {
    var ratedMoviesArray = Object.keys(ratedMovies).map(movieId => {
        return {
            item_id: parseInt(movieId),
            rating: parseFloat(ratedMovies[movieId].rating)
        };
    });

    fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(ratedMoviesArray)
    })
        .then(response => response.json())
        .then(data => {
            currentRecommendations[containerId] = data;
            paginateRecommendations(data, containerId);
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// Paginates the recommendations for display
function paginateRecommendations(recommendations, containerId) {
    var container = document.getElementById(containerId);
    var tableHeader = document.getElementById(containerId + '-table').querySelector('thead');
    container.innerHTML = '';

    tableHeader.style.display = '';

    var startIndex = (currentPage - 1) * itemsPerPage;
    var endIndex = startIndex + itemsPerPage;
    var paginatedItems = recommendations.slice(startIndex, endIndex);

    paginatedItems.forEach((movie, index) => {
        var row = document.createElement('tr');

        var cellIndex = document.createElement('td');
        cellIndex.textContent = startIndex + index + 1;
        row.appendChild(cellIndex);

        var cellName = document.createElement('td');
        cellName.textContent = movie['movie name'];
        row.appendChild(cellName);

        container.appendChild(row);
    });

    updatePaginationButtons(containerId, recommendations.length);
}

// Updates the pagination buttons based on the current page and total number of items
function updatePaginationButtons(containerId, totalItems) {
    var totalPages = Math.ceil(totalItems / itemsPerPage);
    var paginationContainer = document.getElementById(containerId + '-pagination');
    paginationContainer.innerHTML = '';

    var prevButton = document.createElement('button');
    prevButton.textContent = 'Previous';
    prevButton.disabled = currentPage === 1;
    prevButton.onclick = function () {
        currentPage--;
        paginateRecommendations(currentRecommendations[containerId], containerId);
    };
    paginationContainer.appendChild(prevButton);

    var nextButton = document.createElement('button');
    nextButton.textContent = 'Next';
    nextButton.disabled = currentPage === totalPages;
    nextButton.onclick = function () {
        currentPage++;
        paginateRecommendations(currentRecommendations[containerId], containerId);
    };
    paginationContainer.appendChild(nextButton);
}

