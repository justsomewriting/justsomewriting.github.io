$(window).on("load", function(){

    pages=[".six", ".cinq", ".quatre", ".trois", ".deux", ".une"]; //Add more as I write more

    var cnt = 0; //Page count, could be replaced with indexOf() but I'm lazy

    hideAll();
    
    const lastPage = sessionStorage.getItem("lastPage"); //Pull last page from local storage
    if (lastPage !== null){ //If last page exists
        var lastIdx = parseInt(lastPage, 10);
        if (isNaN(lastIdx) || lastIdx < 0 || lastIdx >= pages.length) {
            lastIdx = 0;
        }
        cnt = lastIdx; //Set cnt so the pop up still works
        $(pages[0]).hide(); //Hide page 1
        $(pages[cnt]).show(); //Show last page
        $(window).scrollTop(0);
    };

    buildPager();
    updatePagerUI();

    $("#next").on("click", nextPage);
    $("#prev").on("click", prevPage);

    // position pager under .tm-main (centered relative to main content, not whole page)
    function positionPager(){
        var $main = document.querySelector('.tm-main');
        var $pager = document.querySelector('.pager-wrapper');
        var popupPrev = document.getElementById('popupPrev');
        var popupNext = document.getElementById('popupNext');

        if (!$main || !$pager) return;

        var rect = $main.getBoundingClientRect();
        // centerX relative to viewport
        var centerX = rect.left + (rect.width / 2);

        // apply to fixed elements (use px; keep translateX(-50%) so left is center)
        $pager.style.left = Math.round(centerX) + 'px';
        if (popupPrev) popupPrev.style.left = Math.round(centerX) + 'px';
        if (popupNext) popupNext.style.left = Math.round(centerX) + 'px';
    }

    // debounce helper for resize
    var _posTimer = null;
    function schedulePosition(){
        if (_posTimer) clearTimeout(_posTimer);
        _posTimer = setTimeout(function(){
            positionPager();
            _posTimer = null;
        }, 80);
    }

    // Call after building UI so sizes exist
    positionPager();
    // keep centered on resize
    window.addEventListener('resize', schedulePosition);
    // If the template has a nav toggle that changes layout, also reposition when it's clicked
    var navToggle = document.querySelector('.navbar-toggler');
    if (navToggle) navToggle.addEventListener('click', function(){ setTimeout(positionPager, 220); });

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

        // ensure position recalculated because pager width changed
        positionPager();
    }

    function updatePagerUI(){
        $("#pageNumbers .page-num").removeClass("active")
            .filter(function(){ return parseInt($(this).attr("data-idx"),10) === cnt; })
            .addClass("active");
        // when UI changes, keep pager centered
        positionPager();
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