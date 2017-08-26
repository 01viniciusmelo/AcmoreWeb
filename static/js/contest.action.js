/**
 * Created by moon on 16-12-17.
 */

"use strict";

var contestId = $("#contestName").attr("data-contest-id");
var dataProblemCache ={};
var changeHash = 1;
var lastShowProblem = "A";

var loadContestStatus = function () {
    $.ajax({
        "url": statusRequestUrl,
        "data": table.query,
        cache:false,
        "success":function(data) {
            table.showData(data);
        }
    });
};
var autoLoadContestStatus = function () {
    loadContestStatus();
};
var autoLoadContestStatusCall = null;
$('#autoLoadContestStatus').on('change', function () {
    if ($(this).prop("checked")) {
        autoLoadContestStatusCall = setInterval("autoLoadContestStatus()", 1500);
    }else {
        clearInterval(autoLoadContestStatusCall);
    }
});

var loadContestRank = function () {
    $.ajax({
        "url":rankRequestUrl,
        "data":{contest:contestId},
        cache:false,
        "success":function(data) {
            rank.users = data.users;
            rank.problem_number = data.problem_number;
        }
    });
};
var autoLoadContestRank = function () {
    loadContestRank();
};
var autoLoadContestRankCall = null;
$('#autoLoadContestRank').on('change', function () {
    if ($(this).prop("checked")) {
        autoLoadContestRankCall = setInterval("autoLoadContestRank()", 3000);
    }else {
        clearInterval(autoLoadContestRankCall);
    }
});

$("input[name='onlyMyCode']").on("change", function () {
    if ($(this).is(':checked')) {
        $('#autoLoadContestStatus').bootstrapToggle('off');
        table.query.only = 1;
    }else {
        $('#autoLoadContestStatus').bootstrapToggle('on');
        table.query.only = 0;
    }
    autoLoadContestStatus();
});

var autoLoadControl = function () {
    if (window.location.hash === "#status") {
        $('#autoLoadContestStatus').bootstrapToggle('on');
        $('#autoLoadContestRank').bootstrapToggle('off');
    }else if(window.location.hash === "#rank") {
        $('#autoLoadContestRank').bootstrapToggle('on');
        $('#autoLoadContestStatus').bootstrapToggle('off');
    }else {
        $('#autoLoadContestStatus').bootstrapToggle('off');
        $('#autoLoadContestRank').bootstrapToggle('off');
    }
};

$(window).bind('hashchange', function() {
    autoLoadControl();
});
$(function() {
    autoLoadControl();
});

var timer = new Vue({
    el: '#timeProgress',
    data: {
        timestamp: $("input[name='nowTimestamp']").val(),
        startTime: $("input[name='startTimestamp']").val(),
        endTime: $("input[name='endTimestamp']").val(),
        passedTime: 0,
        remainderTime: 0,
        dateTime: 0,
        progress: 0
    },
    mounted:function() {
        this.loadData();
    },
    methods:{
        loadData: function() {
            var _this = this;

            _this.passedTime = function() {
                var secNum  = Math.round(_this.timestamp - _this.startTime);
                if (secNum < 0) {
                    return "Not Start";
                }
                return sec2time(secNum);
            }();

            _this.remainderTime = function() {
                if (_this.timestamp > _this.endTime) {
                    return "Contest Ended";
                }
                var secNum  = Math.round(_this.endTime - _this.timestamp);
                return sec2time(secNum);
            }();

            _this.progress = function(){
                if (_this.timestamp > _this.endTime) {
                    return 100;
                }else {
                    return 100*((_this.timestamp - _this.startTime) / (_this.endTime - _this.startTime));
                }
            }();


            _this.dateTime = function() {
                var date = new Date(_this.timestamp * 1000);
                return ""+date.getFullYear() +"/"+(date.getMonth()+1) + "/" + date.getDate()
                + " " + date.getHours() + ":"+ date.getMinutes() + ":" + date.getSeconds() + timezoneName;
            }();

            setTimeout(function() {
                _this.timestamp++;
                _this.loadData();
            }, 1000);
        }
    }
});

