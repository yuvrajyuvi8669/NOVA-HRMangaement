 // ------------------------------------------------ Display Time to message --------------------------------------

//window.resources_path/img/novaavatar2.png

// for production
window.resources_path = "/Digital_Assistant/Test UI/static"

// for uat
//window.resources_path = "resources/acemaster/static"

// for development
//window.resources_path = "./static"

// for pwa
//window.resources_path = "./assets"

function timeclock() {
    var dt = new Date();
    var min = dt.getMinutes();
    var minute = (min < 10) ? ('0' + min) : min;
    var times = dt.getHours() + ":" + minute;
    var H = +times.substr(0, 2);
    var h = H % 12 || 12;
    var ampm = (H < 12 || H === 24) ? " AM" : " PM";
    //var time = h +":"+minute;
    var time = h + times.substr(2, 4) + ampm;
    return time;
}

var password_data = "";
var bot_previous_response = "";
var second_value = new Array();
// ------------------------------------------------on input/text enter--------------------------------------------------------------------------------------

$('.usrInput').on('keyup keypress', function(e) {
    var keyCode = e.keyCode || e.which;
    var text = $(".usrInput").val();
    console.log("data from user " + text)

    if(document.getElementById("keypad").value != ""){
        document.getElementById("micshow").style.display = "none";
        document.getElementById("arrowshow").style.display = "block";
    }else{
        document.getElementById("micshow").style.display = "block";
        document.getElementById("arrowshow").style.display = "none";
    }
    
    

   
    if (keyCode === 13) {
        if (text == "" || $.trim(text) == '') {
            e.preventDefault();
            return false;
        } else if (text.toLowerCase() == "clear") {
            document.getElementById("chats").innerHTML = "";
            $(".usrInput").val('');
            // send('Hi');
            e.preventDefault();
            return false;
        } else {
            //$(".usrInput").blur(); To keep cursor un-focus
            setUserResponse(text);
            send(text);
            password_data = text;
            e.preventDefault();
            return false;
        }
    }
});





//------------------------------------- Set user response------------------------------------
function setUserResponse(val) {

    console.log("previsoulksjdflsdjfsdjf " + window.bot_previous_response)
    if (window.bot_previous_response.includes("password")) {
        time = timeclock();
        console.log("pass " + val)
        stars = "";
        for (i = 0; i < val.length; i++) {
            stars = stars + "*"
            console.log("value of i" + i);
        }
        console.log(stars);
        var UserResponse = '<p class="userMsg">' + stars + '</p><div class="clearfix"></div><time1>' + time + '</time1><div class="clearfix"></div>';
        $(UserResponse).appendTo('.chats').show('slow');
        $(".usrInput").val('');
        scrollToBottomOfResults();
        $('.menu').remove();
        $('.action_menu').remove();
    } else {
        time = timeclock();

        var UserResponse = '<p class="userMsg">' + val + '</p><div class="clearfix"></div><time1>' + time + '</time1><div class="clearfix"></div>';
        $(UserResponse).appendTo('.chats').show('slow');
        $(".usrInput").val('');
        scrollToBottomOfResults();
        $('.menu').remove();
        $('.action_menu').remove()
    }
}

//---------------------------------- Scroll to the bottom of the chats-------------------------------
function scrollToBottomOfResults() {
    var terminalResultsDiv = document.getElementById('chats');
    terminalResultsDiv.scrollTop = terminalResultsDiv.scrollHeight;
}

