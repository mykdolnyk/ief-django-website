function main() {
    const messagesWindow = document.getElementsByClassName('messages')[0];
    if (!messagesWindow) {
        // If there is no Message Window - stop the script
        return;
    };
        
    const dismissButton = messagesWindow.getElementsByClassName('button')[0];

    // The message appears smoothly on the page load
    messagesWindow.classList.remove('dismissed'); 

    // The message disappears smoothly on the button click
    dismissButton.onclick = function() {
        messagesWindow.classList.add('dismissed');
        setTimeout(() => {
            messagesWindow.style.display = 'none';
        }, 750);
    };
}

main()