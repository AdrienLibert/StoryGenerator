async function generateStory() {
    const genre = document.getElementById('genre').value;
    const character = document.getElementById('character').value;
    const location = document.getElementById('location').value;

    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `genre=${genre}&character=${character}&location=${location}`
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const result = await response.json();

        if (result.segments && result.segments.length > 0) {
            const contentContainer = document.getElementById('content');
            contentContainer.innerHTML = "";

            result.segments.forEach((segment, index) => {
                const segmentElement = document.createElement("p");
                segmentElement.innerText = segment;
                segmentElement.style.marginBottom = "15px";
                contentContainer.appendChild(segmentElement);
            });
        } else {
            console.warn("No segments found in the response.");
            alert("No story content generated.");
        }
    } catch (error) {
        console.error("Error:", error);
        alert("An error occurred: " + error.message);
    }
}


async function generateImage() {
    try {
        const response = await fetch('/generate_image', {
            method: 'POST'
        });

        if (!response.ok) {
            const result = await response.json();
            if (result.error) {
                alert(result.error);
            } else {
                throw new Error(`Server error: ${response.status}`);
            }
            return;
        }

        const result = await response.json();
        console.log("Image URLs:", result.image_urls);

        const imageContainer = document.getElementById('image-container');
        
        if (!imageContainer) {
            console.error("Image container not found in the DOM.");
            return;
        }

        imageContainer.innerHTML = "";

        result.image_urls.forEach((imageUrl, index) => {
            if (imageUrl) {
                const imageElement = document.createElement("img");
                imageElement.src = imageUrl;
                imageElement.alt = `Image for segment ${index + 1}`;
                imageElement.classList.add("output-image");
                imageContainer.appendChild(imageElement);
                console.log(`Image added: ${imageUrl}`);
            } else {
                console.warn(`Image for segment ${index + 1} was not generated.`);
            }
        });
    } catch (error) {
        console.error("Error:", error);
        alert("An error occurred: " + error.message);
    }
}


async function sendTweet() {
    try {
        const response = await fetch('/send', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const result = await response.json();
        alert(result.message);
        console.log(result.message); 

    } catch (error) {
        console.error("Error sending tweet:", error);
        alert("An error occurred while sending the tweet: " + error.message);
    }
}

