document.addEventListener("DOMContentLoaded", function(){
    // get current user id from element
    const current_user_id = document.querySelector('#current_user_id').innerHTML;
    // get current user name from layout
    const current_username = document.querySelector('#current_username').innerHTML;
    document.querySelector('#front-page').addEventListener('click', () => load_view('main', current_user_id, current_username));
    document.querySelector('#following').addEventListener('click', () => load_view('following', current_user_id, current_username));
    document.querySelector('#my-profile').addEventListener('click', () => load_view('profile',current_user_id, current_username));
    // load main page automatically when site is loaded
    load_view('main', current_user_id, current_username)
})


function load_view(page, profile_id, profile_name){
    // clear div for new view
    const div = document.querySelector('#posts-view');
    div.innerHTML = "";
    // hide profile view by default when loading into a new view 
    document.querySelector('#posts-view').style.display = 'block';
    document.querySelector('#create-view').style.display = 'block';
    document.querySelector('#profile-view').style.display = 'none';
    // display profile section on profile view
    if(page === "profile"){
        const profile_div = document.querySelector('#profile-view')
        profile_div.style.display = 'block';
        document.querySelector('#create-view').style.display = 'none';
        // clear div for new view
        profile_div.innerHTML = "";
        generate_profile(profile_name, profile_id);
        // set api url for fetch request
        const uri = `profile/${profile_id}`;
        // fetch post for this profile
        fetch(uri)
        .then(res=>res.json())
        .then(posts=>{
            posts.forEach(post=>list_post(post, profile_id));
        }).catch(err=>console.log(err))
    } else {
        // set api url for fetch request
        const uri = 'posts/'+page
        // fetch post according to view
        fetch(uri)
        .then(res=>res.json())
        .then(posts=>{
            posts.forEach(post=>list_post(post, profile_id));
        }).catch(err=>console.log(err))
    }
}


function generate_profile(username, user_id){
    // get current user id from element
    const current_user_id = document.querySelector('#current_user_id').innerHTML;
    // create profile title
    const t = document.createElement('h3');
    t.innerHTML = username+"'s Profile";
    // create section to display follower & following numbers
    const fDiv = document.createElement('div');
    fDiv.id = 'f-div-'+user_id;
    // create follow button div
    const fBtnDiv = document.createElement('div');
    fBtnDiv.id = 'f-btns-'+user_id;
    fBtnDiv.className = 'text-right';
    // create follow button 
    const fBtn = document.createElement('button');
    fBtn.id = 'f-btn-'+user_id;
    fBtn.className = 'btn btn-primary mx-3';
    fBtn.innerHTML = 'Follow'
    // add follow method to button
    fBtn.addEventListener('click', () => follow_action(user_id))
    // add button to button div
    if(current_user_id != user_id ) fBtnDiv.append(fBtn);
    // add each component to create a post
    document.querySelector('#profile-view').append(t, fBtnDiv, fDiv)
    create_follow_number("followings", user_id)
    create_follow_number("followers", user_id)
    if(current_user_id != user_id ) follow_status(user_id);
}

function create_follow_number(f_type, user_id){
    const type_span = document.createElement('span');
    type_span.id = `${f_type}-number-${user_id}`;
    type_span.className = 'mx-2'
    type_span.innerHTML = f_type==="followings" ? "Following: " : "Followers: ";
    // get following number
    fetch(`${f_type}/${user_id}`)
    .then(res=>res.json())
    .then(data=>{
        console.log(f_type)
        const type_num = document.createElement('b');
        type_num.id = `${f_type}-count-${user_id}`;
        type_num.innerHTML = f_type==="followings" ? data.followings : data.followers;
        type_span.append(type_num) 
        document.querySelector(`#f-div-${user_id}`).append(type_span) 
    }).catch(err=>console.log(err))
}


// TO DISPLAY EACH POST WITHIN THE POSTS DIV
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
    d.innerHTML = `submitted on ${post.post_date} by `
    // create link to post creator
    const pc = document.createElement('span');
    pc.id = 'check-profile-'+post.user.id;
    pc.className = 'text-primary'
    pc.innerHTML = post.user
    // add action to profile name
    pc.addEventListener('click', () => load_view('profile', post.user_id, post.user))
    d.append(pc)
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

// TO EDIT A POST
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

    // when the submit edit button is clicked
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


// WHEN A LIKE BUTTON IS CLICKED
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


// WHEN A FOLLOW BUTTON IS CLICKED
function follow_action(user_id) {
    // select follow button by id
    const f = document.querySelector(`#f-btn-${user_id}`);
    const numElm = document.querySelector(`#followers-count-${user_id}`);
    const num = parseInt(numElm.innerHTML)
    // perform
    fetch('/follow/'+user_id, {
        method: 'PUT',
    })
    .then(res=>res.json())
    .then(data=>{
        f.innerHTML = data.msg
        numElm.innerHTML = f.innerHTML === "Follow" ? num-1 : num+1;
    })
    .catch(err=>console.log(err));
}

// Check FOLLOWING STATUS
function follow_status(user_id) {
    // select like button by id
    const f = document.querySelector(`#f-btn-${user_id}`);
    // perform
    fetch('/follow/'+user_id, {
        method: 'GET',
    })
    .then(res=>res.json())
    .then(data=>{
        f.innerHTML = data.msg
    })
    .catch(err=>console.log(err));

}