function send(message) {
    window.previous_user_msg = message;
    console.log("User Message:", message)
    var username = window.localStorage.getItem("username");
    console.log("username is " + username);
    if (document.getElementById("carousel")) {
        $('#carousel').remove();

    }
    if (document.getElementById("full_form")) {
        var form1 = document.getElementById("full_form");
        $(form1).remove();
    }
    // Rasa core url's:
    // URL = "https://novabackend.omfysgroup.com:7443/webhooks/rest/webhook";
    // URL = "https://b2d9a3e1.ngrok.io/webhooks/rest/webhook";
    // URL = "http://" +
    // "43.231.254.81:5005/webhooks/rest/webhook";
    // URL = "http://13.127.186.145:5005/webhooks/rest/webhook";
    // URL = "http://103.109.13.198:5005/webhooks/rest/webhook";
    //URL = "http://106.201.234.246:5005/webhooks/rest/webhook";
     //URL = "http://localhost:5005/webhooks/rest/webhook";
	 //URL = "http://localhost:5005/webhooks/rest/webhook"
    //  URL = " http://localhost:5005/webhooks/rest/webhook";
    //  URL = " http://uat-java.omfysgroup.com:5000/message"
	 URL = " http://localhost:5000/message" // Digital Ass??istant flask url
	 //URL = "http://localhost:5005/webhooks/rest/webhook"
    //URL = "http://152.67.1.206:5006/webhooks/rest/webhook"; //OCI ubuntu UAT Nova webhook
    //URL = "http://152.67.1.206:5001/nova-webhook"; //OCI ubuntu UAT Nova webservice
    //URL = "https://uat-chatbotbackend.omfysgroup.com:8443/nova-faq-webhook" //OCI ubuntu UAT Nova webservice
    $.ajax({
        url: URL,
        type: 'POST',
        contentType: 'application/json',
        datatype: "json",
        data: JSON.stringify({
            "message": message,
            "sender": username
			
        }),
        beforeSend: function() {
            if (window.previous_user_msg == "/restart") {
                console.log("Inside beforeSend ajax request on /restart msg");

            } else {

                var spinn = spin();

                var BotResponse = '<spinn><img class="botAvatar" src="' + window.resources_path + '/img/novaavatar2.png"><strong>' + spinn + '</strong><div class="clearfix"></div></spinn>';
                $(BotResponse).appendTo('.chats').show();
                scrollToBottomOfResults();
            }
        },
        success: function(data, textStatus) {
            console.log(data);
            //document.getElementsByClassName('spinner').innerHTML = "";
            if (window.previous_user_msg == "Hi") {
                console.log("Inside if statement for popup msg");
                popmsg = "Hey! I am Nova. Your HR Digital Assistant. Please click here so that I can assist you."

            }
            popup(popmsg)
            console.log("Rasa Response: ", data, "\n Status:", textStatus)
            console.log(Object.keys(data).length)
            console.log("afetr success data - "+data)


            // ---------------------------flask webservice--------------------------------------------

            if (typeof(data) == "object") {

                if (Object.keys(data).length > 1) {
                    for (i = 0; i < Object.keys(data).length; i++) {

                        setBotResponse(data[i]);
                        // console.log("Rasa Response: ", data[i], "\n Status:", textStatus)
                        $('strong').remove();
                    }

                } else {
                    setBotResponse(data[0]);
                    console.log("Rasa Response: ", data[0], "\n Status:", textStatus)
                    $('strong').remove();
                }
            } else if (typeof(data) == "string") {
                Flask_data = JSON.parse(data)
                if (Object.keys(data).length > 1) {
                    for (i = 0; i < Object.keys(Flask_data).length; i++) {

                        setBotResponse(Flask_data[i]);
                        // console.log("Rasa Response: ", data[i], "\n Status:", textStatus)
                        $('strong').remove();
                    }

                } else {
                    setBotResponse(Flask_data[0]);
                    console.log("Rasa Response: ", Flask_data[0], "\n Status:", textStatus)
                    $('strong').remove();
                }

            } else {
                console.log("If data is nor object nor string then");
            }




            //-----------------------------end flask webservce--------------------------
            // if (Object.keys(data).length > 1) {
            //     for (i = 0; i < Object.keys(data).length; i++) {

            //         setBotResponse(data[i]);
            //         console.log("Rasa Response: ", data[i], "\n Status:", textStatus)
            //         $('strong').remove();
            //     }

            // } else {
            //     setBotResponse(data[0]);
            //     console.log("Rasa Response: ", data[0], "\n Status:", textStatus)
            //     $('strong').remove();
            // }

        },
        error: function(errorMessage) {
            $('strong').remove();
            setBotResponse("");
            if (window.previous_user_msg == "Hi") {
                console.log("Inside if statement for popup msg");
                popmsg = "Hey, I am Nova. Your HR Digital Assistant.<br> Please click here so that I can assist you."

            }
            popup(popmsg)
            console.log('Error' + errorMessage);
        }
    });
}
//------------------------------------ Set bot response -------------------------------------
function setBotResponse(val) {

    setTimeout(function() {

        if (val == null) {

            if (window.previous_user_msg == "/restart") {
                console.log("Inside if statement for /restart msg");
                send('Hi');

            } else {

                time = timeclock();

                // if there is no response from Rasa
                msg = 'I couldn\'t get that. Let\' try something else!';
                //  msg = 'I couldn\'t get that. Let\' try something else!lkjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjhhhhkjghjknbhkyuturtfghgbjkbnknmbjhgfjgkhjhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh'
                //  +'I couldnt get that. Let try something else!lkjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjhhhhkjghjknbhkyuturtfghgbjkbnknmbjhgfjgkhjhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh';

                var BotResponse = '<p class="botMsg">' + msg + '</p><div class="clearfix"></div><time2>' + time + '</time2><div class="clearfix"></div>';
                $(BotResponse).appendTo('.chats').hide().fadeIn(1000);

                bot_previous_response = msg;
                if (bot_previous_response.includes("password")) {
                    $(".usrInput").attr('type', 'password');
                } else {

                    $(".usrInput").attr('type', 'text');
                }

                scrollToBottomOfResults();

            }
        } else {

            //if we get response from Rasa
            //for (i = 0; i < val.length; i++) {
            //check if there is text message
            if (val.hasOwnProperty("text")) {
                time = timeclock();


                var BotResponse = '<p class="botMsg">' + val.text + '</p><div class="clearfix"></div><time2>' + time + '</time2><div class="clearfix"></div>';
                $(BotResponse).appendTo('.chats').hide().fadeIn(1000);
                window.bot_previous_response = val.text;
                if (bot_previous_response.includes("password")) {
                    $(".usrInput").attr('type', 'password');
                } else {

                    $(".usrInput").attr('type', 'text');
                }

            }

            //check if there is image
            if (val.hasOwnProperty("image")) {
                time = timeclock();
                var BotResponse = '<div class="singleCard">' +
                    '<img class="imgcard" src="' + val.image + '">' +
                    '</div><div class="clearfix"><time2>' + time + '</time2><div class="clearfix"></div>'
                $(BotResponse).appendTo('.chats').hide().fadeIn(1000);
            }

            //check if there is  button message
            if (val.hasOwnProperty("buttons")) {
                addSuggestion(val.buttons);
                console.log(val.buttons,"---------------------------------------------------------------------")
                $('.menu').remove();
                $('.action_menu').remove();
            }

            if (val.hasOwnProperty("custom")) {
                data = JSON.parse(JSON.stringify(val))
                data1 = data.custom
                console.log(data1[0].type)
                    // if (JSON.parse(JSON.stringify(val)).custom.type == "table") {
                if (data1[0].type == "table") {
                    console.log("Checked for table");

                    window.row_count = val.length;

                    var title = JSON.parse(JSON.stringify(val)).custom.title;
                    var table_row_head = JSON.parse(JSON.stringify(val)).custom.table_row_head;
                    var row_data = JSON.parse(JSON.stringify(val)).custom.row_data;

                    window.row_data = row_data;


                    addTable(title, table_row_head, row_data);
                } else if (JSON.parse(JSON.stringify(val)).custom.type == "Hyperlink") {
                    console.log("Checked for hyperlink");

                    window.vall = val.length;
                    var links = JSON.parse(JSON.stringify(val)).custom.links;
                    var title = JSON.parse(JSON.stringify(val)).custom.title;
                    var level = JSON.parse(JSON.stringify(val)).custom.level;

                    window.level = level;
                    window.links = links;

                    addLinks(links, title, level);
                } else
                if (data1[0].type == "FAQ") {
                    console.log("Checked for FAQ");

                    window.row_count = val.length;

                    var QnA = JSON.parse(JSON.stringify(val)).custom.QnA;

                    addFAQScroll();
                } else {
                    console.log("Inside custom")
                    console.log(val)
                    data = JSON.parse(JSON.stringify(val))
                    console.log("data", data)
                    data1 = data.custom
                    console.log("data1", data1)
                    window.more_l = new Array();
                    window.link_href = new Array();
                    window.download = new Array();
                    var btn1_text, btn2_text, btn1_payload, btn2_payload;
                    console.log(data1.length)






                    if (data1.length > 0 && data1[0].type == 'List') {
                        // var btn1 = data1[0].links[0].button[0].title;
                        // var btn2 = data1[0].links[0].button[1].title;
                        // var btn1_p = data1[0].links[0].button[0].payload;
                        // var btn2_p = data1[0].links[0].button[1].payload;

                        // var BotResponse = '<p class="botMsg">' + data1[0].title + '<div class="clearfix"></div><ol class="ordered_list"></ol></p><div class="clearfix"></div><time2>' + time + '</time2><div class="clearfix"></div>'
                        // $(BotResponse).appendTo('.chats').hide().fadeIn(1000);
                        addLists(title);
                    } else if (data1[0].type == "Form") {

                        console.log("Checked forForm");


                        // var links = JSON.parse(JSON.stringify(val)).custom.links;
                        // var title = JSON.parse(JSON.stringify(val)).custom.title;
                        // window.level = level;
                        // window.links = links;
                        addForm(title);
                    }


                    // if (data1.length > 0 && data1[0].type == 'List' && data1[0].links[0].download != null) {
                    //     console.log("inside if")
                    //     for (i = 0; i < data1.length; i++) {

                    //         scrollToBottomOfResults();

                    //         $('<li class="parent_li" class="child_li"><List><a onclick = clickListElement("' + i + '")>' + data1[i].links[0].more_link + '</a></List></li><div class = "clearfix"></div>').appendTo('.ordered_list');
                    //         window.more_l[i] = data1[i].links[0].more_link;
                    //         window.download[i] = data1[i].links[0].download;
                    //         window.btn1_text = data1[i].links[0].button[0].title;
                    //         window.btn2_text = data1[i].links[0].button[1].title;
                    //         window.btn1_payload = data1[i].links[0].button[0].payload;
                    //         window.btn2_payload = data1[i].links[0].button[1].payload;
                    //         scrollToBottomOfResults();


                    //     }
                    // } else {
                    //     if (data1.length > 0 && data1[0].type == 'List') {
                    //         console.log("inside if")
                    //         for (i = 0; i < data1.length; i++) {

                    //             scrollToBottomOfResults();

                    //             $('<li class="parent_li" class="child_li"><List><a onclick = clickListElement("' + i + '")>' + data1[i].links[0].more_link + '</a></List></li><div class = "clearfix"></div>').appendTo('.ordered_list');
                    //             window.more_l[i] = data1[i].links[0].more_link;
                    //             window.link_href[i] = data1[i].links[0].link_href;
                    //             window.btn1_text = data1[i].links[0].button[0].title;
                    //             window.btn2_text = data1[i].links[0].button[1].title;
                    //             window.btn1_payload = data1[i].links[0].button[0].payload;
                    //             window.btn2_payload = data1[i].links[0].button[1].payload;
                    //             scrollToBottomOfResults();


                    //         }


                    //     } else {
                    //         $('<m>' + data1.errorDesc + '</m>').appendTo('.ordered_list');
                    //     }
                    // }
                    else if (data1[0].list_title) {
                        $('<m>' + data1[0].list_title + '</m>').appendTo('.ordered_list');

                    } else {
                        $('<m>' + data1.errorDesc + '</m>').appendTo('.ordered_list');
                    }

                }

                console.log("lsjdflsdkjfsdljfsdlkfjsdlkfjsdlkfjsdlkfjds " + JSON.stringify(data1[1]));
                console.log("lsjdflsdkjfsdljfsdlkfjsdlkfjsdlkfjsdlkfjds " + data1[2]);

            }

        }


        //}

        scrollToBottomOfResults();
    }, 500);
}
// ----------------------------------------------------------------------Start FAQ----------------------------------------
function addFAQScroll() {
    console.log("Inside Add Faq Scroll")

    var Qna = data1[0].QnA;
    Qna_length = Qna.length;
    console.log(Qna_length)

    var BotResponse = '<p class="botMsg">' + data1[0].title + '<div class="clearfix"></div><div id="carousel"></div></p><div class="clearfix"></div><time2>' + time + '</time2><div class="clearfix"></div>';
    $(BotResponse).appendTo('.chats').hide().fadeIn(1000);


    display_caurosel(1)

}

