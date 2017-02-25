/**
* Created by moon on 17-1-5.
*/
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

            var activePage = table.table[table.type].offset - pageAction[0];
            pageClass[activePage]= "active";
            var activeOffset = table.table[table.type].offset;

            var temp = [];

            if (activeOffset == 0) {
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
        loadContent: function() {
            var offset = $(event.target).attr("data-offset");

            table.isRepeat = offset == "0";

            if (offset == undefined) {
                offset = $(event.target).parent().attr("data-offset");
            }
            if (offset == undefined) {
                return false;
            }

            table.query["offset"] =offset;
            table.changeStatus(table.type);
            table.loadData(0);
        }
    }
});
var table = new Vue({
    el: '#tbody',
    data: {
        items: [],
        query: {
            "content":"json",
            "problem":problem_id,
        },
        type: 0,//1 record, 2 rank
        table: [],
        loadingImg: rootUrl+loadingImg,
        isRepeat: false,
        isRepeating: 1,
        freshTime: 1000
    },
    methods:{
        datetime: function(t) {
            return timestamp2time(t);
        },
        loadData: function(cache) {
            var showData = function(data) {
                table.items = data.solutions;
                $("#usedTime").text(data.used_time);
                pagination.setPage(data.offset, data.limit, data.page_number);
            };

            if (cache && (table.table[table.type] != undefined)) {
                showData(table.table[table.type]);
            }else {
                var haveNoJudge = false;
                $.ajax({
                    "url": problemStatusUrl,
                    "data":table.query,
                    cache:false,
                    "success":function(data) {
                        $.each(data.solutions, function(index, item) {
                            item.language = languageName[item.language];
                            var result = item.result;
                            if (item.result < 4) {
                                haveNoJudge = true;
                            }
                            item.result = result;
                            item.resultText = judgeResult[result];
                            item.resultType = judgeResultType[result];
                        });
                        if (haveNoJudge) {
                            table.freshTime = 1000;
                        }else {
                            table.freshTime = 4500;
                            table.isRepeat = false;
    table.stopRepeat();
    $('#autoLoadStatus').bootstrapToggle('off');
                        }
                        table.stopRepeat();
                        table.isRepeating = table.repeat();
                        table.table[table.type] = data;
                        showData(data);
                    }
                });
            }
        },
        loadPage: function(type) {
            delete table.query.offset;
            table.changeStatus(type);
            table.loadData(1);

        },
        changeStatus: function(type) {
            if (type == 1) {
                table.type = 1;
                delete table.query.result;
                delete table.query.order;
            }else if (type == 2) {
                table.type = 2;
                table.query["order"] =  "time";
                table.query["result"] =  4;
            }
        },
        repeat: function() {
            return setInterval(function () {
                var buttonCheck = $('#autoLoadStatus').prop('checked');
                if (!table.isRepeat) {
                    if (buttonCheck) {
                        $('#autoLoadStatus').bootstrapToggle('off');
                    }
                    table.isRepeating = 0;
                    return false;
                }

                table.loadData(0);
            },table.freshTime);
        },
        stopRepeat: function() {
            clearInterval(table.isRepeating);
        }
    }
});

$(function() {
    $('#autoLoadStatus').bootstrapToggle('off');
    var hash = window.location.hash.split("#")[1];

    if (hash == "") {

    }else if(hash == "desc") {

    }else if(hash == "submit"){
        changToSubmit();
    }else if(hash == "submissions"){
        changToSubmissions();
    }else if(hash == "rank") {
        changeToRank();
    }

    $("select[name='language']").on("change", function() {
        localStorage.setItem("submit-language", $(this).val());
    });

    $('#autoLoadStatus').change(function() {
        table.isRepeat = $('#autoLoadStatus').prop('checked');
        if (table.isRepeat) {
            table.freshTime = 1000;
            table.stopRepeat();
            table.isRepeating = table.repeat();
        }else {
            table.stopRepeat();
        }
    });

    $("a[href='#problemSubmit']").on("click", function(e) {
        e.preventDefault();
        changToSubmit();
    });
    $("a[href='#problemDesc']").on("click", function(e) {
        e.preventDefault();
        $(this).tab('show');
        table.isRepeat = false;
        table.stopRepeat();
        window.location.hash = "desc";
    });
    $("a[data-href='record']").on("click", function(e) {
        e.preventDefault();
        changToSubmissions();
    });
    $("a[data-href='rank']").on("click", function(e) {
        e.preventDefault();
        changeToRank();
    });
});

function changToSubmit() {
    table.isRepeat = false;
    table.freshTime = 1000;
    table.stopRepeat();
    $("a[href='#problemSubmit']").tab('show');

    window.location.hash = "submit";
    if (localStorage.getItem("submit-language") != null) {
        $("option[value="+localStorage.getItem("submit-language")+"]").attr("selected", "selected");
    }
}
function changToSubmissions() {
    if (!isMobile) {
        table.isRepeat = true;
        if (!$(this).prop('checked')) {
            $('#autoLoadStatus').bootstrapToggle('on');
            table.isRepeat = $('#autoLoadStatus').prop('checked');
            if (table.isRepeat) {
                table.stopRepeat();
                table.isRepeating = table.repeat();
            }else {
                table.stopRepeat();
            }
        }
    }

    $("a[data-href='record']").tab('show');
    window.location.hash = "submissions";

    table.loadPage(1);
}
function changeToRank() {
    table.isRepeat = false;
    table.stopRepeat();
    $('#autoLoadStatus').bootstrapToggle('off');
    $("a[data-href='rank']").tab('show');
    window.location.hash = "rank";
    table.loadPage(2);
}

