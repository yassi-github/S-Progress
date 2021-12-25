async function sendPost(url, data) {
    isCorrectElement.textContent = 'Executing...'
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

function renewResult(rawScript, jsonStdout, showingResultIdx) {
    let prevIdx = showingResultIdx - 1
    let nextIdx = showingResultIdx + 1
    try {
        prevResultAreaElement.innerHTML = jsonStdout[prevIdx][prevIdx].join('<br>')
    } catch (error) {
        prevResultAreaElement.innerHTML = ''
    }
    
    currentResultAreaElement.innerHTML = jsonStdout[showingResultIdx][showingResultIdx].join('<br>')
    
    try {
        nextResultAreaElement.innerHTML = jsonStdout[nextIdx][nextIdx].join('<br>')
    } catch (error) {
        nextResultAreaElement.innerHTML = ''
    }

    // show your command
    yourCommandElement.innerHTML = '<b>'+rawScript.split('|').slice(0, showingResultIdx + 1).join('|')+'</b>'+'👀'+rawScript.split('|').slice(showingResultIdx + 1).join('|')
}

let problemsElement = document.getElementById('problems')
let resultAreaElement = document.getElementById('result-area')
let prevResultAreaElement = document.getElementById('prev-result')
let currentResultAreaElement = document.getElementById('current-result')
let nextResultAreaElement = document.getElementById('next-result')
let isCorrectElement = document.getElementById('is-correct')
let prevButtonElement = document.getElementById('prev-button')
let nextButtonElement = document.getElementById('next-button')
let yourCommandElement = document.getElementById('your-command')
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
                <a href="problems/${problem.id}/hint1">No.${problem.id} Hint 1</a>
                <a href="problems/${problem.id}/hint2">No.${problem.id} Hint 2</a>
            </div>
            <div id="input-area">
                <input autofocus type="text" size="50" id="${problemElementInputareaID}" placeholder="cat q_${problem.id}.txt | ...">
                <button id="send-button-${problem.id}">EXECUTE</button>
            </div>
            `
        problemsElement.appendChild(problemElement)

        // submit solution
        document.getElementById(`send-button-${problem.id}`).addEventListener('click', () => {
            let rawScript = document.getElementById(problemElementInputareaID).value
            let urlEncodedScript = encodeURIComponent(rawScript)
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
                    // resultAreaElement.innerHTML = decodeURIComponent(response.result).replaceAll(/\n/g, '<br>')
                    let resultJsonData = decodeURIComponent(response.result)
                    let jsonStdout = JSON.parse(resultJsonData)['stdout']
                    let finalCommandResultPhase = jsonStdout.length - 1
                    // 現在注目している出力のインデックス
                    let showingResultIdx = finalCommandResultPhase
                    // show final result
                    renewResult(rawScript, jsonStdout, showingResultIdx)
                    prevButtonElement.addEventListener('click', e => {
                        // 0 or lower: do nothing
                        if (showingResultIdx > 0) {
                            showingResultIdx -= 1
                            renewResult(rawScript, jsonStdout, showingResultIdx)
                        }
                    })
                    nextButtonElement.addEventListener('click', e => {
                        // last array idx or higher: do nothing
                        if (showingResultIdx < finalCommandResultPhase) {
                            showingResultIdx += 1
                            renewResult(rawScript, jsonStdout, showingResultIdx)
                        }
                    })
                }

                // C or W
                if (response.is_correct) {
                    isCorrectElement.textContent = 'Correct!'
                } else {
                    isCorrectElement.textContent = 'Incorrect!'
                }
            }, error => {
                // コマンドがおかしくて実行エラーが出た場合、コンテナが死んでしまう。
                // つまりフロントに返るのは`Internal Server Error`という文字列。
                currentResultAreaElement.innerHTML = "Error...<br>The command could not be executed correctly."
                isCorrectElement.innerHTML = 'Error!'
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