function display_caurosel(user_click) {
    var Qna = data1[0].QnA;
    Qna_length = Qna.length;
    console.log(Qna_length)

    $('#carousel').empty();
    console.log(typeof(user_click))

    if (user_click == 1) {
        firstSlide(Number(user_click))
    } else if (user_click == Qna_length) {
        lastSlide(Number(user_click))
    } else {
        middleSlide(Number(user_click))
    }
}

function firstSlide(user_click) {
    prev = (user_click - 1)
    next = (user_click + 1)
    console.log("First Element")
        // caurosel for first element
    console.log(data1[0]['QnA'][user_click - 1]['q'])
    $("<div id='Box'><div id='question'>" + data1[0]['QnA'][user_click - 1]['q'] + "</div><div id='answer' onclick=ViewAnswer(" + prev + ")>View Answer</div></div><div id='right_arrow' onclick = display_caurosel(" + next + ")> > </div>").appendTo('#carousel');
    scrollToBottomOfResults();
}

function middleSlide(user_click) {
    next = user_click + 1
    console.log(user_click, "user click")
    prev = user_click - 1
        // caurosel for all middle element
    console.log("Middle Elements")
    console.log(data1[0]['QnA'][user_click - 1]['q'])
    console.log(data1[0]['QnA'][user_click - 1]['a'])
    $("<div id='left_arrow' onclick = display_caurosel(" + prev + ")><</div><div id='Box'><div id='question'>" + data1[0]['QnA'][user_click - 1]['q'] + "</div><div id='answer'  onclick=ViewAnswer(" + prev + ")>View Answer</div></div><div id='right_arrow' onclick = display_caurosel(" + next + ")>></div>").appendTo('#carousel');
    scrollToBottomOfResults();

}

function lastSlide(user_click) {
    prev = user_click - 1
    console.log("last Element")
    console.log(data1[0]['QnA'][user_click - 1]['q'])
    console.log(data1[0]['QnA'][user_click - 1]['a'])
    $("<div id='left_arrow' onclick = display_caurosel(" + prev + ")><</div><div id='Box'><div id='question'>" + data1[0]['QnA'][user_click - 1]['q'] + "</div><div id='answer'  onclick=ViewAnswer(" + prev + ")>View Answer</div></div>").appendTo('#carousel');
    scrollToBottomOfResults();

}

function ViewAnswer(answer_number) {
    setUserResponse(data1[0]['QnA'][answer_number]['q']);
    send(data1[0]['QnA'][answer_number]['q'])
    console.log(data1[0]['QnA'][answer_number]['a'])
        // var BotResponse = '<p class="botMsg">' + data1[0]['QnA'][answer_number]['a'] + '</p><div class="clearfix"></div><time2>' + time + '</time2><div class="clearfix"></div>';
        // $(BotResponse).appendTo('.chats').hide().fadeIn(1000);
}
//----------------------------------------------------------------------------end FAQ -----------------------------------------------------------------


// -----------------------------------------------------------------------------------------------Links--------------------------------------------------------------------------------------------------------------
function addLists(title) {
    window.more_l = new Array()
    window.link_href = new Array()

    listLength = Math.floor(data1.length / 15) + 1;
    console.log("data1.length / 15", data1.length / 15)
    console.log("listlength", listLength)
        // var btn1 = data1[0].links[0].button[0].title;
        // var btn2 = data1[0].links[0].button[1].title;
        // var btn1_p = data1[0].links[0].button[0].payload;
        // var btn2_p = data1[0].links[0].button[1].payload;

    var BotResponse = '<p class="botMsg">' + data1[0].title + '<div class="clearfix"></div><ol class="ordered_list"></ol></p><div class="clearfix"></div><time2>' + time + '</time2><div class="clearfix"></div>'
    $(BotResponse).appendTo('.chats').hide().fadeIn(1000);

    displaylistNumber(1)
}

function displaylistNumber(usrClick) {


    $('.ordered_list').empty();
    console.log(typeof(usrClick))

    if (usrClick == 1) {
        if (data1.length < 15) {
            firstNode(1, data1.length);
        } else {
            firstNode(1, 15);
        }
    } else if (usrClick == listLength) {
        lastNode(Number(usrClick), data1.length);

    } else {

        middleNodes(Number(usrClick), Number(usrClick) * 15);
    }
}


function firstNode(usrClick, totalList) {
    next = usrClick + 1;

    if (data1.length <= 15) {
        $('<div class="currentRange">' + (1) + '&nbsp;to&nbsp;' + (totalList) + '&nbsp;out of&nbsp;' + data1.length + '</div>').appendTo('.ordered_list');
        scrollToBottomOfResults();
    } else {
        $('<div class="currentRange">' + (1) + '&nbsp;to&nbsp;' + (totalList) + '&nbsp;out of&nbsp;' + data1.length + '</div><div class="nextElement" onclick = displaylistNumber("' + (usrClick + 1) + '")> > <div>').appendTo('.ordered_list');
        scrollToBottomOfResults();

    }

    if (data1.length > 0 && data1[0].type == 'List' && data1[0].links[0].download != null) {
        console.log("inside if")
        for (i = 0; i < totalList; i++) {

            scrollToBottomOfResults();

            $('<div class="parent_li" class="child_li"><List><a onclick = clickListElement("' + i + '")>' + data1[i].links[0].more_link + '</a></List></div><div class = "clearfix"></div>').appendTo('.ordered_list');
            window.more_l[i] = data1[i].links[0].more_link;
            window.download[i] = data1[i].links[0].download;
            // window.btn1_text = data1[i].links[0].button[0].title;
            // window.btn2_text = data1[i].links[0].button[1].title;
            // window.btn1_payload = data1[i].links[0].button[0].payload;
            // window.btn2_payload = data1[i].links[0].button[1].payload;
            scrollToBottomOfResults();
        }
    } else {
        if (data1.length > 0 && data1[0].type == 'List') {
            console.log("inside if")
            for (i = 0; i < totalList; i++) {

                if (data1[i].links[0].hover) {
                    $('<div class="parent_li child_li ListHover"><div class="hoverEffect">' +
                        data1[i].links[0].hover + '</div><List><a onclick = clickListElement("' + i + '")>' + data1[i].links[0].more_link + '</a></List></div><div class = "clearfix"></div>').appendTo('.ordered_list');
                    window.more_l[i] = data1[i].links[0].more_link;
                    window.link_href[i] = data1[i].links[0].link_href;

                } else {
                    $('<div class="parent_li" class="child_li"><List><a onclick = clickListElement("' + i + '")>' + data1[i].links[0].more_link + '</a></List></div><div class = "clearfix"></div>').appendTo('.ordered_list');
                    window.more_l[i] = data1[i].links[0].more_link;
                    window.link_href[i] = data1[i].links[0].link_href;

                }

                scrollToBottomOfResults();
                // $('<div class="parent_li" class="child_li"><List><a onclick = clickListElement("' + i + '")>' + data1[i].links[0].more_link + '</a></List></div><div class = "clearfix"></div>').appendTo('.ordered_list');
                // window.more_l[i] = data1[i].links[0].more_link;
                // window.link_href[i] = data1[i].links[0].link_href;
                // window.btn1_text = data1[i].links[0].button[0].title;
                // window.btn2_text = data1[i].links[0].button[1].title;
                // window.btn1_payload = data1[i].links[0].button[0].payload;
                // window.btn2_payload = data1[i].links[0].button[1].payload;
                scrollToBottomOfResults();
            }

        } else {
            $('<m>' + data1.errorDesc + '</m>').appendTo('.ordered_list');
        }
    }
}


