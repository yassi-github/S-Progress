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

let problemsElement = document.getElementById('problems')
let resultAreaElement = document.getElementById('result-area')

// get all problems
getApi('/problems').then(data => {
    // show problems
    data.forEach(problem => {
        let problemElement = document.createElement('div')
        let problemElementInputareaID = 'input-command-' + problem.id
        problemElement.className = 'problem'
        problemElement.id = 'problem-' + problem.id
        problemElement.innerHTML = `
            <div class="problem-title">
                <h3>${problem.title}</h3>
                <p>${problem.text}</p>
                <a onclick="" href="problems/${problem.id}/file">No.${problem.id} Question File</a>
            </div>
            <div id="input-area">
                <input autofocus type="text" size="50" id="${problemElementInputareaID}" placeholder="cat q_${problem.id}.txt | ...">
                <button id="send-button-${problem.id}">EXECUTE</button>
            </div>
            `
        problemsElement.appendChild(problemElement)

        // submit solution
        document.getElementById(`send-button-${problem.id}`).addEventListener('click', () => {
            let urlEncodedScript = encodeURIComponent(document.getElementById(problemElementInputareaID).value)
            let answerRequestBody = {
                "username": "sample",
                "script": urlEncodedScript
            }
            let url = location.origin + `/problems/${problem.id}/answer`

            sendPost(url, answerRequestBody).then(response => {
                // show command result
                // HTTPExceptionのときはdetailにメッセージが入る
                if (response.detail) {
                    resultAreaElement.innerHTML = response.detail
                } else {
                    resultAreaElement.innerHTML = decodeURIComponent(response.result).replaceAll(/\n/g, '<br>')
                }

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
        // input要素が入力されていてかつ、Enterが押されたら、button要素をクリックする
        document.getElementById(problemElementInputareaID).addEventListener('keyup', e => {
            if (e.key === 'Enter') {
                document.getElementById(`send-button-${problem.id}`).click()
            }
        })
    })
})
