$('#payerselect').on('change', function()
{
    value= this.value;
    console.log(value)
  });

function getPayerFormData(form) {
    // creates a FormData object and adds chips text
    var formData = new FormData(document.getElementById(form));
    console.log(formData)
    return formData
};

function jqAlert(outputMsg, titleMsg, onCloseCallback) {
    if (!titleMsg)
        titleMsg = 'Alert';

    if (!outputMsg)
        outputMsg = 'No Message to Display.';

    $("<div></div>").html(outputMsg).dialog({
        title: titleMsg,
        resizable: false,
        modal: true,
        buttons: {
            "OK": onCloseCallback,
            "Cancel": function() {
          $( this ).dialog( "destroy" );
            }

        }},
    });