function middleNodes(usrClick, totalList) {


    end = totalList

    initial = (Math.floor(end / 15) * 15) - 15;
    next = usrClick + 1;

    previous = usrClick - 1;

    $('<div class="currentRange">' + (initial + 1) + '&nbsp;to&nbsp;' + totalList + '&nbsp;out of&nbsp;' + data1.length + '</div><div class="previousElement" onclick=displaylistNumber("' + previous + '")><</div><div class="nextElement" onclick = displaylistNumber("' + next + '")>></div>').appendTo('.ordered_list');
    scrollToBottomOfResults();

    if (data1.length > 0 && data1[0].type == 'List' && data1[0].links[0].download != null) {
        console.log("inside if")
        for (i = initial; i < totalList; i++) {

            scrollToBottomOfResults();

            $('<div class="parent_li" class="child_li"><List><a onclick = clickListElement("' + i + '")>' + data1[i].links[0].more_link + '</a></List></div><div class = "clearfix"></div>').appendTo('.ordered_list');
            window.more_l[i] = data1[i].links[0].more_link;
            window.download[i] = data1[i].links[0].download;
            window.btn1_text = data1[i].links[0].button[0].title;
            window.btn2_text = data1[i].links[0].button[1].title;
            window.btn1_payload = data1[i].links[0].button[0].payload;
            window.btn2_payload = data1[i].links[0].button[1].payload;
            scrollToBottomOfResults();


        }
    } else {
        if (data1.length > 0 && data1[0].type == 'List') {
            console.log("inside if")
            for (i = initial; i < totalList; i++) {

                scrollToBottomOfResults();

                if (data1[i].links[0].hover) {
                    $('<div class="parent_li child_li ListHover"><div class="hoverEffect">' +
                        data1[i].links[0].hover + '</div><List><a onclick = clickListElement("' + i + '")>' + data1[i].links[0].more_link + '</a></List></div><div class = "clearfix"></div>').appendTo('.ordered_list');
                    window.more_l[i] = data1[i].links[0].more_link;
                    window.link_href[i] = data1[i].links[0].link_href;

                } else {
                    $('<div class="parent_li" class="child_li"><List><a onclick = clickListElement("' + i + '")>' + data1[i].links[0].more_link + '</a></List></div><div class = "clearfix"></div>').appendTo('.ordered_list');
                    window.more_l[i] = data1[i].links[0].more_link;
                    window.link_href[i] = data1[i].links[0].link_href;

                }

                // $('<div class="parent_li" class="child_li"><List><a onclick = clickListElement("' + i + '")>' + data1[i].links[0].more_link + '</a></List></div><div class = "clearfix"></div>').appendTo('.ordered_list');
                // window.more_l[i] = data1[i].links[0].more_link;
                // window.link_href[i] = data1[i].links[0].link_href;
                // window.btn1_text = data1[i].links[0].button[0].title;
                // window.btn2_text = data1[i].links[0].button[1].title;
                // window.btn1_payload = data1[i].links[0].button[0].payload;
                // window.btn2_payload = data1[i].links[0].button[1].payload;
                scrollToBottomOfResults();


            }


        } else {
            $('<m>' + data1.errorDesc + '</m>').appendTo('.ordered_list');
        }
    }
}



function lastNode(usrClick, totalList) {


    var previous = (usrClick - 1);

    var end = totalList;

    var before_initial = Number(end);


    var initial = Math.floor(before_initial / 15) * 15;


    $('<div class="currentRange">' + (initial + 1) + '&nbsp;to&nbsp;' + (totalList) + '&nbsp;out of&nbsp;' + data1.length + '</div><div class="previousElement" onclick=displaylistNumber("' + previous + '")><</div>').appendTo('.ordered_list');
    scrollToBottomOfResults();

    if (data1.length > 0 && data1[0].type == 'List' && data1[0].links[0].download != null) {
        console.log("inside if")
        for (i = initial; i < totalList; i++) {

            scrollToBottomOfResults();

            $('<div class="parent_li" class="child_li"><List><a onclick = clickListElement("' + i + '")>' + data1[i].links[0].more_link + '</a></List></div><div class = "clearfix"></div>').appendTo('.ordered_list');
            window.more_l[i] = data1[i].links[0].more_link;
            window.download[i] = data1[i].links[0].download;
            window.btn1_text = data1[i].links[0].button[0].title;
            window.btn2_text = data1[i].links[0].button[1].title;
            window.btn1_payload = data1[i].links[0].button[0].payload;
            window.btn2_payload = data1[i].links[0].button[1].payload;
            scrollToBottomOfResults();

        }
    } else {
        if (data1.length > 0 && data1[0].type == 'List') {
            console.log("inside if")
            for (i = initial; i < totalList; i++) {

                scrollToBottomOfResults();
                if (data1[i].links[0].hover) {
                    $('<div class="parent_li child_li ListHover"><div class="hoverEffect">' +
                        data1[i].links[0].hover + '</div><List><a onclick = clickListElement("' + i + '")>' + data1[i].links[0].more_link + '</a></List></div><div class = "clearfix"></div>').appendTo('.ordered_list');
                    window.more_l[i] = data1[i].links[0].more_link;
                    window.link_href[i] = data1[i].links[0].link_href;

                } else {
                    $('<div class="parent_li" class="child_li"><List><a onclick = clickListElement("' + i + '")>' + data1[i].links[0].more_link + '</a></List></div><div class = "clearfix"></div>').appendTo('.ordered_list');
                    window.more_l[i] = data1[i].links[0].more_link;
                    window.link_href[i] = data1[i].links[0].link_href;

                }

                // $('<div class="parent_li" class="child_li"><List><a onclick = clickListElement("' + i + '")>' + data1[i].links[0].more_link + '</a></List></div><div class = "clearfix"></div>').appendTo('.ordered_list');
                // window.more_l[i] = data1[i].links[0].more_link;
                // window.link_href[i] = data1[i].links[0].link_href;
                // window.btn1_text = data1[i].links[0].button[0].title;
                // window.btn2_text = data1[i].links[0].button[1].title;
                // window.btn1_payload = data1[i].links[0].button[0].payload;
                // window.btn2_payload = data1[i].links[0].button[1].payload;
                scrollToBottomOfResults();

            }


        } else {
            $('<m>' + data1.errorDesc + '</m>').appendTo('.ordered_list');
        }
    }
}

function addLinks(links, title, level) {
    setTimeout(function() {

        console.log("Inside addlinks1");
        var link_length = links.length;
        window.len = link_length;
        $('<p class="botMsg">' + title + '<ul class="unordered_list"></ul></p><time2>' + time + '</time2><div class="clearfix"></div>').appendTo('.chats').hide().fadeIn(1000);
        //var BotResponse = '<img class="botAvatar" src="./static/img/novaavatar2.png"><p class="botMsg">' + title + '</p><div class="clearfix"></div><time2>'+time+'</time2><div class="clearfix"></div>';
        //$(BotResponse).appendTo('.chats').hide().fadeIn(1000);
        scrollToBottomOfResults();


        if (level == 'first level') {
            console.log("Inside addlinks2");


            for (i = 0; i < Number(link_length); i++) {
                $('<li class="parent_li"><a class="child_li"  onclick = send("' + links[i].link_text + '")>' + links[i].payload + '</a></li><div class="clearfix"></div>').appendTo('.unordered_list').hide().fadeIn(1000);
                //var BotResponse = links[i].link_text + '</p><div class="clearfix"></div><time2>'+time+'</time2><div class="clearfix"></div>';
                //$(BotResponse).appendTo('.chats').hide().fadeIn(1000);
                scrollToBottomOfResults();

            }

        }
        if (level == 'second level') {
            window.level = level;
            console.log("Inside href addlink");

            for (i = 0; i < Number(link_length); i++) {
                console.log('links  text ' + links[i].link_text);
                // window.new_page_url = window.open(links[i].link_href);
                $('<li type = "square" class="parent_li"><a class="child_li" href="' + links[i].link_href + '"target="_blank">' + links[i].link_text + '</a></li><div class="clearfix"></div>').appendTo('.unordered_list');
                $('<li type = "square" class="parent_li"><a class="child_li" href="' + links[i].link_href + '"target="_blank">' + links[i].link_text + '</a></li><div class="clearfix"></div>').appendTo('.unordered_list');
            }
        }

        scrollToBottomOfResults();

    }, 1000);
}

