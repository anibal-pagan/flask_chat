document.addEventListener('DOMContentLoaded', load);

// Connect to websocket
var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

document.addEventListener('click', event => {
    const element = event.target;
    let el = element.parentElement.parentElement.parentElement;
    if (element.className === 'delete') {
        let index = el.id;
        socket.emit('delete message', index);
    }
});

socket.on('connect', () => {

    document.querySelectorAll('button').forEach(button => {
        if(button.classList.contains('send')) {
            button.onclick = () => {
                const message = document.getElementById('message-text').value;
                const username = document.getElementById('username').innerHTML;
                if(message != "") {
                    socket.emit('send message', {'message': message, 'username': username});
                }
                document.getElementById('message-text').value = "";
            };
        }
    });
});

socket.on('messages', data => {
    const name = document.getElementById('name').innerHTML;
    const user = document.getElementById('username').innerHTML;
    //name = name of chat
    add_message(data['chats'][name][data['chats'][name].length - 1], user, data['chats'][name].length - 1)
});

socket.on('deleted', data => {
    let el = document.getElementById(data);
    el.style.animationPlayState = 'running';
    el.addEventListener('animationend', () =>  {
        el.remove();
    });
});

Handlebars.registerHelper('ifCond', function(v1, v2, options) {
    if(v1 === v2) {
      return options.fn(this);
    }
    return options.inverse(this);
});

// Load next set of messages.
function load() {

    // Open new request to get new posts.
    const request = new XMLHttpRequest();
    request.open('POST', '/messages');
    const name = document.getElementById('name').innerHTML;
    const user = document.getElementById('username').innerHTML;
    request.onload = () => {
        const data = JSON.parse(request.responseText);

        for (let i = 0; i < data[name].length; i++) {
            add_message(data[name][i], user, i);
        }
    };

    const data = new FormData();
    data.append('name', name);
    data.append('username', user);

    // Send request.
    request.send(data);
};

// Add a new post with given contents to DOM.
const post_template = Handlebars.compile(document.querySelector('#message').innerHTML);
function add_message(contents, user, index) {
    // Create new message.
    const message = post_template({'contents': contents, 'user': user, 'index': index});

    // Add message to DOM.
    document.querySelector('#messages').innerHTML += message;
    window.scrollTo(0,document.body.scrollHeight);
}
