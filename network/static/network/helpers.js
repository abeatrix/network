document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('#edit-btn').addEventListener('click', () => load_mailbox('inbox'));
    document.querySelector('#like-btn').addEventListener('click', () => load_mailbox('sent'));
})