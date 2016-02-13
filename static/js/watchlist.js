"use strict";
(function(){


    function WatchlistItem(movie){
    }

    WatchlistItem.prototype = {
    };

    function Watchlist(container){
    }

    Watchlist.prototype = {
        add: function(id){
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/watchlist/add');
            xhr.setRequestHeader('Content-Type', 'application/json');
            var csrftoken = null;
            for(var cookie of document.cookie.split(';')){
                if(cookie.split('=')[0] == 'csrftoken'){
                    csrftoken = cookie.split('=')[1];
                }
            }
            xhr.setRequestHeader('X-CSRFToken', csrftoken);
            xhr.send(JSON.stringify({
                movie: id,
            }));
        },

        remove: function(id){
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/watchlist/remove');
            xhr.setRequestHeader('Content-Type', 'application/json');
            var csrftoken = null;
            for(var cookie of document.cookie.split(';')){
                if(cookie.split('=')[0] == 'csrftoken'){
                    csrftoken = cookie.split('=')[1];
                }
            }
            xhr.setRequestHeader('X-CSRFToken', csrftoken);
            xhr.send(JSON.stringify({
                id: id,
            }));
        },

        fetch: function(){
            var xhr = new XMLHttpRequest();
            xhr.open('GET', '/watchlist/list');
            xhr.setRequestHeader('Accept', 'application/json');
            xhr.onreadystatechange = function(){
                if(xhr.readyState == xhr.DONE){
                    for(var item of JSON.parse(xhr.responseText)){
                    }
                }
            }.bind(this);
            xhr.send();
        },
    };


    window.addEventListener('load', function(){
        window.watchlist = new Watchlist(document.getElementById('watchlist'));
    });
})();

