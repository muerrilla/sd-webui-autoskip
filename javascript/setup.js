function setupAutoSkip() {
  fixAccordionAutoSkip('tab_txt2img');  
  fixAccordionAutoSkip('tab_img2img');  
  fixInputsAutoSkip('tab_txt2img');
  fixInputsAutoSkip('tab_img2img');
}

function fixInputsAutoSkip(tab) {
  const npwSlider = document.querySelector(`#${tab} #autoskip-slider`);

  npwSlider.querySelector('.head').remove(); 

  const newSpan = document.createElement("span");
  newSpan.innerHTML = "Skip";
  const ancestor = npwSlider.parentNode.parentNode.parentNode;
  ancestor.insertBefore(newSpan, ancestor.firstChild);

  document.querySelector(`#${tab} #autoskip-number input[type="number"]`).setAttribute("step", "0.01");
}

function fixAccordionAutoSkip(tab) {
  document.querySelector(`#${tab} #autoskip .icon`).remove();
  document.querySelector(`#${tab} #autoskip .open`).remove();  
}

onUiLoaded(setupAutoSkip);
