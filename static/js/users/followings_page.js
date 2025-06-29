// HTML Elements
const displayCurrentlyText = document.getElementById('currently-displaying');

const followersButton = document.getElementById('followers-button');
const followingButton = document.getElementById('following-button');

const followersSection = document.getElementById('followers-section');
const followingSection = document.getElementById('following-section');

// Class Names
const hiddenElementClassName = 'display-none';
const chosenButtonClassName = 'chosen';


// On Click
followersButton.onclick = function() {
    followingSection.classList.add(hiddenElementClassName);
    followersSection.classList.remove(hiddenElementClassName);

    displayCurrentlyText.innerHTML = 'Followers';

    followingButton.classList.remove(chosenButtonClassName)
    followersButton.classList.add(chosenButtonClassName)
};

followingButton.onclick = function() {
    followersSection.classList.add(hiddenElementClassName);
    followingSection.classList.remove(hiddenElementClassName);

    displayCurrentlyText.innerHTML = 'Following';

    followersButton.classList.remove(chosenButtonClassName)
    followingButton.classList.add(chosenButtonClassName)
};