// on click event of link 
$(document).on("click", ".unordered_list .parent_li .child_li", function() {
    console.log("click on url");
    console.log("window.level " + window.level);
    var links = window.links;
    console.log("Length of link" + Number(links.length));
    if (window.level == 'first level') {
        var text = this.innerText;
        setUserResponse(text);
    }

    if (window.level == 'second level') {
        //for(i = 0; i< Number(links.length); i++){
        //console.log("inside second_level if statement");
        var text = this.innerText;
        setUserResponse(text);
        //send(text);
        var BotResponse = '<img class="botAvatar" src="' + window.resources_path + '/img/novaavatar2.png"><div class="clearfix"></div><p class="botMsg">Visited</p><div class="clearfix"></div><time2>' + time + '</time2><div class="clearfix"></div>';
        $(BotResponse).appendTo('.chats').hide().fadeIn(1000);
        scrollToBottomOfResults();

        $('.unordered_list').remove();

        //}   
        //}   
    } else
    if (window.level == 'third level') {
        //for(i = 0; i< Number(links.length); i++){
        //console.log("inside second_level if statement");
        var text = "this.innerText";

        scrollToBottomOfResults();
        //send(text);
        $('.unordered_list').remove();
        //}   
        //}   
    } else {
        var text = this.innerText;
        setUserResponse(text);
        send(text);
        $('.unordered_list').remove();
    }
    scrollToBottomOfResults();
});
//----------------------------------------------------------------------------Click event on list element-------------------------------------------------------------------------
function clickListElement(LstEle) {
    ListElements = document.getElementsByTagName('List')
    console.log("Length of list is", ListElements.length)
    if (ListElements.length > 0 && window.link_href[LstEle]) {
        console.log(LstEle)
        console.log(window.link_href[LstEle])
        send(" " + window.link_href[LstEle])
        $('.ordered_list').remove();
        scrollToBottomOfResults();
    } else {
        console.log(LstEle)
            // console.log(window.download[LstEle])
        setBotResponse("Payslip downloaded")
        open(window.download[LstEle])
        scrollToBottomOfResults();
    }
}

// --------------------------------------------------------------------------Toggle chatbot -------------------------------------------------------------------------------------

$('#profile_div').click(function() {
    $('.profile_div').toggle();
    $('.widget').toggle();
    scrollToBottomOfResults();
    document.getElementById("prompt").style.display = "None";
    // document.getElementsByClassName("popup").style.visibility = "hidden";
});

$('#close').click(function() {
    $('.profile_div').toggle();
    $('.popup').show();
    $('.widget').toggle();
});

// ----------------------------------------------------------------------------- Suggestions ----------------------------------------------------------------------------------------

function addSuggestion(textToAdd) {
    setTimeout(function() {
        var suggestions = textToAdd;
        var suggLength = textToAdd.length;
        $(' <div class="menu"></div><div class="action_menu"></div>').appendTo('.chats').hide().fadeIn(1000);
        // Loop through suggestions
        window.btnObj = [];
        for (i = 0; i < suggLength; i++) {
            console.log('-------------------------------suggestions[i].title ' + suggestions[i].title);
            console.log('-------------------------------------suggestions[i].payload ' + suggestions[i].payload);
            window.btnObj[i] = {
                'title': suggestions[i].title,
                'payload': suggestions[i].payload
            };
            console.log(suggestions[i].title+'-------------')
            //$('<div class="menuChips">' + suggestions[i].payload + '</div>').appendTo('.menu');
            if (suggestions[i].notifications) {
                $('<div class="menuChips"><div class = "scrollmenu"><div class = "btn-group"><button>' + suggestions[i].title + '<notification>' + suggestions[i].notifications + '</notification></button></div></div></div>').appendTo('.menu');
            } else if (suggestions[i].badge) {
                $('<div class = "btn-group"><button><div class="tooltip_badge">' + suggestions[i].title + '<span class="tooltiptext">' + suggestions[i].badge + '</span></div></button></div>').appendTo('.menu');
                //                 <div class="tooltip">Hover over me <span class="tooltiptext">Tooltip text</span></div>

            } else if (suggestions[i].text) {
                $('<div class = "btn-group"><button>' + suggestions[i].title + '<div class= "badge">' + suggestions[i].text + '</div></button></div>').appendTo('.menu');

            } else if (suggestions[i].title == 'Back') {
                $('<div class="menuChips"><div class = "scrollmenu"><div class = "btn-group_back" ><button onclick = send("' + suggestions[i].title + '") id= "back">Back</button></div></div></div>').appendTo('.action_menu');

            } else if (suggestions[i].title == 'Home') {
                $('<div class="menuChips"><div class = "scrollmenu"><div class = "btn-group_back"><button onclick = send("' + suggestions[i].title + '") id= "home"><span class="material-icons">home</span></button></div></div></div>').appendTo('.action_menu');

            } else if (suggestions[i].title == 'Exit') {
                $('<div class="menuChips"><div class = "scrollmenu"><div class = "btn-group_back"><button onclick = send("' + suggestions[i].payload + '") id = "logout">Exit</button></div></div></div>').appendTo('.action_menu');

            } else {
                $('<div class="menuChips"><div class = "scrollmenu"><div class = "btn-group"><button>' + suggestions[i].title + '</button></div></div></div>').appendTo('.menu');
            }
        }
        scrollToBottomOfResults();
    }, 1000);
}


// on click of suggestions, get the value and send to rasa
$(document).on("click", ".menu .menuChips", function() {
    var len = window.btnObj.length;
    var text = "";
    var payload = "";
    for (i = 0; i < len; i++) {

        if (window.btnObj[i].title == this.innerText) {
            console.log('title ' + window.btnObj[i].title);
            console.log('payload ' + window.btnObj[i].payload);
            console.log('this.innerText ' + this.innerText);
            text = window.btnObj[i].title;
            payload = window.btnObj[i].payload;
            var text = this.innerText;
            setUserResponse(text);
            console.log(payload)
            send(payload);
            $('.menu').remove(); //delete the suggestions
            $('.action_menu').remove(); //delete the suggestions

        } else if (this.innerText.search(window.btnObj[i].title) != -1) {
            console.log('title ' + window.btnObj[i].title);
            console.log('payload ' + window.btnObj[i].payload);
            console.log('this.innerText ' + this.innerText);
            text = window.btnObj[i].title;
            payload = window.btnObj[i].payload;

            setUserResponse(text);
            console.log(payload)
            send(payload);
            $('.menu').remove(); //delete the suggestions
            $('.action_menu').remove(); //delete the suggestions


        }



    }

});
//---------------------------------------------close button --------------------------------------------------------------------------

var d = document.getElementById("chats");
d.insertAdjacentHTML("afterend", "<div id='prompt'>Do you wish to end the <br>conversation?<br><br><a id='Ybut' class='confirmbutton' onclick='CloseY();'>Yes</a><a id='Nbut' class='confirmbutton' onclick='CloseN();'>No</a></div>");

function Close() {
    //document.getElementById("widget").style.opacity = 0.5;
    //document.getElementById("widget").style.pointerEvents = "None";
    $('#chats').css("opacity", "0.5");
    $('#chats').css("pointer-events", "None");
    $('.keypad').css("pointer-events", "None");
    document.getElementById("prompt").style.display = "inline-block ";
    document.getElementById("prompt").style.opacity = 1;

    //$('.widget>').wrap('<div class="blur-all">').append("afterend","<div id='prompt' >Do you wish to end the conversation?<br><br><a id='Ybut' class='confirmbutton' href='CloseY();'>Yes</a><a id='Nbut' class='confirmbutton' href='javascript:window.parent.CloseN();'>No</a></div>");"afterend","<div id='prompt'>Do you wish to end the conversation?<br><br><a id='Ybut' class='confirmbutton' href='javascript:window.parent.CloseY();'>Yes</a><a id='Nbut' class='confirmbutton' href='javascript:window.parent.CloseN();'>No</a></div>");

}

