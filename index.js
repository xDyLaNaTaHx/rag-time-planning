import OpenAI from "openai"

// OpenAI client
const aiClient = new OpenAI({
    apiKey: process.env.AI_KEY,
    baseURL: process.env.AI_URL,
    dangerouslyAllowBrowser: true
})

// String
const userPrompt = "Suggest some gifts for someone who loves hiphop music"

// Message for the prompt
const userMessage = {
    role: "user",
    content: userPrompt
}

// Send an API request with a model and messages array.
const aiResponse = await aiClient.chat.completions.create({
    model: process.env.AI_MODEL,
    messages: [ userMessage ]
})

// Model response
console.log(aiResponse.choices[0].message.content)
    