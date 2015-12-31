/*
 * Copyright (c) 2015 Arnaud Levaufre <arnaud@levaufre.name>
 *
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */



/*
 * Retractable.js
 * ==============
 *
 * Simple piece of code that handle saved state retractable element.
 *
 * User can retract and expand allowed element at will and the state will be
 * stored clientside using the webstorage html5 api.
 *
 * Documentation
 * -------------
 *
 *  It's quite simple, you can allow user to retract a given element like so:
 *
 *  new Retractable(elementId, triggerId);
 *
 *  where elementId is the id of the html element you want to be able to
 *  retract or expand and triggerId is the id of the element which will trigger
 *  the retractation/expantion
 *
 * Advanced arguments
 * ------------------
 *
 *  You can pass an objects with the following attributes:
 *  {
 *      retractedClass: 'retracted',
 *      expandedClass: '',
 *      icon: {
 *          id: 'myiconeid',
 *          retracted: {
 *              class: 'fa fa-chevron-left',
 *              text: '<',
 *          },
 *          expanded: {
 *              class: 'fa fa-chevron-right',
 *              text: '>',
 *          },
 *      },
 *  }
 */


"use strict";

(function(){
    function log(message){
        console.log("retract.js :: error :: "+message);
    }

    function debug(message){
        console.log("retract.js :: debug :: "+message);
    }

    function Icon(options){
        this.options = options;
        this.icon = document.getElementById(options.id);
        if(!this.icon){
            log("Could not find element with id "+options.id);
        }
    }

    Icon.prototype = {
        expand: function(){
            if(this.options.expanded.class !== undefined){
                this.icon.setAttribute('class', this.options.expanded.class);
            }
            if(this.options.expanded.text !== undefined){
                this.icon.innerHTML = this.options.expanded.text;
            }
        },

        retract: function(){
            if(this.options.retracted.class !== undefined){
                this.icon.setAttribute('class', this.options.retracted.class);
            }
            if(this.options.retracted.text !== undefined){
                this.icon.innerHTML = this.options.retracted.text;
            }
        },
    };


    function Retractable(retractableId, triggerId, options){
        this.containerId = retractableId;
        this.options = Object.create({
            retractedClass: 'retracted',
            expandedClass: '',
        }, options);
        this.container = document.getElementById(retractableId);
        this.trigger = document.getElementById(triggerId);
        if(options.icon !== undefined){
            this.icon = new Icon(options.icon);
        }

        if(!this.container){
            log("Could not find element with id " + retractableId);
        }
        if(!this.trigger){
            log("Could not find element with id " + triggerId);
        }

        this.loadState();
        this.trigger.addEventListener('click', this.toggle.bind(this));
    }

    Retractable.prototype = {
        retract: function(){
            this.container.setAttribute('class', this.options.retractedClass);
            this.saveState(true);
            if(this.icon){
                this.icon.retract();
            }
        },

        expand: function(){
            this.container.setAttribute('class', this.options.expandedClass);
            this.saveState(false);
            if(this.icon){
                this.icon.expand();
            }
        },

        toggle: function(){
            if(this.container.getAttribute('class') == 'retracted'){
                this.expand();
            }
            else{
                this.retract();
            }
        },

        saveState: function(retracted){
            localStorage.setItem(this.containerId + '_retracted', retracted);
        },

        loadState: function(){
            if(localStorage.getItem(this.containerId + '_retracted') === "true"){
                this.retract();
            }
        },
    };

    window.Retractable = Retractable;
})();
