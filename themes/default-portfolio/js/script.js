$('button.nav-button').click(function(){
    $(".nav-button").each(function(i ,obj) {
        obj.classList.remove("selected")
    })
    this.classList.add("selected")

    $(".main-content").each(function(i ,obj) {
        obj.classList.add("hidden")
    })
    document.getElementById(this.id + "-content").classList.remove("hidden")
});

$(document).ready(function () {
    $(".github-repo").each(function() {
        let a = $(this)
        let url = $(this).attr("href")
        if (!url.includes("github.com/"))
            return
        let api_url = url.replace("github.com", "api.github.com/repos")
        if (api_url.endsWith("/"))
            api_url = api_url.substring(0, api_url.length - 1);
        $.ajax({
            beforeSend: function(request) {
                if ($(a).attr("data-modified") !== undefined )
                    request.setRequestHeader("If-Modified-Since", $(a).attr("data-modified"))
            },
            dataType: "json",
            url: api_url,
            success: function(data, t, r) {
                let cur_text = $(a).text()
                $(a).attr("data-modified", r.getResponseHeader("Last-Modified"))
                $(a).html(cur_text + " (<i class=\"fas fa-star\"></i>" + data["stargazers_count"] + ")")
            }
        });
    });
});