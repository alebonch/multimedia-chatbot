const me = {};
const you = {};
const micro_div = $("#microphone")
const micro_icon = $("#micro-icon")
const flag_icon = $("#flag-image")
const languageDropDown = $("#language-select")
let languages = {}
let userLang = navigator.language || navigator.userLanguage;
let isSupported = false;
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
const SpeechGrammarList = window.SpeechGrammarList || window.webkitSpeechGrammarList
// const SpeechRecognitionEvent = window.SpeechRecognitionEvent || window.webkitSpeechRecognitionEvent
let unsupportedBrowser = false;
let recognition;
if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
    recognition = new SpeechRecognition();
    let speechRecognitionList = new SpeechGrammarList();
    recognition.grammars = speechRecognitionList;
    recognition.continuous = false;
} else {
    unsupportedBrowser = true;

    micro_icon.attr('title', 'It looks like your mic is unavailable');
    flag_icon.addClass('grayed-out')
    console.log('Using speech-polyfill not allowed');
}

let userLanguageName = 'English (United Kingdom)';
window.onload = function () {
    fetch('../../static/assets/json/languages.json')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            languages = data;
            // let userLanguageName;
            isSupported = Object.keys(languages).some(key => {
                if (languages[key][0] === userLang) {
                    userLanguageName = key;
                    return true;
                }
                return false;
            });
            console.log(isSupported, userLang);
            if (isSupported) {
                console.log('User language is supported:', userLang);
                if (recognition) {
                    recognition.lang = userLang;
                } else {
                    console.log('SpeechRecognition is not defined');
                }
                let flagUrl = languages[userLanguageName][1];
                let placeholderText = languages[userLanguageName][2];
                flag_icon.attr("src", flagUrl);
                $(".input_text").attr("placeholder", placeholderText);
            } else {
                console.log('User language is not supported:', userLang);
                recognition.lang = 'English (United Kingdom)'; // default language
            }

            populateDropdownMenu(languages);
        })
        .catch(error => console.error('Error:', error));
}
// Create a dropdown menu for language selection
function populateDropdownMenu(languages) {
    let defaultOption = $('<option></option>');
    defaultOption.text("Choose your preferred language");
    defaultOption.val("");
    defaultOption.prop("disabled", true);
    defaultOption.prop("selected", true);
    languageDropDown.append(defaultOption);
    for (let language in languages) {
        let option = $('<option></option>');
        option.text(language);
        option.val(languages[language][0]);
        languageDropDown.append(option);
    }
}

// Add the dropdown menu to the page
flag_icon.click(function() {
    if (unsupportedBrowser) {
        window.alert("Sorry, your browser does not support speech recognition. Please try a different browser.");
        return;
    } else {
        $("#language-select").toggle();
    }

});
console.log(languages['English (United Kingdom)'])
// Add an event listener to the dropdown menu
$("#language-select").change(function() {
    let selectedLanguage = $(this).val();
    userLanguageName = $(this).find('option:selected').text();

    let flagUrl = languages[$(this).find('option:selected').text()][1];
    let placeholderText = languages[$(this).find('option:selected').text()][2];
    console.log(selectedLanguage);
    recognition.lang = selectedLanguage;
    flag_icon.attr("src", flagUrl);
    $(".input_text").attr("placeholder", placeholderText);
    $("#language-select").toggle();
});
const checkMicrophoneAvailability = () => {
    navigator.mediaDevices.enumerateDevices()
        .then(function (devices) {
            const audioDevices = devices.filter(device => device.kind === "audioinput");
            if (audioDevices.length > 0 && !unsupportedBrowser)  {
                console.log("Microphone is available");
                if (micro_icon.hasClass('bx-microphone-off')) {
                    micro_icon.removeClass('bx-microphone-off');
                    micro_icon.addClass('bx-microphone');
                    micro_icon.attr('title', 'Click to use your voice');
                }
            } else {
                console.log("Microphone is not available");
                if (micro_icon.hasClass('bx-microphone')) {
                    micro_icon.removeClass('bx-microphone');
                    micro_icon.addClass('bx-microphone-off');
                    micro_icon.attr('title', 'It looks like your mic is unavailable');
                    flag_icon.addClass('grayed-out')
                }
                window.alert("Please activate your microphone or plug in a microphone and refresh this page to use this app.");
            }
        })
        .catch(error => console.error("Error occurred while trying to enumerate devices:", error));
};

