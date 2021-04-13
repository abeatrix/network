document.addEventListener("DOMContentLoaded", function(){

    // toggle views with buttons
    document.querySelector("#index").addEventListener("click", () => load_view("index"));
    document.querySelector("#following").addEventListener("click", () => load_view("following"));
    document.querySelector("#profile").addEventListener("click", () => load_view("profile"));

    load_view('index')
});

function load_view(page){
    document.querySelector('#posts-view').style.display = 'block';
    document.querySelector('#create-view').style.display = 'block';
    document.querySelector('#profile-view').style.display = 'none';

    fetch('/'+page)
}


function list_posts(post)