//addEventListener("keypress", function(event){
//  if (event.code == 'KeyY' && event.which == '13'){
// CloseY();

//}
//});
//addEventListener("keypress", function(event){
//  if (event.code == 'KeyN'){
// CloseN();

//}
//});


// If user select Yes on Pop-up dialogue
function CloseY() {
    console.log("inside y");

    $('#chats').css("opacity", "1");
    localStorage.removeItem("username");
    document.getElementById("chats").innerText = "";
    var n = Math.floor(Math.random() * 1000000000);
    window.localStorage.setItem("username", n);
    document.getElementById("prompt").style.display = "none";
    $('.profile_div').show();
    $('.widget').hide();
    $('.popup').show();
    send('/restart');

    // $('.widget').close();
    $('.keypad').css("pointer-events", "auto");
    $('#chats').css("pointer-events", "auto");
    //this.parent.hideframe();
}

// If user select No on Pop-up dialogue
function CloseN() {
    document.getElementById("prompt").style.display = "none";
    //$('.widget>').unwarp('<div class="blur-all">');
    $('#chats').css("opacity", "1");
    $('.keypad').css("pointer-events", "auto");
    $('#chats').css("pointer-events", "auto");
}
//----------------------------------------------Three dot spinner----------------------------------------------------------------------------
function spin() {

    var spinner = '<div class="spinner"><div class="bounce1"></div><div class="bounce2"></div><div class="bounce3"></div></div>';
    return spinner;
}

//-----------------------------------------enter-icon----------------------------------------------------------------------------------------
function enter() {

    console.log("inside enter")
    var text = $(".usrInput").val();
    if (text == "" || $.trim(text) == '') {
        return false
    } else if (text.toLowerCase() == "clear") {
        document.getElementById("chats").innerHTML = "";
        $(".usrInput").val('');
        // send('Hi');
        return false;
    } else {
        //$(".usrInput").blur(); To keep cursor un-focus
        setUserResponse(text);
        send(text);
        password_data = text;
        console.log(password_data, "--------Mohini-------");
        return false;
    }
}
// //-----------------------------------------------------leavedisply--------------------------------------------------------------------------------------------
// function leaveDisplayFunction(i) {
//     // console.log("leave id is "+JSON.stringify(this));
//     console.log(i)
//     var dot = document.getElementsByClassName("dots");
//     console.log(dot)
//     console.log(dot.length)

//     var moreText = document.getElementsByClassName("more");
//     var btnText = document.getElementsByClassName('child_li');
//     // var btnText = document.getElementById("myBtn");

//     if (dot[i].style.display == "none") {
//         dot[i].style.display = "inline";
//         btnText[i].innerHTML = "more";
//         moreText[i].style.display = "none";

//     } else {
//         dot[i].style.display = "none";
//         btnText[i].innerHTML = "less";
//         moreText[i].style.display = "inline";
//         moreText[i].innerText = window.more_l[i];
//     }

// console.log('more link :' + i)
// var BotResponse = '<img class="botAvatar" src="./static/img/novaavatar2.png"><div class="clearfix"></div><p class="botMsg">' + window.more_l[i] + '<br><btn_style><button onclick = "reject(' + i + ')">' + window.btn1_text + '</button></btn_style><btn_style><button onclick="reject(' + i + ')">' + window.btn2_text + '</button></btn_style></p><div class="clearfix"></div><time2>' + time + '</time2><div class="clearfix"></div>';
// $(BotResponse).appendTo('.chats').hide().fadeIn(1000);

// scrollToBottomOfResults();

// return true;
// }
$(document).on("click", "btn_style", function() {
    // send(this.innerText);
    setUserResponse(this.innerText);
    console.log("user:", this.innerText)
});

//----------------------------------------------------------------------checked values--------------------------------------------------------------------
// function getCheckedValues() {
//     var check = new Array();
//     var checks = document.getElementsByTagName("input");
//     console.log(checks.length)
//     for (i = 0; i < checks.length; i++) {
//         if (checks[i].checked) {
//             check.push(checks[i].value)
//         }
//     }
//     send(check);
// }

// const checkbox1 = document.getElementsByTagName('checkbox')

// checkbox1.addEventListener('change', function(event) {
//     if (event.target.checked) {
//         send(event.target.value)
//         console.log(event.target.value)
//     }
// // });
// function approve() {
//     var checkboxes = document.getElementsByTagName("input");
//     for (var i = 0; i < checkboxes.length; i++) {
//         console.log(checkboxes.length)
//         if (checkboxes[i].type == "checkbox") {
//             if (checkboxes[i].checked) {
//                 send(checkboxes[i].value + "" + btn1_payload)
//                 console.log(checkboxes[i].value + "" + btn1_payload)
//             }
//         }
//     }
// }

// function reject(numm) {
//     var checkboxes = document.getElementsByTagName("input");
//     console.log(checkboxes.length)
//     if (checkboxes[numm].type == "checkbox") {
//         if (checkboxes[numm].checked) {

//             send(checkboxes[numm].value + "" + data1[numm].emp1_code)
//                 // send(data1[numm].emp1_code)
//                 // console.log(data1[numm].emp1_code)
//             console.log("fghfgfghfghfghfgffgf", checkboxes[numm].value + "" + data1[numm].emp1_code)
//         } else {
//             send(checkboxes[numm].value + "" + data1[numm].emp1_code)

//             // send(data1[numm].emp1_code)
//             // console.log(data1[numm].emp1_code)
//             console.log("fghfgfghfghfghfgffgf", checkboxes[numm].value + "" + data1[numm].emp1_code)
//         }
//     } else {
//         send(checkboxes[numm].value + "" + data1[numm].emp1_code)

//         // send(data1[numm].emp1_code)
//         // console.log(data1[numm].emp1_code)
//         console.log(checkboxes[numm].value + "" + data1[numm].emp1_code)
//     }
// }
// --------------------------------------- scroll bar-------------------------------------------------------------------------------------------------------------------------------
// When the user scrolls down 20px from the top of the document, slide down the navbar
window.onscroll = function() { scrollFunction() };

function scrollFunction() {
    if (document.body.scrollTop > 50 || document.documentElement.scrollTop > 20) {
        document.getElementById("chats").style.top = "0";
    } else {
        document.getElementById("chats").style.top = "";
    }
}

