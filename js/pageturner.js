$(window).on("load", function(){

    pages=[".six", ".cinq", ".quatre", ".trois", ".deux", ".une"]; //Add more as I write more

    var cnt = 0; //Page count, could be replaced with indexOf() but I'm lazy

    hideAll();
    
    const lastPage = sessionStorage.getItem("lastPage"); //Pull last page from local storage
    if (lastPage){ //If last page exists
        cnt = lastPage; //Set cnt so the pop up still works
        $(pages[0]).hide(); //Hide page 1
        $(pages[lastPage]).show(); //Show last page
        $(window).scrollTop(0);
    };

    buildPager();
    updatePagerUI();

    $("#next").on("click", nextPage);
    $("#prev").on("click", prevPage);

    function hideAll(){ //Hide all pages and pop ups except P1
        for (var i = 1; i < pages.length; i++){
            $(pages[i]).hide();
        }
        $("#popupNext").hide();
        $("#popupPrev").hide();
    };

    function buildPager(){
        var $p = $("#pageNumbers");
        $p.empty();
        for (var i = 0; i < pages.length; i++){
            var $el = $("<span>")
                .addClass("page-num")
                .attr("data-idx", i)
                .text(i+1);
            if (i === cnt) $el.addClass("active");
            $p.append($el);
        }
        // click handler
        $p.on("click", ".page-num", function(){
            var idx = parseInt($(this).attr("data-idx"), 10);
            goToPage(idx);
        });
    }

    function updatePagerUI(){
        $("#pageNumbers .page-num").removeClass("active")
            .filter(function(){ return parseInt($(this).attr("data-idx"),10) === cnt; })
            .addClass("active");
    }

    function goToPage(target){ //navigate directly to a given page index
        if (target === cnt) return;
        if (target < 0 || target >= pages.length) return;
        $(pages[cnt]).fadeOut("fast", function(){
            cnt = target;
            $(pages[cnt]).fadeIn("fast");
            $(window).scrollTop(0);
            sessionStorage.setItem("lastPage", cnt);
            updatePagerUI();
        });
    }

    function nextPage(){ //Turn to next page
        if (cnt < (pages.length-1)){ //If not on last page
            $(pages[cnt]).fadeOut("fast");
            cnt++;
            $(pages[cnt]).fadeIn("fast");
            $(window).scrollTop(0);
            sessionStorage.setItem("lastPage", cnt);
            updatePagerUI();
            //console.log("Updated last page");
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
            updatePagerUI();
            //console.log("Updated last page");
        }
        else { //Show pop up
            $("#popupPrev").fadeIn("fast")
            setTimeout(() => {$("#popupPrev").fadeOut("fast")}, 1000);
        };
    };

});
