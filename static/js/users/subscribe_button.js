const onUserPage = window.location.pathname.startsWith('/user/')

const subscriberCount = document.getElementById('subscriber-count')


function processSubscription(userURL, subscribeButton) {
    fetch(userURL)
    .then((response) => {
        return response.json();
    })
    .then((response) => {
        if (response['success'] == true) {
            updateSubscribeLabel(subscribeButton, response['action'])
        }
    })
}

function updateSubscribeLabel(subscribeButton, action) {
    if (action == 'add') {
        subscribeButton.textContent = 'Unfollow';
        if (onUserPage) {
            subscriberCount.textContent++;
        };
    }
    else if (action == 'remove') {
        subscribeButton.textContent = 'Follow!';
        if (onUserPage) {
            subscriberCount.textContent--;
        };
    }
}