var desc = new Vue({
    el: '#problemDesc',
    data: {
        diy: "label-diy",
        problem: {},
    },
    updated: function () {
        MathJax.Hub.Queue(["Typeset",MathJax.Hub, "tex2jax"]);
    }
});
var pageOptions = {
    left: '<span class="glyphicon glyphicon-chevron-left"></span>',
    right: '<span class="glyphicon glyphicon-chevron-right"></span>',
};

var pagination = new Vue({
    el: '#pagination',
    data: {
        items:[]
    },
    methods: {
        setPage: function(now, limit, count) {
            var pageClass = [];
            var pageAction = [];

            var k = 0;
            if ((now  + 1)* limit > count) {
                for (var i = 6; i >= 0; i--) {
                    if (now - i < 0) continue;
                    pageAction[k++] = now - i;
                }
            }else {
                if (now >= 2) {
                    if((now  + 3)* limit > count){
                        for (var i = (7 - (Math.ceil(count/limit) - now)); i >= -3 && (now-i)*limit<count; i--) {
                            if (now - i < 0) continue;
                            pageAction[k++] = now - i;
                        }
                    }else {
                        for (var i = 3; i >= -5 && (now-i)*limit<count; i--) {
                            if (now - i < 0) continue;
                            pageAction[k++] = now - i;
                            if (k>6) break;
                        }
                    }

                }else {
                    for (var i = 0; i <= 6 && i*limit<count; i++) {
                        pageAction[k++] = i;
                    }
                }
            }

            var activePage = now - pageAction[0];
            pageClass[activePage]= "active";
            var activeOffset = now;

            var temp = [];

            if (activeOffset === 0) {
                temp.push(["disabled", , pageOptions.left]);
            }else {
                temp.push(["", activeOffset - 1, pageOptions.left]);
            }
            if (activeOffset > 4) {
                temp.push(["", 0, 0]);
                temp.push(["disabled", , "..."]);
            }
            for(var i = 0; i < pageAction.length; i++) {
                temp.push([pageClass[i], pageAction[i], pageAction[i]]);
            }
            pagination.items = temp;
        },
        loadContent: function(event) {
            var offset = $(event.target).attr("data-offset");
            if (offset === undefined) {
                offset = $(event.target).parent().attr("data-offset");
            }
            if (offset === undefined) {
                return false;
            }

            table.query["offset"] =offset;
            table.loadData();
        }
    }
});
var table = new Vue({
    el: '#statusBody',
    data: {
        items: [],
        query: {
            "contest": contestId,
            "only": $("input[name='onlyMyCode']").is(":checked")?1:0
        }
    },
    methods: {
        timestamp2time: timestamp2time,
        showData: function(data) {
            table.items = data.solutions;
            $("#usedTime").text(data.used_time);
            pagination.setPage(data.offset, data.limit, data.page_number);
        },
        loadData: function() {
            loadContestStatus();
        },
        loadPage: function() {
            this.loadData();
        }
    }
});

var resultRow = {
    data: function() {
        var _wa = false;
        var _class = "warning";
        var acTime = undefined;

        if (this.dataUserWaNumber !== undefined && this.dataUserWaNumber > 0) {
            _wa = true;
            _class = "danger";
        }

        if (this.dataUserAcTime !== undefined) {
            if (this.dataFirstSolved !== undefined) {
                _class = "info";
            }else {
                _class = "success";
            }
            acTime = sec2time(this.dataUserAcTime, 1);
        }

        return {
            wa: _wa,
            styleClass: _class,
            acTime:acTime
        }
    },
    template: '<td :class="styleClass">{{ acTime }}<br><span v-if="wa">(-{{ dataUserWaNumber }})</span></td>',
    props: [
        'dataUserAcTime',
        'dataUserWaNumber',
        'dataFirstSolved'
    ]
};

