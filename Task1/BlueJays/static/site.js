function loadPage() {
    activeDiv = '<div class="active"></div>';
    currentPath = window.location.pathname;

    if (currentPath.includes('leaderboards')) {
        document.getElementById('leaderboards').innerHTML += activeDiv;
    }
    else {
        document.getElementById('teams').innerHTML += activeDiv
    }

    var tableBodies = document.querySelectorAll("tbody");
    for (var i = 0; i < tableBodies.length; i++) {
        tableBodies[i].style.removeProperty("--bs-table-color");
    }

    var header = document.querySelectorAll(".tableHeader");
    for (var i = 0; i < header.length; i++) {
        header[i].style.setProperty("--bs-table-bg", "#3E9FCA");
        header[i].style.setProperty("--bs-table-color", "#FFFFFF");
    }

    count = 0
    var standings = document.querySelectorAll(".standingsRow");
    for (var i = 1; i < standings.length; i += 2) {
        standings[i].style.setProperty("--bs-table-bg", "#F7F7F7");
        count++;
        if (count % 2 == 0) {
            i++;
        }
    }

    var years = document.querySelectorAll(".yearRow")
    for (var i = 1; i < years.length; i += 2) {
        years[i].style.setProperty("--bs-table-bg", "#F7F7F7");
    }

    var pitchers = document.querySelectorAll(".pitcherRow")
    for (var i = 1; i < pitchers.length; i += 2) {
        pitchers[i].style.setProperty("--bs-table-bg", "#F7F7F7");
    }

    var hitters = document.querySelectorAll(".hitterRow")
    for (var i = 1; i < hitters.length; i += 2) {
        hitters[i].style.setProperty("--bs-table-bg", "#F7F7F7");
    }

    var hitYears = document.querySelectorAll(".hittingYears")
    for (var i = 1; i < hitYears.length; i += 2) {
        hitYears[i].style.setProperty("--bs-table-bg", "#F7F7F7");
    }

    var pitchYears = document.querySelectorAll(".pitchingYears")
    for (var i = 1; i < pitchYears.length; i += 2) {
        pitchYears[i].style.setProperty("--bs-table-bg", "#F7F7F7");
    }

    var leaderRows = document.querySelectorAll(".leaderRow")
    for (var i = 1; i < leaderRows.length; i += 3) {
        leaderRows[i].style.setProperty("--bs-table-bg", "#F7F7F7");
    }
}

function switchTable(checkbox) {

    if (checkbox.checked) {
        document.getElementById("hitter").style.display = "none";
        document.getElementById("pitcher").style.display = "block";
    }
    else {
        document.getElementById("hitter").style.display = "block";
        document.getElementById("pitcher").style.display = "none";
    }
}