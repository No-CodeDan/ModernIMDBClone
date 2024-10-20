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
                                data.forEach(result => {
                                    const resultElement = document.createElement('div');
                                    resultElement.classList.add('search-result-item');
                                    resultElement.innerHTML = `
                                        <img src="https://image.tmdb.org/t/p/w92${result.poster_path}" alt="${result.title}" onerror="this.onerror=null;this.src='/static/img/no-poster.png';">
                                        <div>
                                            <h4>${result.title}</h4>
                                            <p>${result.release_date ? result.release_date.substring(0, 4) : 'N/A'} - ${result.media_type.toUpperCase()}</p>
                                        </div>
                                    `;
                                    resultElement.addEventListener('click', () => {
                                        if (result.media_type === 'movie') {
                                            window.location.href = `/movie/${result.id}`;
                                        } else if (result.media_type === 'tv') {
                                            window.location.href = `/tv_show/${result.id}`;
                                        }
                                    });
                                    searchResultsDropdown.appendChild(resultElement);
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

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('#search-input');
    const searchResults = document.querySelector('#search-results');

    if (searchInput && searchResults) {
        let debounceTimer;

        searchInput.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                const query = this.value.trim();
                if (query.length >= 2) {
                    fetch(`/ajax_search?query=${encodeURIComponent(query)}`)
                        .then(response => response.json())
                        .then(data => {
                            searchResults.innerHTML = '';
                            data.forEach(result => {
                                const resultElement = document.createElement('div');
                                resultElement.classList.add('search-result', 'p-2', 'hover:bg-gray-100');
                                resultElement.innerHTML = `
                                    <a href="/${result.media_type}/${result.id}" class="flex items-center">
                                        <img src="https://image.tmdb.org/t/p/w92${result.poster_path}" alt="${result.title}" class="w-12 h-18 object-cover mr-2">
                                        <div>
                                            <h3 class="font-semibold">${result.title}</h3>
                                            <p class="text-sm text-gray-600">${result.media_type} | ${result.release_date}</p>
                                        </div>
                                    </a>
                                `;
                                searchResults.appendChild(resultElement);
                            });
                            searchResults.classList.remove('hidden');
                        })
                        .catch(error => console.error('Error:', error));
                } else {
                    searchResults.innerHTML = '';
                    searchResults.classList.add('hidden');
                }
            }, 300);
        });

        // Hide search results when clicking outside
        document.addEventListener('click', function(event) {
            if (!searchInput.contains(event.target) && !searchResults.contains(event.target)) {
                searchResults.classList.add('hidden');
            }
        });
    }
});