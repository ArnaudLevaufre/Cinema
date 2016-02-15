"use strict";

function csrftoken(){
    for(var cookie of document.cookie.split(';')){
        if(cookie.split('=')[0] == 'csrftoken'){
            return cookie.split('=')[1];
        }
    }
}
