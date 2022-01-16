$('button#projects-btn').click(function(){
    document.getElementById("cv-btn").classList.remove("selected")
    this.classList.add("selected")

    document.getElementById("cv-content").classList.add("hidden")
    document.getElementById("projects-content").classList.remove("hidden")
});

$('button#cv-btn').click(function(){
    document.getElementById("projects-btn").classList.remove("selected")
    this.classList.add("selected")

    document.getElementById("projects-content").classList.add("hidden")
    document.getElementById("cv-content").classList.remove("hidden")
});