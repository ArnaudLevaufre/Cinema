"use strict";

(function(){


    function Movie(element){
        this.title = element.value;
        this.poster = element.dataset.poster;
        this.link = element.dataset.link;
        this.container = document.createElement('div');
        if(this.poster){
            this.img = document.createElement('img');
            this.img.src = this.poster;
        }
        else{
            this.img = document.createElement('div');
        }
        this.container.appendChild(this.img);
        this.container.appendChild(document.createTextNode(this.title));

        this.container.addEventListener('click', function(event){
            document.location.href = this.link;
        }.bind(this));
    }

    Movie.prototype = {
        show: function(){
            this.container.style.display = "block";
        },

        hide: function(){
            this.container.style.display = "none";
        },

        select: function(){
            this.container.setAttribute('class', 'selected');
        },

        deselect: function(){
            this.container.setAttribute('class', '');
        },

        isDisplayed: function(){
            return this.container.style.display == 'block';
        },
    };


    function MovieList(){
        this.container = document.createElement('div');
        this.container.id = "completion";
        this.movies = [];
        this.selected = 0;
    }

    MovieList.prototype = {
        push: function(movie){
            this.movies.push(movie);
            this.container.appendChild(movie.container);
        },

        show: function(){
            this.container.style.display = "block";
            this.selected = 0;
            this.updateSelected();
        },

        hide: function(){
            this.container.style.display = "none";
        },

        filter: function(text){
            var reg = new RegExp(text, 'i');
            for(var movie of this.movies){
                if(reg.test(movie.title)){
                    movie.show();
                }
                else{
                    movie.hide();
                }
            }
            this.selected = 0;
            this.updateSelected();
        },

        next: function(){
            var displayed = function(movie){
                return movie.isDisplayed();
            }

            var movies = this.movies.filter(displayed);

            this.selected = (this.selected + 1) % movies.length;
            this.updateSelected();
        },

        previous: function(){
            var displayed = function(movie){
                return movie.isDisplayed();
            }

            var movies = this.movies.filter(displayed);

            this.selected = (this.selected - 1) % movies.length;
            if(this.selected < 0){
                this.selected = movies.length + this.selected;
            }
            this.updateSelected();
        },

        updateSelected: function(){
            var displayed = function(movie){
                return movie.isDisplayed();
            }

            var movies = this.movies.filter(displayed);
            for(var index in movies){
                if(index == this.selected){
                    movies[index].select();
                }
                else{
                    movies[index].deselect();
                }
            }

        },

        watch: function(){
            var displayed = function(movie){
                return movie.isDisplayed();
            }

            var movies = this.movies.filter(displayed);
            document.location.href = movies[this.selected].link;
        },
    };


    function Completion(inputId){
        this.input = document.getElementById(inputId);
        this.movies = new MovieList();
        this.movies.hide();
        this.enabled = true;

        for(var item of this.input.list.getElementsByTagName('option')){
            this.movies.push(new Movie(item));
        }
        this.input.removeAttribute('list');
        this.input.parentNode.parentNode.insertBefore(this.movies.container, this.input.parentNode.nextSibling);

        this.input.addEventListener('focus', function(){
            if(!this.enabled){
                return;
            }
            this.movies.filter(this.input.value);
            this.movies.show();
        }.bind(this));

        this.input.addEventListener('blur', function(event){
            if(!this.enabled){
                return;
            }
            setTimeout(function(){
                this.movies.hide()
            }.bind(this), 250);
        }.bind(this));

        this.input.addEventListener('keyup', function(event){
            if(!this.enabled){
                return;
            }
            switch(event.key){
                case "ArrowUp":
                    this.movies.previous();
                    break;
                case "ArrowDown":
                    this.movies.next();
                    break;
                case "Enter":
                    this.movies.watch();
                default:
                    this.movies.filter(this.input.value);
                    break;
            }
        }.bind(this));
    }

    Completion.prototype = {

    };

    window.Completion = Completion;

})();
