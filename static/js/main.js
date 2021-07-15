async function sendPost(url, data) {
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    return await response.json()
}

async function getApi(url) {
    const response = await fetch(url)
    return await response.json()
}

let problemTitleElement = document.getElementById('title')
let problemDescriptionElement = document.getElementById('desc')
let resultAreaElement = document.getElementById('result-area')

// get all problems
getApi('/problems').then(data => {
    problemTitleElement.innerText = data.title
    problemDescriptionElement.innerText = data.description
})

// submit solution
document.getElementById('send-button').addEventListener('click', () => {
    let b64ScriptText = btoa(document.getElementById('input-area').value)
    let answerRequestBody = {
        "username": "sample",
        "script": b64ScriptText
    }
    let url = location.origin + '/problems/1/answer'

    sendPost(url, answerRequestBody).then(response => {
        // show command result
        resultAreaElement.innerHTML = atob(response.result).replace(/\n/g, '<br>')
        
        // C or W
        if (response.is_correct) {
            document.getElementById('is-correct').innerHTML = 'Correct!'
        } else {
            document.getElementById('is-correct').innerHTML = 'Incorrect!'
        }
    }, error => {
        resultAreaElement.innerHTML = error
    })
})

