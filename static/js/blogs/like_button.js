const likeCountLabel = document.getElementById('like-count');

function processLike(likeButton) {
    fetch('like/')
    .then((response) => {
        return response.json();
    })
    .then((response) => {
        if (response['success'] == true) {
            updateLikeCount(response['action'])
        }
    })
}

function updateLikeCount(action) {
    if (action == 'add') {
        likeCountLabel.textContent++;
    }
    else if (action == 'remove') {
        likeCountLabel.textContent--;
    }
}
