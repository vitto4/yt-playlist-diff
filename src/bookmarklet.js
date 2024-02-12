javascript: 

/* --------------------------------- ARCHIVE -------------------------------- */

/// Do not take into account the playlist owner's channel name and playlist title. This offset is used on `channels` elements, but not on `videos`, since these already get detected accurately.
/// If we don't do this, `channels` and `videos` are out of phase, and we'll get the channel name wrong for every video.
function getOffset() {
    var channels = document.getElementsByClassName("yt-simple-endpoint style-scope yt-formatted-string");           // HTML class used by youtube to render channel names under video titles.
    var videos = document.getElementsByClassName("yt-simple-endpoint style-scope ytd-playlist-video-renderer");     // HTML used to render video titles. It also contains the `href` link to the video.
    var offset = 0; // initial offset of 0
    // console.log("[OFFSET] Entered the function.")
    // console.log('[OFFSET] There are ' + channels.length + ' channels')
    // console.log("[OFFSET] There are " + videos.length + " videos")


    // We want to go over every elements in `videos`, and update the offset for every invalid element detected.
    for (var i = 0; i < videos.length; i++) {
        // If the outer html is contains the following string, the element is valid. The offset remains the same.
        if ((i < channels.length) && (channels[i].parentNode.outerHTML.toString().includes("style-scope ytd-channel-name complex-string"))) {
            // console.log("[OFFSET] Valid element : " + channels[i].innerHTML.trim())
        } else if (i >= channels.length) {   // If `i` is more than the total amount of channels (could happen because private/deleted videos have a title, but no associated channel), ignore.
            // console.log("[OFFSET] Overflow")
        }  else { // Else, this is an invalid channel, add one to the offset.
            // console.log("[OFFSET] Invalid element : " + channels[i].innerHTML.trim())
            offset += 1;
        }
        // console.log('[OFFSET] Offset is now : ' + offset + ". i = " + i)
    } 
    return offset;
}


/// Creating the csv inside a string
function getTitlesCsv() {
    var videos = document.getElementsByClassName("yt-simple-endpoint style-scope ytd-playlist-video-renderer");     // HTML class used by youtube to render channel names under video titles.
    var channels = document.getElementsByClassName("yt-simple-endpoint style-scope yt-formatted-string");           // HTML used to render video titles. It also contains the `href` link to the video.
    var offset = getOffset();                                                                                       // Get the offset.
    var result = "";
    // console.log("[CSV] Entered the function.")
    // console.log('[CSV] There are ' + channels.length + ' channels')
    // console.log("[CSV] There are " + videos.length + " videos")
    // console.log('[CSV] Offset is : ' + offset)
     
    // Generating the csv file, by iterating through each video, taking the offset into account.
    for (var i = 0; i < videos.length; i++) {

        // Extracting the metadata
        let url = new URL(videos[i].href);
        let params = new URLSearchParams(url.search);
        let index = params.get("index");
        let id = params.get("v");

        // Logic to detect the youtube thumbnail corresponding to an unavailable video. If it matches, we know the video is no longer available
        // The way unavailable videos are displayed seems to change from time to time ; hence this section may need to be updated in the future.
        // console.log("[CSV] Evaluating " + videos[i])
 
        if (videos[i].parentNode.parentNode.childNodes[3].childNodes[3].childNodes[1].hidden == true) {
            // console.log("[CSV] Unavailable video found : " + videos[i].innerHTML.trim())
            result += index + ", " + id + ", True, \"Unknown channel\", \"Unknown link\", \"" + videos[i].innerHTML.trim() + "\"\n";
            // An unavailable video doesn't have any associated channel. we need to adjust the offset accordingly, or channel names will be lagging behind `videos`.
            offset -= 1
            // console.log('[CSV] Success ; new offset : ' + offset)
        }

        // If : added recently, checks whether the video is in the « Recommended videos » section at the end of the playlist. If yes, do not include it in the csv.
        else if (videos[i].parentNode.parentNode.parentNode.parentNode.parentNode.styleType != "playlist-video-renderer-style-recommended-video") {
            // `href` contains the link, `innerHTML` the actual title.
            result += index + ", " + id + ", False, \"" + channels[i+offset].innerHTML.trim() + "\", \"" + channels[i+offset].href + "\", \"" + videos[i].innerHTML.trim() + "\"\n";
            // console.log('[CSV] Success ; available video : ' + videos[i].innerHTML.trim() + ' from ' + channels[i+offset].innerHTML.trim() +' saved !')
        }
        // console.log('[CSV] i = ' + i)
    } 
     
    return result; 
} 

