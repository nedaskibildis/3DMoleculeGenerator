// Initialize Variables 
const addElement = $("#addElement")
const removeElement = $("#removeElement")
const uploadSDF = $("#uploadSDF")
const selectMolecule = $("#selectMolecule")
const addElementSubmit = $("#addElementSubmit")
const addElementForm = $("#addElementForm")
const removeElementForm = $("#removeElementForm")
const uploadSDFDialog = $("#uploadSDFDialog")
const uploadSDFForm = $("#uploadSDFForm")
const selectMoleculeForm = $("#selectMoleculeForm")
const removeElem = $("#removeElemForm")
const listOfDialogs = [addElementForm, removeElementForm, uploadSDFDialog, selectMoleculeForm];


// Get Modals To Display On Click Of Buttons
addElement.click( () => {
    closeForms();
    addElementForm.show("fast");
})

removeElement.click( () => {
    closeForms();
    removeElementForm.show("fast");
})

uploadSDF.click( () => {
    closeForms();
    uploadSDFDialog.show("fast");
})

selectMolecule.click( () => {
    closeForms();
    selectMoleculeForm.show("fast");
})

// Function That Lets A User Add An Element To The DataBase
$(document).ready(() => {
    addElementForm.submit( (e) => {
        e.preventDefault();

        // Get The Value Of Each Input in the HTML
        let elementNumber = document.getElementById("elementNumber");
        let elementCode = document.getElementById("elementCode");
        let elementName = document.getElementById("elementName");
        let color1 = document.getElementById("color1");
        let color2 = document.getElementById("color2");
        let color3 = document.getElementById("color3");
        let elementRadius = document.getElementById("elementRadius");

        // Create a list of inputs that must be set to something
        let inputList = [elementNumber, elementCode, elementName, elementRadius];

        // Loop to make sure there is data in every field
        for (i = 0; i < 4; i++) {
            if (inputList[i].value.length == 0) {
                alert("Please Enter Data In All Fields");
                return;
            }
        }

        // If Statements to verify data
        if (elementCode.value.length > 3 || checkForNum(elementCode.value)) {
            alert("Please Enter A Valid Element Code");
        }
        else if (checkForNum(elementName.value)) {
            alert("Element Names May Not Contain Numbers, Please Try Again");
        }
        else if (elementRadius.value <= 0) {
            alert("Element Radius Must Be Greater Then 0, Please Try Again");
        } else {
            // Create a json object to send to the backend
            let dataToSend = {
                elementNumber: elementNumber.value,
                elementCode: elementCode.value,
                elementName: elementName.value,
                color1: color1.value,
                color2: color2.value,
                color3: color3.value,
                elementRadius: elementRadius.value
            }
            // 
            $.ajax({
                url: '/add-element',
                type: 'POST',
                data: dataToSend,
                success: (data) => {
                console.log("WORKING")
            },
            error: (data) => {
                console.log("ERROR")
            }
            })

            let elementToAdd = document.createElement("input")
            elementToAdd.setAttribute("type", "checkbox")
            elementToAdd.setAttribute("name", elementName.value)
            let elementLabel = document.createElement("label")
            elementLabel.textContent = elementName.value
            elementLabel.appendChild(elementToAdd)
            removeElem.prepend(elementLabel)
            addElementForm.hide("fast");
        }
    })
})


$(document).ready(() => {
    removeElementForm.submit((e) => {
    e.preventDefault();
    let checkedBoxes = document.querySelectorAll('#removeElementForm input[type=checkbox]:checked')
    let allBoxes = document.querySelectorAll('#removeElementForm input[type=checkbox]')
    allBoxes.forEach(function(checkbox) {
    // if the checkbox is checked, remove it
    if (checkbox.checked) {
        label = checkbox.parentNode
        checkbox.remove();
        label.remove()

    }
  });
    let values = [];
    for (let i = 0; i < checkedBoxes.length; i++) {
        values.push(checkedBoxes[i].name)
    }
    let toSend = {
        value: values[0]
    }
    $.ajax({
                url: '/remove-element',
                type: 'POST',
                data: toSend,
                success: (data) => {
                console.log("WORKING")
            },
            error: (data) => {
                console.log("ERROR")
            }
            })

            addElementForm.hide("fast");
    removeElementForm.hide("fast");
    })    
})


$(document).ready(function() {
    uploadSDFForm.submit(function(e) {
        e.preventDefault();
        let form = $("#uploadSDFForm")[0]; 
        var fileData = new FormData();
        fileData.append('sdf-file', $('#sdf-file')[0].files[0])
        fileData.append('moleculeName', $("#moleculeName").val())
        console.log( $("#moleculeName").val())
        $.ajax({
            url: '/upload-sdf',
            type: 'POST',
            data: fileData,
            processData: false,
            contentType: false,
            success: function(data) {
                console.log("WORKING")
            },
            error: function(data) {
                console.log("ERROR")
            }
        });
        let newOption = $("<option>").val($("#moleculeName").val()).text($("#moleculeName").val());
        let selectMenu = $("#selectMoleculeMenu");
        selectMenu.append(newOption);
        uploadSDFDialog.hide("fast");
        })
})

$(document).ready(() => {
    selectMoleculeForm.submit((e) => {
    e.preventDefault();
    let selectedOption = $("#selectMoleculeMenu option:selected").val()
    let toAdd = `<img src="${selectedOption}.svg">`
    let svgArea = document.getElementById("molDisplay")
    while (svgArea.firstChild) {
        svgArea.removeChild(svgArea.firstChild)
    }
    $('#molDisplay').html(toAdd)
    selectMoleculeForm.hide("fast");
})
})



// Simple function that checks for a number in a string using RegEx
function checkForNum(string) {
    return /\d/.test(string);
}

function closeForms() {
    for (let i = 0; i < 4; i++){
        listOfDialogs[i].hide("fast");
    }
}