/**
 * assist notransition and transition. after the page is load
 * remove the class notransition so we can get the transitions back*/

$(document).ready(function(){
    $('body').removeClass('notransition');
});