/// I stole this function from someone, see readme.
/// Saves everything in a text file.
function saveTextToFile(textToWrite, fileName) {
    var textFileAsBlob = new Blob([textToWrite], {type:'text/plain'}); 
    var fileNameToSaveAs = fileName; 
    var downloadLink = document.createElement("a"); 
    downloadLink.download = fileNameToSaveAs; 
    downloadLink.innerHTML = "My Hidden Link"; 
    window.URL = window.URL || window.webkitURL; 
    downloadLink.href = window.URL.createObjectURL(textFileAsBlob); 
    downloadLink.onclick = destroyClickedElement; 
    downloadLink.style.display = "none"; 
    document.body.appendChild(downloadLink); 
    downloadLink.click(); 
} 

/// I don't even know what that is
function destroyClickedElement(event) {
    document.body.removeChild(event.target); 
} 

/// Gathers metadata about the playlist itself, returns a string that'll be used
/// as a header in the csv export.
function metadata() {
    // Finding the youtube `list` ID for this playlist
    let url = new URL(location.href.toString());
    let params = new URLSearchParams(url.search);
    let playlist = params.get("list");
    // Get the archive date as well
    var today = Date.now();
    var out = "Playlist ID : " + playlist + "\n" + "Archived on : " + today.toString() + "\n";
    return out;
}

/// Returns the file name to be used for the exported file.
/// Contains the display name of the playlist, and the date at which
/// the archive was made. Format : YYYY-MM-DD
function fileName() {
    playlistTitle = document.getElementsByClassName("style-scope yt-dynamic-sizing-formatted-string")[1].innerHTML.trim();
    currentDate =  new Date().toLocaleDateString("en-CA");
    return playlistTitle + " - " + currentDate;
}


/* ------------------------------ SCROLL LOGIC ------------------------------ */

/// Start the observer, will trigger when new videos are loaded.
function startObserving(observer) {
    // Observe changes within the specific container
    const playlistContainer = document.querySelector('ytd-section-list-renderer[page-subtype="playlist"]');
    if (playlistContainer) {
        observer.observe(playlistContainer, { childList: true, subtree: true });
    }
}

/// Find the currently loaded last video (bottom of the page).
function getLastVideo() {
    var videos = document.getElementsByClassName("yt-simple-endpoint style-scope ytd-playlist-video-renderer");
    var lastValid = videos[videos.length -1];
    let done = false;
    for (let i = 0; i < videos.length; i++) {
        if (videos[i].parentNode.parentNode.parentNode.parentNode.parentNode.styleType == "playlist-video-renderer-style-recommended-video" && !done) {
            lastValid = videos[i-1];
            done = true;
        }
    }
    return lastValid;
}

/// Scroll to the last video (bottom of the page, just before recommended videos)
function scrollToLastVideo() {
    getLastVideo().scrollIntoView({ behavior: "smooth" });
}

/// Combines previous functions, constantly scrolls to the bottom of the page, will stop
/// if no new video appears for 8 seconds, and then trigger the archive mechanism.
function startScroll() {
    let oldHeight = document.documentElement.scrollHeight;
    let observerTimeout;


    // OBSERVER
    const observer = new MutationObserver(mutations => {
        var now = Date.now();
        
        for (const mutation of mutations) {
            if (mutation.type === 'childList') {
                // New content added
                const newScrollHeight = document.documentElement.scrollHeight;
                // console.log("[SCROLL] New scroll height: ${newScrollHeight}px, old : ${oldHeight}");
                if (oldHeight != newScrollHeight) {
                    clearTimeout(observerTimeout);
                    scrollToLastVideo();
                    oldHeight = newScrollHeight;
    
                    // FIXME This is not really elegant, if for some reason videos take more than 
                    // x seconds to load, it'll stop anyway.
                    // Set a new timeout to disconnect after 8 seconds
                    observerTimeout = setTimeout(() => {
                        observer.disconnect();
                        // console.log("[SCROLL] Observer disconnected due to inactivity.");

                        mainArchiveLogic();
                    }, 8000);
                }
            }
        } // END OBSERVER
    });

    // Start observing for new videos
    startObserving(observer);
    // Scroll to the end of the playlist, will trigger video loading
    scrollToLastVideo();
}



/* ------------------------------- MAIN LOGIC ------------------------------- */

function mainArchiveLogic() {
    var titles = "";

    // Run the whole code.
    titles += metadata() + "index, id, title, artist, artistUrl, isUnavailable\n" + getTitlesCsv();
    fName = fileName();
    fName += ".csv"
    // If export was successful, save the file.
    if (titles != undefined || titles != "") { 
        saveTextToFile(titles, fName);
    }
}


function main() {
    // Prompts user. Gives the option to enable autoscroll.
    if (window.confirm("Your playlist is going to be exported to a CSV file.\nMake sure you've followed the instructions over at https://github.com/vitto4/yt-playlist-bookmarklet\n\nClick « Ok » to enable auto-scrolling to the end of the playlist, click « Cancel » otherwise.")) {
        startScroll();
    } else {
        mainArchiveLogic();
    }
}

main();
void(0);