//--------------------------------------------------------------pop up message-------------------------------------------------------------------------------------------------------------
function popup(val) {
    var popup = document.getElementById('profile_div')

    popup.insertAdjacentHTML("beforeend", '<div class = "popup"><span class="popuptext" id = "myPopup">' + val + '</span><div>');

    console.log(val)
        //    var popup = document.getElementById('profile_div')
        //



}
///------------------------------------------------------------------------------------TABLE DISPLAY----------------------------------------------------------
function addTable(title, table_head, row_data) {
    var table_head_length = data1[0]["table_row_head"].length
    console.log("length of coloumn", table_head_length);
    var row_data_length = data1[0]["row_data"].length
    console.log("length of data", row_data_length);

    var BotResponse = '<p class="botMsg">' + data1[0].title + '<div class="clearfix"></div><div class="tb"><table id="table_data"></table></div></p><div class="clearfix"></div><time2>' + time + '</time2><div class="clearfix"></div>';
    $(BotResponse).appendTo('.chats').hide().fadeIn(1000);


    // Find a <table> element with id="myTable":
    var table = document.getElementById("table_data");
    //console.log(data1[3]["table_row_head"][0]["title"])
    // add table heading <th>
    $("<tr>").appendTo("#table_data");
    for (i = 0; i < table_head_length; i++) {

        $("<th>" + data1[0]["table_row_head"][i]["title"] + "</th>").appendTo("#table_data");
    }
    $("</tr>").appendTo("#table_data");
    for (i = 0; i < data1.length; i++) {
        $("<tr>").appendTo("#table_data");
        for (j = 0; j < row_data_length; j++) {

            $("<td>" + data1[i]["row_data"][j]["title"] + "</td>").appendTo("#table_data");


        }
        $("</tr>").appendTo("#table_data");
    }


    scrollToBottomOfResults();

    // var table_head_length = data1[0]["table_row_head"].length
    // console.log("length of coloumn", table_head_length);
    // var row_data_length = data1[0]["row_data"].length
    // console.log("length of data", row_data_length);

    // // var BotResponse = '<p class="botMsg">' + data1[0].title + '<div class="clearfix"></div><div class="tb"><table id="table_data"></table></div></p><div class="clearfix"></div><time2>' + time + '</time2><div class="clearfix"></div>';
    // // $(BotResponse).appendTo('.chats').hide().fadeIn(1000);
    // // Find a <table> element with id="myTable":
    // var table_data = document.getElementById("table_data");
    // // console.log(data1[0]["table_row_head"][0]["title"])
    // // add table heading <th>
    // // $("<div class='tb'><table id='table_data'></table></div>").appendTo(".chats");
    // // $("<div class='tb'><table id='table_data'>").appendTo('.chats');
    // // $("<tr>").appendTo('#table_data');
    // var head = "";
    // var row_data = "";
    // var str = "";

    // window.bad = new Array()


    // for (i = 0; i < table_head_length; i++) {

    //     head += "<th>"
    //     head += data1[0]["table_row_head"][i]["title"];
    //     head += "</th>";

    //     // $("<th>" + data1[0]["table_row_head"][i]["title"] + "</th>").appendTo('#table_data');
    // }
    // $("</tr>").appendTo("#table_data");

    // for (i = 0; i < data1.length; i++) {
    //     // $("<tr>").appendTo('#table_data');
    //     row_data += "<tr>";
    //     var cell_data = "";
    //     for (j = 0; j < row_data_length; j++) {
    //         // $("<td>" + data1[i]["row_data"][j]["title"] + "</td>").appendTo('#table_data');

    //         if (data1[i]["row_data"][j]["badge"]) {
    //             var str = data1[i]["row_data"][j]["title"];
    //             var res = str.split(" ").join("");
    //             id1 = res.replace(",", "");
    //             id2 = id1.replace(")", "");
    //             id3 = id2.replace(" ", "");


    //             window.bad[i] = data1[i]["row_data"][j]["badge"]
    //             cell_data += "<td><div id = '" + id3 + "'></div>";
    //             cell_data += "<div onmouseover = cellPopup('" + id3 + "','" + i + "'); onmouseout = removehtml('" + id3 + "') style='color:blue; text-decoration:underline;'>" + data1[i]["row_data"][j]["title"];
    //             cell_data += "<div></td>";

    //         } else {
    //             cell_data += "<td>";
    //             cell_data += data1[i]["row_data"][j]["title"];
    //             cell_data += "</td>";
    //         }

    //     }
    //     row_data += cell_data;
    //     row_data += "</tr>";
    //     // $("</tr>").appendTo('#table_data');


    // }
    // title = data1[0].title
    // var BotResponse = '<p class="botMsg">' + title + '<div class="clearfix"></div><div class="tb"><table id="table_data"><tr>' + head + '</tr><tr>' + row_data + '</tr></table></div></p><div class="clearfix"></div><time2>' + time + '</time2><div class="clearfix"></div>';
    // $(BotResponse).appendTo('.chats').hide().fadeIn(1000);

    // scrollToBottomOfResults();


}


//----------------------------------------------------------------------------speech recognisition -----------------------------------------------------------------
mic = document.getElementById("speech");
mic.onclick = function() {
    window.mic_status = document.getElementById("speech").innerHTML;
    if (window.mic_status == "keyboard_voice") {
        runspeechRecognition()
        document.getElementById("speech").innerHTML = "settings_voice";
        document.getElementById("speech").style.color = "#1227af";
    } else if (window.mic_status == "settings_voice") {
        recognition.stop();
        document.getElementById("keypad").placeholder = "Type a message.......";
        document.getElementById("speech").innerHTML = "keyboard_voice";
        document.getElementById("speech").style.color = "#6072e6";
    }
};

function runspeechRecognition() {
    console.log("Inside speech recognition")

    if (window.mic_status == "keyboard_voice") {
        document.getElementById("speech").innerHTML = "settings_voice";
        document.getElementById("speech").style.color = "#1227af";
    }

    document.getElementById("speech").innerHTML

    // get output div reference
    // var action = document.getElementById("action");
    // get action element reference

    // new speech recognition object
    var SpeechRecognition = SpeechRecognition || webkitSpeechRecognition;
    var recognition = new SpeechRecognition();
    recognition.continuous = true;
    mic = document.getElementById("speech");
    mic.onclick = function() {
        window.mic_status = document.getElementById("speech").innerHTML;
        if (window.mic_status == "keyboard_voice") {
            runspeechRecognition()
            document.getElementById("speech").innerHTML = "settings_voice";
            document.getElementById("speech").style.color = "#1227af";
        } else if (window.mic_status == "settings_voice") {
            recognition.stop();
            document.getElementById("keypad").placeholder = "Type a message.......";
            document.getElementById("speech").innerHTML = "keyboard_voice";
            document.getElementById("speech").style.color = "#6072e6";
        }
    };


    // This runs when the speech recognition service starts
    recognition.onstart = function() {
        //action.innerHTML = "<small>listening, please speak...</small>";
        document.getElementById("keypad").placeholder = "listening, please speak...";
    };

    recognition.onspeechend = function() {
        // action.innerHTML = "<small>stopped listening, hope you are done...</small>";
        document.getElementById("keypad").placeholder = "stopped listening, hope you are done...";
        recognition.stop();
        document.getElementById("keypad").placeholder = "Type a message.......";

    }

    //var output = document.getElementsByClassName("usrInput");
    // This runs when the speech recognition service returns result
    recognition.onresult = function(event) {
        var transcript = event.results[0][0].transcript;
        var confidence = event.results[0][0].confidence;
        $('.usrInput').val(transcript);
        setUserResponse(transcript);
        send(transcript);
        console.log("output", transcript);
        //output.innerHTML = "<b>Text:</b> " + transcript + "<br/> <b>Confidence:</b> " + confidence * 100 + "%";
        //output.classList.remove("hide");
        document.getElementById("keypad").placeholder = "Type a message.......";
        document.getElementById("speech").innerHTML = "keyboard_voice";
        document.getElementById("speech").style.color = "#6072e6";
    };

    // start recognition
    recognition.start();

}
//---------------------------------------------------form------------------------------------------------------

