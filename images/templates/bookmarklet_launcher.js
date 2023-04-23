(function (){
    if (!window.bookmarklet) {
        const bookmarklet_js = document.createElement('script');
        document.body.appendChild(bookmarklet_js);
        bookmarklet_js.src = '//mysite.ru:8000/static/js/bookmarklet.js?r='+Math.floor(Math.random()*99999999999999);
        window.bookmarklet = true;
    } else {
        bookmarkletLaunch();
    }
})();