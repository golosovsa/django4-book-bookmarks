const siteUrl = '//mysite.ru:8000/';
const styleUrl = siteUrl + 'static/css/bookmarklet.css';
const minWidth = 250;
const minHeight = 250;

const head = document.getElementsByTagName('head')[0];
const link = document.createElement('link');
link.rel = 'stylesheet';
link.type = 'text/css';
link.href = styleUrl + '?r=' + Math.floor(Math.random() * 9999999999);
head.appendChild(link);

const body = document.body;
const boxHTML = `
    <div id="bookmarklet">
        <a href="#" id="close">&times;</a>
        <h1>Select an image to bookmark:</h1>
        <div class="images"></div>
    </div>    
`;
body.innerHTML += boxHTML;

function bookmarkletLaunch() {
    const bookmarklet = document.getElementById('bookmarklet');
    const imagesFound = bookmarklet.querySelector('.images');
    imagesFound.innerHTML = '';
    bookmarklet.style.display = 'block';
    bookmarklet.querySelector('#close').addEventListener('click', function () {
        bookmarklet.style.display = 'none';
    });

    const images = document.querySelectorAll(
        'img[src$=".jpg"], img[src$=".jpeg"], img[src$=".png"]'
    );
    images.forEach(image => {
        if (image.naturalWidth >= minWidth && image.naturalHeight >= minHeight) {
            const imageFound = document.createElement('img')
            imageFound.src = image.src
            imagesFound.append(imageFound)
        }
    });

    imagesFound.querySelectorAll('img').forEach(image => {
        image.addEventListener('click', event => {
            const imageSelected = event.target;
            const url = encodeURIComponent(imageSelected.src);
            const title = encodeURIComponent(document.title);
            bookmarklet.style.display = 'none';

            window.open(`${siteUrl}images/create/?url=${url}&title=${title}`, '_blank');
        });
    });
}

bookmarkletLaunch();