function addForm() {
    console.log("Inside form printing")

    // window.more_l = new Array()
    // window.link_href = new Array()

    // listLength = Math.floor(data1.length / 15) + 1;
    // console.log("data1.length / 15", data1.length / 15)
    // console.log("listlength", listLength)


    window.bot_previous_response = data1[0].title


    console.log(data1.length)
    console.log(data1[0].fields)
    console.log(data1[0].fields.length)



    // window.field[i] = data1[i].fields[0].field;
    // window.type[i] = data1[i].fields[0].type;
    // window.name[i] = data1[i].fields[0].name;
    // // window.placeholder[i] = data1[i].fields[0].placeholder;
    // var form_created = "";
    // form_created += '<form id = "chat-bot-productsalesform">';
    // for (i = 0; i < data1[0].fields.length; i++) {
    //     if (data1[0].fields[i].type == 'tel') {
    //         form_created += '<label id= "chat-bot-lb1" class="chat-bot-compulsary">' + data1[0].fields[i].field + '</label><input type="' + data1[0].fields[i].type + '" class= "infield" id="chat-bot-' + data1[0].fields[i].field + '" name="' + data1[0].fields[i].name + '" placeholder="' + data1[0].fields[i].placeholder + '" pattern="' + data1[0].fields[i].pattern + '"required><br>';
    //     } else {
    //         form_created += '<label id= "chat-bot-lb1" class="chat-bot-compulsary">' + data1[0].fields[i].field + '</label><input type="' + data1[0].fields[i].type + '" class= "infield" id="chat-bot-' + data1[0].fields[i].field + '" name="' + data1[0].fields[i].name + '" placeholder="' + data1[0].fields[i].placeholder + '" required><br>';
    //     }
    // }
    // console.log(form_created)

    // second chanage
    var dropdown = "";
    var form_created = "";
    console.log("printing data befor passing to html form - "+JSON.stringify(data1[0]))
    form_created += '<form id = "chat-bot-productsalesform">';

    for (i = 0; i < data1[0].fields.length; i++) {

        if (data1[0].fields[i].type == 'tel') {
            form_created += '<label id= "chat-bot-lb1" class="chat-bot-compulsary">' + data1[0].fields[i].field + '</label><input type="' + data1[0].fields[i].type + '" class= "infield" id="chat-bot-' + data1[0].fields[i].field + '" name="' + data1[0].fields[i].name + '" placeholder="' + data1[0].fields[i].placeholder + '" pattern="' + data1[0].fields[i].pattern + '" autocomplete = "off" required />';

        } else if (data1[0].fields[i].type == 'dropdown') {
           
            if(data1[0].fields[i].name == 'leaveType'){
                dropdown = "";
                for (j = 0; j < data1[0].fields[i].value_list.length; j++) {
                    dropdown += '<option value="' + data1[0].fields[i].value_list[j].option_value +
                        '">' + data1[0].fields[i].value_list[j].option_value + '</option>';
                }
    
                form_created += '<label id= "chat-bot-lb1" class="chat-bot-compulsary">' + data1[0].fields[i].field +
                    '</label><select class= "infield" id="chat-bot-' + data1[0].fields[i].field + '" name="' + data1[0].fields[i].name +
                    '" required>' + dropdown + '</select>';
            } else if(data1[0].fields[i].name == 'handOverEmployee'){
                dropdown = "";
				dropdown = '<option value='+ JSON.stringify("All") +
                        '> '+ ("All")+'</option>'
				dropdown += '<option value='+ JSON.stringify("Not Applicable") +
                        '> '+("Not Applicable")+'</option>'
                for (j = 0; j < data1[0].fields[i].value_list.length; j++) {
                    dropdown += '<option value='+ JSON.stringify(data1[0].fields[i].value_list[j].emp_code) +
                        '> '+ (data1[0].fields[i].text[j].text)+'</option>'; 
					console.log("full data "+JSON.stringify(data1[0].fields[i].value_list[j].emp_code))
                }
    
                form_created += '<label id= "chat-bot-lb1" class="chat-bot-compulsary">' + data1[0].fields[i].field +
                    '</label><select class= "infield" id="chat-bot-' + data1[0].fields[i].field + '" name="' + data1[0].fields[i].name +
                    '" required>' + dropdown + '</select>';
            } else{
                for (j = 0; j < data1[0].fields[i].value_list.length; j++) {
                    dropdown += '<option value="' + data1[0].fields[i].value_list[j].option_value +
                        '">' + data1[0].fields[i].value_list[j].option_value + '</option>';
					
                }
    
                form_created += '<label id= "chat-bot-lb1" class="chat-bot-compulsary">' + data1[0].fields[i].field +
                    '</label><select class= "infield" id="chat-bot-' + data1[0].fields[i].field + '" name="' + data1[0].fields[i].name +
                    '" required>' + dropdown + '</select>';
            }
            

        } else {
            form_created += '<label id= "chat-bot-lb1" class="chat-bot-compulsary">' + data1[0].fields[i].field + '</label><input type="' + data1[0].fields[i].type + '" class= "infield" id="chat-bot-' + data1[0].fields[i].field + '" name="' + data1[0].fields[i].name + '" placeholder="' + data1[0].fields[i].placeholder + '" autocomplete = "off" required /><br>';
        }
    }
    console.log(form_created)



    // var form_created = "";
    // form_created += '<form id = "chat-bot-productsalesform">';
    // for (i = 0; i < data1[0].fields.length; i++) {
    //     if (data1[0].fields[i].type == 'tel') {
    //         form_created += '<input type="' + data1[0].fields[i].type + '" class= "infield" id="chat-bot-' + data1[0].fields[i].field + '" name="' + data1[0].fields[i].name + '" placeholder="' + data1[0].fields[i].field + '" pattern="' + data1[0].fields[i].pattern + '" autocomplete = "off" required><br>';
    //     } else {
    //         form_created += '<input type="' + data1[0].fields[i].type + '" class= "infield" id="chat-bot-' + data1[0].fields[i].field + '" name="' + data1[0].fields[i].name + '" placeholder="' + data1[0].fields[i].field + '" autocomplete = "off" required><br>';
    //     }
    // }
    // console.log(form_created)

    var BotResponse = '<p class="botMsg">' + data1[0].title + '<div class="clearfix"></div><div id=full_form><form id = "chat-bot-productsalesform">' + form_created + '<button id="chat-bot-pfsubmit" onclick="PersonalDeatails()">Proceed</button></form></p></div><div class="clearfix"></div><time2> ' + time + ' </time2><div class="clearfix"></div>';
    $(BotResponse).appendTo('.chats').hide().fadeIn(1000);
}


// var form_created =<form id ="chat-bot-productsalesform">
// <label for = "text" id= "chat-bot-lb1" class="chat-bot-compulsary">Full Name:</label><input type="text" id="chat-bot-fullname" name="fullname" placeholder="Full Name" required></br>
// <label for = "text" id= "chat-bot-lb2" class="chat-bot-compulsary">Statename:</label><input type="text" id="chat-bot-sname" name="sname" placeholder="Statename" required></br>
// <label for = "text" id= "chat-bot-lb3" class="chat-bot-compulsary">Cityname:</label><input type="text" id="chat-bot-cname" name="cname" placeholder=" Cityname" required></br>
// <label for = "text" id= "chat-bot-lb4" class="chat-bot-compulsary">Pincode:</label><input type="text" id="chat-bot-pincode" name="pincode" placeholder="Pincode" required></br>
// <label for = "text" id= "chat-bot-lb5" class="chat-bot-compulsary">CityArea:</label><input type="text" id="chat-bot-carea" name="carea" placeholder="Cityarea" required></br>
// <label for = "text" id= "chat-bot-lb6" class="chat-bot-compulsary">CityLocalityArea:</label><input type="text" id="chat-bot-clname" name="clname" placeholder="CityLocalityArea" required></br>
// <label for = "email" id="chat-bot-lb7" class="chat-bot-compulsary">Email ID:</label><input type="email" id="chat-bot-email" name="email" placeholder="ex:email@gmail.com" pattern="[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$" required></br>
// <a id="chat-bot-pfsubmit" href='javascript:window.parent.PersonalDeatails();'>Proceed</a> 
// </form>


function PersonalDeatails() {


    msg = ""
    console.log("Form Function called");
    for (i = 0; i < data1[0].fields.length; i++) {
        fld = "chat-bot-" + data1[0].fields[i].field;
        console.log("fld"+fld)

        var value = document.getElementById(fld).value;
        if(value.trim() === "")
        {
            // console.log("Please fill in all fields");
            var errorMessage = "Please fill in all fields";
            var errorElement = document.getElementById("errorMessage")
            errorElement.textContent = errorMessage;
            // alert("Please fill in the fields");
        }
        msg += value + "|";

        msg += document.getElementById(fld).value + "|";
        if (msg === "") 
        { 
            // Validation failed
            console.log("Input is required.");
        }else 
        {
            // Validation passed
            console.log("Input is valid.");
        }
        console.log("Data from Form ------  " + msg) 


        // var Statename = document.getElementById("chat-bot-sname").value;
        // var Cityname = document.getElementById("chat-bot-cname").value;
        // var Pincode = document.getElementById("chat-bot-pincode").value;
        // var CityArea = document.getElementById("chat-bot-carea").value;
        // var CityLocalityArea = document.getElementById("chat-bot-clname").value;
        // var Email ID: = document.getElementById("chat-bot-email").value;
        // var ProfieData = firstname + "|" + lastname + "|" + EmailId + "|" + MobileNumber;
        // Bots.sendMessage(ProfieData, { hidden: true });
    }
    console.log("sending message")
    send(msg)
    console.log("Data from Form Form  " + msg)

        // $('#chat-bot-productsalesform').remove();
        // $('#chat-bot-pfsubmit').remove();
    $('#full_form').remove();
    $('#myCarousel').remove();



}