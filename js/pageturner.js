$(window).on("load", function(){

    pages=[".trois", ".deux", ".une"]; //Add more as I write more

    var cnt = 0; //Page count, could be replaced with indexOf() but I'm lazy

    hideAll();
    
    const lastPage = sessionStorage.getItem("lastPage"); //Pull last page from local storage
    if (lastPage){ //If last page exists
        cnt = lastPage; //Set cnt so the pop up still works
        $(pages[0]).hide(); //Hide page 1
        $(pages[lastPage]).show(); //Show last page
        $(window).scrollTop(0);
    };

    $("#next").on("click", nextPage);
    $("#prev").on("click", prevPage);

    function hideAll(){ //Hide all pages and pop ups except P1
        for (var i = 1; i < pages.length; i++){
            $(pages[i]).hide();
        }
        $("#popupNext").hide();
        $("#popupPrev").hide();
    };

    function nextPage(){ //Turn to next page
        if (cnt < (pages.length-1)){ //If not on last page
            $(pages[cnt]).fadeOut("fast");
            cnt++;
            $(pages[cnt]).fadeIn("fast");
            $(window).scrollTop(0);
            sessionStorage.setItem("lastPage", cnt);
            console.log("Updated last page");
        }
        else { //Show pop up
            $("#popupNext").fadeIn("fast")
            setTimeout(() => {$("#popupNext").fadeOut("fast")}, 1000);
        };
    };

    function prevPage(){//Turn to previous page
        if (cnt > 0){ //If not on first page
            $(pages[cnt]).fadeOut("fast");
            cnt--;
            $(pages[cnt]).fadeIn("fast");
            $(window).scrollTop(0);
            sessionStorage.setItem("lastPage", cnt);
            console.log("Updated last page");
        }
        else { //Show pop up
            $("#popupPrev").fadeIn("fast")
            setTimeout(() => {$("#popupPrev").fadeOut("fast")}, 1000);
        };
    };

});