const formatAMPM = (date) => {
    let hours = date.getHours();
    let minutes = date.getMinutes();
    let ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12; // the hour '0' should be '12'
    minutes = minutes < 10 ? '0' + minutes : minutes;
    let strTime = hours + ':' + minutes + ' ' + ampm;
    return strTime;
}

//-- No use time. It is a javaScript effect.
const insertChat = (who, text, time = 0) => {
    if (time === undefined) {
        time = 0;
    }
    let control = "";
    let date = formatAMPM(new Date());
    if (who === "you") {
        control = '<li style="width:100%">' +
            '<div class="msj macro">' +
            '<div class="text">' +
            '<p class="text-l">' + text + '</p>' +
            '<p>' + date + '</p>' +
            '</div>' +
            '</div>' +
            '</li>';
    } else {
        control = '<li style="width:100%;">' +
            '<div class="msj-rta macro">' +
            '<div class="text">' +
            '<p class="text-r">' + text + '</p>' +
            '<p>' + date + '</p>' +
            '</div>' +
            '</li>';
    }

    setTimeout(
        function () {
            $(".chat-ul ul").append(control).scrollTop($(".chat-ul ul").prop('scrollHeight'));
        }, time);

}

const resetChat = () => {
    $(".chat-ul ul").empty();
}

const goPython = (text, p_link) => {
    const token = $('input[name="csrfToken"]').attr('value');
    console.log(userLanguageName, userLang)
    $.ajax({
        type: "POST",
        url: "/handle_chat_question/",
        data: {
            'question': text,
            'language': userLanguageName,
            'url': p_link.toString(),
            'csrfmiddlewaretoken': token
        }
    }).done(result => {
        const answer = result['answer'].toString();
        insertChat("you", answer, 150);
    }).fail((jqXHR, textStatus, errorThrown) => {
        console.error("Request failed: " + textStatus + ", " + errorThrown);
        window.alert("An error occurred while processing your request. Please try again.");
    });
};

$(".input_text").on("keydown", function (e) {
    if (e.which === 13) {
        const currentUrl = window.location.href;
        console.log('Current URL:', currentUrl);
        let text = $(this).val();
        if (text !== "") {
            insertChat("me", text);
            goPython($(this).val(), currentUrl)
            $(this).val('');
        }
    }
});



const startRecording = () => {
    if (!('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)) {
        console.log('SpeechRecognition API is not supported in this browser');
        micro_icon.removeClass('bx-microphone');
        micro_icon.addClass('bx-microphone-off');
        micro_icon.attr('title', 'SpeechRecognition API is not supported in this browser');
        alert('Sorry, your browser does not support speech recognition. Please try a different browser.');
        return;
    }

    console.log('start');
    micro_icon.addClass("blink-image");

    const stopStreamAndRecognition = (stream) => {
        console.log('stop');
        stream.getTracks().forEach((track) => {
            track.stop();
        });
        recognition.stop();
        micro_icon.removeClass("blink-image");
    };

    const handleRecognitionResult = (event) => {
        const currentUrl = window.location.href;
        const question = event.results[0][0].transcript + '?';
        insertChat("me", question);
        goPython(question, currentUrl);
    };

    const handleRecognitionError = (event) => {
        console.error(event.error);
    };

    const handleMicrophoneError = () => {
        console.log("Microphone is not available or not active");
        window.alert("Please activate your microphone or plug in a microphone to use this feature.");
        micro_icon.attr("src", no_micro_icon_path);
        micro_icon.removeClass("blink-image");
    };

    navigator.mediaDevices.getUserMedia({audio: true})
        .then((stream) => {
            console.log("Microphone is available and active");

            setTimeout(() => stopStreamAndRecognition(stream), 5000);

            recognition.start();

            recognition.onresult = handleRecognitionResult;
            recognition.onerror = handleRecognitionError;
            recognition.onspeechend = () => {
                recognition.stop();
                console.log('stop recognition');
            };
        })
        .catch(handleMicrophoneError);
};

micro_icon.click(() => {
    startRecording();
    console.log('Ready to receive a question.');
});

$('body > div > div > div:nth-child(2) > span').click(function () {
    $(".input_text").trigger({type: 'keydown', which: 13, keyCode: 13});
})

//-- Clear Chat
resetChat();

//-- Print Messages
insertChat("you", "Hi! Nice to meet you!", 0);
insertChat("you", "Ask me something about this artwork!", 1500);

checkMicrophoneAvailability();