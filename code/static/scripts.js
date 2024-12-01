function playAudio(text, speaker=null, stability=0.5) {
    // Use the fetch API to send a POST request to the server
    fetch("/audio", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({text: text,
                                    speaker: speaker,
                                    stability: stability})
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Failed to fetch audio");
        }
        return response.blob();
    })
    .then(audioBlob => {
        // Convert the response to a blob and set it as the source of the audio player
        const audioUrl = URL.createObjectURL(audioBlob);
        const audioPlayer = document.getElementById("audioPlayer");
        audioPlayer.src = audioUrl;
        audioPlayer.play();
    })
    .catch(error => {
        console.error("Error:", error);
    });
}


function sendRequest(path, method, requestBody) {
    fetch(path, {
      method: method,
      headers: {'Content-Type': 'application/json',},
      body: JSON.stringify(requestBody)
      })

      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok ' + response.statusText);
        }
        return response.json(); // Parse the JSON response
      })

      .then(data => {
        console.log(data); // Handle the data from the response
      })

      .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
      });
}

async function sendRequestWait(path, method, requestBody) {
  try {
    const response = await fetch(path, {
      method: method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
        throw new Error('Network response was not ok ' + response.statusText);
    }

    const data = await response.json(); // Parse the JSON response
    console.log(data); // Handle the data from the response
  } catch (error) {
    console.error('There was a problem with the fetch operation:', error);
  }
}


function updateSetting(setting){
    const settingElement = document.getElementById(setting);
    const inputValue = settingElement.value;
    const requestBody = {setting: setting, value: inputValue};
    sendRequest("settings/update", "PUT", requestBody);

    if (setting === "speaker"){
        text = `Hi there! I'm ${inputValue}.`;
        playAudio(text, inputValue, 0.9);
    }

    else if (setting === "story_sections"){
        const storySectionsValueElement = document.getElementById("story_sections_value");
        storySectionsValueElement.textContent = inputValue;
    }
}


function getStory(storyId){
    window.location.href = `/library/${storyId}`
}


function deleteStory(storyId){
    const requestBody = {story_id: storyId};
    sendRequest("/library/delete_story", "DELETE", requestBody)
    window.location.href = "/library";
}


function updateInput(itemsClass, inputId, is_voice_guidance) {

    const items = document.querySelectorAll(`.${itemsClass}`);
    const input = document.getElementById(inputId);

    items.forEach(item => {
        item.addEventListener("click", () => {

            const highlightedItem = document.querySelector(`.${itemsClass}-highlighted`);

            if (highlightedItem) {
                highlightedItem.classList.remove(`${itemsClass}-highlighted`);
            }

            item.classList.add(`${itemsClass}-highlighted`);
            input.value = item.getAttribute("data-value");

            if (is_voice_guidance) {
                playAudio(input.value, null, 0.9)
            }
        });
    });
}


function setStorySetting(story_setting){
    const inputValue = document.getElementById(`${story_setting}-input`).value;
    const requestBody = {[story_setting]: inputValue};
    sendRequest(`/${story_setting}/set`, "POST", requestBody)
}


function validateEmail(email) {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
}


function openEmailInput(storyId) {
    document.getElementById("email-popup").style.display = "block";
    document.getElementById("email-story-id").value = storyId;
}


function closeEmailInput() {
    document.getElementById("email-popup").style.display = "none";
}


function submitEmail() {
    const email = document.getElementById("email-input").value;

    if (!validateEmail(email)){
      alert("Please provide a valid email address");
      return
    }

    const storyId = document.getElementById("email-story-id").value;
    const requestBody = {receiver_email: email, story_id: storyId};
    sendRequest("/library/email_story", "POST", requestBody);

    alert("Email Sent!");
    closeEmailInput();
}


async function generateSection(gen_type) {
    const loadingScreen = document.getElementById('loading-screen');
    loadingScreen.style.display = 'flex';

    const requestBody = {gen_type: gen_type}
    await sendRequestWait("/story/generate_section", "POST", requestBody)

    window.location.href = "/story";
}


async function saveStory(){
    const loadingScreen = document.getElementById('loading-screen');
    loadingScreen.style.display = 'flex';
    await sendRequestWait("/story_end/save", "POST", null)
    alert("Story saved to your Library!")
    window.location.href = "/";
}
