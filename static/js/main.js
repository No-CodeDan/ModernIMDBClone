document.addEventListener('DOMContentLoaded', (event) => {
    console.log('DOM fully loaded and parsed');

    // Example: Add smooth scrolling to all links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();

            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Example: Add a back-to-top button
    const backToTopButton = document.createElement('button');
    backToTopButton.innerHTML = '↑';
    backToTopButton.setAttribute('id', 'backToTop');
    backToTopButton.setAttribute('title', 'Go to top');
    backToTopButton.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 99;
        border: none;
        outline: none;
        background-color: #3b82f6;
        color: white;
        cursor: pointer;
        padding: 15px;
        border-radius: 50%;
        font-size: 18px;
    `;
    document.body.appendChild(backToTopButton);

    backToTopButton.addEventListener('click', () => {
        window.scrollTo({top: 0, behavior: 'smooth'});
    });

    window.addEventListener('scroll', () => {
        if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
            backToTopButton.style.display = 'block';
        } else {
            backToTopButton.style.display = 'none';
        }
    });

    // Real-time search functionality
    const searchInput = document.getElementById('search-input');
    const searchResultsDropdown = document.getElementById('search-results-dropdown');
    let debounceTimer;

    if (searchInput && searchResultsDropdown) {
        searchInput.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                const query = this.value.trim();
                if (query.length > 2) {
                    fetch(`/ajax_search?query=${encodeURIComponent(query)}`)
                        .then(response => response.json())
                        .then(data => {
                            searchResultsDropdown.innerHTML = '';
                            if (data.length > 0) {
                                data.forEach(movie => {
                                    const movieElement = document.createElement('div');
                                    movieElement.classList.add('search-result-item');
                                    movieElement.innerHTML = `
                                        <img src="https://image.tmdb.org/t/p/w92${movie.poster_path}" alt="${movie.title}" onerror="this.onerror=null;this.src='/static/img/no-poster.png';">
                                        <div>
                                            <h4>${movie.title}</h4>
                                            <p>${movie.release_date}</p>
                                        </div>
                                    `;
                                    movieElement.addEventListener('click', () => {
                                        window.location.href = `/movie/${movie.id}`;
                                    });
                                    searchResultsDropdown.appendChild(movieElement);
                                });
                                searchResultsDropdown.style.display = 'block';
                            } else {
                                searchResultsDropdown.style.display = 'none';
                            }
                        });
                } else {
                    searchResultsDropdown.style.display = 'none';
                }
            }, 300);
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function(event) {
            if (!searchInput.contains(event.target) && !searchResultsDropdown.contains(event.target)) {
                searchResultsDropdown.style.display = 'none';
            }
        });
    }
});