var rank = new Vue({
    el: "#rankBody",
    data: {
        users: [],
        problem_number: 0
    },
    components: {
        'result-row': resultRow
    },
    mounted:function() {
        this.loadData();
    },
    methods: {
        loadData: function() {
            loadContestRank();
        },
        getFormatTime: function(s) {
            return sec2time(s, 1);
        }
    }
});

var lang = new Vue({
    el: "#language",
    data: {
        selected:0,
        support_language: []
    }
});

$(function() {
    statusChange();

    window.onhashchange = function() {
        statusChange();
    };

    $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
        if (changeHash) {
            if ($(this).attr("href") === "#problem") {
                window.location.hash = "#problem/"+lastShowProblem;
            }else {
                var scrollTop = document.body.scrollTop;
                window.location.hash = $(this).attr("href");
                document.body.scrollTop = scrollTop;
            }
        }

    });
});

function statusChange() {
    if (window.location.hash) {
        if (window.location.hash.indexOf("problem") === 1) {
            changeHash = 0;
            $('a[href="#problem"]').tab('show');
            changeHash = 1;
            var problem = window.location.hash.split("/")[1];

            if (problem !== '' && problem !== undefined) {
                lastShowProblem = problem;
                showProblem(problem);
            }else {
                window.location.hash = "#problem/"+lastShowProblem;
            }
        }else {
            $('a[href="' + window.location.hash + '"]').tab('show');

            if (window.location.hash === "#status") {
                table.loadPage();
            }
        }
    }
}

function showProblem(problem_id) {
    var setTitle = function() {
        $(".problem-number").text(problem_id);
        $(".problem-submit-launcher").attr("data-num-id", problem_id);
    }();
    var changeLabel = function() {
        $(".problem-list").children().children("a").removeClass("btn-warning");
        $(".problem-list a[href='"+window.location.hash+"']").addClass("btn-warning");
    }();
    desc.problem = function() {
        if (dataProblemCache[problem_id] === undefined) {
            var result;
            $.ajax({
                url:contestOnlyProblemById,
                data: {
                    problem:problem_id,
                    contest:contestId
                },
                async:false,
                success: function(data) {
                    if (Number(data.status) === 200) {
                        dataProblemCache[problem_id] = data;
                        result = data;
                    }

                }
            });
            return result.problem;
        }else {
            return dataProblemCache[problem_id].problem;
        }
    }();
}

var $problemSelector = $("select[name='problem']");
$(".problem-submit-launcher").on("click", function () {
    var problem_id = $(this).attr("data-num-id");
    if (problem_id == "") {
        problem_id = "A";
    }
    $problemSelector.val($("select[name='problem']>option[data-num-id='"+problem_id+"']").val());
    var problemNumber = $problemSelector[0].selectedIndex;
    $("input[name='problemNumber']").val(problemNumber);

    lang.support_language = dataProblemCache[$problemSelector.val()]['problem']['l'];
    lang.selected = 0;
});
$problemSelector.on("change", function() {
    var problemNumber = $(this)[0].selectedIndex;
    $("input[name='problemNumber']").val(problemNumber);
    lang.support_language = dataProblemCache[$problemSelector.val()]['problem']['l'];
    lang.selected = 0;
});

$(".delete-contest-launcher").on("click", function () {
    $("#alertModal").modal("show");
});
$("#deleteContest").on("click", function () {
    $.ajax({
        url:deleteContestUrl,
        data:{
            contest_id:$(".delete-contest-launcher").attr("data-contest-id"),
            csrfmiddlewaretoken:$("meta[name='csrf']").attr("content"),
        },
        type:'post',
        success:function (result) {
            if (result.status == 200)
                window.location.href = result.next_page;
            else {
                alert(result.message);
            }
        }
    });
});

