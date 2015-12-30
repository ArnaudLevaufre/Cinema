"use strict";


(function(){
    function log(message){
        console.log("simplesearch.js :: error :: "+message);
    }

    function debug(message){
        console.log("simplesearch.js :: debug :: "+message);
    }

    function SearchItem(value, element){
        this.value = value;
        this.element = element;
    }

    SearchItem.prototype = {
        hide: function(){
            this.element.style.display = 'none';
        },

        show: function(){
            this.element.style.display = 'block';
        },
    };

    function SimpleSearch(input, itemSelector, valueSelector){
        this.input = document.getElementsByName(input)[0] || document.getElementById(input);
        this.items = [];
        for(var element of document.querySelectorAll(itemSelector)){
            this.items.push(new SearchItem(
                element.querySelectorAll(valueSelector)[0].innerHTML,
                element
            ));
        }

        if(!this.input){
            log("Could not find input with id " + input);
        }
        log(this.input);
        this.input.addEventListener('keyup', function(event){
            this.update();
        }.bind(this));
    }

    SimpleSearch.prototype = {
        update: function(){
            var start = new Date();
            var reg = new RegExp(this.input.value, 'i');
            for(var item of this.items){
                if(reg.test(item.value)){
                    item.show();
                }
                else{
                    item.hide();
                }
            }

            log("Update time: " + (new Date() - start) + "ms");
        },
    };

    window.SimpleSearch = SimpleSearch;
})();

