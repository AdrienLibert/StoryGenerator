// Function to generate a story based on user inputs
async function generateStory() {
    // Retrieve values from input fields
    const genre = document.getElementById('genre').value;
    const character = document.getElementById('character').value;
    const location = document.getElementById('location').value;

    try {
        // Send a POST request to the /generate endpoint with input data
        const response = await fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `genre=${genre}&character=${character}&location=${location}`
        });

        // If the response is not OK, throw an error
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        // Parse the response as JSON
        const result = await response.json();

        // Check if segments were returned in the response
        if (result.segments && result.segments.length > 0) {
            // Clear any existing content in the content container
            const contentContainer = document.getElementById('content');
            contentContainer.innerHTML = "";

            // Display each story segment as a separate paragraph
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

// Function to generate images for each story segment
async function generateImage() {
    try {
        // Send a POST request to the /generate_image endpoint
        const response = await fetch('/generate_image', {
            method: 'POST'
        });

        // Handle unsuccessful responses
        if (!response.ok) {
            const result = await response.json();
            if (result.error) {
                alert(result.error);
            } else {
                throw new Error(`Server error: ${response.status}`);
            }
            return;
        }

        // Parse the response to get the image URLs
        const result = await response.json();
        console.log("Image URLs:", result.image_urls);

        // Get the image container in the DOM
        const imageContainer = document.getElementById('image-container');
        
        // Check if the image container exists
        if (!imageContainer) {
            console.error("Image container not found in the DOM.");
            return;
        }

        // Clear any previous images in the container
        imageContainer.innerHTML = "";

        // Create and display each image based on the URLs provided
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

// Function to send the generated story and images as a Twitter thread
async function sendTweet() {
    try {
        // Send a POST request to the /send endpoint
        const response = await fetch('/send', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        // Handle unsuccessful responses
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        // Parse the response and alert the user with the result message
        const result = await response.json();
        alert(result.message);
        console.log(result.message); 

    } catch (error) {
        console.error("Error sending tweet:", error);
        alert("An error occurred while sending the tweet: " + error.message);
    }
}