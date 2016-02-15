"use strict";
(function(){

    function WatchlistItem(movie){
        this.movie = movie;
        this.element = document.createElement('div');
        this.element.className = 'movie';
        this.posterContainer = document.createElement('div');
        this.posterContainer.className = 'poster_container';
        this.poster = document.createElement('div');
        this.poster.className = 'poster';
        this.poster.style.backgroundImage = 'url("'+movie.poster+'")';
        this.overlay = document.createElement('div');
        this.overlay.className = 'overlay';
        this.title = document.createElement('h4');
        this.title.appendChild(document.createTextNode(movie.title));
        this.actions = document.createElement('div');
        this.actions.className = 'actions';
        this.action_play = document.createElement('a');
        this.action_play.href = movie.url;
        this.action_play.innerHTML = "<i class='fa fa-play'></i>";
        this.action_remove = document.createElement('a');
        this.action_remove.href = "#";
        this.action_remove.innerHTML = "<i class='fa fa-trash'></i>";

        this.action_remove.addEventListener('click', function(){
            watchlist.remove(movie.id);
        });


        this.element.appendChild(this.posterContainer);
        this.element.appendChild(this.overlay);

        this.posterContainer.appendChild(this.poster);

        this.overlay.appendChild(this.title);
        this.overlay.appendChild(this.actions);

        this.actions.appendChild(this.action_play);
        this.actions.appendChild(this.action_remove);
    }

    WatchlistItem.prototype = {
    };

    function Watchlist(container){
        this.element = container;
        this.element.style.display = "none";
        this.leftArrow = document.createElement('div');
        this.leftArrow.className = 'arrow left';
        this.leftArrowIcon = document.createElement('i');
        this.leftArrowIcon.className = 'fa fa-chevron-left';
        this.rightArrow = document.createElement('div');
        this.rightArrow.className = 'arrow right';
        this.rightArrowIcon = document.createElement('i');
        this.rightArrowIcon.className = 'fa fa-chevron-right';
        this.container = document.createElement('div');

        this.element.appendChild(this.leftArrow);
        this.element.appendChild(this.container);
        this.element.appendChild(this.rightArrow);

        this.leftArrow.appendChild(this.leftArrowIcon);
        this.rightArrow.appendChild(this.rightArrowIcon);

        this.items = [];
        this.fetch();

        this.scroll = 0;

        this.rightArrow.addEventListener('click', function(){
            if(this.scroll  > -this.items.length * 200 + this.container.offsetWidth){
                this.scroll -= 200;
                this.container.style.marginLeft = this.scroll + 'px';
                this.rightArrow.style.marginLeft = -this.scroll + 'px';
            }
        }.bind(this));

        this.leftArrow.addEventListener('click', function(){
            if(this.scroll < 0){
                this.scroll += 200;
                this.container.style.marginLeft = this.scroll + 'px';
                this.rightArrow.style.marginLeft = -this.scroll + 'px';
            }
        }.bind(this));

    }

    Watchlist.prototype = {
        toggle: function(){
            if(this.element.style.display == "none"){
                this.element.style.display = "flex";
            }
            else{
                this.element.style.display = "none";
            }
        },
        add: function(id){
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/watchlist/add');
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.setRequestHeader('X-CSRFToken', csrftoken());
            xhr.send(JSON.stringify({
                movie: id,
            }));

            xhr.onreadystatechange = function(){
                if(xhr.readyState == xhr.DONE){
                    var data = JSON.parse(xhr.responseText);
                    if(data['error'] != undefined){
                        return;
                    }
                    var movie = data['movie'];
                    var item = new WatchlistItem(movie);
                    this.container.appendChild(item.element);
                    this.items.push(item);
                }
            }.bind(this);
        },

        remove: function(id){
            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/watchlist/remove');
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.setRequestHeader('X-CSRFToken', csrftoken());
            xhr.send(JSON.stringify({
                movie: id,
            }));

            for(var index in this.items){
                var item = this.items[index];
                if(item.movie.id == id){
                    this.container.removeChild(item.element);
                    this.items.splice(index, 1);
                }
            }
        },

        fetch: function(){
            var xhr = new XMLHttpRequest();
            xhr.open('GET', '/watchlist/list');
            xhr.setRequestHeader('Accept', 'application/json');
            xhr.onreadystatechange = function(){
                if(xhr.readyState == xhr.DONE){
                    for(var movie of JSON.parse(xhr.responseText)['movies']){
                        var item = new WatchlistItem(movie);
                        this.container.appendChild(item.element);
                        this.items.push(item);
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

