

function DropDown(element){
    this.element = element;
    this.header = this.element.querySelector('header');
    this.main = this.element.querySelector('main');

    this.main.style.display = "none";

    this.element.addEventListener('click', this.toggle.bind(this));
    window.addEventListener('click', function(e){
        if(!this.element.contains(e.target)){
            this.close();
        }
    }.bind(this));
}

DropDown.prototype.toggle = function(){
    if(this.main.style.display == "none"){
        this.open();
    }
    else{
        this.close();
    }
}

DropDown.prototype.open = function(){
    this.main.style.display = "block";
}

DropDown.prototype.close = function(){
    this.main.style.display = "none";
}


window.addEventListener('load', function(){
    var dropdownItems = document.querySelectorAll(".dropdown");
    for(var item of dropdownItems){
        new DropDown(item);
    }
});
