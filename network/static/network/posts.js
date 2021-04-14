document.addEventListener("DOMContentLoaded", function(){
    // get current user id
    const current_user_id = document.querySelector('#current_user_id').innerHTML;

    document.querySelector('#front-page').addEventListener('click', () => load_view('main', current_user_id));
    document.querySelector('#following').addEventListener('click', () => load_view('following', current_user_id));
    document.querySelector('#profile').addEventListener('click', () => load_view('profile', current_user_id));

    load_view('main', current_user_id)
})

function load_view(page, current_user_id){
    document.querySelector('#posts-view').style.display = 'block';
    document.querySelector('#create-view').style.display = 'block';
    document.querySelector('#profile-view').style.display = 'none';
    // clear div for new view
    const div = document.querySelector('#posts-view');
    div.innerHTML = "";
    const profile_div = document.querySelector('#profile-view')

    if(page === "profile"){
        profile_div.style.display = 'block';
        // clear div for new view
        profile_div.innerHTML = "";
        generate_profile(current_user_id);
    } 

    fetch('posts/'+page)
    .then(res=>res.json())
    .then(posts=>{
        posts.forEach(post=>list_post(post, current_user_id));
    }).catch(err=>console.log(err))
}

function generate_profile(user_id){
    const t = document.createElement('h3');
    t.innerHTML = "My Profile";

    const fDiv = document.createElement('div');
    fDiv.id = 'f-btns-'+user_id;
    fDiv.className = 'text-right';

    const fBtn = document.createElement('button');
    fBtn.id = 'f-btn-'+user_id;
    fBtn.className = 'btn btn-primary mx-3';
    fBtn.innerHTML = 'Follow'

    fDiv.append(fBtn)

    // add each component to create a post
    t.append(fDiv)
    // add individual email to posts-view div
    document.querySelector('#profile-view').append(t)
}

function list_post(post, current_user_id){
    // create post div
    const p = document.createElement('div');
    p.id = 'post-card-'+post.id;
    p.className = 'card my-5 p-3';
    // create post body
    const b = document.createElement('p');
    b.id ='post-body-'+post.id;
    b.innerHTML = post.body;
    // create post details
    const d = document.createElement('p');
    d.id = 'post-details-'+post.id;
    d.innerHTML = `submitted by <a href="/profile/${post.user_id}">${post.user}</a> on ${post.post_date}`
    // create buttons div
    const btns = document.createElement('div');
    btns.id = 'btns-'+post.id;
    btns.className = 'text-right';
    // create edit button
    const e = document.createElement('button');
    e.id = 'edit-btn-'+post.id;
    e.className = 'btn btn-outline-primary m-1';
    e.innerHTML = 'Edit'
    // create like button
    const l = document.createElement('button');
    l.id = 'likes-btn-'+post.id;
    // fill button if the user has liked the post
    post.likes.includes(parseInt(current_user_id)) ? l.className = 'btn btn-danger m-1' : l.className = 'btn btn-outline-danger m-1';
    l.innerHTML = post.likes.length+' Likes'
    // add action to buttons
    e.addEventListener('click', () => edit_action(post))
    l.addEventListener('click', () => like_action(post, current_user_id))
    // only post creator can edit their posts
    current_user_id==post.user_id ? btns.append(e, l) :  btns.append(l);
    // add each component to create a post
    p.append(b, d, btns)
    // add individual email to posts-view div
    document.querySelector('#posts-view').append(p)
}

function edit_action(post) {
    const b = document.querySelector(`#post-body-${post.id}`);
    const edit_textarea = document.createElement('textarea');
    edit_textarea.id = 'edit-textarea-'+post.id;
    edit_textarea.value = b.innerHTML
    b.parentNode.replaceChild(edit_textarea, b)

    const btns_div = document.querySelector(`#btns-${post.id}`);
    const submit_btn = document.createElement('button');
    submit_btn.id = 'submit-btn-'+post.id;
    submit_btn.className = 'btn btn-success m-1';
    submit_btn.innerHTML = 'Submit Edit';
    btns_div.append(submit_btn)

    submit_btn.addEventListener('click', () => {
        const edited_body = document.querySelector(`#edit-textarea-${post.id}`).value;
        fetch('/edit/'+post.id, {
            method: 'PUT', 
            body: JSON.stringify({
                body: edited_body
            })
        })
        .then(()=>{
            b.innerHTML = edited_body;
            edit_textarea.parentNode.replaceChild(b, edit_textarea)
            submit_btn.remove()
        })
        .then(res=>console.log(res))
        .catch(err=>console.log(err));
    })
}

function like_action(post) {
    // select like button by id
    const l = document.querySelector(`#likes-btn-${post.id}`);
    // perform
    fetch('/likes/'+post.id, {
        method: 'PUT',
    })
    .then(res=>res.json())
    .then(data=>{
        l.innerHTML = data.likes+' Likes'
    })
    .catch(err=>console.log(err));
}
