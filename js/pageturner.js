$(window).on("load", function(){

    pages=[".deux", ".une"]; //Add more as I write more

    var cnt = 0; //Page count

    hideAll();
    $("#next").on("click", nextPage);
    $("#prev").on("click", prevPage);

    function hideAll(){ //Hide all pages except P1
        for (var i = 1; i < pages.length; i++){
            $(pages[i]).hide();
        };
    };

    function nextPage(){ //Turn to next page
        if (cnt < (pages.length-1)){ //If not on last page
            $(pages[cnt]).fadeOut("fast");
            cnt++;
            $(pages[cnt]).fadeIn("fast");
            $(window).scrollTop(0);
        }
        else {
            window.alert("You're already on the last page.");
        };
    };

    function prevPage(){//Turn to previous page
        if (cnt > 0){ //If not on last page
            $(pages[cnt]).fadeOut("fast");
            cnt--;
            $(pages[cnt]).fadeIn("fast");
            $(window).scrollTop(0);
        }
        else {
            window.alert("You're already on the first page.");
        };
    };


});
