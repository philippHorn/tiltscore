$(document).ready(function(){
    var progress = 0;
    var get_progress = setInterval(function(){
        $.getJSON(progress_url, function (response, status, xhr) {
            progress = response.progress;
            $("#percentage").text(progress + "%");
            if (progress === 100){
                clearInterval(get_progress);
                window.location.href = result_url
            }
        });
    }, 1000);
});