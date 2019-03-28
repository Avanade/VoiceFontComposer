//webkitURL is deprecated but nevertheless
URL = window.URL || window.webkitURL;

var gumStream; 						//stream from getUserMedia()
var recorder; 						//WebAudioRecorder object
var input; 							//MediaStreamAudioSourceNode  we'll be recording
var encodingType; 					//holds selected encoding for resulting audio (file)
var encodeAfterRecord = true;       // when to encode

// shim for AudioContext when it's not avb
var AudioContext = window.AudioContext || window.webkitAudioContext;
var audioContext; //new audio context to help us record

var encodingTypeSelect = "wav";
var recordButton = document.getElementById("recordButton");
var nextButton = document.getElementById("nextButton");
var prevButton = document.getElementById("prevButton");
var expButton = document.getElementById("expButton");

//add events to those 2 buttons
recordButton.addEventListener("click", startRecording);
stopButton.addEventListener("click", stopRecording);

function startRecording() {
    console.log("startRecording() called");
    encodingType = "wav"
    __log(encodingType)

	/*
		Simple constraints object, for more advanced features see
		https://addpipe.com/blog/audio-constraints-getusermedia/
	*/

    var constraints = { audio: true, video: false }

    /*
    	We're using the standard promise based getUserMedia() 
    	https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia
	*/

    navigator.mediaDevices.getUserMedia(constraints).then(function (stream) {
        __log("getUserMedia() success, stream created, initializing WebAudioRecorder...");

		/*
			create an audio context after getUserMedia is called
			sampleRate might change after getUserMedia is called, like it does on macOS when recording through AirPods
			the sampleRate defaults to the one set in your OS for your playback device
		*/
        audioContext = new AudioContext();

        //assign to gumStream for later use
        gumStream = stream;

        /* use the stream */
        input = audioContext.createMediaStreamSource(stream);

        //stop the input from playing back through the speakers
        //input.connect(audioContext.destination)


        recorder = new WebAudioRecorder(input, {
            workerDir: "static/scripts/", // must end with slash
            encoding: "wav",
            numChannels: 2, //2 is the default, mp3 encoding supports only 2
            onEncoderLoading: function (recorder, encoding) {
                // show "loading encoder..." display
                __log("Loading " + encoding + " encoder...");
            },
            onEncoderLoaded: function (recorder, encoding) {
                // hide "loading encoder..." display
                __log(encoding + " encoder loaded");
            }
        });

        recorder.onComplete = function (recorder, blob) {
            __log("Encoding complete");
            nextButton.disabled = true;
            prevButton.disabled = true;
            recordButton.disabled = true;
            expButton.disabled = true;

            createDownloadLink(blob);
            encodingTypeSelect.disabled = false;
            //send to blob here

            __log('start call');
            var ID = document.getElementById("ID").textContent.split(": ")[1];
            var SID = document.getElementById("SessionID").textContent.split(": ")[1];;

            const Http = new XMLHttpRequest();
            Http.withCredentials = true;
            //Type?
            const api_url='https://voicefontfunctions.azurewebsites.net/api/PassBlob?'+'sessionID='+ SID +'&fileID='+ ID+'.wav';
            Http.open("POST",api_url);
            var fd=new FormData();
            fd.append("file",blob);

            __log(blob)

            Http.send(fd);
            Http.onreadystatechange=(e)=>{
                if(Http.readyState==4 && Http.status==200){
                    __log(Http.responseText)
                    nextButton.disabled = false;
                    prevButton.disabled = false;
                    recordButton.disabled = false;
                    expButton.disabled = false;
                }
            }
        }

        recorder.setOptions({
            timeLimit: 120,
            encodeAfterRecord: encodeAfterRecord,
            ogg: { quality: 0.5 },
            mp3: { bitRate: 160 }
        });

        //start the recording process
        recorder.startRecording();

        __log("Recording started");

    }).catch(function (err) {
        //enable the record button if getUSerMedia() fails
        recordButton.disabled = false;
        stopButton.disabled = true;

    });

    //disable the record button
    recordButton.disabled = true;
    stopButton.disabled = false;
}

function stopRecording() {
    console.log("stopRecording() called");

    //stop microphone access
    gumStream.getAudioTracks()[0].stop();

    //disable the stop button
    stopButton.disabled = true;
    recordButton.disabled = false;

    //tell the recorder to finish the recording (stop recording + encode the recorded audio)
    recorder.finishRecording();

    __log('Recording stopped');
}

function createDownloadLink(blob) {

    var url = URL.createObjectURL(blob);
    var au = document.createElement('audio');
    var li = document.createElement('li');
    var link = document.createElement('a');

    var ID = document.getElementsByTagName("h2")[0].textContent;
    
    __log('save audio to blob - azure')

    //add controls to the <audio> element
    au.controls = true;
    au.src = url;

    //link the a element to the blob
    link.href = url;
    link.download = ID + '.' + 'wav';
    link.innerHTML = link.download;

    //add the new audio and a elements to the li element
    li.appendChild(au);
    li.appendChild(link);

    //add the li element to the ordered list
    recordingsList.appendChild(li);

}

//helper function
function __log(e, data) {
    log.innerHTML += "\n" + e + " " + (data || '');
}