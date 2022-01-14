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
    let spanInsertedScript = '<span>' + rawScript.replaceAll('|', '</span>|<span>') + '</span>'
    yourCommandElement.innerHTML = '<b>'
        + spanInsertedScript.split('|').slice(0, showingResultIdx).join('|').replaceAll('</span>|<span>', '|').replace('<span>', '<span style="background-color: darkblue;color: white;">')
        + '</span>|<span>'
        + spanInsertedScript.split('|').slice(showingResultIdx, showingResultIdx + 1).join('|').replace('<span>', '<span style="background-color: black;color: white;">')
        // pipe version
        // + '</b>' + '|'
        // PiMie version
        + '</b>' + '👀|'
        + spanInsertedScript.split('|').slice(showingResultIdx + 1).join('|').replace('<span>', '<span style="background-color: forestgreen;color: white;">')



    // show your command to label
    prevLabelElement.innerText = rawScript.split('|').slice(showingResultIdx - 1, showingResultIdx)
    currentLabelElement.innerText = rawScript.split('|').slice(showingResultIdx, showingResultIdx + 1)
    nextLabelElement.innerText = rawScript.split('|').slice(showingResultIdx + 1, showingResultIdx + 2)
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
let prevLabelElement = document.getElementById('prev-cmd')
let currentLabelElement = document.getElementById('current-cmd')
let nextLabelElement = document.getElementById('next-cmd')

let incorrectedCountArr = []

// get all problems
getApi('/problems').then(data => {
    // show problems
    data.forEach(problem => {
        incorrectedCountArr.push(0)
        let problemElement = document.createElement('div')
        let problemElementInputareaID = 'input-command-' + problem.id
        problemElement.className = 'problem'
        problemElement.id = 'problem-' + problem.id
        let problemTextBr = problem.text.replaceAll('\n', '<br>')
        problemElement.innerHTML = `
            <div class="problem-title">
                <h3>${problem.title}</h3>
                <p>${problemTextBr}</p>
                <a onclick="" href="problems/${problem.id}/file">q_${problem.id}.txt</a>
                <button id="hint1-${problem.id}">Hint 1</button>
                <button id="hint2-${problem.id}">Hint 2</button>
                <button id="answer-${problem.id}" style="display: none;">Answer</button>
            </div>
            <div id="input-area">
                <input autofocus type="text" id="${problemElementInputareaID}" placeholder="cat q_${problem.id}.txt | ..." style="width: 90%;">
                <button id="send-button-${problem.id}">EXECUTE</button>
            </div>
            `
        problemsElement.appendChild(problemElement)

        // show sample answer and hint
        document.getElementById(`hint1-${problem.id}`).addEventListener('click', () => {
            getApi(`/problems/${problem.id}/hint1`).then(data => {
                alert(data.hint1)
            })
        })
        document.getElementById(`hint2-${problem.id}`).addEventListener('click', () => {
            getApi(`/problems/${problem.id}/hint2`).then(data => {
                alert(data.hint2)
            })
        })
        document.getElementById(`answer-${problem.id}`).addEventListener('click', () => {
            getApi(`/problems/${problem.id}/answer`).then(data => {
                alert(data.shell)
            })
        })

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
                    currentResultAreaElement.innerHTML = response.detail
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
                    incorrectedCountArr[problem.id - 1] = 0
                } else {
                    isCorrectElement.textContent = 'Incorrect!'
                    incorrectedCountArr[problem.id - 1] += 1
                    // incorrect (or error)が5回になったら，answerボタンが表示される
                    if (incorrectedCountArr[problem.id - 1] > 4) {
                        document.getElementById(`answer-${problem.id}`).style.display = ''
                    }
                }
            }, error => {
                // コマンドがおかしくて実行エラーが出た場合、コンテナが死んでしまう。
                // つまりフロントに返るのは`Internal Server Error`という文字列。
                currentResultAreaElement.innerHTML = "Error...<br>The command could not be executed correctly."
                isCorrectElement.innerHTML = 'Error!'

                // エラーの場合もincoreect countをプラス
                incorrectedCountArr[problem.id - 1] += 1
                if (incorrectedCountArr[problem.id - 1] > 5) {
                    document.getElementById(`answer-${problem.id}`).style.display = ''
                }
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
