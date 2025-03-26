document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('uploads')
    const fileList = document.getElementById('file-list')

    fileInput?.addEventListener('change', () => {
        fileList.innerHTML = ''
        const files = Array.from(fileInput.files)

        files.forEach((file, index) => {
            const listItem = document.createElement('li')
            listItem.className = 'list-group-item d-flex justify-content-between align-items-center'
            listItem.innerHTML = `
                ${file.name}
                <div class="form-check">
                    <input class="form-check-input web-build-checkbox" type="checkbox" data-index="${index}" id="checkbox-${index}">
                    <label class="form-check-label" for="checkbox-${index}">This file will be played in the browser</label>
                </div>`
            fileList.appendChild(listItem)
        })
    })

    fileList?.addEventListener('change', (event) => {
        if (event.target.classList.contains('web-build-checkbox')) {
            const checkboxes = document.querySelectorAll('.web-build-checkbox')

            if (event.target.checked) {
                checkboxes.forEach(checkbox => {
                    if (checkbox !== event.target) {
                        checkbox.disabled = true
                        checkbox.checked = false
                    }
                })
            } else {
                checkboxes.forEach(checkbox => {
                    checkbox.disabled = false
                })
            }
        }
    })

    document.getElementById('edit-game-form')?.addEventListener('submit', () => {
        const uploadsMetadata = Array.from(document.querySelectorAll('#file-list .list-group-item')).map(item => {
            const webBuildCheckbox = item.querySelector('.web-build-checkbox');
            return {
                is_web_build: webBuildCheckbox.checked
            }
        })

        document.getElementById("uploads_metadata").value = JSON.stringify(uploadsMetadata);
    })


    const iframePlaceholder = document.getElementById('iframe-placeholder')
    const runGameButton = document.getElementById('run-game-button')
    
    runGameButton?.addEventListener('click', () => {
        runGameButton.remove()
        const iframe = iframePlaceholder.getAttribute('data-iframe')
        iframePlaceholder.removeAttribute('data-iframe')
        iframePlaceholder.innerHTML = iframe
    })
})
